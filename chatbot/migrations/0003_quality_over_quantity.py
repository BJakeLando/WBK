"""Teach the assistant Karla's "quality over quantity" pace (from Brandon, Sept 22, 2026).

Visitors often assume a live painter turns out a portrait in 5 minutes or less.
Karla is classically trained, has a degree in design, and paints every detail,
so each portrait takes roughly 15 to 20 minutes. She finishes as many as she can
during the event, then finishes the rest at home and mails them to the bride and
groom. This replaces the older "7 to 10 minutes" and "faces are not detailed"
wording from the site graphics.

Answers Karla has already edited in the admin are left alone.
"""
import re

from django.db import migrations
from django.utils import timezone

HOW_IT_WORKS_QUESTION = "How does live painting work for guests?"
HOW_IT_WORKS_OLD = (
    "1. Guests pose for a quick photo. Karla just needs to see their outfits; faces are not "
    "detailed.\n"
    "2. Karla paints while they go enjoy the party.\n"
    "3. The first dozen portraits are finished at the event, and the rest are mailed to the "
    "couple to send as post-wedding thank-you cards."
)
HOW_IT_WORKS_NEW = (
    "1. Guests pose for a quick photo so Karla can paint them.\n"
    "2. Karla paints while they go enjoy the party. She paints each portrait in full detail, "
    "which takes roughly 15 to 20 minutes.\n"
    "3. She completes as many portraits as she can in the time booked, then takes the rest "
    "home to finish with the same care and mails them to the bride and groom, who can share "
    "them as post-wedding thank-you cards."
)

TIMING_QUESTION = "How long does each portrait take?"
TIMING_OLD = (
    "About 7 to 9 minutes for a half-body portrait with eyes only, and about 10 minutes for a "
    "full-body portrait with faces (not counting time spent chatting with guests). The bigger "
    "newlyweds' portrait is finished within 3 hours on the same day, and it's framed."
)
TIMING_NEW = (
    "Roughly 15 to 20 minutes per guest portrait, because Karla paints every detail instead of "
    "a quick sketch. The bigger newlyweds' portrait is finished within 3 hours on the same "
    "day, and it's framed."
)

QUALITY_QUESTION = "Is Karla fast? Will every portrait be finished at the event?"
QUALITY_ANSWER = (
    "Karla focuses on quality over quantity. Her portraits aren't five-minute sketches: she's "
    "classically trained, has a degree in design, and paints every detail by hand, so each "
    "portrait takes roughly 15 to 20 minutes. During the event she completes as many portraits "
    "as she can in the time booked, then takes the rest home to finish with the same care and "
    "mails them to the bride and groom."
)

NEW_QUESTION_TO_ANSWER = (
    "Is there an extra charge for the portraits Karla finishes at home after the event?"
)


def _normalize(text):
    text = re.sub(r"[^\w\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", text).strip()[:500]


def forwards(apps, schema_editor):
    FAQ = apps.get_model("chatbot", "FAQ")
    UnansweredQuestion = apps.get_model("chatbot", "UnansweredQuestion")
    now = timezone.now()

    # Only replace answers that still match the original starter text.
    FAQ.objects.filter(question=HOW_IT_WORKS_QUESTION, answer=HOW_IT_WORKS_OLD).update(
        answer=HOW_IT_WORKS_NEW, updated_at=now
    )
    FAQ.objects.filter(question=TIMING_QUESTION, answer=TIMING_OLD).update(
        answer=TIMING_NEW, updated_at=now
    )

    if not FAQ.objects.filter(question=QUALITY_QUESTION).exists():
        FAQ.objects.create(question=QUALITY_QUESTION, answer=QUALITY_ANSWER, sort_order=55)

    normalized = _normalize(NEW_QUESTION_TO_ANSWER)
    if not UnansweredQuestion.objects.filter(normalized=normalized).exists():
        UnansweredQuestion.objects.create(
            question=NEW_QUESTION_TO_ANSWER, normalized=normalized, times_asked=0
        )


def backwards(apps, schema_editor):
    FAQ = apps.get_model("chatbot", "FAQ")
    UnansweredQuestion = apps.get_model("chatbot", "UnansweredQuestion")
    FAQ.objects.filter(question=HOW_IT_WORKS_QUESTION, answer=HOW_IT_WORKS_NEW).update(
        answer=HOW_IT_WORKS_OLD
    )
    FAQ.objects.filter(question=TIMING_QUESTION, answer=TIMING_NEW).update(answer=TIMING_OLD)
    FAQ.objects.filter(question=QUALITY_QUESTION, answer=QUALITY_ANSWER).delete()
    UnansweredQuestion.objects.filter(
        question=NEW_QUESTION_TO_ANSWER, conversation__isnull=True, status="new"
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("chatbot", "0002_seed_knowledge"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
