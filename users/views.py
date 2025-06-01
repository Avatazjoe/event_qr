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

    # GET request or fall-through from invalid POST
    current_form = None
    show_role_selection_form = False

    if profile.role in ROLE_SPECIFIC_FORMS:
        # User has an advanced role
        # If role_specific_form is already set (from invalid POST), use it, else create new
        current_form = role_specific_form if role_specific_form else ROLE_SPECIFIC_FORMS[profile.role](instance=profile)
    elif profile.role == Profile.ROLE_USER:
        if profile.advanced_role_selected_once:
            # Scenario 2: User is 'user' but selected an advanced role before
            show_role_selection_form = True
            current_form = advanced_role_form if advanced_role_form else AdvancedRoleSelectionForm()
        else:
            # Scenario 3: User is 'user' and choosing for the first time OR initial view
            if request.GET.get('action') == 'select_role':
                show_role_selection_form = True
                current_form = advanced_role_form if advanced_role_form else AdvancedRoleSelectionForm()
            else:
                # Initial view for a 'user' not yet selecting a role.
                # No form is shown by default, template will show "Elegir Rol Avanzado" button.
                # If you want to show a basic ProfileForm (avatar/bio) here, you could instantiate it.
                # For this task, current_form remains None if no action and not advanced_role_selected_once.
                pass # current_form remains None

    # Default/Fallback form assignment if still None but should have one
    if current_form is None:
        if show_role_selection_form: # This implies advanced_role_form should have been set or is new
            current_form = advanced_role_form if advanced_role_form else AdvancedRoleSelectionForm()
        elif profile.role == Profile.ROLE_USER and not show_role_selection_form and not profile.advanced_role_selected_once:
            # This is the state where the user is basic, hasn't selected a role via ?action=select_role
            # and hasn't selected an advanced role before. The template will show a button.
            # Optionally, show a basic ProfileForm for avatar/bio.
            # For now, we assume role-specific forms handle all profile fields including avatar/bio.
            # If you need a basic form: current_form = ProfileForm(instance=profile)
            pass


    context = {
        'form': current_form,
        'profile': profile,
        'show_role_selection_form': show_role_selection_form,
        'current_role': profile.role,
        'advanced_role_selected_once': profile.advanced_role_selected_once,
        'show_select_advanced_role_button': (
            profile.role == Profile.ROLE_USER and
            not profile.advanced_role_selected_once and
            not show_role_selection_form and
            request.GET.get('action') != 'select_role' # Also hide if action=select_role is present
        )
    }
    return render(request, 'users/profile.html', context)


