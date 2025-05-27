from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login # Removed authenticate, logout as they are not used in CBVs directly this way
# from django.contrib.auth.decorators import login_required # Replaced by LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import UpdateView, TemplateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import HttpResponseRedirect


from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile, Follow, Activity
from event.models import Evento


def register(request): # Stays as function-based view
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user) # Ensure UserProfile is created
            login(request, user) # Log the user in
            return redirect('event:home')  # Redirect to namespaced home page after registration
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'users/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Fetch events created by the logged-in user
        context['user_events'] = Evento.objects.filter(creator=user).select_related('creator').order_by('-created_at')
        
        # Fetch activities for the feed
        following_users_qs = User.objects.filter(followers__follower=user)
        context['activity_feed'] = Activity.objects.filter(
            Q(user=user) | Q(user__in=following_users_qs)
        ).select_related('user__userprofile').order_by('-created_at')[:20]
        return context

class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile_view.html'
    context_object_name = 'viewed_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        # Optimize by selecting related UserProfile
        return User.objects.select_related('userprofile').prefetch_related('followers', 'following')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewed_user = self.object # self.object is the User instance
        
        # UserProfile might not exist if get_or_create wasn't called before,
        # but User.userprofile should handle this via OneToOne relation.
        # If UserProfile is guaranteed by register view, this is fine.
        # Otherwise, use get_or_create for user_profile.
        user_profile, created = UserProfile.objects.get_or_create(user=viewed_user)
        context['user_profile'] = user_profile
        
        context['is_following'] = Follow.objects.filter(follower=self.request.user, followed=viewed_user).exists()
        context['followers_count'] = viewed_user.followers.count() # Uses related_name from Follow model
        context['following_count'] = viewed_user.following.count() # Uses related_name from Follow model
        return context

class FollowUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs): # Original was GET based
        username = self.kwargs.get('username')
        user_to_follow = get_object_or_404(User, username=username)
        
        if request.user != user_to_follow:
            follow_instance, created = Follow.objects.get_or_create(follower=request.user, followed=user_to_follow)
            if created:
                Activity.objects.create(
                    user=request.user,
                    activity_type='user_followed',
                    description=f'Started following {user_to_follow.username}.',
                    # Corrected to use users:profile_view
                    content_object_url=reverse('users:profile_view', kwargs={'username': user_to_follow.username})
                )
        return HttpResponseRedirect(reverse('users:profile_view', kwargs={'username': username}))

class UnfollowUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs): # Original was GET based
        username = self.kwargs.get('username')
        user_to_unfollow = get_object_or_404(User, username=username)
        
        Follow.objects.filter(follower=request.user, followed=user_to_unfollow).delete()
        # Optionally, create an 'unfollowed' activity if desired
        return HttpResponseRedirect(reverse('users:profile_view', kwargs={'username': username}))
