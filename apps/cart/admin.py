from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('added_at', 'updated_at')

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_or_session', 'total_items', 'subtotal', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'session_key')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]

    def user_or_session(self, obj):
        if obj.user:
            return obj.user.username
        return f"Guest ({obj.session_key[:8]}...)" if obj.session_key else "Guest"
    user_or_session.short_description = "User/Session"

    def total_items(self, obj):
        return obj.get_total_items()
    total_items.short_description = "Total Items"

    def subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    subtotal.short_description = "Subtotal"

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'subtotal', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('product__name',)

    def subtotal(self, obj):
        return f"${obj.get_subtotal():.2f}"
    subtotal.short_description = "Subtotal"

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
