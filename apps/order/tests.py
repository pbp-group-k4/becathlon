from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import F
from decimal import Decimal
from datetime import timedelta
from apps.main.models import Product, ProductType
from apps.cart.models import Cart, CartItem
from apps.order.models import Order, OrderItem, ShippingAddress, Payment, ProductRating


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

