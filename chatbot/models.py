import re

from django.db import models
from django.utils import timezone


class FAQ(models.Model):
    """One thing the website assistant knows.

    Every active FAQ is handed to the assistant on each chat, so editing an
    answer here changes what it tells visitors right away (no deploy needed).
    """

    question = models.CharField(
        max_length=300,
        help_text="Write it the way a client would ask it.",
    )
    answer = models.TextField(
        help_text=(
            "Write it the way you'd answer a client. The assistant only knows "
            "what's written in these FAQs, so include real prices, policies and details."
        ),
    )
    is_active = models.BooleanField(
        "Assistant uses this",
        default=True,
        help_text="Untick to hide this from the assistant without deleting it.",
    )
    sort_order = models.PositiveIntegerField(
        default=100,
        help_text="Lower numbers are listed first.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs (what the assistant knows)"

    def __str__(self):
        return self.question


class Conversation(models.Model):
    """One visitor's chat session."""

    ip_hash = models.CharField(max_length=64, blank=True, db_index=True)
    user_agent = models.CharField(max_length=300, blank=True)
    started_on_page = models.CharField(max_length=200, blank=True)
    user_message_count = models.PositiveIntegerField(default=0)
    questions_flagged = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Chat transcript"
        verbose_name_plural = "Chat transcripts"

    def __str__(self):
        return f"Chat #{self.pk} ({timezone.localtime(self.created_at):%b %d, %Y %I:%M %p})"


class Message(models.Model):
    ROLE_USER = "user"
    ROLE_ASSISTANT = "assistant"
    ROLE_CHOICES = [
        (ROLE_USER, "Visitor"),
        (ROLE_ASSISTANT, "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    # A canned reply we sent because the AI was unavailable or a limit was hit.
    # These are shown in transcripts but never sent back to the AI as history.
    is_fallback = models.BooleanField(default=False)
    ip_hash = models.CharField(max_length=64, blank=True)
    # Token usage for assistant replies (lets you keep an eye on API cost).
    input_tokens = models.PositiveIntegerField(default=0)
    output_tokens = models.PositiveIntegerField(default=0)
    cache_read_tokens = models.PositiveIntegerField(default=0)
    cache_write_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["role", "created_at"]),
            models.Index(fields=["ip_hash", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_role_display()}: {self.content[:60]}"


def normalize_question(text):
    """Lowercase, drop punctuation and extra spaces, so repeat questions match."""
    text = re.sub(r"[^\w\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", text).strip()[:500]


class UnansweredQuestion(models.Model):
    """A question the assistant couldn't answer from the FAQs.

    Type an answer and save: it becomes an FAQ and the assistant knows it from
    the next chat on. That's how Karla trains the assistant.
    """

    STATUS_NEW = "new"
    STATUS_ANSWERED = "answered"
    STATUS_DISMISSED = "dismissed"
    STATUS_CHOICES = [
        (STATUS_NEW, "Needs an answer"),
        (STATUS_ANSWERED, "Answered (added to FAQs)"),
        (STATUS_DISMISSED, "Dismissed"),
    ]

    question = models.CharField(max_length=500)
    normalized = models.CharField(max_length=500, blank=True, db_index=True, editable=False)
    answer = models.TextField(
        blank=True,
        help_text=(
            "Type the answer the way you'd tell a client, then Save. It's added to "
            "the FAQs automatically and the assistant starts using it right away."
        ),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_NEW)
    times_asked = models.PositiveIntegerField(default=1)
    conversation = models.ForeignKey(
        Conversation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="unanswered_questions",
        help_text="The chat where this was most recently asked.",
    )
    faq = models.OneToOneField(
        FAQ,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="source_question",
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_asked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-last_asked_at"]
        verbose_name = "Question to answer"
        verbose_name_plural = "Questions to answer"

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        self.normalized = normalize_question(self.question)
        answer = (self.answer or "").strip()
        if answer and self.status != self.STATUS_DISMISSED:
            question = self.question.strip()[:300]
            faq = self.faq
            if faq is None:
                faq = FAQ(sort_order=500)
            faq.question = question
            faq.answer = answer
            faq.is_active = True
            faq.save()
            self.faq = faq
            self.status = self.STATUS_ANSWERED
        super().save(*args, **kwargs)
