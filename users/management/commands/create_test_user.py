from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile

class Command(BaseCommand):
    help = 'Creates a test user with a specific role'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username for the new user')
        parser.add_argument('password', type=str, help='The password for the new user')
        parser.add_argument('email', type=str, help='The email for the new user')
        parser.add_argument('role', type=str, choices=['organizer', 'owner', 'professional', 'group_team'], help='The role for the user profile')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        role = options['role']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists.'))
            user = User.objects.get(username=username)
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            self.stdout.write(self.style.SUCCESS(f'Successfully created user "{username}"'))

        # Create or update UserProfile
        user_profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': role}
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created profile for "{username}" with role "{role}"'))
        else:
            # If profile already existed, update the role if it's different
            if user_profile.role != role:
                user_profile.role = role
                user_profile.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully updated role for "{username}" to "{role}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Profile for "{username}" already exists with role "{role}". No change made.'))

        # Verify the role
        try:
            profile = UserProfile.objects.get(user=user)
            if profile.role == role:
                self.stdout.write(self.style.SUCCESS(f'Verified: User "{username}" has role "{profile.role}".'))
            else:
                self.stdout.write(self.style.ERROR(f'Verification FAILED: User "{username}" has role "{profile.role}", expected "{role}".'))
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Verification FAILED: UserProfile for "{username}" does not exist.'))
