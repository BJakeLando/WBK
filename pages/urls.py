from django.urls import path

from .views import (
    AboutView,
    home,
    entrance,
    LivePaintView,
    CommissionsView,
    PrintsView,
    BioView,
    WelcomeView,
    GalleryView,
    PricingView,
    # Pet portrait views
    pet_gallery_view,
    create_pet_portrait_checkout,
    pet_portrait_success,
    pet_portrait_cancel,
    stripe_webhook,
)

urlpatterns = [
    # Entrance landing page (new root)
    path('', entrance, name='entrance'),

    # Wedding site
    path('wedding/', home, name='home'),
    path("about/", AboutView.as_view(), name='about'),
    path("pricing/", PricingView.as_view(), name='pricing'),
    path("livepaint/", LivePaintView.as_view(), name='livepaint'),
    path("commissions/", CommissionsView.as_view(), name='commissions'),
    path("prints/", PrintsView.as_view(), name='prints'),
    path("bio/", BioView.as_view(), name='bio'),
    path("welcome/", WelcomeView.as_view(), name='welcome'),
    path("gallery/", GalleryView.as_view(), name='gallery'),

    # Pet portrait pages
    path("pets/", pet_gallery_view, name='pets'),
    path("pets/checkout/", create_pet_portrait_checkout, name='create_pet_portrait_checkout'),
    path("pets/success/", pet_portrait_success, name='pet_portrait_success'),
    path("pets/cancel/", pet_portrait_cancel, name='pet_portrait_cancel'),
    path("pets/webhook/", stripe_webhook, name='pet_portrait_webhook'),
]