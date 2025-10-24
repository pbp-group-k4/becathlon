from django.test import TestCase
from apps.stores.models import Store


class StoreModelTestCase(TestCase):
    """Test cases for Store model"""

    def test_store_creation(self):
        """Test creating a store"""
        store = Store.objects.create(
            name='Decathlon Jakarta',
            address='123 Main Street',
            city='Jakarta',
            country='Indonesia',
            longitude=106.8456,
            latitude=-6.2088,
            store_hours='Mon-Sun: 9:00 AM - 9:00 PM'
        )
        self.assertEqual(store.name, 'Decathlon Jakarta')
        self.assertEqual(store.city, 'Jakarta')
        self.assertTrue(store.is_active)
        self.assertEqual(str(store), 'Decathlon Jakarta — Jakarta, Indonesia')

    def test_store_default_values(self):
        """Test store default values"""
        store = Store.objects.create(
            name='Decathlon Bandung',
            address='456 Second Street',
            longitude=107.6191,
            latitude=-6.9175
        )
        self.assertEqual(store.country, 'Indonesia')
        self.assertTrue(store.is_active)
        self.assertEqual(store.city, '')

    def test_store_coordinates(self):
        """Test store geographical coordinates"""
        store = Store.objects.create(
            name='Decathlon Surabaya',
            address='789 Third Street',
            city='Surabaya',
            longitude=112.7521,
            latitude=-7.2575
        )
        self.assertEqual(store.longitude, 112.7521)
        self.assertEqual(store.latitude, -7.2575)

    def test_store_is_active_field(self):
        """Test store is_active field"""
        active_store = Store.objects.create(
            name='Active Store',
            address='Address 1',
            longitude=100.0,
            latitude=-5.0,
            is_active=True
        )
        inactive_store = Store.objects.create(
            name='Inactive Store',
            address='Address 2',
            longitude=100.0,
            latitude=-5.0,
            is_active=False
        )
        self.assertTrue(active_store.is_active)
        self.assertFalse(inactive_store.is_active)

    def test_store_ordering(self):
        """Test that stores are ordered by name"""
        Store.objects.create(
            name='Zebra Store',
            address='Address 1',
            longitude=100.0,
            latitude=-5.0
        )
        Store.objects.create(
            name='Alpha Store',
            address='Address 2',
            longitude=100.0,
            latitude=-5.0
        )
        Store.objects.create(
            name='Beta Store',
            address='Address 3',
            longitude=100.0,
            latitude=-5.0
        )
        
        stores = list(Store.objects.all())
        self.assertEqual(stores[0].name, 'Alpha Store')
        self.assertEqual(stores[1].name, 'Beta Store')
        self.assertEqual(stores[2].name, 'Zebra Store')

