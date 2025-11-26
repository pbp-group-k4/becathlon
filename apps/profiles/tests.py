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


class ProfileFormsTestCase(TestCase):
    """Test cases for profile forms"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_form_valid(self):
        """Test ProfileForm with valid data"""
        from .forms import ProfileForm
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferred_sports': 'Running, Swimming',
            'newsletter_opt_in': True
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())

    def test_profile_form_phone_validation_valid(self):
        """Test ProfileForm phone validation with valid phone numbers"""
        from .forms import ProfileForm
        valid_phones = ['+1234567890', '08123456789', '5551234567', '1234567890']
        for phone in valid_phones:
            form_data = {
                'first_name': 'John',
                'email': 'john@example.com',
                'phone': phone,
                'newsletter_opt_in': False
            }
            form = ProfileForm(data=form_data, instance=self.profile)
            self.assertTrue(form.is_valid(), f"Phone {phone} should be valid")

    def test_profile_form_phone_validation_invalid(self):
        """Test ProfileForm phone validation with invalid phone numbers"""
        from .forms import ProfileForm
        invalid_phones = ['abc', 'invalid-phone', 'phone@number']
        for phone in invalid_phones:
            form_data = {
                'first_name': 'John',
                'email': 'john@example.com',
                'phone': phone,
                'newsletter_opt_in': False
            }
            form = ProfileForm(data=form_data, instance=self.profile)
            self.assertFalse(form.is_valid(), f"Phone {phone} should be invalid")
            self.assertIn('phone', form.errors)

    def test_profile_form_newsletter_default(self):
        """Test ProfileForm newsletter_opt_in defaults to False when not provided"""
        from .forms import ProfileForm
        form_data = {
            'first_name': 'John',
            'email': 'john@example.com',
            'phone': '+1234567890'
            # newsletter_opt_in is missing
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
        # Django forms handle BooleanField defaults
        self.assertFalse(form.cleaned_data.get('newsletter_opt_in', False))

    def test_profile_form_field_widgets(self):
        """Test ProfileForm field widgets have correct attributes"""
        from .forms import ProfileForm
        form = ProfileForm(instance=self.profile)
        classes = 'form-control'

        # Check that form fields have the correct CSS classes
        self.assertIn(classes, form.fields['first_name'].widget.attrs.get('class', ''))
        self.assertIn(classes, form.fields['last_name'].widget.attrs.get('class', ''))
        self.assertIn(classes, form.fields['email'].widget.attrs.get('class', ''))
        self.assertIn(classes, form.fields['phone'].widget.attrs.get('class', ''))

        # Check placeholders
        self.assertEqual(form.fields['first_name'].widget.attrs.get('placeholder'), 'Enter your first name')
        self.assertEqual(form.fields['preferred_sports'].widget.attrs.get('placeholder'), 'e.g. football, running, cycling')


class ProfileViewsTestCase(TestCase):
    """Test cases for profile views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_profile_detail_view_requires_login(self):
        """Test profile detail view requires authentication"""
        response = self.client.get(reverse('profiles:detail'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login/', response['Location'])

    def test_profile_detail_view(self):
        """Test profile detail view displays correctly"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profiles:detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertTemplateUsed(response, 'profiles/profile_detail.html')

    def test_profile_edit_view_get(self):
        """Test profile edit view GET request"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profiles:edit'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
        self.assertTemplateUsed(response, 'profiles/profile_edit.html')

    def test_profile_edit_view_post_valid(self):
        """Test profile edit view POST with valid data"""
        self.client.login(username='testuser', password='testpass123')

        edit_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com',
            'phone': '+1234567890',
            'preferred_sports': 'Running, Swimming',
            'newsletter_opt_in': True
        }

        response = self.client.post(reverse('profiles:edit'), edit_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profiles:detail'))

        # Check profile was updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'John')
        self.assertEqual(self.profile.last_name, 'Doe')
        self.assertTrue(self.profile.newsletter_opt_in)

    def test_profile_edit_view_post_invalid(self):
        """Test profile edit view POST with invalid data"""
        self.client.login(username='testuser', password='testpass123')

        invalid_data = {
            'first_name': 'John',
            'email': 'invalid-email',  # Invalid email
            'phone': '+1234567890',
            'newsletter_opt_in': False
        }

        response = self.client.post(reverse('profiles:edit'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Stays on edit page
        self.assertContains(response, 'Enter a valid email address')

    def test_profile_edit_ajax_post_valid(self):
        """Test profile edit AJAX POST with valid data"""
        self.client.login(username='testuser', password='testpass123')

        edit_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone': '+0987654321',
            'preferred_sports': 'Cycling',
            'newsletter_opt_in': False
        }

        response = self.client.post(
            reverse('profiles:edit'),
            edit_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])

        # Check profile was updated
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'Jane')
        self.assertEqual(self.profile.last_name, 'Smith')

    def test_toggle_newsletter_ajax(self):
        """Test newsletter toggle AJAX endpoint"""
        self.client.login(username='testuser', password='testpass123')

        # Initially False
        self.assertFalse(self.profile.newsletter_opt_in)

        # Toggle to True
        response = self.client.post(
            reverse('profiles:toggle_newsletter_ajax'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['data']['newsletter_opt_in'])

        # Check database
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.newsletter_opt_in)

    def test_toggle_newsletter_ajax_requires_post(self):
        """Test newsletter toggle requires POST"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('profiles:toggle_newsletter_ajax'))
        self.assertEqual(response.status_code, 400)

    def test_toggle_newsletter_ajax_requires_ajax(self):
        """Test newsletter toggle requires AJAX header"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(reverse('profiles:toggle_newsletter_ajax'))
        self.assertEqual(response.status_code, 400)

    def test_switch_account_type_to_seller(self):
        """Test switching account type from BUYER to SELLER"""
        self.client.login(username='testuser', password='testpass123')

        # Ensure profile is BUYER
        self.profile.account_type = 'BUYER'
        self.profile.save()

        response = self.client.post(
            reverse('profiles:switch_account_type_ajax'),
            {'account_type': 'SELLER'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('Seller', data['message'])
        self.assertEqual(data['account_type'], 'SELLER')

        # Check database
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.account_type, 'SELLER')

    def test_switch_account_type_to_buyer_with_products(self):
        """Test switching from SELLER to BUYER deletes products"""
        self.client.login(username='testuser', password='testpass123')

        # Create a seller profile and products
        self.profile.account_type = 'SELLER'
        self.profile.save()

        product = Product.objects.create(
            name='Test Product',
            description='Test',
            price=Decimal('10.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )

        response = self.client.post(
            reverse('profiles:switch_account_type_ajax'),
            {'account_type': 'BUYER'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('removed', data['message'])
        self.assertEqual(data['account_type'], 'BUYER')

        # Check product was deleted
        self.assertFalse(Product.objects.filter(id=product.id).exists())

        # Check profile type
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.account_type, 'BUYER')

    def test_switch_account_type_invalid_type(self):
        """Test switching to invalid account type fails"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.post(
            reverse('profiles:switch_account_type_ajax'),
            {'account_type': 'INVALID'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('Invalid account type', data['error'])

    def test_switch_account_type_already_set(self):
        """Test switching to same account type fails"""
        self.client.login(username='testuser', password='testpass123')

        # Profile is already BUYER (default)
        response = self.client.post(
            reverse('profiles:switch_account_type_ajax'),
            {'account_type': 'BUYER'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('already set', data['error'])

