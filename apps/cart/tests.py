from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError
from decimal import Decimal
from apps.main.models import Product, ProductType
from apps.cart.models import Cart, CartItem
from apps.cart.utils import get_or_create_cart, transfer_guest_cart_to_user, validate_cart_item_stock


class CartModelTestCase(TestCase):
    """Test cases for Cart model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.product_type = ProductType.objects.create(
            name='Running Shoes',
            description='High-performance running shoes'
        )
        
        self.product = Product.objects.create(
            name='Test Running Shoe',
            description='A great running shoe for testing',
            price=Decimal('99.99'),
            product_type=self.product_type,
            stock=10,
            created_by=self.user
        )

    def test_cart_creation_for_user(self):
        """Test creating a cart for an authenticated user"""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.user, self.user)
        self.assertIsNone(cart.session_key)
        self.assertEqual(str(cart), f"Cart for {self.user.username}")

    def test_cart_creation_for_guest(self):
        """Test creating a cart for a guest session"""
        cart = Cart.objects.create(session_key='test_session_123')
        self.assertIsNone(cart.user)
        self.assertEqual(cart.session_key, 'test_session_123')
        self.assertEqual(str(cart), "Guest cart test_session_123")

    def test_unique_user_cart_constraint(self):
        """Test that only one cart per user is enforced"""
        Cart.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            Cart.objects.create(user=self.user)

    def test_unique_session_cart_constraint(self):
        """Test that only one cart per session is enforced"""
        Cart.objects.create(session_key='test_session_123')
        with self.assertRaises(IntegrityError):
            Cart.objects.create(session_key='test_session_123')

    def test_get_total_items_empty_cart(self):
        """Test get_total_items returns 0 for empty cart"""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.get_total_items(), 0)

    def test_get_total_items_with_items(self):
        """Test get_total_items returns sum of quantities"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)
        product2 = Product.objects.create(
            name='Product 2',
            description='Test',
            price=Decimal('50.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )
        CartItem.objects.create(cart=cart, product=product2, quantity=2)
        self.assertEqual(cart.get_total_items(), 5)

    def test_get_subtotal_empty_cart(self):
        """Test get_subtotal returns 0 for empty cart"""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.get_subtotal(), 0)

    def test_get_subtotal_with_items(self):
        """Test get_subtotal calculates correctly"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        # 2 * 99.99 = 199.98
        self.assertEqual(cart.get_subtotal(), Decimal('199.98'))

    def test_get_item_count(self):
        """Test get_item_count returns number of distinct items"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)
        product2 = Product.objects.create(
            name='Product 2',
            description='Test',
            price=Decimal('50.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )
        CartItem.objects.create(cart=cart, product=product2, quantity=2)
        self.assertEqual(cart.get_item_count(), 2)

    def test_merge_carts_with_different_products(self):
        """Test merging two carts with different products"""
        cart1 = Cart.objects.create(user=self.user)
        cart2 = Cart.objects.create(session_key='test_session')
        
        product2 = Product.objects.create(
            name='Product 2',
            description='Test',
            price=Decimal('50.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )
        
        CartItem.objects.create(cart=cart1, product=self.product, quantity=2)
        CartItem.objects.create(cart=cart2, product=product2, quantity=3)
        
        cart1.merge_carts(cart2)
        
        self.assertEqual(cart1.get_item_count(), 2)
        self.assertEqual(cart1.get_total_items(), 5)
        self.assertFalse(Cart.objects.filter(id=cart2.id).exists())

    def test_merge_carts_with_same_products(self):
        """Test merging two carts with overlapping products"""
        cart1 = Cart.objects.create(user=self.user)
        cart2 = Cart.objects.create(session_key='test_session')
        
        CartItem.objects.create(cart=cart1, product=self.product, quantity=2)
        CartItem.objects.create(cart=cart2, product=self.product, quantity=3)
        
        cart1.merge_carts(cart2)
        
        self.assertEqual(cart1.get_item_count(), 1)
        self.assertEqual(cart1.get_total_items(), 5)
        self.assertFalse(Cart.objects.filter(id=cart2.id).exists())

    def test_clear_cart(self):
        """Test clearing all items from cart"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)
        
        self.assertEqual(cart.get_item_count(), 1)
        cart.clear()
        self.assertEqual(cart.get_item_count(), 0)
        self.assertEqual(cart.get_total_items(), 0)


class CartItemModelTestCase(TestCase):
    """Test cases for CartItem model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.product_type = ProductType.objects.create(
            name='Running Shoes',
            description='High-performance running shoes'
        )
        
        self.product = Product.objects.create(
            name='Test Running Shoe',
            description='A great running shoe for testing',
            price=Decimal('99.99'),
            product_type=self.product_type,
            stock=10,
            created_by=self.user
        )
        
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_item_creation(self):
        """Test creating a cart item"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.product, self.product)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(str(cart_item), f"2 x {self.product.name}")

    def test_unique_cart_product_constraint(self):
        """Test that same product can't be added twice to same cart"""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        with self.assertRaises(IntegrityError):
            CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)

    def test_get_subtotal(self):
        """Test get_subtotal calculates correctly"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )
        self.assertEqual(cart_item.get_subtotal(), Decimal('299.97'))

    def test_get_item_total(self):
        """Test get_item_total alias for get_subtotal"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(cart_item.get_item_total(), cart_item.get_subtotal())

    def test_update_quantity(self):
        """Test updating cart item quantity"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        cart_item.quantity = 5
        cart_item.save()
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_delete_cart_item(self):
        """Test deleting a cart item"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        item_id = cart_item.id
        cart_item.delete()
        self.assertFalse(CartItem.objects.filter(id=item_id).exists())


class CartUtilsTestCase(TestCase):
    """Test cases for cart utility functions"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.product_type = ProductType.objects.create(
            name='Running Shoes',
            description='High-performance running shoes'
        )
        
        self.product = Product.objects.create(
            name='Test Running Shoe',
            description='A great running shoe for testing',
            price=Decimal('99.99'),
            product_type=self.product_type,
            stock=10,
            created_by=self.user
        )

    def test_get_or_create_cart_for_authenticated_user(self):
        """Test get_or_create_cart for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('cart:cart_view'))
        cart = get_or_create_cart(response.wsgi_request)
        
        self.assertIsNotNone(cart)
        self.assertEqual(cart.user, self.user)
        self.assertIsNone(cart.session_key)

    def test_get_or_create_cart_for_guest(self):
        """Test get_or_create_cart for guest user"""
        response = self.client.get(reverse('cart:cart_view'))
        cart = get_or_create_cart(response.wsgi_request)
        
        self.assertIsNotNone(cart)
        self.assertIsNone(cart.user)
        self.assertIsNotNone(cart.session_key)

    def test_get_or_create_cart_creates_session_if_needed(self):
        """Test that get_or_create_cart creates session if it doesn't exist"""
        # Create a request without a session
        from django.test import RequestFactory
        from django.contrib.sessions.middleware import SessionMiddleware
        
        factory = RequestFactory()
        request = factory.get('/')
        
        # Add session middleware
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()
        
        # Clear session key to simulate no session
        request.session.flush()
        
        cart = get_or_create_cart(request)
        self.assertIsNotNone(cart)
        self.assertIsNotNone(cart.session_key)

    def test_transfer_guest_cart_to_user(self):
        """Test transferring guest cart to authenticated user"""
        # Create guest cart
        session = self.client.session
        session.save()
        guest_cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=guest_cart, product=self.product, quantity=2)
        
        # Login user
        self.client.login(username='testuser', password='testpass123')
        
        # Simulate login view calling transfer
        from django.test import RequestFactory
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.contrib.auth.middleware import AuthenticationMiddleware
        
        factory = RequestFactory()
        request = factory.get('/')
        request.session = session
        request.user = self.user
        
        transfer_guest_cart_to_user(request)
        
        # Check that user cart now has the item
        user_cart = Cart.objects.get(user=self.user)
        self.assertEqual(user_cart.get_total_items(), 2)
        
        # Guest cart should be deleted
        self.assertFalse(Cart.objects.filter(session_key=session.session_key).exists())

    def test_transfer_guest_cart_merges_with_existing_user_cart(self):
        """Test that transfer merges guest cart with existing user cart"""
        # Create user cart with one item
        user_cart = Cart.objects.create(user=self.user)
        product2 = Product.objects.create(
            name='Product 2',
            description='Test',
            price=Decimal('50.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )
        CartItem.objects.create(cart=user_cart, product=product2, quantity=1)
        
        # Create guest cart with different item
        session = self.client.session
        session.save()
        guest_cart = Cart.objects.create(session_key=session.session_key)
        CartItem.objects.create(cart=guest_cart, product=self.product, quantity=2)
        
        # Simulate transfer
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.session = session
        request.user = self.user
        
        transfer_guest_cart_to_user(request)
        
        # Check that user cart has both items
        user_cart.refresh_from_db()
        self.assertEqual(user_cart.get_item_count(), 2)
        self.assertEqual(user_cart.get_total_items(), 3)

    def test_validate_cart_item_stock_sufficient(self):
        """Test stock validation when stock is sufficient"""
        is_valid, error_msg = validate_cart_item_stock(self.product, 5)
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)

    def test_validate_cart_item_stock_insufficient(self):
        """Test stock validation when stock is insufficient"""
        is_valid, error_msg = validate_cart_item_stock(self.product, 15)
        self.assertFalse(is_valid)
        self.assertIn("Only 10 items available", error_msg)

    def test_validate_cart_item_stock_exact_amount(self):
        """Test stock validation when requesting exact stock amount"""
        is_valid, error_msg = validate_cart_item_stock(self.product, 10)
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)


class CartViewsTestCase(TestCase):
    """Test cases for cart views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.product_type = ProductType.objects.create(
            name='Running Shoes',
            description='High-performance running shoes'
        )
        
        self.product = Product.objects.create(
            name='Test Running Shoe',
            description='A great running shoe for testing',
            price=Decimal('99.99'),
            product_type=self.product_type,
            stock=10,
            created_by=self.user
        )

    def test_cart_view_authenticated(self):
        """Test cart view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('cart:cart_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart.html')

    def test_cart_view_guest(self):
        """Test cart view for guest user"""
        response = self.client.get(reverse('cart:cart_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart.html')

    def test_add_to_cart_authenticated(self):
        """Test adding product to cart as authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.get_total_items(), 2)
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_add_to_cart_guest(self):
        """Test adding product to cart as guest"""
        response = self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 1}
        )
        
        # Get the session key from the response
        session_key = self.client.session.session_key
        cart = Cart.objects.get(session_key=session_key)
        self.assertEqual(cart.get_total_items(), 1)

    def test_add_to_cart_ajax(self):
        """Test adding product via AJAX"""
        response = self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 2)

    def test_add_to_cart_insufficient_stock(self):
        """Test adding more items than available stock"""
        response = self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 15}
        )
        
        # Should redirect back to product page with error
        self.assertEqual(response.status_code, 302)

    def test_add_to_cart_insufficient_stock_ajax(self):
        """Test adding insufficient stock via AJAX"""
        response = self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 15},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_add_to_cart_increments_existing_item(self):
        """Test that adding same product increments quantity"""
        self.client.login(username='testuser', password='testpass123')
        
        # Add product first time
        self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 2}
        )
        
        # Add same product again
        self.client.post(
            reverse('cart:add_to_cart', kwargs={'product_id': self.product.id}),
            {'quantity': 3}
        )
        
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.get_total_items(), 5)
        self.assertEqual(cart.get_item_count(), 1)  # Still one distinct item

    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        self.client.login(username='testuser', password='testpass123')
        
        # Add item to cart
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        # Update quantity
        response = self.client.post(
            reverse('cart:update_cart_item', kwargs={'item_id': cart_item.id}),
            {'quantity': 5}
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_update_cart_item_to_zero_removes_item(self):
        """Test that updating quantity to 0 removes item"""
        self.client.login(username='testuser', password='testpass123')
        
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        item_id = cart_item.id
        
        # Update to 0
        response = self.client.post(
            reverse('cart:update_cart_item', kwargs={'item_id': item_id}),
            {'quantity': 0}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CartItem.objects.filter(id=item_id).exists())

    def test_remove_from_cart(self):
        """Test removing item from cart"""
        self.client.login(username='testuser', password='testpass123')
        
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        item_id = cart_item.id
        
        response = self.client.post(
            reverse('cart:remove_from_cart', kwargs={'item_id': item_id})
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(CartItem.objects.filter(id=item_id).exists())

    def test_clear_cart(self):
        """Test clearing entire cart"""
        self.client.login(username='testuser', password='testpass123')
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        response = self.client.post(reverse('cart:clear_cart'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        cart.refresh_from_db()
        self.assertEqual(cart.get_item_count(), 0)

    def test_api_cart_summary(self):
        """Test cart summary API endpoint"""
        self.client.login(username='testuser', password='testpass123')
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        response = self.client.get(reverse('cart:api_cart_summary'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['total_items'], 2)
        self.assertEqual(data['item_count'], 1)
        self.assertIn('subtotal', data)
        self.assertIn('items', data)
        self.assertEqual(len(data['items']), 1)

    def test_api_cart_count(self):
        """Test cart count API endpoint"""
        self.client.login(username='testuser', password='testpass123')
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)
        
        response = self.client.get(reverse('cart:api_cart_count'))
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 3)
