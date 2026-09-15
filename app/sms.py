
import logging

import requests

from app.config import settings

logger = logging.getLogger("oncall.sms")

class SmsResult:
    def __init__(self, status: str, sid: str | None = None, error: str | None = None):
        self.status = status
        self.sid = sid
        self.error = error


def send_sms(to_number: str, body: str) -> SmsResult:
    """Send an SMS via ClickSend, or log-only if DRY_RUN is set.

    Kept as a thin wrapper so the notify endpoint doesn't care which
    provider is behind it - swap this out if you move providers later.
    """
    if settings.dry_run:
        logger.info("[DRY RUN] Would send SMS to %s: %s", to_number, body)
        return SmsResult(status="dry_run")

    import clicksend_client
    from clicksend_client import SmsMessage
    from clicksend_client.rest import ApiException

    configuration = clicksend_client.Configuration()
    configuration.username = settings.clicksend_username
    configuration.password = settings.clicksend_api_key

    api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))

    message_kwargs = {"source": "python", "body": body, "to": to_number}
    if settings.clicksend_from_number:
        message_kwargs["from_"] = settings.clicksend_from_number

    sms_message = SmsMessage(**message_kwargs)
    sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])

    try:
        api_response = api_instance.sms_send_post(sms_messages)
        result = api_response.data.messages[0]
        return SmsResult(status=result.status, sid=result.message_id)
    except ApiException as exc:
        logger.exception("Failed to send SMS to %s", to_number)
        return SmsResult(status="failed", error=str(exc))