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


@login_required
def profile(request):
    user_profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=user_profile)

    return render(request, 'users/profile.html', {
        'form': form,
        'user': request.user
    })


# === Selección y edición por rol ===

@login_required
def profile_view(request):
    """
    Muestra el perfil del usuario y permite seleccionar un rol avanzado.
    Si ya tiene un rol avanzado, redirige a la vista específica.
    """
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        selected_role = request.POST.get('role')
        valid_roles = [choice[0] for choice in Profile.USER_ROLE_CHOICES if choice[0] != 'user']

        if selected_role in valid_roles:
            profile.role = selected_role
            profile.save()
            return redirect(f'update_{selected_role}_profile')

    #return render(request, 'users/profile.html', {'profile': profile})
    return redirect('users:update_{}_profile'.format(selected_role))


@login_required
def update_owner_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = OwnerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = OwnerProfileForm(instance=profile)

    return render(request, 'users/update_owner_profile.html', {'form': form})


@login_required
def update_organizer_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = OrganizerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = OrganizerProfileForm(instance=profile)

    return render(request, 'users/update_organizer_profile.html', {'form': form})


@login_required
def update_professional_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = ProfessionalProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = ProfessionalProfileForm(instance=profile)

    return render(request, 'users/update_professional_profile.html', {'form': form})


@login_required
def update_group_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        form = GroupProfileForm(request.POST, instance=profile)
        if form.is_valid():
            group_profile = form.save(commit=False)
            group_profile.team_leader = request.user
            group_profile.save()
            form.save_m2m()  # Guarda las relaciones ManyToMany
            return redirect('users:profile')
    else:
        form = GroupProfileForm(instance=profile)

    return render(request, 'users/update_group_profile.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .models import Profile


@login_required
def set_advanced_role(request):
    """
    Permite al usuario cambiar su rol desde 'user' a uno de los roles avanzados.
    La vista solo acepta peticiones POST y valida que el nuevo rol esté permitido.
    """
    if request.method == 'POST':
        new_role = request.POST.get('role')

        # Lista de roles avanzados válidos
        ADVANCED_ROLES = [
            Profile.ROLE_ORGANIZER,
            Profile.ROLE_OWNER,
            Profile.ROLE_PROFESSIONAL,
            Profile.ROLE_GROUP_TEAM,
        ]

        if new_role in ADVANCED_ROLES:
            request.user.profile.role = new_role
            request.user.profile.save()
            messages.success(request, f"Rol actualizado a: {new_role}")
        else:
            messages.error(request, "Rol no válido.")

    return redirect('users:profile')


