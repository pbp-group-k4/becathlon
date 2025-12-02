from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import F
from urllib.parse import urlencode
from decimal import Decimal
from datetime import timedelta
from apps.main.models import Product, ProductType
from apps.cart.models import Cart, CartItem
from apps.order.models import Order, OrderItem, ShippingAddress, Payment, ProductRating
from apps.order.views import CheckoutResult, process_checkout_service


class ShippingAddressModelTestCase(TestCase):
    """Test cases for ShippingAddress model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_shipping_address_creation(self):
        """Test creating a shipping address"""
        address = ShippingAddress.objects.create(
            user=self.user,
            full_name='John Doe',
            phone_number='+62123456789',
            address_line1='123 Main St',
            city='Jakarta',
            postal_code='12345',
            country='Indonesia'
        )
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.full_name, 'John Doe')
        self.assertIn('John Doe', str(address))
        self.assertIn('Jakarta', str(address))

    def test_shipping_address_optional_fields(self):
        """Test shipping address with optional fields"""
        address = ShippingAddress.objects.create(
            full_name='Jane Doe',
            phone_number='+62987654321',
            address_line1='456 Second St',
            address_line2='Apt 789',
            city='Bandung',
            state='West Java',
            postal_code='54321',
            country='Indonesia'
        )
        self.assertIsNone(address.user)
        self.assertEqual(address.address_line2, 'Apt 789')
        self.assertEqual(address.state, 'West Java')


class OrderModelTestCase(TestCase):
    """Test cases for Order model"""

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
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)
        
        self.shipping_address = ShippingAddress.objects.create(
            user=self.user,
            full_name='John Doe',
            phone_number='+62123456789',
            address_line1='123 Main St',
            city='Jakarta',
            postal_code='12345'
        )

    def test_order_creation(self):
        """Test creating an order"""
        order = Order.objects.create(
            user=self.user,
            shipping_address=self.shipping_address
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.delivery_status, Order.DeliveryStatus.PROCESSING)
        self.assertIsNone(order.delivery_started_at)

    def test_order_str_representation(self):
        """Test order string representation"""
        order = Order.objects.create(user=self.user)
        self.assertIn(f"Order #{order.id}", str(order))
        self.assertIn("PENDING", str(order))

    def test_get_total_items(self):
        """Test get_total_items returns sum of quantities"""
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, product=self.product, quantity=3, price=self.product.price)
        product2 = Product.objects.create(
            name='Product 2',
            description='Test',
            price=Decimal('50.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )
        OrderItem.objects.create(order=order, product=product2, quantity=2, price=product2.price)
        self.assertEqual(order.get_total_items(), 5)

    def test_get_item_count(self):
        """Test get_item_count returns number of distinct items"""
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, product=self.product, quantity=3, price=self.product.price)
        product2 = Product.objects.create(
            name='Product 2',
            description='Test',
            price=Decimal('50.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )
        OrderItem.objects.create(order=order, product=product2, quantity=2, price=product2.price)
        self.assertEqual(order.get_item_count(), 2)

    def test_calculate_total(self):
        """Test calculate_total updates total_price"""
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, product=self.product, quantity=2, price=Decimal('99.99'))
        OrderItem.objects.create(
            order=order,
            product=Product.objects.create(
                name='Product 2',
                description='Test',
                price=Decimal('50.00'),
                product_type=self.product_type,
                stock=5,
                created_by=self.user
            ),
            quantity=1,
            price=Decimal('50.00')
        )
        
        total = order.calculate_total()
        # 2 * 99.99 + 1 * 50.00 = 249.98
        self.assertEqual(total, Decimal('249.98'))
        order.refresh_from_db()
        self.assertEqual(order.total_price, Decimal('249.98'))

    def test_start_delivery_tracking(self):
        """Test starting delivery tracking"""
        order = Order.objects.create(user=self.user)
        self.assertIsNone(order.delivery_started_at)
        
        order.start_delivery_tracking()
        order.refresh_from_db()
        
        self.assertIsNotNone(order.delivery_started_at)
        self.assertEqual(order.delivery_status, Order.DeliveryStatus.PROCESSING)

    def test_get_current_delivery_status_processing(self):
        """Test delivery status during PROCESSING phase"""
        order = Order.objects.create(user=self.user)
        order.delivery_started_at = timezone.now()
        order.save()
        
        status, remaining = order.get_current_delivery_status()
        self.assertEqual(status, Order.DeliveryStatus.PROCESSING)
        self.assertGreater(remaining, 0)
        self.assertLessEqual(remaining, order.PROCESSING_DURATION)

    def test_get_current_delivery_status_en_route(self):
        """Test delivery status during EN_ROUTE phase"""
        order = Order.objects.create(user=self.user)
        # Set delivery started to PROCESSING_DURATION + 10 seconds ago
        order.delivery_started_at = timezone.now() - timedelta(seconds=order.PROCESSING_DURATION + 10)
        order.save()
        
        status, remaining = order.get_current_delivery_status()
        self.assertEqual(status, Order.DeliveryStatus.EN_ROUTE)
        self.assertGreater(remaining, 0)

    def test_get_current_delivery_status_delivered(self):
        """Test delivery status after complete delivery"""
        order = Order.objects.create(user=self.user)
        # Set delivery started to total duration ago
        total_duration = order.PROCESSING_DURATION + order.EN_ROUTE_DURATION
        order.delivery_started_at = timezone.now() - timedelta(seconds=total_duration + 10)
        order.save()
        
        status, remaining = order.get_current_delivery_status()
        self.assertEqual(status, Order.DeliveryStatus.DELIVERED)
        self.assertEqual(remaining, 0)

    def test_update_delivery_status(self):
        """Test updating delivery status"""
        order = Order.objects.create(user=self.user)
        order.delivery_started_at = timezone.now() - timedelta(seconds=order.PROCESSING_DURATION + 10)
        order.save()
        
        changed = order.update_delivery_status()
        self.assertTrue(changed)
        order.refresh_from_db()
        self.assertEqual(order.delivery_status, Order.DeliveryStatus.EN_ROUTE)

    def test_get_delivery_progress_percentage(self):
        """Test delivery progress percentage calculation"""
        order = Order.objects.create(user=self.user)
        
        # No tracking started
        self.assertEqual(order.get_delivery_progress_percentage(), 0)
        
        # Start tracking
        order.delivery_started_at = timezone.now()
        order.save()
        progress = order.get_delivery_progress_percentage()
        self.assertGreaterEqual(progress, 0)
        self.assertLessEqual(progress, 100)
        
        # Delivered
        order.delivery_status = Order.DeliveryStatus.DELIVERED
        order.save()
        self.assertEqual(order.get_delivery_progress_percentage(), 100)

    def test_create_from_cart(self):
        """Test creating order from cart"""
        initial_stock = self.product.stock
        order = Order.create_from_cart(self.cart, self.shipping_address)
        
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.shipping_address, self.shipping_address)
        self.assertEqual(order.get_item_count(), 1)
        self.assertEqual(order.get_total_items(), 2)
        
        # Check stock was decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 2)
        
        # Check cart was cleared
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.get_item_count(), 0)

    def test_create_from_cart_insufficient_stock(self):
        """Test creating order with insufficient stock raises error"""
        # Set cart quantity higher than stock
        cart_item = self.cart.items.first()
        cart_item.quantity = 20  # More than available stock
        cart_item.save()
        
        with self.assertRaises(ValueError) as context:
            Order.create_from_cart(self.cart, self.shipping_address)
        
        self.assertIn("Insufficient stock", str(context.exception))

    def test_create_from_cart_snapshots_price(self):
        """Test that order creation snapshots current product price"""
        original_price = self.product.price
        order = Order.create_from_cart(self.cart, self.shipping_address)
        
        # Change product price
        self.product.price = Decimal('150.00')
        self.product.save()
        
        # Order item should still have original price
        order_item = order.items.first()
        self.assertEqual(order_item.price, original_price)


class OrderItemModelTestCase(TestCase):
    """Test cases for OrderItem model"""

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
        
        self.order = Order.objects.create(user=self.user)

    def test_order_item_creation(self):
        """Test creating an order item"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('99.99')
        )
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, Decimal('99.99'))
        self.assertEqual(str(order_item), f"2 × {self.product.name}")

    def test_order_item_subtotal_calculation(self):
        """Test that subtotal is calculated on save"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price=Decimal('99.99')
        )
        self.assertEqual(order_item.subtotal, Decimal('299.97'))

    def test_unique_order_product_constraint(self):
        """Test that same product can't be added twice to same order"""
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('99.99')
        )
        with self.assertRaises(IntegrityError):
            OrderItem.objects.create(
                order=self.order,
                product=self.product,
                quantity=1,
                price=Decimal('99.99')
            )

    def test_get_subtotal(self):
        """Test get_subtotal method"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=4,
            price=Decimal('50.00')
        )
        self.assertEqual(order_item.get_subtotal(), Decimal('200.00'))

    def test_get_item_total(self):
        """Test get_item_total alias"""
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=Decimal('99.99')
        )
        self.assertEqual(order_item.get_item_total(), order_item.get_subtotal())


class PaymentModelTestCase(TestCase):
    """Test cases for Payment model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.order = Order.objects.create(
            user=self.user,
            total_price=Decimal('199.98')
        )

    def test_payment_creation(self):
        """Test creating a payment"""
        payment = Payment.objects.create(
            order=self.order,
            method=Payment.Method.CREDIT_CARD,
            amount=Decimal('199.98')
        )
        self.assertEqual(payment.order, self.order)
        self.assertEqual(payment.method, Payment.Method.CREDIT_CARD)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.amount, Decimal('199.98'))
        self.assertIn(f"Order #{self.order.id}", str(payment))

    def test_payment_status_transitions(self):
        """Test payment status changes"""
        payment = Payment.objects.create(
            order=self.order,
            method=Payment.Method.E_WALLET,
            amount=Decimal('199.98')
        )
        
        # Mark as success
        payment.status = Payment.Status.SUCCESS
        payment.paid_at = timezone.now()
        payment.save()
        
        self.assertEqual(payment.status, Payment.Status.SUCCESS)
        self.assertIsNotNone(payment.paid_at)

    def test_payment_method_choices(self):
        """Test all payment method choices"""
        for method, _ in Payment.Method.choices:
            payment = Payment.objects.create(
                order=Order.objects.create(user=self.user),
                method=method,
                amount=Decimal('100.00')
            )
            self.assertEqual(payment.method, method)


