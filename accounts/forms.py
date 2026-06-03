from django import forms
from django.forms import ModelForm
from .models import LivePaintEvent

# Create a live paint event form
class EventForm(ModelForm):
    class Meta:
        model = LivePaintEvent
        fields = ('name','phone','email','event_date','venue_name','venue','reference','guest_count','wedding_planner','instagram','budget','choice','typeofclient', 'description',)
        labels = {
            'name':'', 
            'phone':'',
            'email':'',
            'event_date':'',
            'venue_name':'',
            'venue':'',
            'reference':'',
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
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'text',
                'placeholder': 'Event Date',
                'onfocus': "this.type='date'",
                'onblur': "if(!this.value) this.type='text'",
            }),
            'venue_name':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Venue Name'}),
            'venue':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Venue Location (City, St)'}),
            'reference':forms.TextInput(attrs={'class': 'form-control','placeholder': 'How did you about us?'}),
            'guest_count':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Estimated Guest Count'}),
            'reference':forms.TextInput(attrs={'class': 'form-control','placeholder': 'How did you hear about us?'}),
            'wedding_planner':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Event Coordinator or Planner Name'}),
            'description':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Brief Description of event. ( Wedding, Birthday, etc )'}),
            'source':forms.TextInput(attrs={'class': 'form-control','placeholder': 'How did you hear about me?'}),
            'instagram':forms.TextInput(attrs={'class': 'form-control','placeholder': 'What is your Instagram?'}),
            'budget': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', 'What is your budget for live painting?'),
                ('below_1500', 'Below $1,500'),
                ('above_1500', '$1,500 and above'),
            ]),
            'choice':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Inquiring for Guests or Bride and Groom Painting?'}),
            'typeofclient':forms.TextInput(attrs={'class': 'form-control','placeholder': 'I would love for you to be there or just curious?'}),
            'description':forms.TextInput(attrs={'class': 'form-control','placeholder': 'Brief Description of event. ( Wedding Dress Code, Birthday, Corporate Event, ETC)', 'rows': 3}),


        }