from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.forms import UserCreationForm
from .models import LivePaintEvent
from django.urls import reverse_lazy
from .forms import EventForm
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings

class SignupView(CreateView):
    form_class = UserCreationForm
    template_name= "registration/signup.html"



def add_event(request):
    submitted = False
    event_list = LivePaintEvent.objects.all()
    if request.method == 'POST':
        form = EventForm(request.POST)
        mysiteurl = 'https://wbk-production.up.railway.app/admin/accounts/livepaintevent/'
        message_name = 'NEW CLIENT SUBMITTED'
        message_email = 'Default Email'
        message = 'A New Client has filled out the form on your website!' + '\n' + mysiteurl
        if form.is_valid():
            form.save()
            send_mail(
                message_name,
                message,
                message_email,
                ['karlaportraits@gmail.com'],
            )
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