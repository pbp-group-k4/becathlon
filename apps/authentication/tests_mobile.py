from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.main.models import Customer
from apps.profiles.models import Profile
import json

class MobileAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('auth:flutter_login')
        self.register_url = reverse('auth:flutter_register')
        self.logout_url = reverse('auth:flutter_logout')
        
        # Create a test user
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        Customer.objects.create(user=self.user)
        # Profile is created by signal, so get and update it
        profile = Profile.objects.get(user=self.user)
        profile.account_type = 'BUYER'
        profile.save()

    def test_flutter_login_success(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['status'])
        self.assertEqual(data['username'], self.username)
        self.assertEqual(data['message'], 'Login successful!')

    def test_flutter_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertFalse(data['status'])

    def test_flutter_login_disabled_account(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertFalse(data['status'])
        # authenticate() returns None for inactive users, so we get the generic error
        self.assertIn('Login failed', data['message'])

    def test_flutter_register_success(self):
        new_user_data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(
            self.register_url,
            json.dumps(new_user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertTrue(data['status'])
        self.assertEqual(data['username'], 'newuser')
        
        # Verify user created in DB
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Profile.objects.filter(user__username='newuser').exists())

    def test_flutter_register_password_mismatch(self):
        data = {
            'username': 'mismatch',
            'password': 'password123',
            'password2': 'different123'
        }
        response = self.client.post(
            self.register_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['status'])
        self.assertEqual(data['message'], 'Passwords do not match')

    def test_flutter_register_existing_username(self):
        data = {
            'username': self.username, # Existing user
            'password': 'password123',
            'password2': 'password123'
        }
        response = self.client.post(
            self.register_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['status'])
        self.assertEqual(data['message'], 'Username already exists')

    def test_flutter_logout(self):
        # Login first
        self.client.login(username=self.username, password=self.password)
        
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['status'])
        self.assertEqual(data['message'], 'Logout successful')
