from django.test import TestCase, Client
from django.contrib.auth.models import User
from apps.profiles.models import Profile


class ProfileModelTestCase(TestCase):
    """Test cases for Profile model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_profile_creation(self):
        """Test creating a profile"""
        profile = Profile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            phone='+62123456789',
            email='john@example.com',
            account_type='BUYER'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.first_name, 'John')
        self.assertEqual(profile.last_name, 'Doe')
        self.assertEqual(profile.account_type, 'BUYER')
        self.assertEqual(str(profile), f"Profile({self.user.username})")

    def test_profile_default_values(self):
        """Test profile default values"""
        profile = Profile.objects.create(user=self.user, email='test@example.com')
        self.assertEqual(profile.account_type, 'BUYER')
        self.assertFalse(profile.newsletter_opt_in)
        self.assertEqual(profile.first_name, '')
        self.assertEqual(profile.last_name, '')

    def test_profile_account_type_choices(self):
        """Test profile account type choices"""
        # Test BUYER
        profile = Profile.objects.create(
            user=self.user,
            email='test@example.com',
            account_type='BUYER'
        )
        self.assertEqual(profile.account_type, 'BUYER')
        
        # Test SELLER
        user2 = User.objects.create_user(username='seller', password='test')
        profile2 = Profile.objects.create(
            user=user2,
            email='seller@example.com',
            account_type='SELLER'
        )
        self.assertEqual(profile2.account_type, 'SELLER')

    def test_get_full_name_with_names(self):
        """Test get_full_name with first and last name"""
        profile = Profile.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com'
        )
        self.assertEqual(profile.get_full_name(), 'John Doe')

    def test_get_full_name_without_names(self):
        """Test get_full_name falls back to username"""
        profile = Profile.objects.create(user=self.user, email='test@example.com')
        self.assertEqual(profile.get_full_name(), self.user.username)

    def test_get_full_name_with_only_first_name(self):
        """Test get_full_name with only first name"""
        profile = Profile.objects.create(
            user=self.user,
            first_name='John',
            email='john@example.com'
        )
        self.assertEqual(profile.get_full_name(), 'John')

    def test_profile_one_to_one_relationship(self):
        """Test profile has one-to-one relationship with user"""
        profile = Profile.objects.create(user=self.user, email='test@example.com')
        
        # Test reverse relationship
        self.assertEqual(self.user.profile, profile)

    def test_profile_cascade_delete(self):
        """Test that profile is deleted when user is deleted"""
        profile = Profile.objects.create(user=self.user, email='test@example.com')
        profile_id = profile.id
        
        self.user.delete()
        
        self.assertFalse(Profile.objects.filter(id=profile_id).exists())

    def test_profile_newsletter_opt_in(self):
        """Test newsletter opt-in field"""
        profile = Profile.objects.create(
            user=self.user,
            email='test@example.com',
            newsletter_opt_in=True
        )
        self.assertTrue(profile.newsletter_opt_in)

    def test_profile_preferred_sports(self):
        """Test preferred sports field"""
        profile = Profile.objects.create(
            user=self.user,
            email='test@example.com',
            preferred_sports='Running, Swimming, Cycling'
        )
        self.assertIn('Running', profile.preferred_sports)
        self.assertIn('Swimming', profile.preferred_sports)

    def test_profile_email_required(self):
        """Test that email is a required field"""
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user)

