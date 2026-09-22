"""Chatbot settings, with safe defaults.

Anything here can be overridden in mysite/settings.py (which reads Railway
environment variables). Values are read at call time, so tests can use
override_settings.
"""
from django.conf import settings

DEFAULTS = {
    "CHATBOT_ENABLED": False,
    "ANTHROPIC_API_KEY": "",
    # Claude model and how hard it thinks. "low" effort keeps replies fast and cheap.
    "CHATBOT_MODEL": "claude-sonnet-5",
    "CHATBOT_EFFORT": "low",
    "CHATBOT_API_URL": "https://api.anthropic.com/v1/messages",
    "CHATBOT_MAX_TOKENS": 1024,
    # Guard rails (per visitor and site-wide) so a viral post can't run up the bill.
    "CHATBOT_MAX_MESSAGE_CHARS": 800,
    "CHATBOT_HISTORY_MESSAGES": 16,
    "CHATBOT_MAX_MESSAGES_PER_CONVERSATION": 30,
    "CHATBOT_IP_LIMIT_10_MIN": 20,
    "CHATBOT_IP_LIMIT_PER_DAY": 120,
    "CHATBOT_DAILY_MESSAGE_LIMIT": 600,
    "CHATBOT_MAX_FLAGS_PER_CONVERSATION": 3,
    # Email Karla when the assistant gets a question it can't answer.
    "CHATBOT_EMAIL_UNANSWERED": True,
    "CHATBOT_UNANSWERED_EMAILS_PER_DAY": 10,
    "CHATBOT_CONTACT_EMAIL": "WatercolorsbyKarla@gmail.com",
    "SITE_URL": "https://www.paintedbykarla.com",
}


def get(name):
    return getattr(settings, name, DEFAULTS[name])


def enabled():
    return bool(get("CHATBOT_ENABLED")) and bool(get("ANTHROPIC_API_KEY"))


def admin_url(path):
    """Absolute link into the Django admin, for emails."""
    return get("SITE_URL").rstrip("/") + path
