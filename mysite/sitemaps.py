from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    protocol = "https"

    priority_map = {
        "home": 1.0,
        "pricing": 0.9,
        "livepaint": 0.9,
        "about": 0.8,
        "gallery": 0.8,
        "welcome": 0.7,
        "commissions": 0.7,
        "list": 0.6,
        "add-event": 0.6,
    }

    def items(self):
        return list(self.priority_map.keys())

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.priority_map.get(item, 0.5)

    def changefreq(self, item):
        if item in ("home", "gallery", "list"):
            return "weekly"
        return "monthly"