from django.urls import path
from . import views # This will import all views from users/views.py

# Removed auth_views import here as login/logout are handled at project level now
# from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing_page'), # New landing page URL
    path('register/', views.register, name='register'),
    # path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'), # Handled at project level
    # path('logout/', auth_views.LogoutView.as_view(next_page='event:home'), name='logout'), # Handled at project level
    path('profile/', views.profile, name='profile'), # Changed to function-based view
    path('dashboard/', views.dashboard, name='dashboard'), # Changed to function-based view
    path('user/<str:username>/', views.UserProfileDetailView.as_view(), name='profile_view'),
    path('user/<str:username>/follow/', views.FollowUserView.as_view(), name='follow_user'),
    path('user/<str:username>/unfollow/', views.UnfollowUserView.as_view(), name='unfollow_user'),
]
