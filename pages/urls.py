from django.urls import path

from .views import (
    AboutView,
    PricingView,
    home,
    LivePaintView,
    CommissionsView,
    PrintsView,
    BioView,

)

urlpatterns =[
    path('', home, name='home'),
    path("about/", AboutView.as_view(), name ='about'),
    path("pricing/", PricingView.as_view(), name ='pricing'),
    path("livepaint/", LivePaintView.as_view(), name ='livepaint'),
    path("commissions/", CommissionsView.as_view(), name ='commissions'),
    path("prints/", PrintsView.as_view(), name ='prints'),
    path("bio/", BioView.as_view(), name ='bio'),
]