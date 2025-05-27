from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True)
    phone_number = PhoneNumberField(blank=True)
    ROLE_CHOICES = [
        ('organizer', 'Organizer'),
        ('owner', 'Owner'),
        ('professional', 'Professional'),
        ('group_team', 'Group/Team'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='professional')

    def __str__(self):
        return self.user.username

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed') # Ensures a user cannot follow another user multiple times
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"

class Activity(models.Model):
    ACTIVITY_TYPES = (
        ('event_created', 'Event Created'),
        ('user_followed', 'User Followed'),
        # Add more types as needed
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    # Generic foreign key to link to related objects (e.g., Evento, User)
    # For simplicity, we might start with just storing a description or link manually
    # For a more robust solution, GenericForeignKey from django.contrib.contenttypes.fields would be used.
    content_object_url = models.URLField(blank=True, null=True) # URL to the related object
    description = models.TextField(blank=True) # A textual description of the activity

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Activities"

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
