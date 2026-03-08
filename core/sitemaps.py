"""
Sitemaps for ZooBozor — helps Google index all listings.
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Animal


class AnimalSitemap(Sitemap):
    """Sitemap for individual animal listing pages."""
    changefreq = 'daily'
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Animal.objects.filter(is_sold=False).order_by('-created_at')

    def lastmod(self, obj):
        return obj.updated_at if hasattr(obj, 'updated_at') else obj.created_at

    def location(self, obj):
        return reverse('animal_detail', args=[obj.pk])


class StaticPagesSitemap(Sitemap):
    """Sitemap for static pages (home, about, etc.)."""
    changefreq = 'weekly'
    priority = 1.0
    protocol = 'https'

    def items(self):
        return ['home', 'add_animal']

    def location(self, item):
        return reverse(item)
