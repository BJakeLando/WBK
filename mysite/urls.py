from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

from mysite.sitemaps import StaticViewSitemap


sitemaps = {
    "static": StaticViewSitemap,
}


urlpatterns = [
    path('admin/', admin.site.urls),

    # ── SEO ──
    path(
        'sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    path(
        'robots.txt',
        TemplateView.as_view(
            template_name='robots.txt',
            content_type='text/plain',
        ),
        name='robots',
    ),

    path('', include('pages.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('accounts.urls')),
    path('reviews/', include('reviews.urls')),
    path('shop/', include('shop.urls')),
]