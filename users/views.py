from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404 # Added get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile, Follow, Activity 
from event.models import Evento 
from django.urls import reverse 
from django.db.models import Q # For complex queries

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('home')  # Redirect to home page after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile') # Redirect to profile page after saving
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'users/profile.html', {'form': form})

@login_required
def dashboard(request):
    # Fetch events created by the logged-in user
    user_events = Evento.objects.filter(creator=request.user).order_by('-created_at')
    
    # Fetch activities for the feed: user's own activities and activities of users they follow
    following_users = User.objects.filter(followers__follower=request.user)
    activity_feed = Activity.objects.filter(
        Q(user=request.user) | Q(user__in=following_users)
    ).select_related('user').order_by('-created_at')[:20] # Get latest 20 activities

    return render(request, 'users/dashboard.html', {
        'user_events': user_events, 
        'activity_feed': activity_feed
    })

@login_required
def profile_view(request, username):
    viewed_user = get_object_or_404(User, username=username)
    user_profile, created = UserProfile.objects.get_or_create(user=viewed_user)
    is_following = Follow.objects.filter(follower=request.user, followed=viewed_user).exists() if request.user.is_authenticated else False
    followers_count = viewed_user.followers.count()
    following_count = viewed_user.following.count()
    # Add user's events to context if needed
    # user_events = Evento.objects.filter(creator=viewed_user).order_by('-created_at')
    
    context = {
        'viewed_user': viewed_user,
        'user_profile': user_profile,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        # 'user_events': user_events,
    }
    return render(request, 'users/profile_view.html', context)

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if request.user != user_to_follow: # Users cannot follow themselves
        follow_instance, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
        if created:
            Activity.objects.create(
                user=request.user,
                activity_type='user_followed',
                description=f'Started following {user_to_follow.username}.',
                content_object_url=reverse('profile_view', kwargs={'username': user_to_follow.username})
            )
    return redirect('profile_view', username=username)

@login_required
def unfollow_user(request, username):
    user_to_unfollow = get_object_or_404(User, username=username)
    Follow.objects.filter(follower=request.user, followed=user_to_unfollow).delete()
    return redirect('profile_view', username=username)
