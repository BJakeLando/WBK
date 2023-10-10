from django.shortcuts import render

from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'pages/home.html'

class AboutView(TemplateView):
    template_name = 'pages/about.html'

class PricingView(TemplateView):
    template_name = 'pages/pricing.html'