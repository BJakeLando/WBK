from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.forms import UserCreationForm
from .models import LivePaintEvent
from django.urls import reverse_lazy
from .forms import EventForm
from django.http import HttpResponseRedirect


class SignupView(CreateView):
    form_class = UserCreationForm
    template_name= "registration/signup.html"


def all_events(request):
    event_list = LivePaintEvent.objects.all().order_by('event_date')
    return render(request, 'accounts/events.html',
                  {'event_list': event_list})


def add_event(request):
    submitted = False
    event_list =LivePaintEvent.objects.all()
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'accounts/success.html',
                  {'event_list': event_list})
    else:
        form = EventForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'accounts/add_event.html',
                  {'form': form,'submitted': submitted})


class EventDeleteView(DeleteView):
    template_name = "delete.html"
    model = LivePaintEvent
    success_url = reverse_lazy('home')

    def test_fun(self, pk):
        issue_obj = self.get_object(pk)
        issue_obj.delete()
        return self.request.user