from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.forms import UserCreationForm
from .models import LivePaintEvent
from django.urls import reverse_lazy
from .forms import EventForm
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
        mysiteurl = 'https:www.paintedbykarla.com/admin/accounts/livepaintevent/'
        message_name = 'NEW CLIENT FORM SUBMITTED'
        # Change the sender email to the one configured in settings
        sender_email = settings.EMAIL_HOST_USER 
        message = 'Hey baba, a new client just filled out the form. Okay bye I love you! ' + '\n' + mysiteurl
        if form.is_valid():
            form.save()
            send_mail(
                message_name,
                message,
                sender_email, # Use the valid sender email
                ['karlaportraits@gmail.com'], # The recipient list
                fail_silently=False, # Add this to get an error if it fails
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
    
class SignupView(CreateView):
    form_class = UserCreationForm
    template_name= "registration/signup.html"
    success_url= reverse_lazy('login')