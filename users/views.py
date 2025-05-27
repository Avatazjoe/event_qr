from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login # Removed authenticate, logout as they are not used in CBVs directly this way
from django.contrib.auth.decorators import login_required # Added import
from django.contrib.auth.models import User
from django.views.generic import UpdateView, DetailView, View, TemplateView # Added TemplateView back
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm # Use Django's built-in form
from django.contrib import messages # Optional: for success messages


# from .forms import UserRegistrationForm # UserRegistrationForm no longer used for this view
from .forms import ProfileForm, UserProfileForm # Added UserProfileForm back
from .models import UserProfile, Follow, Activity # UserProfile might be needed if we auto-create it
from event.models import Evento
from marketplace.models import Product


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save() # This saves the new user
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login') # Redirect to login page after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form, 'title': 'Register'})


class LandingPageView(TemplateView): # Make sure TemplateView is imported if not already
    template_name = 'users/landing_page.html' # Or a more generic path like 'landing_page.html'

    def get_context_data(self, **kwargs): # Make sure TemplateView is imported
        # Need to import TemplateView from django.views.generic
        # from django.views.generic import TemplateView
        context = super().get_context_data(**kwargs)
        # Fetch latest 5 events (order by most recent or upcoming, e.g., by 'created_at' or 'fecha')
        context['events'] = Evento.objects.order_by('-created_at')[:5]
        # Fetch latest 5 products
        context['products'] = Product.objects.order_by('-created_at')[:5]
        return context

# Need to ensure UpdateView is imported if not already (it is)
# from django.views.generic import UpdateView

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm # This form might need adjustment if it conflicts with Profile model
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

# from marketplace.models import Order # Assuming Order model is in marketplace app. This will be needed later.
                                        # For now, orders will be an empty list or a placeholder.
@login_required
def dashboard(request):
    user_events = []  # Placeholder for actual event participation
    # orders = Order.objects.filter(user=request.user).select_related('product')[:5] # Placeholder, Order model might not exist yet or accessible
    orders = [] # Using empty list for now as Order model might not be fully set up or might be in Phase 2
    
    # Example of how you might fetch actual orders if the model is ready:
    # try:
    #     from marketplace.models import Order
    #     orders = Order.objects.filter(user=request.user).select_related('product').order_by('-created_at')[:5]
    # except ImportError:
    #     orders = [] # Fallback if Order model isn't found

    return render(request, 'users/dashboard.html', {
        'user_events': user_events,
        'orders': orders,
        'user': request.user # Explicitly passing user, though it's available via request in template
    })

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

# from django.contrib.auth.forms import UserChangeForm # Not used directly here for Profile
from .forms import ProfileForm # Assuming ProfileForm is in the same app's forms.py
# from .models import Profile # Profile model needed for instance

@login_required
def profile(request):
    # Ensure profile exists, or create if using a signal doesn't cover all cases (e.g. existing users)
    # For this implementation, we assume the post_save signal handles profile creation.
    # Accessing profile via the OneToOneField related name.
    # If the Profile model has `related_name='profile'` on its OneToOneField to User,
    # then `request.user.profile` is correct. Otherwise, it's `request.user.profile_set` or similar.
    # Given the model was defined as `user = models.OneToOneField(User, on_delete=models.CASCADE)`,
    # the default related name is `profile`.
    user_profile = request.user.profile 

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            # messages.success(request, 'Your profile was successfully updated!') # Optional: add messages
            return redirect('users:profile') # Redirect to the same page, often to show changes (or a success page)
        # else:
            # messages.error(request, 'Please correct the error below.') # Optional
    else:
        form = ProfileForm(instance=user_profile)
    
    return render(request, 'users/profile.html', {
        'form': form,
        'user': request.user # Explicitly passing user
    })
