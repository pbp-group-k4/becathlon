from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from apps.main.models import Product, ProductType
from apps.catalog.models import ProductImage
import json

class MobileCatalogTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.products_url = reverse('catalog:mobile_products_list')
        self.categories_url = reverse('catalog:mobile_categories_list')
        
        # Create user for product creation
        self.user = User.objects.create_user(username='seller', password='password')
        
        # Create test data
        self.category = ProductType.objects.create(
            name='Sports',
            description='Sports equipment'
        )
        
        self.product1 = Product.objects.create(
            name='Football',
            description='A standard football',
            price=29.99,
            stock=10,
            product_type=self.category,
            brand='Nike',
            created_by=self.user
        )
        
        self.product2 = Product.objects.create(
            name='Tennis Racket',
            description='Pro racket',
            price=199.99,
            stock=0, # Out of stock
            product_type=self.category,
            brand='Wilson',
            created_by=self.user
        )

    def test_mobile_products_list_all(self):
        response = self.client.get(self.products_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        
        # Check structure (Django pk/fields format)
        self.assertIn('pk', data[0])
        self.assertIn('fields', data[0])
        self.assertEqual(data[0]['fields']['name'], self.product2.name) # Default sort is newest (created_at desc)

    def test_mobile_products_list_search(self):
        response = self.client.get(self.products_url, {'search': 'Football'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['fields']['name'], 'Football')

    def test_mobile_products_list_category_filter(self):
        response = self.client.get(self.products_url, {'category': 'Sports'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        
        response = self.client.get(self.products_url, {'category': 'NonExistent'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 0)

    def test_mobile_products_list_stock_filter(self):
        response = self.client.get(self.products_url, {'in_stock_only': 'true'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['fields']['name'], 'Football')

    def test_mobile_product_detail_success(self):
        url = reverse('catalog:mobile_product_detail', args=[self.product1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['pk'], self.product1.id)
        self.assertEqual(data['fields']['name'], self.product1.name)
        self.assertEqual(data['fields']['price'], str(self.product1.price))

    def test_mobile_product_detail_not_found(self):
        url = reverse('catalog:mobile_product_detail', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_mobile_categories_list(self):
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Sports')
        self.assertEqual(data[0]['product_count'], 2)
