from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, F
from apps.cart.models import Cart, CartItem
from apps.main.models import Product


class ShippingAddress(models.Model):
    """Stores delivery details for an order"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="Indonesia")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name}, {self.address_line1}, {self.city}"


class Order(models.Model):
    """Represents a completed checkout derived from a Cart"""
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        PAID = "PAID", _("Paid")
        SHIPPED = "SHIPPED", _("Shipped")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELED = "CANCELED", _("Canceled")

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    cart = models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id or 'N/A'} ({self.status})"

    def calculate_total(self):
        """Recalculate total based on order items"""
        total = self.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total'] or 0
        self.total_price = total
        self.save(update_fields=['total_price'])
        return total

    def get_total_items(self):
        """Return sum of all item quantities"""
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0

    def get_item_count(self):
        """Return number of distinct items"""
        return self.items.count()

    def get_subtotal(self):
        """Return sum of all item subtotals"""
        return self.items.aggregate(
            subtotal=Sum(F('quantity') * F('price'))
        )['subtotal'] or 0

    @classmethod
    def create_from_cart(cls, cart, shipping_address=None):
        """
        Convert an existing Cart into an Order
        """
        # Create order without cart reference to avoid unique constraint issues
        order = cls.objects.create(
            user=cart.user,
            shipping_address=shipping_address,
        )

        # Copy items into OrderItem table
        for item in cart.items.select_related('product'):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,  # snapshot current price
            )

        # Set total and clear cart
        order.calculate_total()
        cart.clear()
        return order


class OrderItem(models.Model):
    """Snapshot of a CartItem at checkout"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order', 'product'], name='unique_order_product'),
        ]

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

    def get_subtotal(self):
        """Return quantity * price"""
        return self.quantity * self.price

    def get_item_total(self):
        """Alias for get_subtotal for display purposes"""
        return self.get_subtotal()

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"


class Payment(models.Model):
    """Tracks payment info for each order"""
    class Method(models.TextChoices):
        CREDIT_CARD = "CREDIT_CARD", _("Credit Card")
        BANK_TRANSFER = "BANK_TRANSFER", _("Bank Transfer")
        E_WALLET = "E_WALLET", _("E-Wallet")
        COD = "COD", _("Cash on Delivery")

    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        SUCCESS = "SUCCESS", _("Success")
        FAILED = "FAILED", _("Failed")
        REFUNDED = "REFUNDED", _("Refunded")

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    method = models.CharField(max_length=30, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} ({self.status})"