class ProductRatingModelTestCase(TestCase):
    """Test cases for ProductRating model"""

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
        
        self.order = Order.objects.create(user=self.user)
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )

    def test_product_rating_creation(self):
        """Test creating a product rating"""
        rating = ProductRating.objects.create(
            user=self.user,
            product=self.product,
            order=self.order,
            rating=5,
            review='Excellent product!'
        )
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.product, self.product)
        self.assertEqual(rating.order, self.order)
        self.assertEqual(rating.rating, 5)
        self.assertIn(self.user.username, str(rating))
        self.assertIn('5★', str(rating))

    def test_unique_user_product_order_constraint(self):
        """Test that user can only rate product once per order"""
        ProductRating.objects.create(
            user=self.user,
            product=self.product,
            order=self.order,
            rating=4
        )
        with self.assertRaises(IntegrityError):
            ProductRating.objects.create(
                user=self.user,
                product=self.product,
                order=self.order,
                rating=5
            )

    def test_rating_choices_validation(self):
        """Test rating value choices (1-5)"""
        for rating_value in range(1, 6):
            rating = ProductRating.objects.create(
                user=self.user,
                product=self.product,
                order=Order.objects.create(user=self.user),
                rating=rating_value
            )
            self.assertEqual(rating.rating, rating_value)

    def test_product_aggregate_rating_update(self):
        """Test that product rating is updated when rating is saved"""
        # Create multiple users and ratings
        user2 = User.objects.create_user(username='user2', password='test')
        order2 = Order.objects.create(user=user2)
        
        ProductRating.objects.create(
            user=self.user,
            product=self.product,
            order=self.order,
            rating=5
        )
        
        ProductRating.objects.create(
            user=user2,
            product=self.product,
            order=order2,
            rating=3
        )
        
        # Check aggregate rating
        self.product.refresh_from_db()
        # Average of 5 and 3 is 4.0
        self.assertEqual(self.product.rating, Decimal('4.00'))

    def test_optional_review_text(self):
        """Test rating without review text"""
        rating = ProductRating.objects.create(
            user=self.user,
            product=self.product,
            order=self.order,
            rating=4
        )
        self.assertEqual(rating.review, '')


