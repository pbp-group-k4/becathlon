from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.main.models import Customer
from apps.profiles.models import Profile
from apps.cart.models import Cart, CartItem
from apps.main.models import Product, ProductType
from decimal import Decimal


class SignUpViewTestCase(TestCase):
    """Test cases for sign up view"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()

    def test_signup_page_loads(self):
        """Test signup page loads successfully"""
        response = self.client.get(reverse('auth:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/signup.html')

    def test_signup_creates_user_and_profiles(self):
        """Test that signup creates user, customer, and profile"""
        response = self.client.post(reverse('auth:signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'account_type': 'BUYER',
        })
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        
        # Check customer was created
        customer = Customer.objects.get(user=user)
        self.assertIsNotNone(customer)
        
        # Check profile was created
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.account_type, 'BUYER')
        self.assertEqual(profile.first_name, 'John')
        self.assertEqual(profile.last_name, 'Doe')

    def test_signup_with_invalid_data(self):
        """Test signup with invalid data shows errors"""
        response = self.client.post(reverse('auth:signup'), {
            'username': 'newuser',
            'email': 'invalid-email',
            'password1': 'pass',
            'password2': 'different',
        })
        
        # Should not redirect (stays on signup page)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/signup.html')


class LoginViewTestCase(TestCase):
    """Test cases for login view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_login_page_loads(self):
        """Test login page loads successfully"""
        response = self.client.get(reverse('auth:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.client.post(reverse('auth:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # User should be authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('auth:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authentication/login.html')

    def test_login_redirects_to_home(self):
        """Test that successful login redirects to home page"""
        response = self.client.post(reverse('auth:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        }, follow=True)
        
        # Should redirect to home
        self.assertRedirects(response, reverse('home'))
        
        # User should be authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'testuser')


class LogoutViewTestCase(TestCase):
    """Test cases for logout view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_logout(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Logout
        response = self.client.get(reverse('auth:logout'))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Follow redirect to check user is logged out
        response = self.client.get(reverse('home'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

