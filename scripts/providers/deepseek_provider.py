"""
DeepSeek API — Official balance endpoint.
Docs: https://api-docs.deepseek.com/zh-cn/api/get-user-balance
"""

import os
import requests


class DeepSeekProvider:
    name = "DeepSeek"

    def collect(self) -> dict:
        key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not key:
            raise ValueError("DEEPSEEK_API_KEY not set")

        resp = requests.get(
            "https://api.deepseek.com/user/balance",
            headers={"Authorization": f"Bearer {key}"},
            timeout=15,
        )
        resp.raise_for_status()
        body = resp.json()

        if not body.get("is_available"):
            raise RuntimeError("DeepSeek account has no available balance")

        infos   = body.get("balance_infos", [])
        results = []
        for info in infos:
            results.append({
                "currency":          info.get("currency", "CNY"),
                "total_balance":     float(info.get("total_balance", 0)),
                "granted_balance":   float(info.get("granted_balance", 0)),
                "topped_up_balance": float(info.get("topped_up_balance", 0)),
            })

        primary  = results[0] if results else {}
        total    = primary.get("total_balance", 0)
        granted  = primary.get("granted_balance", 0)
        topped   = primary.get("topped_up_balance", 0)
        currency = primary.get("currency", "CNY")

        return {
            "unit": currency,
            "total_balance": total,
            "granted_balance": granted,
            "topped_up_balance": topped,
            "is_available": body.get("is_available", False),
            "balance_infos": results,
            "display_balance": f"¥{total:.4f} (cash ¥{topped:.4f} + granted ¥{granted:.4f})",
            "note": "",
        }

    def summary(self, data: dict) -> str:
        return data.get("display_balance", "")
