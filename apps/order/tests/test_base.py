"""
Base test case classes for Order app tests.
Provides common setup and fixture data to reduce code duplication.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from apps.main.models import Product, ProductType
from apps.cart.models import Cart, CartItem
from apps.order.models import Order, OrderItem, ShippingAddress, Payment, ProductRating


class BaseOrderTestCase(TestCase):
    """
    Base test case with common setup for order app tests.
    
    Creates standard test fixtures:
    - Test user
    - ProductType
    - Product with stock
    - Cart with CartItem
    - ShippingAddress
    - Order
    
    Inherit from this class to avoid duplicating setup code across test classes.
    """

    @classmethod
    def setUpTestData(cls):
        """Set up test data once for the entire test class"""
        # Create test user
        cls.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create product type
        cls.product_type = ProductType.objects.create(
            name='Running Shoes',
            description='High-performance running shoes'
        )

        # Create product
        cls.product = Product.objects.create(
            name='Test Running Shoe',
            description='A great running shoe for testing',
            price=Decimal('99.99'),
            product_type=cls.product_type,
            stock=10,
            created_by=cls.user
        )

    def setUp(self):
        """Set up test instances for each test method"""
        # Create fresh instances for each test
        self.client = Client()
        
        # Create fresh cart and cart item for each test
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

        # Create shipping address
        self.shipping_address = ShippingAddress.objects.create(
            user=self.user,
            full_name='John Doe',
            phone_number='+62123456789',
            address_line1='123 Main St',
            city='Jakarta',
            postal_code='12345',
            country='Indonesia'
        )

        # Create order
        self.order = Order.objects.create(user=self.user)

    def login(self):
        """Log in the test user"""
        self.client.login(username='testuser', password='testpass123')

    def get_authenticated_headers(self):
        """Get headers for authenticated AJAX requests"""
        return {
            'X-Requested-With': 'XMLHttpRequest',
        }
