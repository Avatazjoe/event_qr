# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.generic import UpdateView, DetailView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from .models import Profile, Follow, Activity
from .forms import (
    ProfileForm,
    OwnerProfileForm,
    OrganizerProfileForm,
    ProfessionalProfileForm,
    GroupProfileForm,
    AdvancedRoleSelectionForm,
)

from event.models import Evento
from marketplace.models import Product


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form, 'title': 'Register'})


class LandingPageView(TemplateView):
    template_name = 'users/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Evento.objects.order_by('-created_at')[:5]
        context['products'] = Product.objects.order_by('-created_at')[:5]
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


@login_required
def dashboard(request):
    user_events = []
    orders = []

    return render(request, 'users/dashboard.html', {
        'user_events': user_events,
        'orders': orders,
        'user': request.user
    })


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile_view.html'
    context_object_name = 'viewed_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return User.objects.select_related('profile').prefetch_related('followers', 'following')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewed_user = self.object

        # Asegurarse de que el perfil existe
        user_profile, created = Profile.objects.get_or_create(user=viewed_user)
        context['user_profile'] = user_profile

        context['is_following'] = Follow.objects.filter(follower=self.request.user, followed=viewed_user).exists()
        context['followers_count'] = viewed_user.followers.count()
        context['following_count'] = viewed_user.following.count()

        return context


class FollowUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user_to_follow = get_object_or_404(User, username=username)

        if request.user != user_to_follow:
            follow_instance, created = Follow.objects.get_or_create(
                follower=request.user,
                followed=user_to_follow
            )
            if created:
                Activity.objects.create(
                    user=request.user,
                    activity_type='user_followed',
                    description=f'Started following {user_to_follow.username}.',
                    content_object_url=reverse('users:profile_view', kwargs={'username': user_to_follow.username})
                )

        return HttpResponseRedirect(reverse('users:profile_view', kwargs={'username': username}))


class UnfollowUserView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        user_to_unfollow = get_object_or_404(User, username=username)

        Follow.objects.filter(follower=request.user, followed=user_to_unfollow).delete()
        return HttpResponseRedirect(reverse('users:profile_view', kwargs={'username': username}))


ROLE_SPECIFIC_FORMS = {
    Profile.ROLE_OWNER: OwnerProfileForm,
    Profile.ROLE_ORGANIZER: OrganizerProfileForm,
    Profile.ROLE_PROFESSIONAL: ProfessionalProfileForm,
    Profile.ROLE_GROUP_TEAM: GroupProfileForm,
}

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Initialize forms to None, they will be set based on context
    advanced_role_form = None
    role_specific_form = None

    if request.method == 'POST':
        if 'submit_advanced_role' in request.POST:
            if profile.advanced_role_selected_once:
                messages.warning(request, "You have already selected an advanced role and cannot change it.")
                return redirect('users:profile')
            # User is submitting the AdvancedRoleSelectionForm
            advanced_role_form = AdvancedRoleSelectionForm(request.POST)
            if advanced_role_form.is_valid():
                profile.role = advanced_role_form.cleaned_data['role']
                profile.advanced_role_selected_once = True
                profile.save()
                messages.success(request, "Role updated successfully!")
                return redirect('users:profile')
            # If form is invalid, it will be passed to the template below
        else:
            # User is submitting a role-specific profile form
            FormClass = ROLE_SPECIFIC_FORMS.get(profile.role)
            if FormClass:
                role_specific_form = FormClass(request.POST, request.FILES, instance=profile)
                if role_specific_form.is_valid():
                    role_specific_form.save()
                    messages.success(request, "Profile updated successfully!")
                    return redirect('users:profile')
                # If form is invalid, it will be passed to the template below
            else:
                # Fallback or error: No specific form for this role or role not set
                # This case should ideally not be reached if logic is correct
                messages.error(request, "Error processing profile update.")
                # Optionally, use a generic form like ProfileForm if appropriate
                # For now, just redirect or let it fall through to GET
                return redirect('users:profile')

    # GET request or fall-through from invalid POST processing
    current_form = None
    show_role_selection_form = False # Default to False

    if advanced_role_form and advanced_role_form.is_bound:
        # Case 1: AdvancedRoleSelectionForm was POSTed and is bound (i.e., invalid, valid would have redirected)
        # This implies profile.advanced_role_selected_once is False (checked in POST section)
        current_form = advanced_role_form
        show_role_selection_form = True
    elif role_specific_form and role_specific_form.is_bound:
        # Case 2: A role-specific form was POSTed and is bound (invalid)
        current_form = role_specific_form
        # show_role_selection_form remains False, as we are dealing with a role-specific form
    else:
        # Case 3: This is a GET request or a POST that didn't result in a bound form here
        # (e.g. successful POSTs redirect, other POSTs are not handled by this view directly)

        # Determine if role selection form should be shown on GET
        if not profile.advanced_role_selected_once and \
           profile.role == Profile.ROLE_USER and \
           request.GET.get('action') == 'select_role':
            show_role_selection_form = True
            current_form = AdvancedRoleSelectionForm()  # New, unbound form for selection

        elif profile.role in ROLE_SPECIFIC_FORMS:
            # User has an existing advanced role (implies advanced_role_selected_once is True,
            # or admin set it)
            # Show the appropriate role-specific form
            current_form = ROLE_SPECIFIC_FORMS[profile.role](instance=profile)
            show_role_selection_form = False # Do not show role selection if they have an advanced role

        # elif profile.role == Profile.ROLE_USER and not show_role_selection_form:
            # This covers:
            # - User is ROLE_USER, advanced_role_selected_once is False, but action is not 'select_role' (button shown)
            # - User is ROLE_USER, advanced_role_selected_once is True (should not select role again, button not shown)
            # In these scenarios, current_form remains None, and show_role_selection_form is False.
            # The template handles showing a button or just profile info.
            pass # current_form remains None, show_role_selection_form is False

    context = {
        'form': current_form,
        'profile': profile,
        'show_role_selection_form': show_role_selection_form, # This is now more directly controlled
        'current_role': profile.role,
        'advanced_role_selected_once': profile.advanced_role_selected_once,
        'show_select_advanced_role_button': (
            profile.role == Profile.ROLE_USER and
            not profile.advanced_role_selected_once and
            not show_role_selection_form # If form isn't shown, button might be
        )
    }
    return render(request, 'users/profile.html', context)


