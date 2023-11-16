from django.urls import path

from .views import (
    AboutView,
    PricingView,
    home,
    categoryPage,
    detailPage,

)

urlpatterns =[
    path('', home, name='home'),
    path('category/<slug:slug>', categoryPage, name='image_category'),
    path('category/<slug:slug>/<slug:slug2>', detailPage, name='image-detail'),
    path("about/", AboutView.as_view(), name ='about'),
    path("pricing/", PricingView.as_view(), name ='pricing'),
]