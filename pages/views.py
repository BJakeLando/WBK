from django.views.generic import TemplateView
import stripe
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import PetPortraitSubmission
from .forms import PetPortraitSubmissionForm

# Set your Stripe secret key
stripe.api_key = settings.STRIPE_SECRET_KEY


# ============= EXISTING VIEWS =============

def home(request):
    return render(request, 'pages/home.html')

class AboutView(TemplateView):
    template_name = 'pages/about.html'

class PricingView(TemplateView):
    template_name = 'pages/pricing.html'

class LivePaintView(TemplateView):
    template_name = 'pages/livepaint.html'

class CommissionsView(TemplateView):
    template_name = 'pages/commissions.html'

class PrintsView(TemplateView):
    template_name = 'pages/prints.html'

class BioView(TemplateView):
    template_name = 'pages/bio.html'

class WelcomeView(TemplateView):
    template_name = 'pages/welcome.html'

class GalleryView(TemplateView):
    template_name = 'pages/gallery.html'


# ============= NEW PET PORTRAIT VIEWS =============

def pet_gallery_view(request):
    """
    Display the pet gallery page with upload form
    (This replaces the old PetsView)
    """
    form = PetPortraitSubmissionForm()
    
    # Get all static pet images for the gallery
    all_pet_images = [
        'img/com_9.PNG',
        'img/com.JPG',
        'img/com_2.jpg',
        'img/com_1.jpg',
        'img/com_4.jpg',
    ]
    
    context = {
        'form': form,
        'all_pet_images': all_pet_images,
        'business_name': 'Watercolors By Karla',
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    
    return render(request, 'pages/pets.html', context)


def create_pet_portrait_checkout(request):
    """
    Handle form submission and create Stripe Checkout session
    """
    print(f"DEBUG: Request method: {request.method}")  # Debug line
    print(f"DEBUG: POST data: {request.POST}")  # Debug line
    print(f"DEBUG: FILES: {request.FILES}")  # Debug line
    
    if request.method == 'POST':
        form = PetPortraitSubmissionForm(request.POST, request.FILES)
        
        print(f"DEBUG: Form is valid? {form.is_valid()}")  # Debug line
        if not form.is_valid():
            print(f"DEBUG: Form errors: {form.errors}")  # Debug line
        
        if form.is_valid():
            # Save the submission (without payment info yet)
            submission = form.save(commit=False)
            submission.payment_status = 'pending'
            submission.save()
            
            print(f"DEBUG: Submission saved with ID: {submission.id}")  # Debug line
            
            # Get the price based on selected size
            price = submission.get_price()
            print(f"DEBUG: Price calculated: {price}")  # Debug line
            
            try:
                # Create Stripe Checkout Session
                print(f"DEBUG: Creating Stripe session...")  # Debug line
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(price * 100),  # Stripe uses cents
                            'product_data': {
                                'name': f'Custom Pet Portrait - {submission.portrait_size}',
                                'description': f'Watercolor portrait of {submission.pet_name}',
                                'images': [],  # You can add image URLs here if needed
                            },
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=request.build_absolute_uri(
                        reverse('pet_portrait_success')
                    ) + '?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=request.build_absolute_uri(
                        reverse('pet_portrait_cancel')
                    ) + f'?submission_id={submission.id}',
                    customer_email=submission.customer_email,
                    metadata={
                        'submission_id': submission.id,
                        'pet_name': submission.pet_name,
                        'customer_name': submission.customer_name,
                    }
                )
                
                print(f"DEBUG: Stripe session created: {checkout_session.id}")  # Debug line
                
                # Save the session ID
                submission.stripe_session_id = checkout_session.id
                submission.save()
                
                # Redirect to Stripe Checkout
                print(f"DEBUG: Redirecting to: {checkout_session.url}")  # Debug line
                return redirect(checkout_session.url)
                
            except Exception as e:
                # Handle Stripe errors
                print(f"DEBUG: Stripe error: {str(e)}")  # Debug line
                form.add_error(None, f"Payment error: {str(e)}")
                
                # Get all static pet images for the gallery
                all_pet_images = [
                    'img/com_9.PNG',
                    'img/com.JPG',
                    'img/com_2.jpg',
                    'img/com_1.jpg',
                    'img/com_4.jpg',
                ]
                
                return render(request, 'pages/pets.html', {
                    'form': form,
                    'all_pet_images': all_pet_images,
                    'business_name': 'Watercolors By Karla',
                    'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
                })
        else:
            # Form is not valid, show errors
            print(f"DEBUG: Form not valid, returning with errors")  # Debug line
            
            # Get all static pet images for the gallery
            all_pet_images = [
                'img/com_9.PNG',
                'img/com.JPG',
                'img/com_2.jpg',
                'img/com_1.jpg',
                'img/com_4.jpg',
            ]
            
            return render(request, 'pages/pets.html', {
                'form': form,
                'all_pet_images': all_pet_images,
                'business_name': 'Watercolors By Karla',
                'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
            })
    
    # If not POST, redirect back to pet gallery
    print(f"DEBUG: Not a POST request, redirecting to pets page")  # Debug line
    return redirect('pets')


def pet_portrait_success(request):
    """
    Handle successful payment
    """
    session_id = request.GET.get('session_id')
    
    if session_id:
        try:
            # Retrieve the session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Find the submission
            submission_id = session.metadata.get('submission_id')
            submission = get_object_or_404(PetPortraitSubmission, id=submission_id)
            
            # Update submission with payment info
            submission.payment_status = 'paid'
            submission.stripe_payment_intent_id = session.payment_intent
            submission.amount_paid = session.amount_total / 100  # Convert from cents
            submission.save()
            
            context = {
                'submission': submission,
                'business_name': 'Watercolors By Karla',
            }
            
            return render(request, 'pages/pet_portrait_success.html', context)
            
        except Exception as e:
            return render(request, 'pages/pet_portrait_success.html', {
                'error': str(e),
                'business_name': 'Watercolors By Karla',
            })
    
    return render(request, 'pages/pet_portrait_success.html', {
        'business_name': 'Watercolors By Karla',
    })


def pet_portrait_cancel(request):
    """
    Handle cancelled payment
    """
    submission_id = request.GET.get('submission_id')
    
    context = {
        'submission_id': submission_id,
        'business_name': 'Watercolors By Karla',
    }
    
    return render(request, 'pages/pet_portrait_cancel.html', context)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhooks for payment events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Retrieve submission and update
        submission_id = session.metadata.get('submission_id')
        if submission_id:
            try:
                submission = PetPortraitSubmission.objects.get(id=submission_id)
                submission.payment_status = 'paid'
                submission.stripe_payment_intent_id = session.payment_intent
                submission.amount_paid = session.amount_total / 100
                submission.save()
                
                # TODO: Send confirmation email to customer and notification to Karla
                
            except PetPortraitSubmission.DoesNotExist:
                pass
    
    return HttpResponse(status=200)