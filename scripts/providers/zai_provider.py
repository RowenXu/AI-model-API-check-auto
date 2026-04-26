"""
Z.ai (智谱 AI 国际版) Provider
Strategy A (主选): 尝试调用 /api/paas/v4/user/balance（非公开，社区发现）
Strategy B (降级): 探针法 —— 发送最小推理请求，通过状态码判断可用性

Base URL (国际): https://api.z.ai/api/paas/v4
Auth:            Authorization: Bearer <KEY>
Docs:            https://docs.z.ai
"""

import os
import requests

BASE_URL    = "https://api.z.ai/api/paas/v4"
PROBE_MODEL = "glm-4-flash"


class ZaiProvider:
    name = "Z.ai (智谱AI)"

    def collect(self) -> dict:
        key = os.environ.get("ZAI_API_KEY", "")
        if not key:
            raise ValueError("ZAI_API_KEY not set")

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

        balance_result = self._try_balance_api(headers)
        if balance_result:
            return balance_result

        return self._probe(headers)

    def _try_balance_api(self, headers: dict):
        try:
            resp = requests.get(
                f"{BASE_URL}/user/balance",
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 404:
                return None
            if resp.status_code == 402:
                return {
                    "unit": "CNY",
                    "account_status": "insufficient_balance",
                    "is_available": False,
                    "data_source": "balance_api_attempt",
                    "display_balance": "余额不足 (HTTP 402)",
                    "note": "Balance API returned 402.",
                }
            resp.raise_for_status()
            body    = resp.json()
            balance = (
                body.get("balance")
                or body.get("available_amount")
                or body.get("data", {}).get("balance")
            )
            if balance is not None:
                return {
                    "unit": "CNY",
                    "account_status": "available",
                    "is_available": True,
                    "raw_balance": balance,
                    "data_source": "balance_api",
                    "display_balance": f"¥{float(balance):.4f} available",
                    "note": "Retrieved via undocumented /user/balance endpoint.",
                }
        except Exception:
            pass
        return None

    def _probe(self, headers: dict) -> dict:
        payload = {
            "model": PROBE_MODEL,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 1,
        }
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=20,
        )

        if resp.status_code == 402:
            return {
                "unit": "CNY",
                "account_status": "insufficient_balance",
                "is_available": False,
                "data_source": "probe",
                "display_balance": "余额不足 (HTTP 402)",
                "note": "No public balance API. Probe returned 402.",
            }

        resp.raise_for_status()

        body               = resp.json()
        usage              = body.get("usage", {})
        remaining_tokens   = resp.headers.get("X-RateLimit-Remaining-Tokens", "N/A")
        remaining_requests = resp.headers.get("X-RateLimit-Remaining-Requests", "N/A")

        return {
            "unit": "CNY",
            "account_status": "available",
            "is_available": True,
            "probe_model": PROBE_MODEL,
            "probe_usage": usage,
            "ratelimit_remaining_tokens":   remaining_tokens,
            "ratelimit_remaining_requests": remaining_requests,
            "data_source": "probe",
            "display_balance": f"账户可用 ✅ (限流剩余 tokens: {remaining_tokens})",
            "note": (
                "No public balance API. "
                "Availability confirmed via probe request. "
                "Check https://dashboard.z.ai for account balance."
            ),
        }

    def summary(self, data: dict) -> str:
        return data.get("display_balance", "")
