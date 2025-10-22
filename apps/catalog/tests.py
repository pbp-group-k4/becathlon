from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from apps.main.models import Product, ProductType
from apps.catalog.models import ProductImage


class CatalogViewsTestCase(TestCase):
    """Test cases for catalog views"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create product types
        self.product_type1 = ProductType.objects.create(
            name='Running Shoes',
            description='High-performance running shoes'
        )
        
        self.product_type2 = ProductType.objects.create(
            name='Tennis Rackets',
            description='Professional tennis equipment'
        )
        
        # Create products
        self.product1 = Product.objects.create(
            name='Test Running Shoe',
            description='A great running shoe for testing',
            price=99.99,
            product_type=self.product_type1,
            stock=10,
            created_by=self.user
        )
        
        self.product2 = Product.objects.create(
            name='Test Tennis Racket',
            description='A professional tennis racket',
            price=149.99,
            product_type=self.product_type2,
            stock=5,
            created_by=self.user
        )
        
        # Create product image
        self.image1 = ProductImage.objects.create(
            product=self.product1,
            image_url='https://example.com/shoe.jpg',
            is_primary=True,
            display_order=1
        )
    
    def test_catalog_home_view(self):
        """Test catalog home page loads correctly"""
        response = self.client.get(reverse('catalog:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Product Catalog')
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)
    
    def test_category_products_view(self):
        """Test category view loads correctly"""
        response = self.client.get(
            reverse('catalog:category', kwargs={'category_id': self.product_type1.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product_type1.name)
        self.assertContains(response, self.product1.name)
        self.assertNotContains(response, self.product2.name)
    
    def test_product_detail_view(self):
        """Test product detail page loads correctly"""
        response = self.client.get(
            reverse('catalog:product_detail', kwargs={'product_id': self.product1.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product1.description)
        self.assertContains(response, str(self.product1.price))
    
    def test_filter_by_category(self):
        """Test filtering products by category"""
        response = self.client.get(
            reverse('catalog:home'),
            {'categories': [self.product_type1.id]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
    
    def test_filter_by_price_range(self):
        """Test filtering products by price range"""
        response = self.client.get(
            reverse('catalog:home'),
            {'min_price': 100, 'max_price': 200}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product2.name)
        self.assertNotContains(response, self.product1.name)
    
    def test_filter_by_stock(self):
        """Test filtering products by stock availability"""
        # Create out of stock product
        out_of_stock = Product.objects.create(
            name='Out of Stock Product',
            description='No stock available',
            price=79.99,
            product_type=self.product_type1,
            stock=0,
            created_by=self.user
        )
        
        response = self.client.get(
            reverse('catalog:home'),
            {'in_stock_only': 'true'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertNotContains(response, out_of_stock.name)
    
    def test_search_products(self):
        """Test searching products"""
        response = self.client.get(
            reverse('catalog:home'),
            {'search': 'running'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertNotContains(response, self.product2.name)
    
    def test_sort_by_price_low(self):
        """Test sorting products by price (low to high)"""
        response = self.client.get(
            reverse('catalog:home'),
            {'sort_by': 'price_low'}
        )
        self.assertEqual(response.status_code, 200)
        # Product 1 ($99.99) should appear before Product 2 ($149.99)
    
    def test_api_filter_products(self):
        """Test AJAX API for filtering products"""
        response = self.client.get(reverse('catalog:api_filter'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('products', data)
        self.assertIn('total_count', data)
        self.assertEqual(len(data['products']), 2)
    
    def test_api_quick_view(self):
        """Test AJAX API for product quick view"""
        response = self.client.get(
            reverse('catalog:api_quick_view', kwargs={'product_id': self.product1.id})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], self.product1.name)
        self.assertEqual(data['product_type'], self.product_type1.name)
        self.assertTrue(data['in_stock'])
    
    def test_api_quick_view_not_found(self):
        """Test quick view API with non-existent product"""
        response = self.client.get(
            reverse('catalog:api_quick_view', kwargs={'product_id': 9999})
        )
        self.assertEqual(response.status_code, 404)


class ProductImageModelTestCase(TestCase):
    """Test cases for ProductImage model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.product_type = ProductType.objects.create(
            name='Test Category'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=50.00,
            product_type=self.product_type,
            stock=10,
            created_by=self.user
        )
    
    def test_create_product_image(self):
        """Test creating a product image"""
        image = ProductImage.objects.create(
            product=self.product,
            image_url='https://example.com/image.jpg',
            is_primary=True,
            display_order=1
        )
        self.assertEqual(image.product, self.product)
        self.assertTrue(image.is_primary)
    
    def test_only_one_primary_image(self):
        """Test that setting a new primary image unsets the old one"""
        image1 = ProductImage.objects.create(
            product=self.product,
            image_url='https://example.com/image1.jpg',
            is_primary=True,
            display_order=1
        )
        
        image2 = ProductImage.objects.create(
            product=self.product,
            image_url='https://example.com/image2.jpg',
            is_primary=True,
            display_order=2
        )
        
        # Refresh image1 from database
        image1.refresh_from_db()
        
        # image1 should no longer be primary
        self.assertFalse(image1.is_primary)
        self.assertTrue(image2.is_primary)
    
    def test_image_ordering(self):
        """Test that images are ordered by display_order"""
        image3 = ProductImage.objects.create(
            product=self.product,
            image_url='https://example.com/image3.jpg',
            display_order=3
        )
        
        image1 = ProductImage.objects.create(
            product=self.product,
            image_url='https://example.com/image1.jpg',
            display_order=1
        )
        
        image2 = ProductImage.objects.create(
            product=self.product,
            image_url='https://example.com/image2.jpg',
            display_order=2
        )
        
        images = ProductImage.objects.filter(product=self.product)
        self.assertEqual(images[0], image1)
        self.assertEqual(images[1], image2)
        self.assertEqual(images[2], image3)
