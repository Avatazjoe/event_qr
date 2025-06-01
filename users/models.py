# users/models.py

from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from django.dispatch import receiver


class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        User, related_name='followers', on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"


class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('event_created', 'Event Created'),
        ('user_followed', 'User Followed'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='activities'
    )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    content_object_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Activities"

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Profile(models.Model):
    # Definimos constantes para los roles
    ROLE_USER = 'user'
    ROLE_ORGANIZER = 'organizer'
    ROLE_OWNER = 'owner'
    ROLE_PROFESSIONAL = 'professional'
    ROLE_GROUP_TEAM = 'group_team'

    # Listado de todos los roles disponibles
    USER_ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_ORGANIZER, 'Organizer'),
        (ROLE_OWNER, 'Owner'),
        (ROLE_PROFESSIONAL, 'Professional'),
        (ROLE_GROUP_TEAM, 'Group/Team'),
    ]

    # Campo de rol con valor por defecto 'user'
    role = models.CharField(
        max_length=20,
        choices=USER_ROLE_CHOICES,
        default=ROLE_USER,
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    phone_number = PhoneNumberField(blank=True)  # Nuevo campo desde UserProfile
    role = models.CharField(
        max_length=20,
        choices=USER_ROLE_CHOICES,
        default='user',
    )

    # Owner fields
    venue_name = models.CharField('Venue Name', max_length=100, blank=True, null=True)
    opening_hours = models.TextField('Opening Hours', blank=True, null=True)
    capacity = models.PositiveIntegerField('Max Capacity', blank=True, null=True)
    gallery = models.JSONField('Gallery', blank=True, null=True)
    menu = models.JSONField('Menu/Pricing', blank=True, null=True)
    drink_menu = models.JSONField('Drink Menu', blank=True, null=True)
    rental_price = models.DecimalField('Rental Price (€)', max_digits=10, decimal_places=2, blank=True, null=True)

    # Organizer
    organizer_description = models.TextField('Organizer Description', blank=True, null=True)

    # Professional
    specialization = models.CharField('Specialization', max_length=100, blank=True, null=True)
    portfolio_url = models.URLField('Portfolio URL', blank=True, null=True)
    availability = models.TextField('Availability', blank=True, null=True)

    # Group / Team
    team_name = models.CharField('Group Name', max_length=100, blank=True, null=True)
    team_leader = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        related_name='led_teams', 
        null=True, 
        blank=True
    )
    team_members = models.ManyToManyField(
        User, 
        related_name='teams_joined', 
        blank=True
    )

    def __str__(self):
        return f"{self.user.username}'s Profile ({self.get_role_display()})"


# --- Signal ---
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()