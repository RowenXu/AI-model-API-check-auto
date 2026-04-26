"""
阿里云百炼 (DashScope) — No dedicated token-quota API.
Uses Aliyun BSS OpenAPI to query overall account cash/voucher balance (CNY).
Requires: ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET
"""

import json
import os

try:
    from aliyunsdkcore.client import AcsClient
    from aliyunsdkcore.request import CommonRequest
    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


class AliyunProvider:
    name = "阿里云百炼 (DashScope)"

    def collect(self) -> dict:
        if not SDK_AVAILABLE:
            raise ImportError(
                "aliyun-python-sdk-core not installed. "
                "Run: pip install aliyun-python-sdk-core aliyun-python-sdk-bssopenapi"
            )
        ak_id  = os.environ.get("ALIYUN_ACCESS_KEY_ID", "")
        ak_sec = os.environ.get("ALIYUN_ACCESS_KEY_SECRET", "")
        if not ak_id or not ak_sec:
            raise ValueError("ALIYUN_ACCESS_KEY_ID or ALIYUN_ACCESS_KEY_SECRET not set")

        client = AcsClient(ak_id, ak_sec, "cn-hangzhou")

        request = CommonRequest()
        request.set_accept_format("json")
        request.set_domain("business.aliyuncs.com")
        request.set_method("GET")
        request.set_protocol_type("https")
        request.set_version("2017-12-14")
        request.set_action_name("QueryAccountBalance")

        response = json.loads(client.do_action_with_exception(request))

        if response.get("Code") != "Success":
            raise RuntimeError(f"Aliyun BSS API error: {response.get('Message')}")

        balance          = response["Data"]
        available_amount = float(balance.get("AvailableAmount", 0))
        currency         = balance.get("Currency", "CNY")
        available_cash   = float(balance.get("AvailableCashAmount", 0))
        credit_amount    = float(balance.get("CreditAmount", 0))

        return {
            "unit": currency,
            "available_amount": available_amount,
            "available_cash_amount": available_cash,
            "credit_amount": credit_amount,
            "display_balance": f"{available_amount:.2f} {currency} available",
            "note": "Aliyun account balance (cash + vouchers). DashScope free-token quota viewable in console only.",
        }

    def summary(self, data: dict) -> str:
        return data.get("display_balance", "")
