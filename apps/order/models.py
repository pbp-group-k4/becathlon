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
    
    class DeliveryStatus(models.TextChoices):
        PROCESSING = "PROCESSING", _("Processing")
        EN_ROUTE = "EN_ROUTE", _("En Route")
        DELIVERED = "DELIVERED", _("Delivered")

    # Configurable delivery timer durations (in seconds)
    PROCESSING_DURATION = 30  # 30 seconds in Processing
    EN_ROUTE_DURATION = 90  # 90 seconds in En Route (total 120s including Processing)
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    cart = models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    delivery_status = models.CharField(
        max_length=20, 
        choices=DeliveryStatus.choices, 
        default=DeliveryStatus.PROCESSING,
        help_text="Current delivery stage"
    )
    delivery_started_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Timestamp when delivery tracking started (when order was paid)"
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id or 'N/A'} ({self.status})"
    
    def get_current_delivery_status(self):
        """
        Calculate current delivery status based on elapsed time since delivery started.
        Returns the current DeliveryStatus and seconds remaining in current stage.
        """
        from django.utils import timezone
        
        if not self.delivery_started_at or self.delivery_status == self.DeliveryStatus.DELIVERED:
            return self.delivery_status, 0
        
        elapsed = (timezone.now() - self.delivery_started_at).total_seconds()
        
        if elapsed < self.PROCESSING_DURATION:
            # Still in Processing stage
            remaining = self.PROCESSING_DURATION - elapsed
            return self.DeliveryStatus.PROCESSING, int(remaining)
        elif elapsed < (self.PROCESSING_DURATION + self.EN_ROUTE_DURATION):
            # In En Route stage
            remaining = (self.PROCESSING_DURATION + self.EN_ROUTE_DURATION) - elapsed
            return self.DeliveryStatus.EN_ROUTE, int(remaining)
        else:
            # Delivered
            return self.DeliveryStatus.DELIVERED, 0
    
    def update_delivery_status(self):
        """
        Update the delivery_status field based on current time.
        Returns True if status was changed, False otherwise.
        """
        current_status, _ = self.get_current_delivery_status()
        if current_status != self.delivery_status:
            self.delivery_status = current_status
            self.save(update_fields=['delivery_status', 'updated_at'])
            return True
        return False
    
    def get_delivery_progress_percentage(self):
        """
        Return delivery progress as a percentage (0-100).
        """
        from django.utils import timezone
        
        if not self.delivery_started_at:
            return 0
        
        if self.delivery_status == self.DeliveryStatus.DELIVERED:
            return 100
        
        total_duration = self.PROCESSING_DURATION + self.EN_ROUTE_DURATION
        elapsed = (timezone.now() - self.delivery_started_at).total_seconds()
        progress = min((elapsed / total_duration) * 100, 100)
        return int(progress)
    
    def start_delivery_tracking(self):
        """
        Initialize delivery tracking when order is paid.
        """
        from django.utils import timezone
        if not self.delivery_started_at:
            self.delivery_started_at = timezone.now()
            self.delivery_status = self.DeliveryStatus.PROCESSING
            self.save(update_fields=['delivery_started_at', 'delivery_status', 'updated_at'])

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
        Convert an existing Cart into an Order and decrement product stock.
        Uses select_for_update() to prevent race conditions.
        Raises ValueError if insufficient stock is detected.
        """
        from django.db import transaction
        
        # Create order without cart reference to avoid unique constraint issues
        order = cls.objects.create(
            user=cart.user,
            shipping_address=shipping_address,
        )

        # Copy items into OrderItem table and decrement stock atomically
        with transaction.atomic():
            for item in cart.items.select_related('product'):
                # Lock the product row to prevent race conditions
                product = Product.objects.select_for_update().get(pk=item.product.pk)
                
                # Double-check stock availability
                if product.stock < item.quantity:
                    raise ValueError(
                        f"Insufficient stock for {product.name}. "
                        f"Available: {product.stock}, Requested: {item.quantity}"
                    )
                
                # Decrement stock using F() expression for atomic update
                product.stock = F('stock') - item.quantity
                product.save(update_fields=['stock'])
                
                # Create order item
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


class ProductRating(models.Model):
    """
    Tracks individual ratings given by users for products in their orders.
    Each user can rate each product only once per order.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='product_ratings')
    rating = models.PositiveSmallIntegerField(
        help_text="Rating from 1 to 5 stars",
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    review = models.TextField(blank=True, help_text="Optional review text")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product', 'order'], 
                name='unique_user_product_order_rating'
            ),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} rated {self.product.name}: {self.rating}★"
    
    def save(self, *args, **kwargs):
        """Update product's aggregate rating when a rating is saved"""
        super().save(*args, **kwargs)
        self.product.update_aggregate_rating()


# Add this method to Product model via monkey patching (or add to main/models.py later)
def update_aggregate_rating(self):
    """
    Recalculate and update the product's aggregate rating based on all ProductRatings.
    Only considers products that still exist (not deleted).
    """
    from django.db.models import Avg
    
    # Import here to avoid circular imports
    aggregate = ProductRating.objects.filter(
        product=self,
        product__isnull=False  # Only if product still exists
    ).aggregate(avg_rating=Avg('rating'))
    
    avg_rating = aggregate['avg_rating']
    if avg_rating is not None:
        self.rating = round(avg_rating, 2)
    else:
        self.rating = 0.00
    
    self.save(update_fields=['rating'])

# Attach the method to Product model
Product.update_aggregate_rating = update_aggregate_rating
