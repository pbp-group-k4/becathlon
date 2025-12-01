from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Customer(models.Model):
    """Customer model extending User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Customer"


class ProductType(models.Model):
    """Product categories/types for Decathlon sports equipment"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Product(models.Model):
    """Product model for sports equipment"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=100, blank=True, default='')
    image_url = models.URLField(blank=True, null=True)
    stock = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.product_type.name}"
    
    class Meta:
        ordering = ['-created_at']

    def get_primary_image_url(self):
        """
        Returns the primary image URL for product. If a ProductImage instance
        exists and marked primary, return `image_url`, else fall back
        to the `image_url` field on the product itself (if present, else an empty
        string.
        """
        # reverse relation `images` from apps.catalog.models.ProductImage
        primary = self.images.filter(is_primary=True).first()
        if primary and getattr(primary, 'image_url', None):
            return primary.image_url
        return self.image_url or ''

    @property
    def primary_image_url(self):
        return self.get_primary_image_url()
