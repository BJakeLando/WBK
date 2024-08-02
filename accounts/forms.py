from django import forms
from django.forms import ModelForm
from .models import LivePaintEvent

# Create a live paint event form
class EventForm(ModelForm):
    class Meta:
        model = LivePaintEvent
        fields = ('name','phone','event_date','venue','guest_count','wedding_planner','description','email', 'source','instagram',)
        labels = {
            'name':'', 
            'phone':'',
            'event_date':'',
            'venue':'',
            'guest_count':'',
            'reference':'',
            'wedding_planner':'',
            'description':'',
            'email':'',
            'source':'',
            'instagram':'',

        }



        widgets = {
            'name':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}), 
            'phone':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Phone Number'}),
            'event_date':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Event Date'}),
            'venue':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Venue Location'}),
            'guest_count':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Estimated Guest Count'}),
            'reference':forms.TextInput(attrs={'class': 'form-control','placeholder': 'How did you hear about us?'}),
            'wedding_planner':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Wedding Planner'}),
            'description':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Brief Description of event. ( Wedding, Birthday, etc )'}),
            'email':forms.EmailInput(attrs={'class': 'form-control','placeholder': 'Email'}),
            'source':forms.TextInput(attrs={'class': 'form-control','placeholder': 'How did you hear about me?'}),
            'instagram':forms.TextInput(attrs={'class': 'form-control','placeholder': 'What is your Instagram?'}),

        }