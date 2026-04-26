"""
GitHub Copilot — Official REST API for seat billing.
Requires a PAT or GitHub App token with manage_billing:copilot (or admin:org).
Set GH_COPILOT_ORG to your GitHub organization login.
"""

import os
import requests


class CopilotProvider:
    name = "GitHub Copilot"

    def collect(self) -> dict:
        token = os.environ.get("GH_COPILOT_TOKEN", "")
        org   = os.environ.get("GH_COPILOT_ORG", "")
        if not token:
            raise ValueError("GH_COPILOT_TOKEN not set")
        if not org:
            raise ValueError("GH_COPILOT_ORG not set")

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        resp = requests.get(
            f"https://api.github.com/orgs/{org}/copilot/billing",
            headers=headers,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()

        breakdown = data.get("seat_breakdown", {})
        total    = breakdown.get("total", 0)
        active   = breakdown.get("active_this_cycle", 0)
        inactive = breakdown.get("inactive_this_cycle", 0)
        pending  = breakdown.get("pending_invitation", 0)

        return {
            "unit": "seats",
            "seats_total": total,
            "seats_active_this_cycle": active,
            "seats_inactive_this_cycle": inactive,
            "seats_pending_invitation": pending,
            "plan_type": data.get("plan_type", "unknown"),
            "seat_management_setting": data.get("seat_management_setting", "unknown"),
            "display_balance": f"{active} / {total} seats active",
            "note": f"plan={data.get('plan_type', '?')}",
        }

    def summary(self, data: dict) -> str:
        return data.get("display_balance", "")
