from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F
from apps.main.models import Product

class Cart(models.Model):
    """Shopping cart for users and guest sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_cart', condition=models.Q(user__isnull=False)),
            models.UniqueConstraint(fields=['session_key'], name='unique_session_cart', condition=models.Q(session_key__isnull=False)),
        ]

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Guest cart {self.session_key}"

    def get_total_items(self):
        """Return sum of all item quantities"""
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0

    def get_subtotal(self):
        """Return sum of all item subtotals"""
        return self.items.aggregate(
            subtotal=Sum(F('quantity') * F('product__price'))
        )['subtotal'] or 0

    def get_item_count(self):
        """Return number of distinct items"""
        return self.items.count()

    def merge_carts(self, other_cart):
        """Merge another cart into this one"""
        for item in other_cart.items.all():
            existing_item = self.items.filter(product=item.product).first()
            if existing_item:
                existing_item.quantity += item.quantity
                existing_item.save()
                item.delete()
            else:
                item.cart = self
                item.save()
        other_cart.delete()

    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Individual item in a shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product'], name='unique_cart_product'),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_subtotal(self):
        """Return quantity * product.price"""
        return self.quantity * self.product.price

    def get_item_total(self):
        """Alias for get_subtotal for display purposes"""
        return self.get_subtotal()