class OrderViewsTestCase(TestCase):
    """Test cases for order views"""

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

        self.shipping_address = ShippingAddress.objects.create(
            user=self.user,
            full_name='John Doe',
            phone_number='+62123456789',
            address_line1='123 Main St',
            city='Jakarta',
            postal_code='12345',
            country='Indonesia'
        )

        # Create a completed order for testing
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.order = Order.create_from_cart(cart, self.shipping_address)
        self.order.status = Order.Status.PAID
        self.order.start_delivery_tracking()
        self.order.save()

        Payment.objects.create(
            order=self.order,
            method=Payment.Method.CREDIT_CARD,
            amount=self.order.total_price,
            status=Payment.Status.SUCCESS
        )

    def test_checkout_view_requires_authentication(self):
        """Test that checkout view redirects unauthenticated users to login"""
        response = self.client.get(reverse('order:checkout'))
        login_url = f"{reverse('auth:login')}?{urlencode({'next': reverse('order:checkout')})}"
        self.assertRedirects(response, login_url)

    def test_checkout_view_empty_cart_redirects(self):
        """Test that checkout view redirects when cart is empty"""
        self.client.login(username='testuser', password='testpass123')

        # Create an empty cart (no items)
        Cart.objects.filter(user=self.user).delete()  # Remove existing cart
        empty_cart = Cart.objects.create(user=self.user)  # Create empty cart

        response = self.client.get(reverse('order:checkout'))
        self.assertRedirects(response, reverse('catalog:home'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertIn('empty', messages[0].message.lower())

    def test_checkout_view_get_renders_form(self):
        """Test checkout form renders correctly for authenticated user with items"""
        self.client.login(username='testuser', password='testpass123')

        # Remove the cart created in setUp and create a fresh one with items
        Cart.objects.filter(user=self.user).delete()
        test_cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=test_cart, product=self.product, quantity=1)

        response = self.client.get(reverse('order:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'checkout')
        self.assertContains(response, self.product.name)

    def test_checkout_success_view(self):
        """Test checkout success page displays correctly"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('order:checkout_success', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"#{self.order.id}")
        self.assertContains(response, 'Order Confirmed')

    def test_checkout_success_view_wrong_user_404(self):
        """Test checkout success view returns 404 for wrong user"""
        other_user = User.objects.create_user(username='other', password='test')
        self.client.login(username='other', password='test')

        response = self.client.get(reverse('order:checkout_success', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 404)

    def test_order_list_view(self):
        """Test order list view displays user's orders"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('order:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{self.order.id}")
        self.assertContains(response, 'Paid')

    def test_order_detail_view(self):
        """Test order detail view displays order information"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('order:order_detail', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.shipping_address.full_name)
        self.assertContains(response, self.product.name)

    def test_order_detail_view_wrong_user_404(self):
        """Test order detail view returns 404 for wrong user"""
        other_user = User.objects.create_user(username='other', password='test')
        self.client.login(username='other', password='test')

        response = self.client.get(reverse('order:order_detail', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 404)

    def test_process_checkout_valid_data(self):
        """Test successful checkout processing with valid data"""
        self.client.login(username='testuser', password='testpass123')

        # Create a fresh cart for this test
        Cart.objects.filter(user=self.user).delete()
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        # Valid checkout data
        checkout_data = {
            'full_name': 'Jane Doe',
            'phone_number': '+62987654321',
            'address_line1': '456 Second St',
            'city': 'Bandung',
            'postal_code': '54321',
            'country': 'Indonesia',
            'payment_method': 'CREDIT_CARD'
        }

        response = self.client.post(reverse('order:checkout'), checkout_data)
        self.assertEqual(response.status_code, 302)  # Redirect to success page

        # Check that order was created
        orders = Order.objects.filter(user=self.user)
        self.assertEqual(orders.count(), 2)  # Original + new order

        new_order = orders.latest('created_at')
        self.assertEqual(new_order.status, Order.Status.PAID)
        self.assertIsNotNone(new_order.payment)

    def test_process_checkout_invalid_address_validation(self):
        """Test checkout fails with invalid address data"""
        self.client.login(username='testuser', password='testpass123')

        # Create a fresh cart
        Cart.objects.filter(user=self.user).delete()
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        # Invalid address data (missing required fields)
        invalid_data = {
            'phone_number': '+62123456789',
            'city': 'Jakarta',
            'payment_method': 'CREDIT_CARD'
        }

        response = self.client.post(reverse('order:checkout'), invalid_data)
        self.assertEqual(response.status_code, 302)  # Redirect back to checkout
        self.assertRedirects(response, reverse('order:checkout'))

        # Check that no new order was created
        order_count_before = Order.objects.filter(user=self.user).count()
        # Should still be 1 (the one created in setUp)
        self.assertEqual(order_count_before, 1)

    def test_process_checkout_invalid_payment_method(self):
        """Test checkout fails with invalid payment method"""
        self.client.login(username='testuser', password='testpass123')

        # Create a fresh cart
        Cart.objects.filter(user=self.user).delete()
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        # Valid address but invalid payment method
        invalid_data = {
            'full_name': 'John Doe',
            'phone_number': '+62123456789',
            'address_line1': '123 Main St',
            'city': 'Jakarta',
            'postal_code': '12345',
            'country': 'Indonesia',
            'payment_method': 'INVALID_METHOD'
        }

        response = self.client.post(reverse('order:checkout'), invalid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order:checkout'))

    def test_process_checkout_insufficient_stock(self):
        """Test checkout fails when stock is insufficient"""
        self.client.login(username='testuser', password='testpass123')

        # Create a fresh cart with more items than available stock
        Cart.objects.filter(user=self.user).delete()
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=20)  # More than stock

        valid_data = {
            'full_name': 'John Doe',
            'phone_number': '+62123456789',
            'address_line1': '123 Main St',
            'city': 'Jakarta',
            'postal_code': '12345',
            'country': 'Indonesia',
            'payment_method': 'CREDIT_CARD'
        }

        response = self.client.post(reverse('order:checkout'), valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order:checkout'))

    def test_check_delivery_status_processing(self):
        """Test delivery status API during processing phase"""
        self.client.login(username='testuser', password='testpass123')

        response = self.client.get(reverse('order:check_delivery_status', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['delivery_status'], 'PROCESSING')
        self.assertGreater(data['seconds_remaining'], 0)

    def test_check_delivery_status_delivered(self):
        """Test delivery status API when order is delivered"""
        self.client.login(username='testuser', password='testpass123')

        # Advance order to delivered state
        self.order.delivery_started_at = timezone.now() - timedelta(seconds=150)  # Past delivery time
        self.order.save()

        response = self.client.get(reverse('order:check_delivery_status', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['delivery_status'], 'DELIVERED')
        self.assertEqual(data['seconds_remaining'], 0)
        self.assertTrue(data['is_delivered'])

    def test_submit_rating_valid(self):
        """Test submitting a valid product rating"""
        self.client.login(username='testuser', password='testpass123')

        # Mark order as delivered by advancing delivery tracking past completion
        self.order.delivery_started_at = timezone.now() - timedelta(seconds=150)  # Past delivery time
        self.order.update_delivery_status()  # This should set status to DELIVERED
        self.order.save()

        rating_data = {
            'product_id': self.product.id,
            'rating': 5,
            'review': 'Excellent product!'
        }

        response = self.client.post(
            reverse('order:submit_rating', kwargs={'order_id': self.order.id}),
            rating_data
        )
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Rating submitted successfully!')

        # Check rating was created
        rating = ProductRating.objects.get(user=self.user, product=self.product, order=self.order)
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.review, 'Excellent product!')

    def test_submit_rating_not_delivered_fails(self):
        """Test rating submission fails for undelivered orders"""
        self.client.login(username='testuser', password='testpass123')

        rating_data = {
            'product_id': self.product.id,
            'rating': 4,
            'review': 'Good product'
        }

        response = self.client.post(
            reverse('order:submit_rating', kwargs={'order_id': self.order.id}),
            rating_data
        )
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('after delivery', data['error'])

    def test_submit_rating_invalid_rating_value(self):
        """Test rating submission fails with invalid rating value"""
        self.client.login(username='testuser', password='testpass123')

        # Mark order as delivered
        self.order.delivery_started_at = timezone.now() - timedelta(seconds=150)
        self.order.update_delivery_status()
        self.order.save()

        rating_data = {
            'product_id': self.product.id,
            'rating': 6,  # Invalid rating (should be 1-5)
            'review': 'Good product'
        }

        response = self.client.post(
            reverse('order:submit_rating', kwargs={'order_id': self.order.id}),
            rating_data
        )
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('between 1 and 5', data['error'])

    def test_submit_rating_wrong_product(self):
        """Test rating submission fails for product not in order"""
        self.client.login(username='testuser', password='testpass123')

        # Mark order as delivered
        self.order.delivery_started_at = timezone.now() - timedelta(seconds=150)
        self.order.update_delivery_status()
        self.order.save()

        # Create another product not in this order
        other_product = Product.objects.create(
            name='Other Product',
            description='Test',
            price=Decimal('50.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )

        rating_data = {
            'product_id': other_product.id,
            'rating': 4,
            'review': 'Good product'
        }

        response = self.client.post(
            reverse('order:submit_rating', kwargs={'order_id': self.order.id}),
            rating_data
        )
        self.assertEqual(response.status_code, 400)

        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('not in this order', data['error'])

    def test_flutter_order_detail_includes_image_url_with_primary_image(self):
        """Test that flutter_order_detail returns image_url from ProductImage primary"""
        from apps.catalog.models import ProductImage

        # Ensure user is logged in
        self.client.login(username='testuser', password='testpass123')

        # Add a primary ProductImage to product
        ProductImage.objects.create(
            product=self.product,
            image_url='https://example.com/img.jpg',
            is_primary=True,
            display_order=0
        )

        response = self.client.get(reverse('order:flutter_order_detail', kwargs={'order_id': self.order.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['status'])
        items = data['order']['items']
        self.assertTrue(len(items) > 0)
        self.assertEqual(items[0]['image_url'], 'https://example.com/img.jpg')

    def test_flutter_order_detail_falls_back_to_product_image_url(self):
        """Test that flutter_order_detail uses Product.image_url when no ProductImage primary exists"""
        # Ensure user is logged in
        self.client.login(username='testuser', password='testpass123')

        # Create product with image_url and a new order
        product2 = Product.objects.create(
            name='Fallback Product',
            description='Fallback image URL',
            price=Decimal('20.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user,
            image_url='https://example.com/fallback.jpg'
        )

        # Get or create cart and add item
        cart, _ = Cart.objects.get_or_create(user=self.user)
        cart.items.all().delete()  # Clear existing items
        CartItem.objects.create(cart=cart, product=product2, quantity=1)
        order2 = Order.create_from_cart(cart, self.shipping_address)
        order2.status = Order.Status.PAID
        order2.start_delivery_tracking()
        order2.save()

        response = self.client.get(reverse('order:flutter_order_detail', kwargs={'order_id': order2.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['status'])
        items = data['order']['items']
        self.assertTrue(len(items) > 0)
        self.assertEqual(items[0]['image_url'], 'https://example.com/fallback.jpg')


class CheckoutResultTestCase(TestCase):
    """Test cases for CheckoutResult class"""

    def test_checkout_result_success(self):
        """Test CheckoutResult with success=True"""
        result = CheckoutResult(success=True, order="mock_order")
        self.assertTrue(result.success)
        self.assertEqual(result.order, "mock_order")
        self.assertIsNone(result.error_type)
        self.assertIsNone(result.error_message)
        self.assertEqual(result.errors, {})

    def test_checkout_result_failure_with_errors(self):
        """Test CheckoutResult with validation errors"""
        errors = {'full_name': 'Full name is required.'}
        result = CheckoutResult(
            success=False,
            error_type='validation',
            error_message='Validation failed',
            errors=errors
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.order)
        self.assertEqual(result.error_type, 'validation')
        self.assertEqual(result.error_message, 'Validation failed')
        self.assertEqual(result.errors, errors)

    def test_checkout_result_failure_stock_error(self):
        """Test CheckoutResult with stock error"""
        result = CheckoutResult(
            success=False,
            error_type='stock',
            error_message='Insufficient stock'
        )
        self.assertFalse(result.success)
        self.assertEqual(result.error_type, 'stock')
        self.assertEqual(result.error_message, 'Insufficient stock')


class ProcessCheckoutServiceTestCase(TestCase):
    """Test cases for process_checkout_service function"""

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
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        self.valid_shipping_data = {
            'full_name': 'John Doe',
            'phone_number': '+62123456789',
            'address_line1': '123 Main St',
            'address_line2': '',
            'city': 'Jakarta',
            'state': '',
            'postal_code': '12345',
            'country': 'Indonesia',
        }

    def test_process_checkout_service_success(self):
        """Test successful checkout through service"""
        cart_items = self.cart.items.select_related('product')

        result = process_checkout_service(
            user=self.user,
            cart=self.cart,
            cart_items=cart_items,
            shipping_data=self.valid_shipping_data,
            payment_method='CREDIT_CARD'
        )

        self.assertTrue(result.success)
        self.assertIsNotNone(result.order)
        self.assertEqual(result.order.user, self.user)
        self.assertEqual(result.order.status, Order.Status.PAID)
        self.assertIsNotNone(result.order.delivery_started_at)

        # Verify stock was decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)

        # Verify payment was created
        self.assertTrue(hasattr(result.order, 'payment'))
        self.assertEqual(result.order.payment.method, 'CREDIT_CARD')

    def test_process_checkout_service_invalid_shipping_address(self):
        """Test checkout fails with invalid shipping address"""
        cart_items = self.cart.items.select_related('product')

        invalid_shipping_data = {
            'full_name': '',  # Required field is empty
            'phone_number': '+62123456789',
            'address_line1': '123 Main St',
            'city': 'Jakarta',
            'postal_code': '12345',
            'country': 'Indonesia',
        }

        result = process_checkout_service(
            user=self.user,
            cart=self.cart,
            cart_items=cart_items,
            shipping_data=invalid_shipping_data,
            payment_method='CREDIT_CARD'
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error_type, 'validation')
        self.assertIn('full_name', result.errors)

    def test_process_checkout_service_invalid_payment_method(self):
        """Test checkout fails with invalid payment method"""
        cart_items = self.cart.items.select_related('product')

        result = process_checkout_service(
            user=self.user,
            cart=self.cart,
            cart_items=cart_items,
            shipping_data=self.valid_shipping_data,
            payment_method='INVALID_METHOD'
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error_type, 'validation')
        self.assertIn('Invalid payment method', result.error_message)

    def test_process_checkout_service_insufficient_stock(self):
        """Test checkout fails with insufficient stock"""
        # Update cart item to have more than available stock
        cart_item = self.cart.items.first()
        cart_item.quantity = 20  # More than available stock (10)
        cart_item.save()

        cart_items = self.cart.items.select_related('product')

        result = process_checkout_service(
            user=self.user,
            cart=self.cart,
            cart_items=cart_items,
            shipping_data=self.valid_shipping_data,
            payment_method='CREDIT_CARD'
        )

        self.assertFalse(result.success)
        self.assertEqual(result.error_type, 'stock')
        self.assertIn(self.product.name, result.error_message)

    def test_process_checkout_service_all_payment_methods(self):
        """Test checkout succeeds with all valid payment methods"""
        valid_methods = ['CREDIT_CARD', 'BANK_TRANSFER', 'E_WALLET', 'COD']

        for payment_method in valid_methods:
            # Get existing cart and refill it (checkout clears the cart)
            cart, _ = Cart.objects.get_or_create(user=self.user)
            cart.items.all().delete()  # Clear any existing items
            CartItem.objects.create(cart=cart, product=self.product, quantity=1)
            cart_items = cart.items.select_related('product')

            result = process_checkout_service(
                user=self.user,
                cart=cart,
                cart_items=cart_items,
                shipping_data=self.valid_shipping_data,
                payment_method=payment_method
            )

            self.assertTrue(result.success, f"Checkout failed for payment method: {payment_method}")
            self.assertEqual(result.order.payment.method, payment_method)

    def test_process_checkout_service_clears_cart(self):
        """Test that checkout clears the cart"""
        cart_items = self.cart.items.select_related('product')

        result = process_checkout_service(
            user=self.user,
            cart=self.cart,
            cart_items=cart_items,
            shipping_data=self.valid_shipping_data,
            payment_method='CREDIT_CARD'
        )

        self.assertTrue(result.success)

        # Verify cart was cleared
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.get_item_count(), 0)

    def test_process_checkout_service_creates_shipping_address(self):
        """Test that checkout creates shipping address correctly"""
        cart_items = self.cart.items.select_related('product')

        result = process_checkout_service(
            user=self.user,
            cart=self.cart,
            cart_items=cart_items,
            shipping_data=self.valid_shipping_data,
            payment_method='CREDIT_CARD'
        )

        self.assertTrue(result.success)

        # Verify shipping address was created with correct data
        shipping = result.order.shipping_address
        self.assertEqual(shipping.full_name, 'John Doe')
        self.assertEqual(shipping.phone_number, '+62123456789')
        self.assertEqual(shipping.address_line1, '123 Main St')
        self.assertEqual(shipping.city, 'Jakarta')
        self.assertEqual(shipping.postal_code, '12345')
        self.assertEqual(shipping.country, 'Indonesia')
