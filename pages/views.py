from django.shortcuts import render
from .models import *

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

class PrintsView(TemplateView):
    template_name = 'pages/prints.html'



