from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.profiles.models import Profile


class ProfileModelTestCase(TestCase):
    """Test cases for Profile model"""

    def setUp(self):
        """Set up test data - profile is auto-created by signal"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Profile is auto-created by signal, so get it
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_auto_creation(self):
        """Test that profile is automatically created with user"""
        # Profile should exist after user creation
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_update(self):
        """Test updating a profile"""
        self.profile.first_name = 'John'
        self.profile.last_name = 'Doe'
        self.profile.phone = '+62123456789'
        self.profile.email = 'john@example.com'
        self.profile.account_type = 'BUYER'
        self.profile.save()
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'John')
        self.assertEqual(self.profile.last_name, 'Doe')
        self.assertEqual(self.profile.account_type, 'BUYER')
        self.assertEqual(str(self.profile), f"Profile({self.user.username})")

    def test_profile_default_values(self):
        """Test profile default values"""
        self.assertEqual(self.profile.account_type, 'BUYER')
        self.assertFalse(self.profile.newsletter_opt_in)
        self.assertEqual(self.profile.first_name, '')
        self.assertEqual(self.profile.last_name, '')

    def test_profile_account_type_choices(self):
        """Test profile account type choices"""
        # Test BUYER (default)
        self.assertEqual(self.profile.account_type, 'BUYER')
        
        # Test SELLER
        user2 = User.objects.create_user(username='seller', password='test')
        profile2 = Profile.objects.get(user=user2)
        profile2.account_type = 'SELLER'
        profile2.save()
        self.assertEqual(profile2.account_type, 'SELLER')

    def test_get_full_name_with_names(self):
        """Test get_full_name with first and last name"""
        self.profile.first_name = 'John'
        self.profile.last_name = 'Doe'
        self.profile.save()
        self.assertEqual(self.profile.get_full_name(), 'John Doe')

    def test_get_full_name_without_names(self):
        """Test get_full_name falls back to username"""
        self.assertEqual(self.profile.get_full_name(), self.user.username)

    def test_get_full_name_with_only_first_name(self):
        """Test get_full_name with only first name"""
        self.profile.first_name = 'John'
        self.profile.save()
        self.assertEqual(self.profile.get_full_name(), 'John')

    def test_profile_one_to_one_relationship(self):
        """Test profile has one-to-one relationship with user"""
        # Test reverse relationship
        self.assertEqual(self.user.profile, self.profile)

    def test_profile_cascade_delete(self):
        """Test that profile is deleted when user is deleted"""
        profile_id = self.profile.id
        
        self.user.delete()
        
        self.assertFalse(Profile.objects.filter(id=profile_id).exists())

    def test_profile_newsletter_opt_in(self):
        """Test newsletter opt-in field"""
        self.profile.newsletter_opt_in = True
        self.profile.save()
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.newsletter_opt_in)

    def test_profile_preferred_sports(self):
        """Test preferred sports field"""
        self.profile.preferred_sports = 'Running, Swimming, Cycling'
        self.profile.save()
        self.profile.refresh_from_db()
        self.assertIn('Running', self.profile.preferred_sports)
        self.assertIn('Swimming', self.profile.preferred_sports)

