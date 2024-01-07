from django.shortcuts import render
from .models import *

from django.views.generic import TemplateView

def home(request):
    categories = Category.objects.all()
    context = {}
    context['categories'] = categories
    return render(request, 'pages/home.html', context)

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


# def categoryPage(request, slug):

#     category = Category.objects.get(slug=slug)
#     images = Image.objects.filter(category=category).order_by('-date_created')
#     context = {}
#     context['images'] = images
#     context['category'] = category

#     return render(request, 'pages/lp.html', context)


# def detailPage(request, slug1, slug2):
#     category = Category.objects.get(slug=slug1)
#     image = Image.objects.get(slug=slug2)

#     context = {}
#     context['category'] = category
#     context['image'] = image

#     return render(request, 'pages/image.html', context)
