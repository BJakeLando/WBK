"""Email alerts for Karla (new booking inquiries, questions for the assistant).

Railway blocks outbound SMTP, so when RESEND_API_KEY is set we send through
Resend's HTTPS API instead. Without a key we fall back to Django's normal
email backend (works locally, fails quietly on Railway). Emails go out in a
background thread so visitors never wait on them.
"""
import logging
import threading

import requests
from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger("mysite.notifications")

RESEND_URL = "https://api.resend.com/emails"
DEFAULT_TO = "WatercolorsByKarla@hotmail.com"
DEFAULT_FROM = "Watercolors By Karla <onboarding@resend.dev>"


def send_notification(subject, body, to=None, reply_to=None):
    """Send a plain-text email to Karla (or `to`). Never raises."""
    subject = " ".join(str(subject).split())  # no line breaks in email headers
    recipients = _as_list(to or getattr(settings, "NOTIFY_TO_EMAIL", DEFAULT_TO))
    if not recipients:
        logger.warning("No NOTIFY_TO_EMAIL set; skipped email: %s", subject)
        return
    args = (subject, body, recipients, reply_to or None)
    if getattr(settings, "NOTIFY_SEND_SYNC", False):
        _deliver(*args)
    else:
        threading.Thread(target=_deliver, args=args, daemon=True).start()


def _as_list(value):
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [v for v in value if v]
    return [v.strip() for v in str(value).split(",") if v.strip()]


def _deliver(subject, body, recipients, reply_to):
    try:
        if getattr(settings, "RESEND_API_KEY", ""):
            _send_with_resend(subject, body, recipients, reply_to)
        else:
            _send_with_django(subject, body, recipients, reply_to)
    except Exception:
        logger.exception("Email failed: %s", subject)


def _send_with_resend(subject, body, recipients, reply_to):
    payload = {
        "from": getattr(settings, "NOTIFY_FROM_EMAIL", "") or DEFAULT_FROM,
        "to": recipients,
        "subject": subject,
        "text": body,
    }
    if reply_to:
        payload["reply_to"] = reply_to
    response = requests.post(
        RESEND_URL,
        headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
        json=payload,
        timeout=15,
    )
    if response.status_code >= 300:
        logger.error(
            "Resend rejected email %r: HTTP %s %s",
            subject,
            response.status_code,
            response.text[:300],
        )
    else:
        logger.info("Email sent via Resend: %s", subject)


def _send_with_django(subject, body, recipients, reply_to):
    EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
        reply_to=[reply_to] if reply_to else None,
    ).send(fail_silently=False)
    logger.info("Email sent via SMTP: %s", subject)
