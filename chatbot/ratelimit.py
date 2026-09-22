"""Per-visitor and site-wide limits for the website assistant.

Counts come from the Message table, so they work across both gunicorn
workers without needing Redis or a shared cache.
"""
import hashlib
import hmac
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from . import conf
from .models import Message

SLOW_DOWN = "slow_down"
BUSY = "busy"


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        # Railway's edge proxy appends the address it actually saw, so the
        # right-most entry is the one a visitor can't fake.
        parts = [part.strip() for part in forwarded.split(",") if part.strip()]
        if parts:
            return parts[-1]
    return request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR") or ""


def hash_ip(ip):
    """Store a keyed hash instead of the raw IP address."""
    if not ip:
        return ""
    return hmac.new(settings.SECRET_KEY.encode(), ip.encode(), hashlib.sha256).hexdigest()[:32]


def limit_reason(ip_hash):
    """Return SLOW_DOWN, BUSY, or None if the visitor may send a message."""
    now = timezone.now()
    visitor_messages = Message.objects.filter(role=Message.ROLE_USER)

    last_day = visitor_messages.filter(created_at__gte=now - timedelta(hours=24))
    if last_day.count() >= conf.get("CHATBOT_DAILY_MESSAGE_LIMIT"):
        return BUSY

    if ip_hash:
        mine = visitor_messages.filter(ip_hash=ip_hash)
        if mine.filter(created_at__gte=now - timedelta(minutes=10)).count() >= conf.get(
            "CHATBOT_IP_LIMIT_10_MIN"
        ):
            return SLOW_DOWN
        if mine.filter(created_at__gte=now - timedelta(hours=24)).count() >= conf.get(
            "CHATBOT_IP_LIMIT_PER_DAY"
        ):
            return SLOW_DOWN
    return None
