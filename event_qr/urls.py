"""
URL configuration for event_qr project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from .sitemaps import EventoSitemap, ProductSitemap, UserProfilesSitemap
from users.views import LandingPageView # Import LandingPageView

sitemaps = {
    'eventos': EventoSitemap,
    'products': ProductSitemap,
    'users': UserProfilesSitemap,
}

urlpatterns = [
    path("", LandingPageView.as_view(), name="landing_page_root"), # Map root to LandingPageView
    path("admin/", admin.site.urls),
    path('event/', include('event.urls', namespace='event')),
    path('users/', include('users.urls', namespace='users')), # users.urls already included
    path('marketplace/', include('marketplace.urls', namespace='marketplace')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
