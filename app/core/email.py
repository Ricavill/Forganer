import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

RESEND_API_URL = "https://api.resend.com/emails"


def send_email(to: list[str], subject: str, html: str, attachments: list[dict] | None = None) -> None:
    """Send an email via the Resend API. `attachments` follows Resend's format:
    [{"filename": ..., "content": <base64-encoded str>}, ...]."""
    if not settings.resend_api_key:
        raise ExternalServiceError("Email sending is not configured on this deployment")

    payload = {"from": settings.resend_from_email, "to": to, "subject": subject, "html": html}
    if attachments:
        payload["attachments"] = attachments

    response = httpx.post(
        RESEND_API_URL,
        headers={"Authorization": f"Bearer {settings.resend_api_key}"},
        json=payload,
        timeout=20,
    )
    if response.status_code >= 400:
        raise ExternalServiceError(f"Failed to send email: {response.text}")
