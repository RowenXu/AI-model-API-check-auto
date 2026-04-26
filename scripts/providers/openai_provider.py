"""
OpenAI (ChatGPT / Codex) — Billing via semi-official dashboard endpoints.
No public balance API exists; uses /dashboard/billing/* endpoints.
"""

import os
import requests
from datetime import date

BASE = "https://api.openai.com"


class OpenAIProvider:
    name = "OpenAI (ChatGPT Codex)"

    def collect(self) -> dict:
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            raise ValueError("OPENAI_API_KEY not set")

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

        sub_resp = requests.get(
            f"{BASE}/dashboard/billing/subscription", headers=headers, timeout=15
        )
        sub_resp.raise_for_status()
        sub = sub_resp.json()
        hard_limit_usd = sub.get("hard_limit_usd") or sub.get("system_hard_limit_usd", 0)

        today = date.today()
        start = today.replace(day=1).isoformat()
        end   = today.isoformat()
        usage_resp = requests.get(
            f"{BASE}/dashboard/billing/usage",
            headers=headers,
            params={"start_date": start, "end_date": end},
            timeout=15,
        )
        usage_resp.raise_for_status()
        usage_data = usage_resp.json()
        used_cents = usage_data.get("total_usage", 0)
        used_usd   = round(used_cents / 100, 4)
        remaining  = round(hard_limit_usd - used_usd, 4)

        return {
            "unit": "USD",
            "hard_limit_usd": hard_limit_usd,
            "used_this_month_usd": used_usd,
            "remaining_usd": remaining,
            "period_start": start,
            "period_end": end,
            "display_balance": f"${remaining:.2f} remaining (${used_usd:.2f} / ${hard_limit_usd:.2f})",
            "note": f"Month-to-date usage ({start} ~ {end})",
        }

    def summary(self, data: dict) -> str:
        return data.get("display_balance", "")
