from django.urls import path

from .views import (
    HomeView,
    AboutView,
    PricingView
)

urlpatterns =[
    path("", HomeView.as_view(), name ='home'),
    path("about/", AboutView.as_view(), name ='about'),
    path("pricing/", PricingView.as_view(), name ='pricing'),
]