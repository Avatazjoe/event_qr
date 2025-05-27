from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone # For EventoSitemap items filtering, if used

from event.models import Evento
from marketplace.models import Product
from django.contrib.auth.models import User

class EventoSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        # As per subtask, starting with all events.
        # Future enhancement: Evento.objects.filter(fecha__gte=timezone.now()).order_by('-fecha')
        return Evento.objects.all()

    def lastmod(self, obj):
        # Assuming 'created_at' is the most relevant field for last modification.
        # If 'fecha' (event date) or another field like 'updated_at' is more appropriate,
        # this should be changed.
        return obj.created_at

    # get_absolute_url is defined in the Evento model

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj):
        return obj.created_at # Product model has created_at

    # get_absolute_url is defined in the Product model

class UserProfilesSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        # Assuming only active users with profiles should be in sitemap
        return User.objects.filter(is_active=True)

    def location(self, obj):
        # Ensure 'users:profile_view' is the correct namespaced URL name for viewing user profiles
        # and it takes 'username' as a kwarg.
        return reverse('users:profile_view', kwargs={'username': obj.username})

    # lastmod can be added if user profiles have a last updated timestamp, e.g., from UserProfile model
    # def lastmod(self, obj):
    #     try:
    #         return obj.userprofile.updated_at # Assuming UserProfile has updated_at
    #     except UserProfile.DoesNotExist:
    #         return None # Or user's date_joined or some default
    # For now, lastmod is omitted as per instructions.
