from django.urls import path
from . import views

from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='event:home'), name='logout'), # Updated to namespaced home
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('user/<str:username>/', views.UserProfileDetailView.as_view(), name='profile_view'),
    path('user/<str:username>/follow/', views.FollowUserView.as_view(), name='follow_user'),
    path('user/<str:username>/unfollow/', views.UnfollowUserView.as_view(), name='unfollow_user'),
]
