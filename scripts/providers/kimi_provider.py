"""
Kimi API (Moonshot AI) — Official balance endpoint.
Docs: https://platform.moonshot.cn/docs/api/misc
"""

import os
import requests


class KimiProvider:
    name = "Kimi (Moonshot)"

    def collect(self) -> dict:
        key = os.environ.get("KIMI_API_KEY", "")
        if not key:
            raise ValueError("KIMI_API_KEY not set")

        resp = requests.get(
            "https://api.moonshot.cn/v1/users/me/balance",
            headers={"Authorization": f"Bearer {key}"},
            timeout=15,
        )
        resp.raise_for_status()
        body = resp.json()

        if not body.get("status"):
            raise RuntimeError(f"Kimi API returned error: {body}")

        d         = body["data"]
        available = float(d.get("available_balance", 0))
        voucher   = float(d.get("voucher_balance", 0))
        cash      = float(d.get("cash_balance", 0))

        return {
            "unit": "CNY",
            "available_balance": available,
            "voucher_balance": voucher,
            "cash_balance": cash,
            "display_balance": f"¥{available:.4f} (cash ¥{cash:.4f} + voucher ¥{voucher:.4f})",
            "note": "",
        }

    def summary(self, data: dict) -> str:
        return data.get("display_balance", "")
