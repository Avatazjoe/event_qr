# users/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Profile  # Solo Profile, ya no UserProfile
from phonenumber_field.formfields import PhoneNumberField


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    ROLE_CHOICES = [
        ('organizer', 'Organizer'),
        ('owner', 'Owner'),
        ('professional', 'Professional'),
        ('group_team', 'Group/Team'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return password_confirm


class ProfileForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        label='Phone Number',
        required=False
    )

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'phone_number']


# === Formularios específicos por rol ===

class OwnerProfileForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        label='Phone Number',
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'bio',
            'phone_number',
            'venue_name',
            'opening_hours',
            'capacity',
            'gallery',
            'menu',
            'drink_menu',
            'rental_price'
        ]


class OrganizerProfileForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        label='Phone Number',
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'bio',
            'phone_number',
            'organizer_description'
        ]


class ProfessionalProfileForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        label='Phone Number',
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'bio',
            'phone_number',
            'specialization',
            'portfolio_url',
            'availability'
        ]


class GroupProfileForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        label='Phone Number',
        required=False
    )
    team_members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'bio',
            'phone_number',
            'team_name',
            'team_leader',
            'team_members'
        ]