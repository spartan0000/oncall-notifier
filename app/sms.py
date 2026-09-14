import logging

from app.config import settings

logger = logging.getLogger("oncall.sms")


class SmsResult:
    def __init__(self, status: str, sid: str | None = None, error: str | None = None):
        self.status = status
        self.sid = sid
        self.error = error


def send_sms(to_number: str, body: str) -> SmsResult:
    """Send an SMS via Twilio, or log-only if DRY_RUN is set.

    Kept as a thin wrapper so the notify endpoint doesn't care which
    provider is behind it - swap this out if you move off Twilio later.
    """
    if settings.dry_run:
        logger.info("[DRY RUN] Would send SMS to %s: %s", to_number, body)
        return SmsResult(status="dry_run")

    try:
        from twilio.rest import Client

        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        message = client.messages.create(
            to=to_number,
            from_=settings.twilio_from_number,
            body=body,
        )
        return SmsResult(status=message.status, sid=message.sid)
    except Exception as exc:  # noqa: BLE001 - surface any provider error to the caller
        logger.exception("Failed to send SMS to %s", to_number)
        return SmsResult(status="failed", error=str(exc))
