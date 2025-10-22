from django.contrib import admin
from .models import Customer, ProductType, Product

# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at',)


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'brand', 'price', 'stock', 'rating', 'created_by', 'created_at')
    list_filter = ('product_type', 'created_at', 'brand')
    search_fields = ('name', 'description', 'created_by__username', 'brand')
    readonly_fields = ('created_at', 'updated_at', 'rating')

