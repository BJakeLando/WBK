from django import forms
from .models import PetPortraitSubmission

class PetPortraitSubmissionForm(forms.ModelForm):
    class Meta:
        model = PetPortraitSubmission
        fields = ['customer_name', 'customer_email', 'customer_phone', 'pet_name', 
                  'pet_photo', 'portrait_size', 'additional_notes']
        
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name',
                'required': True
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': True
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(555) 123-4567 (optional)'
            }),
            'pet_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Your pet's name",
                'required': True
            }),
            'pet_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'required': True
            }),
            'portrait_size': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'additional_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about your pet, any special details you want captured, preferred colors, etc.'
            }),
        }
        
        labels = {
            'customer_name': 'Your Name',
            'customer_email': 'Email Address',
            'customer_phone': 'Phone Number',
            'pet_name': "Pet's Name",
            'pet_photo': "Pet's Photo",
            'portrait_size': 'Portrait Size',
            'additional_notes': 'Additional Details (Optional)',
        }