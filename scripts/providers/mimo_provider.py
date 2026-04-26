"""
小米 MiMo API Provider
官方未提供余额查询 REST 接口，采用"探针法"：
  - 发送最轻量的 chat 请求（max_tokens=1），根据响应状态码判断账户可用性
  - HTTP 402 → 余额不足 / HTTP 200 → 可用 / HTTP 401 → Key 无效
  - 同时尝试解析响应头中可能携带的用量信息（X-RateLimit-Remaining-Tokens 等）

Base URL: https://api.xiaomimimo.com/v1
Auth:     Header "api-key: <KEY>"
Docs:     https://api.xiaomimimo.com/docs
"""

import os
import requests

PROBE_URL   = "https://api.xiaomimimo.com/v1/chat/completions"
PROBE_MODEL = "mimo-v2-flash"


class MiMoProvider:
    name = "小米 MiMo"

    def collect(self) -> dict:
        key = os.environ.get("MIMO_API_KEY", "")
        if not key:
            raise ValueError("MIMO_API_KEY not set")

        headers = {
            "api-key": key,
            "Content-Type": "application/json",
        }
        payload = {
            "model": PROBE_MODEL,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 1,
        }

        resp = requests.post(PROBE_URL, headers=headers, json=payload, timeout=20)

        if resp.status_code == 402:
            return {
                "unit": "CNY",
                "account_status": "insufficient_balance",
                "is_available": False,
                "display_balance": "余额不足 (HTTP 402)",
                "note": "No public balance API. Probe returned 402.",
            }

        resp.raise_for_status()

        body               = resp.json()
        remaining_tokens   = resp.headers.get("X-RateLimit-Remaining-Tokens", "N/A")
        remaining_requests = resp.headers.get("X-RateLimit-Remaining-Requests", "N/A")
        usage              = body.get("usage", {})

        return {
            "unit": "CNY",
            "account_status": "available",
            "is_available": True,
            "probe_model": PROBE_MODEL,
            "probe_usage": usage,
            "ratelimit_remaining_tokens":   remaining_tokens,
            "ratelimit_remaining_requests": remaining_requests,
            "display_balance": f"账户可用 ✅ (限流剩余 tokens: {remaining_tokens}, requests: {remaining_requests})",
            "note": (
                "No public balance API. "
                "Availability confirmed via probe request. "
                "Check https://api.xiaomimimo.com/docs for balance page."
            ),
        }

    def summary(self, data: dict) -> str:
        return data.get("display_balance", "")
