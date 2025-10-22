from django.contrib import admin
from .models import ProductImage
from apps.main.models import Product


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image_url', 'is_primary', 'display_order')


class ProductAdminCatalog(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'price', 'stock', 'created_at')
    list_filter = ('product_type', 'created_at')
    search_fields = ('name', 'description')
    list_per_page = 20
    inlines = [ProductImageInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product_type', 'created_by')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'display_order', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('product__name',)
    list_per_page = 20
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product')


# Re-register Product with catalog-specific admin
# This might conflict if Product is already registered in main.admin
# Only uncomment if Product is not registered elsewhere
# admin.site.unregister(Product)
# admin.site.register(Product, ProductAdminCatalog)
