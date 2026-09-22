from django.contrib import admin, messages
from django.db.models import Case, IntegerField, OuterRef, Subquery, Sum, Value, When
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join, linebreaks
from django.utils.safestring import mark_safe

from .models import FAQ, Conversation, Message, UnansweredQuestion


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "answer_preview", "is_active", "sort_order", "updated_at")
    list_display_links = ("question",)
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    fields = ("question", "answer", "is_active", "sort_order")

    @admin.display(description="Answer")
    def answer_preview(self, obj):
        text = " ".join(obj.answer.split())
        return (text[:110] + "…") if len(text) > 110 else text


@admin.register(UnansweredQuestion)
class UnansweredQuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "times_asked", "status", "last_asked_at")
    list_filter = ("status",)
    search_fields = ("question", "answer")
    fields = ("question", "answer", "status", "times_asked", "chat_link", "faq_link", "created_at")
    readonly_fields = ("status", "times_asked", "chat_link", "faq_link", "created_at")
    actions = ("dismiss_selected", "reopen_selected")

    def get_queryset(self, request):
        # Questions that still need an answer first, most-asked at the top.
        return (
            super()
            .get_queryset(request)
            .annotate(
                needs_answer=Case(
                    When(status=UnansweredQuestion.STATUS_NEW, then=Value(0)),
                    default=Value(1),
                    output_field=IntegerField(),
                )
            )
            .order_by("needs_answer", "-times_asked", "-last_asked_at")
        )

    @admin.display(description="Chat")
    def chat_link(self, obj):
        if not obj.conversation_id:
            return "-"
        url = reverse("admin:chatbot_conversation_change", args=[obj.conversation_id])
        return format_html('<a href="{}">Read the chat</a>', url)

    @admin.display(description="FAQ")
    def faq_link(self, obj):
        if not obj.faq_id:
            return "Not added yet. Type an answer above and save."
        url = reverse("admin:chatbot_faq_change", args=[obj.faq_id])
        return format_html('<a href="{}">View or edit the FAQ</a>', url)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.status == UnansweredQuestion.STATUS_ANSWERED:
            messages.success(request, "Added to the FAQs. The assistant knows this answer now.")

    @admin.action(description="Dismiss (no answer needed)")
    def dismiss_selected(self, request, queryset):
        updated = queryset.filter(status=UnansweredQuestion.STATUS_NEW).update(
            status=UnansweredQuestion.STATUS_DISMISSED
        )
        self.message_user(request, f"Dismissed {updated} question(s).")

    @admin.action(description="Move back to 'Needs an answer'")
    def reopen_selected(self, request, queryset):
        updated = queryset.filter(status=UnansweredQuestion.STATUS_DISMISSED).update(
            status=UnansweredQuestion.STATUS_NEW
        )
        self.message_user(request, f"Reopened {updated} question(s).")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "first_question",
        "user_message_count",
        "questions_flagged",
        "started_on_page",
    )
    date_hierarchy = "created_at"
    search_fields = ("messages__content",)
    fields = (
        "created_at",
        "started_on_page",
        "user_message_count",
        "questions_flagged",
        "tokens_used",
        "transcript",
    )
    readonly_fields = fields

    def get_queryset(self, request):
        first_visitor_message = (
            Message.objects.filter(conversation=OuterRef("pk"), role=Message.ROLE_USER)
            .order_by("created_at", "id")
            .values("content")[:1]
        )
        return super().get_queryset(request).annotate(
            first_question_text=Subquery(first_visitor_message)
        )

    # Transcripts are read-only: they can be viewed and deleted, not edited.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description="First question")
    def first_question(self, obj):
        text = obj.first_question_text or ""
        return (text[:90] + "…") if len(text) > 90 else (text or "-")

    @admin.display(description="API tokens used")
    def tokens_used(self, obj):
        totals = obj.messages.aggregate(
            fresh=Sum("input_tokens"),
            written=Sum("cache_write_tokens"),
            cached=Sum("cache_read_tokens"),
            output=Sum("output_tokens"),
        )
        return (
            f"{totals['fresh'] or 0:,} input · {totals['written'] or 0:,} cache write · "
            f"{totals['cached'] or 0:,} cache read · {totals['output'] or 0:,} output"
        )

    @admin.display(description="Transcript")
    def transcript(self, obj):
        rows = (
            (
                "#3d5c3d" if m.role == Message.ROLE_USER else "#c9a96e",
                "#f4f7f4" if m.role == Message.ROLE_USER else "#fdfaf5",
                m.get_role_display(),
                timezone.localtime(m.created_at).strftime("%b %d, %I:%M %p"),
                " · canned reply" if m.is_fallback else "",
                # linebreaks() escapes the text first, so marking it safe is OK.
                mark_safe(linebreaks(m.content, autoescape=True)),
            )
            for m in obj.messages.order_by("created_at", "id")
        )
        return format_html(
            '<div style="max-width:760px">{}</div>',
            format_html_join(
                "",
                '<div style="margin:0 0 14px;padding:10px 14px;border-left:3px solid {};'
                'background:{};color:#2f3a2f"><div style="font-size:11px;letter-spacing:.08em;'
                'text-transform:uppercase;color:#6b7a6b;margin-bottom:4px">{} · {}{}</div>'
                "{}</div>",
                rows,
            ),
        )
