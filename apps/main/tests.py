from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from apps.main.models import Product, ProductType, Customer
from apps.profiles.models import Profile


class ProductTypeModelTestCase(TestCase):
    """Test cases for ProductType model"""

    def test_product_type_creation(self):
        """Test creating a product type"""
        product_type = ProductType.objects.create(
            name='Running Shoes',
            description='High-performance running shoes for athletes'
        )
        self.assertEqual(product_type.name, 'Running Shoes')
        self.assertEqual(str(product_type), 'Running Shoes')

    def test_product_type_unique_name(self):
        """Test that product type names must be unique"""
        ProductType.objects.create(name='Running Shoes')
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ProductType.objects.create(name='Running Shoes')

    def test_product_type_ordering(self):
        """Test that product types are ordered by name"""
        ProductType.objects.create(name='Yoga Mats')
        ProductType.objects.create(name='Basketball')
        ProductType.objects.create(name='Running Shoes')
        
        types = list(ProductType.objects.all())
        self.assertEqual(types[0].name, 'Basketball')
        self.assertEqual(types[1].name, 'Running Shoes')
        self.assertEqual(types[2].name, 'Yoga Mats')


class ProductModelTestCase(TestCase):
    """Test cases for Product model"""

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

    def test_product_creation(self):
        """Test creating a product"""
        product = Product.objects.create(
            name='Test Running Shoe',
            description='A great running shoe for testing',
            price=Decimal('99.99'),
            product_type=self.product_type,
            brand='Nike',
            stock=10,
            created_by=self.user
        )
        self.assertEqual(product.name, 'Test Running Shoe')
        self.assertEqual(product.price, Decimal('99.99'))
        self.assertEqual(product.stock, 10)
        self.assertEqual(product.rating, Decimal('0.00'))
        self.assertEqual(str(product), f"{product.name} - {self.product_type.name}")

    def test_product_with_optional_fields(self):
        """Test product with optional fields"""
        product = Product.objects.create(
            name='Basic Shoe',
            description='Simple shoe',
            price=Decimal('50.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )
        self.assertEqual(product.brand, '')
        self.assertIsNone(product.image_url)

    def test_product_default_stock(self):
        """Test product default stock is 0"""
        product = Product.objects.create(
            name='Out of Stock Shoe',
            description='No stock',
            price=Decimal('75.00'),
            product_type=self.product_type,
            created_by=self.user
        )
        self.assertEqual(product.stock, 0)

    def test_product_default_rating(self):
        """Test product default rating is 0.00"""
        product = Product.objects.create(
            name='New Shoe',
            description='Brand new',
            price=Decimal('100.00'),
            product_type=self.product_type,
            stock=10,
            created_by=self.user
        )
        self.assertEqual(product.rating, Decimal('0.00'))

    def test_product_ordering(self):
        """Test that products are ordered by created_at descending"""
        import time
        product1 = Product.objects.create(
            name='Product 1',
            description='First',
            price=Decimal('50.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )
        time.sleep(0.01)  # Small delay to ensure different timestamps
        product2 = Product.objects.create(
            name='Product 2',
            description='Second',
            price=Decimal('60.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )
        
        products = list(Product.objects.all())
        self.assertEqual(products[0], product2)  # Most recent first
        self.assertEqual(products[1], product1)

    def test_product_relationships(self):
        """Test product foreign key relationships"""
        product = Product.objects.create(
            name='Test Shoe',
            description='Test',
            price=Decimal('99.99'),
            product_type=self.product_type,
            stock=10,
            created_by=self.user
        )
        
        # Test reverse relationship from product_type
        self.assertIn(product, self.product_type.products.all())
        
        # Test reverse relationship from user
        self.assertIn(product, self.user.products.all())


class CustomerModelTestCase(TestCase):
    """Test cases for Customer model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_customer_creation(self):
        """Test creating a customer profile"""
        customer = Customer.objects.create(
            user=self.user,
            phone_number='+62123456789',
            address='123 Main St, Jakarta'
        )
        self.assertEqual(customer.user, self.user)
        self.assertEqual(customer.phone_number, '+62123456789')
        self.assertEqual(str(customer), f"{self.user.username} - Customer")

    def test_customer_optional_fields(self):
        """Test customer with optional fields blank"""
        customer = Customer.objects.create(user=self.user)
        self.assertEqual(customer.phone_number, '')
        self.assertEqual(customer.address, '')

    def test_customer_one_to_one_relationship(self):
        """Test that customer has one-to-one relationship with user"""
        customer = Customer.objects.create(user=self.user)
        
        # Test reverse relationship
        self.assertEqual(self.user.customer, customer)

    def test_customer_cascade_delete(self):
        """Test that customer is deleted when user is deleted"""
        customer = Customer.objects.create(user=self.user)
        customer_id = customer.id
        
        self.user.delete()
        
        self.assertFalse(Customer.objects.filter(id=customer_id).exists())


class MainViewsTestCase(TestCase):
    """Test cases for main app views"""

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
            brand='Nike',
            stock=10,
            created_by=self.user
        )

    def test_home_page_loads(self):
        """Test home page loads successfully"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/home.html')

    def test_home_page_has_products_grid(self):
        """Test home page has products grid container"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'productsGrid')
        self.assertContains(response, 'Equipment Catalog')

    def test_product_detail_view(self):
        """Test product detail view"""
        response = self.client.get(
            reverse('product_detail', kwargs={'product_id': self.product.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)
        self.assertContains(response, self.product.description)

    def test_product_detail_404_for_invalid_id(self):
        """Test product detail returns 404 for invalid product ID"""
        response = self.client.get(
            reverse('product_detail', kwargs={'product_id': 99999})
        )
        self.assertEqual(response.status_code, 404)

    def test_products_api_endpoint(self):
        """Test products API endpoint returns JSON"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('products', data)
        self.assertIn('pagination', data)
        
        # Check that our product is in the results
        product_names = [p['name'] for p in data['products']]
        self.assertIn(self.product.name, product_names)

    def test_add_product_ajax_seller_only(self):
        """Test add product AJAX requires seller account"""
        self.client.login(username='testuser', password='testpass123')

        # Create buyer profile (default)
        Profile.objects.update_or_create(user=self.user, defaults={'account_type': 'BUYER'})

        product_data = {
            'name': 'New Product',
            'description': 'Test product',
            'price': '29.99',
            'product_type': self.product_type.id,
            'stock': 5
        }

        response = self.client.post(
            reverse('add_product_ajax'),
            data=product_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('seller accounts', data['error'])

    def test_add_product_ajax_success(self):
        """Test successful product addition via AJAX"""
        self.client.login(username='testuser', password='testpass123')

        # Create seller profile
        Profile.objects.update_or_create(user=self.user, defaults={'account_type': 'SELLER'})

        product_data = {
            'name': 'New Seller Product',
            'description': 'Product added by seller',
            'price': '49.99',
            'product_type': self.product_type.id,
            'stock': 10,
            'image_url': 'https://example.com/image.jpg'
        }

        response = self.client.post(
            reverse('add_product_ajax'),
            data=product_data,
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['product']['name'], 'New Seller Product')
        self.assertEqual(data['product']['stock'], 10)

        # Verify product was created
        product = Product.objects.get(name='New Seller Product')
        self.assertEqual(product.created_by, self.user)
        self.assertEqual(product.price, Decimal('49.99'))

    def test_delete_product_ajax_wrong_account_type(self):
        """Test delete product AJAX requires seller account"""
        self.client.login(username='testuser', password='testpass123')

        # Create buyer profile
        Profile.objects.update_or_create(user=self.user, defaults={'account_type': 'BUYER'})

        response = self.client.delete(
            reverse('delete_product_ajax', kwargs={'product_id': self.product.id})
        )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('seller accounts', data['error'])

    def test_delete_product_ajax_wrong_owner(self):
        """Test delete product AJAX requires ownership"""
        # Create another seller user
        other_user = User.objects.create_user(
            username='otherseller',
            password='testpass123'
        )
        Profile.objects.update_or_create(user=other_user, defaults={'account_type': 'SELLER'})

        self.client.login(username='otherseller', password='testpass123')

        response = self.client.delete(
            reverse('delete_product_ajax', kwargs={'product_id': self.product.id})
        )
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('own products', data['error'])

    def test_delete_product_ajax_success(self):
        """Test successful product deletion via AJAX"""
        self.client.login(username='testuser', password='testpass123')

        # Create seller profile
        Profile.objects.update_or_create(user=self.user, defaults={'account_type': 'SELLER'})

        response = self.client.delete(
            reverse('delete_product_ajax', kwargs={'product_id': self.product.id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        # Verify product was deleted
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_get_products_ajax_filtering(self):
        """Test products AJAX endpoint with filtering"""
        # Create additional products for testing
        product2 = Product.objects.create(
            name='Basketball',
            description='Sports ball',
            price=Decimal('25.00'),
            product_type=self.product_type,
            stock=5,
            created_by=self.user
        )

        # Test search filtering
        response = self.client.get(
            reverse('get_products_ajax'),
            {'q': 'running'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        product_names = [p['name'] for p in data['products']]
        self.assertIn('Test Running Shoe', product_names)
        self.assertNotIn('Basketball', product_names)

    def test_get_products_ajax_price_filtering(self):
        """Test products AJAX endpoint with price filtering"""
        # Create product with different price
        Product.objects.create(
            name='Cheap Product',
            description='Low price item',
            price=Decimal('10.00'),
            product_type=self.product_type,
            stock=1,
            created_by=self.user
        )

        # Test price range filtering
        response = self.client.get(
            reverse('get_products_ajax'),
            {'min_price': '20', 'max_price': '150'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])

        # Should only return the original product (99.99)
        self.assertEqual(len(data['products']), 1)
        self.assertEqual(data['products'][0]['name'], 'Test Running Shoe')

    def test_get_products_ajax_pagination(self):
        """Test products AJAX endpoint pagination"""
        # Create many products for pagination testing
        for i in range(25):
            Product.objects.create(
                name=f'Product {i}',
                description=f'Description {i}',
                price=Decimal('20.00'),
                product_type=self.product_type,
                stock=1,
                created_by=self.user
            )

        # Test pagination
        response = self.client.get(
            reverse('get_products_ajax'),
            {'per_page': '10', 'page': '2'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['products']), 10)  # Should return 10 items per page
        self.assertEqual(data['pagination']['page'], 2)
        self.assertTrue(data['pagination']['has_next'])
        self.assertTrue(data['pagination']['has_previous'])
