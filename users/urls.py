from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'), # Redirect to home after logout
    path('profile/', views.profile, name='profile'), # Logged-in user's own profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('user/<str:username>/', views.profile_view, name='profile_view'), # To view other users' profiles
    path('user/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('user/<str:username>/unfollow/', views.unfollow_user, name='unfollow_user'),
]
