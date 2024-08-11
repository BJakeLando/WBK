from django import forms
from django.forms import ModelForm
from .models import LivePaintEvent

# Create a live paint event form
class EventForm(ModelForm):
    class Meta:
        model = LivePaintEvent
        fields = ('name','phone','email','event_date','venue','guest_count','wedding_planner','instagram','budget','choice','typeofclient', 'description',)
        labels = {
            'name':'', 
            'phone':'',
            'email':'',
            'event_date':'',
            'venue':'',
            'guest_count':'',
            'reference':'',
            'wedding_planner':'',
            'source':'',
            'instagram':'',
            'budget': '',
            'choice': '',
            'typeofclient':'',
            'description':'',

        }



        widgets = {
            'name':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bride & Groom or Partner Names'}), 
            'phone':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Phone Number'}),
            'email':forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Email'}),
            'event_date':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Event Date (MO/DD/YYYY)'}),
            'venue':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Venue Location (City, St)'}),
            'guest_count':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Estimated Guest Count'}),
            'reference':forms.TextInput(attrs={'class': 'form-control','placeholder': 'How did you hear about us?'}),
            'wedding_planner':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Event Coordinator or Planner Name'}),
            'description':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Brief Description of event. ( Wedding, Birthday, etc )'}),
            'source':forms.TextInput(attrs={'class': 'form-control','placeholder': 'How did you hear about me?'}),
            'instagram':forms.TextInput(attrs={'class': 'form-control','placeholder': 'What is your Instagram?'}),
            'budget':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Estimated budget for live painting? '}),
            'choice':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Inquiring for Guests or Bride and Groom Painting?'}),
            'typeofclient':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Just Curious/Shopping Around... or I would love for you to be there! '}),
            'description':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Brief Description of event. ( Wedding Theme, Birthday, etc)', 'rows': 3}),


        }