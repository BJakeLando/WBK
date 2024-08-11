from django.shortcuts import render

from django.views.generic import TemplateView

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

class PetsView(TemplateView):
    template_name = 'pages/pets.html'

class PrintsView(TemplateView):
    template_name = 'pages/prints.html'

class BioView(TemplateView):
    template_name = 'pages/bio.html'

class WelcomeView(TemplateView):
    template_name = 'pages/welcome.html'

class GalleryView(TemplateView):
    template_name = 'pages/gallery.html'