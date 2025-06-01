from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from .forms import (
    AdvancedRoleSelectionForm,
    OwnerProfileForm,
    OrganizerProfileForm,
    ProfessionalProfileForm,
    GroupProfileForm
)

# Create your tests here.

class AdvancedRoleSelectionFormTest(TestCase):
    def test_valid_data(self):
        form = AdvancedRoleSelectionForm(data={'role': Profile.ROLE_OWNER})
        self.assertTrue(form.is_valid())

    def test_invalid_role_choice(self):
        form = AdvancedRoleSelectionForm(data={'role': 'invalid_role'})
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)

    def test_empty_data(self):
        form = AdvancedRoleSelectionForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('role', form.errors)

    def test_choices_are_correct(self):
        form = AdvancedRoleSelectionForm()
        expected_choices = [
            (Profile.ROLE_ORGANIZER, 'Organizer'),
            (Profile.ROLE_OWNER, 'Owner'),
            (Profile.ROLE_PROFESSIONAL, 'Professional'),
            (Profile.ROLE_GROUP_TEAM, 'Group/Team'),
        ]
        # choices on the field are rendered as a list of tuples
        # form.fields['role'].choices is a list of tuples like [('value', 'Display Name'), ...]
        self.assertEqual(list(form.fields['role'].choices), expected_choices)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        # Profile should be created automatically by the signal
        self.profile = self.user.profile
        self.profile_url = reverse('users:profile')

    def test_initial_view_new_user(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_select_advanced_role_button'])
        self.assertFalse(response.context['show_role_selection_form'])
        self.assertIn('?action=select_role', response.content.decode())
        self.assertIsNone(response.context.get('form')) # No form initially

    def test_action_select_role(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.profile_url, {'action': 'select_role'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_role_selection_form'])
        self.assertFalse(response.context['show_select_advanced_role_button'])
        self.assertIsInstance(response.context['form'], AdvancedRoleSelectionForm)
        self.assertContains(response, 'name="submit_advanced_role"') # Check for hidden input
        self.assertFalse(self.profile.advanced_role_selected_once) # Ensure this state

    def test_submit_advanced_role_selection_valid_and_message(self):
        self.client.login(username='testuser', password='password123')
        self.assertFalse(self.profile.advanced_role_selected_once)
        post_data = {'role': Profile.ROLE_OWNER, 'submit_advanced_role': 'true'}
        response = self.client.post(self.profile_url, post_data, follow=True) # follow=True to get the final page

        self.assertEqual(response.status_code, 200) # After redirect
        self.assertRedirects(response, self.profile_url, status_code=302, target_status_code=200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Role updated successfully!")

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.role, Profile.ROLE_OWNER)
        self.assertTrue(self.profile.advanced_role_selected_once)

        # Check the view after redirect (already done by follow=True)
        self.assertIsInstance(response.context['form'], OwnerProfileForm)
        self.assertFalse(response.context['show_role_selection_form'])

    def test_view_profile_with_advanced_role_set(self):
        self.profile.role = Profile.ROLE_ORGANIZER
        self.profile.advanced_role_selected_once = True
        self.profile.save()

        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], OrganizerProfileForm)
        self.assertFalse(response.context['show_role_selection_form'])
        self.assertFalse(response.context['show_select_advanced_role_button'])

    def test_submit_role_specific_form_valid_and_message(self):
        self.profile.role = Profile.ROLE_OWNER
        self.profile.advanced_role_selected_once = True
        self.profile.save()

        self.client.login(username='testuser', password='password123')
        post_data = {'venue_name': 'My Awesome Venue'} # Example field for OwnerProfileForm
        response = self.client.post(self.profile_url, post_data, follow=True)

        self.assertEqual(response.status_code, 200) # After redirect
        self.assertRedirects(response, self.profile_url, status_code=302, target_status_code=200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Profile updated successfully!")

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.venue_name, 'My Awesome Venue')

    def test_submit_advanced_role_selection_invalid(self):
        self.client.login(username='testuser', password='password123')
        self.assertFalse(self.profile.advanced_role_selected_once) # Pre-condition
        post_data = {'role': 'invalid_role_again', 'submit_advanced_role': 'true'}
        response = self.client.post(self.profile_url, post_data)

        self.assertEqual(response.status_code, 200) # Should re-render with errors
        self.assertIsInstance(response.context['form'], AdvancedRoleSelectionForm)
        self.assertTrue(response.context['form'].errors)
        self.assertTrue(response.context['show_role_selection_form']) # Still show this form
        self.assertFalse(self.profile.advanced_role_selected_once) # Should not change on invalid

    def test_submit_role_specific_form_invalid(self):
        self.profile.role = Profile.ROLE_OWNER
        self.profile.advanced_role_selected_once = True
        self.profile.save()

        self.client.login(username='testuser', password='password123')
        # Assuming 'capacity' for OwnerProfileForm must be a positive integer
        post_data = {'capacity': 'not-a-number'}
        response = self.client.post(self.profile_url, post_data)

        self.assertEqual(response.status_code, 200) # Re-render with errors
        self.assertIsInstance(response.context['form'], OwnerProfileForm)
        self.assertTrue(response.context['form'].errors)
        self.assertIn('capacity', response.context['form'].errors)
        self.assertFalse(response.context['show_role_selection_form']) # Should show owner form, not selection

    # Tests for Access Control for Role Change
    def test_can_see_advanced_role_form_if_not_selected_yet(self):
        self.client.login(username='testuser', password='password123')
        self.profile.advanced_role_selected_once = False
        self.profile.role = Profile.ROLE_USER # Ensure basic user role
        self.profile.save()

        response = self.client.get(self.profile_url, {'action': 'select_role'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_role_selection_form'])
        self.assertIsInstance(response.context['form'], AdvancedRoleSelectionForm)
        self.assertFalse(response.context['show_select_advanced_role_button'])


    def test_cannot_see_advanced_role_form_if_already_selected(self):
        self.client.login(username='testuser', password='password123')
        self.profile.role = Profile.ROLE_OWNER # Has an advanced role
        self.profile.advanced_role_selected_once = True
        self.profile.save()

        response = self.client.get(self.profile_url, {'action': 'select_role'}) # Attempt to select role
        self.assertEqual(response.status_code, 200)
        # Should show the OwnerProfileForm, not AdvancedRoleSelectionForm
        self.assertIsInstance(response.context['form'], OwnerProfileForm)
        self.assertFalse(response.context['show_role_selection_form'])
        self.assertFalse(response.context['show_select_advanced_role_button'])

    def test_cannot_submit_advanced_role_if_already_selected_and_warning_message(self):
        self.client.login(username='testuser', password='password123')
        original_role = Profile.ROLE_OWNER
        self.profile.role = original_role
        self.profile.advanced_role_selected_once = True
        self.profile.save()

        # Attempt to POST to change role to Organizer
        post_data = {'role': Profile.ROLE_ORGANIZER, 'submit_advanced_role': 'true'}
        response = self.client.post(self.profile_url, post_data, follow=True)

        self.assertEqual(response.status_code, 200) # After redirect
        self.assertRedirects(response, self.profile_url, status_code=302, target_status_code=200)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have already selected an advanced role and cannot change it.")

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.role, original_role) # Role should not have changed

        # The form displayed should be for the original role (Owner)
        self.assertIsInstance(response.context['form'], OwnerProfileForm)
        self.assertFalse(response.context['show_role_selection_form'])
        self.assertFalse(response.context['show_select_advanced_role_button'])
