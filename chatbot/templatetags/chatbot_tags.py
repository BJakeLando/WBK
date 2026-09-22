"""{% chatbot_widget %}: drops the chat bubble onto any page that extends base.html.

Built to fail safe: if the assistant is switched off, or something is wrong
(for example, collectstatic hasn't been run), it renders nothing and logs a
warning instead of breaking Karla's site.
"""
import logging

from django import template
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse

from chatbot import conf

logger = logging.getLogger("chatbot")
register = template.Library()

GREETING = (
    "Hi there! I'm the studio assistant for Watercolors By Karla. Ask me about "
    "live wedding portraits, packages, welcome signs, or how booking works."
)

SUGGESTIONS = [
    "What are your packages?",
    "How does live painting work?",
    "Do you travel to my venue?",
    "Tell me about welcome signs",
    "How do I book my date?",
]


@register.simple_tag(takes_context=True)
def chatbot_widget(context):
    if not conf.enabled():
        return ""
    request = context.get("request")
    if request is None:
        return ""
    try:
        css_url = static("chatbot/chat.css")
        js_url = static("chatbot/chat.js")
    except ValueError:
        logger.warning(
            "Chat widget hidden: chatbot static files are missing from the manifest. "
            "Run `python manage.py collectstatic`."
        )
        return ""
    try:
        config = {
            "messageUrl": reverse("chatbot:message"),
            "historyUrl": reverse("chatbot:history"),
            "resetUrl": reverse("chatbot:reset"),
            "bookUrl": reverse("add-event"),
            "contactEmail": conf.get("CHATBOT_CONTACT_EMAIL"),
            "maxChars": conf.get("CHATBOT_MAX_MESSAGE_CHARS"),
            "greeting": GREETING,
            "suggestions": SUGGESTIONS,
        }
        return render_to_string(
            "chatbot/widget.html",
            {"css_url": css_url, "js_url": js_url, "config": config},
            request=request,
        )
    except Exception:
        logger.exception("Chat widget failed to render")
        return ""
