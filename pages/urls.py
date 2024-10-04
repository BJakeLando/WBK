from django.urls import path

from .views import (
    AboutView,
    home,
    LivePaintView,
    CommissionsView,
    PrintsView,
    BioView,
    WelcomeView,
    GalleryView,
    PetsView,

)

urlpatterns =[
    path('', home, name='home'),
    path("about/", AboutView.as_view(), name ='about'),
    # path("pricing/", PricingView.as_view(), name ='pricing'),
    path("livepaint/", LivePaintView.as_view(), name ='livepaint'),
    path("commissions/", CommissionsView.as_view(), name ='commissions'),
    path("pets/", PetsView.as_view(), name ='pets'),
    path("prints/", PrintsView.as_view(), name ='prints'),
    path("bio/", BioView.as_view(), name ='bio'),
    path("welcome/", WelcomeView.as_view(), name ='welcome'),
    path("gallery/", GalleryView.as_view(), name ='gallery'),
]