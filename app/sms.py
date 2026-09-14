import base64
import logging

import requests

from app.config import settings

logger = logging.getLogger("oncall.sms")

SMS_EVERYONE_URL = "https://smseveryone.com/api/campaign"


class SmsResult:
    def __init__(self, status: str, sid: str | None = None, error: str | None = None):
        self.status = status
        self.sid = sid
        self.error = error


def _to_intl_no_plus(number: str) -> str:
    """SMS Everyone wants international format without the leading '+', e.g. 6421xxxxxxx."""
    return number.lstrip("+")


def send_sms(to_number: str, body: str) -> SmsResult:
    """Send an SMS via SMS Everyone, or log-only if DRY_RUN is set."""
    if settings.dry_run:
        logger.info("[DRY RUN] Would send SMS to %s: %s", to_number, body)
        return SmsResult(status="dry_run")

    auth = base64.b64encode(
        f"{settings.smseveryone_username}:{settings.smseveryone_password}".encode()
    ).decode()

    payload = {
        "Message": body,
        "Originator": settings.smseveryone_originator,
        "Destinations": [_to_intl_no_plus(to_number)],
        "Action": "create",
    }

    try:
        resp = requests.post(
            SMS_EVERYONE_URL,
            json=payload,
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("Code") != 0:
            return SmsResult(status="failed", error=str(data))
        return SmsResult(status="sent", sid=str(data.get("CampaignId")))
    except requests.RequestException as exc:
        logger.exception("Failed to send SMS to %s", to_number)
        return SmsResult(status="failed", error=str(exc))