import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings

from .models import LivePaintEvent

PLAIN_STATIC = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

BOOKING = {
    "name": "Ana & Luis",
    "phone": "555-0100",
    "email": "ana@example.com",
    "event_date": "2027-06-12",
    "venue_name": "Hon-Dah Resort",
    "venue": "Pinetop, AZ",
    "reference": "Instagram",
    "guest_count": "120",
    "wedding_planner": "None",
    "instagram": "@analuis",
    "budget": "above_1500",
    "choice": "Guests",
    "typeofclient": "I would love for you to be there",
    "description": "Black tie wedding",
}


@override_settings(
    STORAGES=PLAIN_STATIC,
    NOTIFY_SEND_SYNC=True,
    NOTIFY_TO_EMAIL="karla@example.com",
    ANTHROPIC_API_KEY="",
)
class BookingFormTests(TestCase):
    @override_settings(RESEND_API_KEY="re_test", NOTIFY_FROM_EMAIL="WBK <onboarding@resend.dev>")
    def test_inquiry_is_saved_and_karla_gets_the_details_via_resend(self):
        with mock.patch("requests.post") as post:
            post.return_value.status_code = 200
            response = self.client.post("/accounts/add_venue/", BOOKING)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Success!")
        event = LivePaintEvent.objects.get()
        self.assertEqual(event.event_date, datetime.date(2027, 6, 12))

        url = post.call_args.args[0]
        payload = post.call_args.kwargs["json"]
        self.assertEqual(url, "https://api.resend.com/emails")
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer re_test")
        self.assertEqual(payload["to"], ["karla@example.com"])
        self.assertEqual(payload["from"], "WBK <onboarding@resend.dev>")
        self.assertEqual(payload["reply_to"], "ana@example.com")
        self.assertEqual(payload["subject"], "New booking inquiry: Ana & Luis (Jun 12, 2027)")
        self.assertIn("Hey baba, a new client just filled out the form.", payload["text"])
        self.assertIn("Venue: Hon-Dah Resort (Pinetop, AZ)", payload["text"])
        self.assertIn("Budget: $1,500 and above", payload["text"])
        self.assertIn(f"/admin/accounts/livepaintevent/{event.pk}/change/", payload["text"])

    @override_settings(RESEND_API_KEY="")
    def test_falls_back_to_django_email_without_resend_key(self):
        self.client.post("/accounts/add_venue/", BOOKING)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["karla@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["ana@example.com"])

    @override_settings(RESEND_API_KEY="re_test")
    def test_email_problems_never_break_the_form(self):
        with mock.patch("requests.post", side_effect=OSError("network down")):
            response = self.client.post("/accounts/add_venue/", BOOKING)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LivePaintEvent.objects.count(), 1)

    def test_invalid_form_is_not_saved(self):
        response = self.client.post("/accounts/add_venue/", {**BOOKING, "email": "not-an-email"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LivePaintEvent.objects.count(), 0)


@override_settings(STORAGES=PLAIN_STATIC, ANTHROPIC_API_KEY="")
class DeleteInquiryTests(TestCase):
    def setUp(self):
        self.event = LivePaintEvent.objects.create(
            **{**BOOKING, "event_date": datetime.date(2027, 6, 12)}
        )
        self.url = f"/accounts/{self.event.pk}/delete/"

    def test_visitors_cannot_delete_inquiries(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])
        self.assertTrue(LivePaintEvent.objects.filter(pk=self.event.pk).exists())

    def test_non_staff_accounts_cannot_delete_inquiries(self):
        user = User.objects.create_user("guest", password="pw-12345-long")
        self.client.force_login(user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(LivePaintEvent.objects.filter(pk=self.event.pk).exists())

    def test_staff_can_delete_inquiries(self):
        staff = User.objects.create_user("karla", password="pw-12345-long", is_staff=True)
        self.client.force_login(staff)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(LivePaintEvent.objects.filter(pk=self.event.pk).exists())
