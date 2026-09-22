from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView
from django.views.generic.edit import DeleteView

from mysite.notifications import send_notification

from .forms import EventForm
from .models import LivePaintEvent

BUDGET_LABELS = {
    'below_1500': 'Below $1,500',
    'above_1500': '$1,500 and above',
}


def booking_alert(event):
    """Subject and body of the email Karla gets for each new inquiry."""
    site_url = getattr(settings, 'SITE_URL', 'https://www.paintedbykarla.com').rstrip('/')
    admin_link = site_url + reverse('admin:accounts_livepaintevent_change', args=[event.pk])
    date_text = event.event_date.strftime('%A, %B %d, %Y')
    subject = f'New booking inquiry: {event.name} ({event.event_date:%b %d, %Y})'
    body = '\n'.join([
        'Hey baba, a new client just filled out the form. Okay bye I love you!',
        '',
        f'Names: {event.name}',
        f'Event date: {date_text}',
        f'Venue: {event.venue_name} ({event.venue})',
        f'Guest count: {event.guest_count}',
        f'Budget: {BUDGET_LABELS.get(event.budget, event.budget)}',
        f'Guests or couple painting: {event.choice}',
        f'Event details: {event.description}',
        f'Planner: {event.wedding_planner}',
        f'Booking or just curious: {event.typeofclient}',
        f'Heard about us: {event.reference}',
        '',
        f'Email: {event.email}',
        f'Phone: {event.phone}',
        f'Instagram: {event.instagram}',
        '',
        f'Open in admin: {admin_link}',
        f'Reply to this email to write back to {event.name} directly.',
    ])
    return subject, body


def add_event(request):
    submitted = False

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            subject, body = booking_alert(event)
            # Sent in the background (via Resend on Railway), so the page returns instantly.
            send_notification(subject, body, reply_to=event.email)
            return render(request, 'accounts/success.html')
    else:
        form = EventForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'accounts/add_event.html', {'form': form, 'submitted': submitted})


class EventDeleteView(UserPassesTestMixin, DeleteView):
    """Staff only. Without this check, anyone could delete booking inquiries."""
    template_name = "delete.html"
    model = LivePaintEvent
    success_url = reverse_lazy('home')

    def test_func(self):
        user = self.request.user
        return user.is_active and user.is_staff


class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy('login')
