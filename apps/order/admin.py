from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress, Payment


class OrderItemInline(admin.TabularInline):
    """Show order items inside each order page in admin."""
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'subtotal')

    def subtotal(self, obj):
        return obj.get_subtotal()
    subtotal.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_name', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    inlines = [OrderItemInline]

    def user_name(self, obj):
        if obj.user:
            return obj.user.username
        return "Guest"
    user_name.short_description = "Customer"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'subtotal')

    def subtotal(self, obj):
        return obj.get_subtotal()
    subtotal.short_description = "Subtotal"


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'city', 'country', 'user', 'created_at')
    list_filter = ('country', 'created_at')
    search_fields = ('full_name', 'city', 'user__username')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'status', 'amount', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('order__id', 'transaction_id')


