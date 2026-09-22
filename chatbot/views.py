import json
import re

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from . import assistant, conf
from .models import Conversation, Message
from .ratelimit import BUSY, client_ip, hash_ip, limit_reason

SESSION_KEY = "chatbot_conversation_id"
# The page path is shown to Claude, so only accept plain URL paths (no free text).
PAGE_PATH = re.compile(r"/[A-Za-z0-9/_.\-]{0,120}")


def _json(data, status=200):
    response = JsonResponse(data, status=status)
    response["Cache-Control"] = "no-store"
    return response


def _clean_page(value):
    page = str(value or "")
    if PAGE_PATH.fullmatch(page) and not page.startswith("//"):
        return page
    return ""


def _current_conversation(request):
    conversation_id = request.session.get(SESSION_KEY)
    if not conversation_id:
        return None
    return Conversation.objects.filter(pk=conversation_id).first()


def _canned(conversation, text, status, **extra):
    """Record a canned reply in the transcript and send it to the visitor."""
    if conversation is not None:
        Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_ASSISTANT,
            content=text,
            is_fallback=True,
        )
    return _json({"reply": text, **extra}, status=status)


@require_POST
def message(request):
    if not conf.enabled():
        return _json({"reply": assistant.busy_reply(), "disabled": True}, status=503)

    try:
        data = json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError):
        return _json({"error": "Invalid request."}, status=400)
    if not isinstance(data, dict):
        return _json({"error": "Invalid request."}, status=400)

    text = str(data.get("message") or "").strip()[: conf.get("CHATBOT_MAX_MESSAGE_CHARS")]
    if not text:
        return _json({"error": "Please type a question."}, status=400)
    page = _clean_page(data.get("page"))

    ip_hash = hash_ip(client_ip(request))
    conversation = _current_conversation(request)

    reason = limit_reason(ip_hash)
    if reason == BUSY:
        return _canned(conversation, assistant.busy_reply(), 429, limited=True)
    if reason:
        return _canned(conversation, assistant.slow_down_reply(), 429, limited=True)

    if conversation is None:
        conversation = Conversation.objects.create(
            ip_hash=ip_hash,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
            started_on_page=page,
        )
        request.session[SESSION_KEY] = conversation.pk

    if conversation.user_message_count >= conf.get("CHATBOT_MAX_MESSAGES_PER_CONVERSATION"):
        return _canned(conversation, assistant.long_chat_reply(), 429, limited=True)

    Message.objects.create(
        conversation=conversation, role=Message.ROLE_USER, content=text, ip_hash=ip_hash
    )
    conversation.user_message_count += 1
    conversation.save(update_fields=["user_message_count", "updated_at"])

    reply = assistant.generate_reply(conversation, page)
    Message.objects.create(
        conversation=conversation,
        role=Message.ROLE_ASSISTANT,
        content=reply.text,
        is_fallback=not reply.ok,
        input_tokens=reply.input_tokens,
        output_tokens=reply.output_tokens,
        cache_read_tokens=reply.cache_read_tokens,
        cache_write_tokens=reply.cache_write_tokens,
    )
    # Always 200 here: Django skips saving the session on 5xx responses, which
    # would split the visitor's chat in two if their first message hit an error.
    return _json({"reply": reply.text, "fallback": not reply.ok})


@require_GET
def history(request):
    conversation = _current_conversation(request)
    messages = []
    if conversation is not None:
        messages = [
            {"role": m.role, "content": m.content}
            for m in conversation.messages.order_by("created_at", "id")[:100]
        ]
    return _json({"messages": messages})


@require_POST
def reset(request):
    request.session.pop(SESSION_KEY, None)
    return _json({"ok": True})
