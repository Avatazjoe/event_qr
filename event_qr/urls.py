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
from django.contrib.auth import views as auth_views # Added for auth views
from django.conf import settings # For media files in development
from django.conf.urls.static import static # For media files in development

# Assuming event.views.home might be used elsewhere or was a placeholder,
# for now, LandingPageView is the effective project home.
# from event.views import home # This was in the provided snippet

sitemaps = {
    'eventos': EventoSitemap,
    'products': ProductSitemap,
    'users': UserProfilesSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", LandingPageView.as_view(), name="project_home"), # Renamed landing_page_root to project_home

    # App-specific URLs
    path('event/', include('event.urls', namespace='event')),
    path('users/', include('users.urls', namespace='users')),
    path('marketplace/', include('marketplace.urls', namespace='marketplace')),

    # Auth URLs from the provided snippet
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='project_home'), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),

    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
