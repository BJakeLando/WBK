from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.forms import UserCreationForm
from .models import LivePaintEvent
from django.urls import reverse_lazy
from .forms import EventForm
from django.core.mail import send_mail
from django.conf import settings
import threading 


# Helper function to send email in a separate thread
def send_email_in_background(subject, message, from_email, recipient_list):
    """Handles the actual send_mail call, isolated in a thread."""
    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False, 
        )
        print("Email successfully dispatched to background thread.")
    except Exception as e:
        # Crucial for debugging: log the actual network/SMTP error in your production logs
        print(f"ERROR: Background email failed to send. Check App Password/Network: {e}")


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
        # The sender email will be pulled from settings.DEFAULT_FROM_EMAIL
        sender_email = settings.DEFAULT_FROM_EMAIL 
        message = 'Hey baba, a new client just filled out the form. Okay bye I love you! ' + '\n' + mysiteurl
        
        if form.is_valid():
            form.save()
            
            # Start the email sending in a new thread
            email_thread = threading.Thread(
                target=send_email_in_background,
                args=(
                    message_name, 
                    message, 
                    sender_email, 
                    # 💡 CORRECTED RECIPIENT LIST
                    ['WatercolorsByKarla@hotmail.com'] 
                )
            )
            email_thread.start()
            
            # Request returns instantly
            return render(request, 'accounts/success.html',
                  {'event_list': event_list})
    else:
        form = EventForm
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'accounts/add_event.html', {'form': form,'submitted': submitted})



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