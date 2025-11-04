# Database Models & Schema



This document provides complete details about Becathlon's data models, relationships, and database design patterns.



## Core Models Overview



```

User (Django Auth)

    └─ Customer (1-to-1)

    ├─ Cart (1-to-1, unique)

    │   └─ CartItem (1-to-many)

    │       └─ Product (FK)

    ├─ Order (1-to-many)

    │   ├─ OrderItem (1-to-many)

    │   │   └─ Product (FK)

    │   ├─ Payment (1-to-1)

    │   └─ ShippingAddress (FK)

    └─ ProductRating (1-to-many)

        └─ Product (FK)



ProductType

    └─ Product (1-to-many)

        ├─ ProductImage (1-to-many)

        ├─ CartItem (1-to-many)

        └─ OrderItem (1-to-many)

```



## Model Details



### main.models.Customer



Extends Django's User model for additional customer data.



```python

class Customer(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Future fields: loyalty_points, preferences, etc.

    

    def __str__(self):

        return f"Customer: {self.user.username}"

```



**Key Points:**

- Auto-created when user signs up

- Links to User account (1-to-1)

- Extensible for future customer attributes



### main.models.ProductType



Categories for organizing products.



```python

class ProductType(models.Model):

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):

        return self.name

    

    class Meta:

        ordering = ['name']

```



**Seed Data (12 Categories):**

- Running, Cycling, Swimming

- Gym & Fitness, Yoga, Hiking

- Water Sports, Team Sports, Tennis

- Winter Sports, Combat Sports, Outdoor



**Seeding Command:**

```bash

python seed_product_types.py

```



### main.models.Product



Main product entity with comprehensive fields.



```python

class Product(models.Model):

    name = models.CharField(max_length=200)

    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    product_type = models.ForeignKey(

        ProductType,

        on_delete=models.CASCADE,

        related_name='products'

    )

    brand = models.CharField(max_length=100, blank=True, default='')

    image_url = models.URLField(blank=True, null=True)

    stock = models.IntegerField(default=0)

    rating = models.DecimalField(

        max_digits=3,

        decimal_places=2,

        default=0.00

    )

    created_by = models.ForeignKey(

        User,

        on_delete=models.CASCADE,

        related_name='products'

    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):

        return f"{self.name} - {self.product_type.name}"

    

    class Meta:

        ordering = ['-created_at']

```



**Fields Explanation:**

| Field | Type | Purpose |
|-------|------|---------|
| name | CharField | Product title |
| description | TextField | Detailed description |
| price | DecimalField | Current selling price |
| product_type | ForeignKey | Category reference |
| brand | CharField | Manufacturer/brand |
| image_url | URLField | External image URL |
| stock | IntegerField | Available quantity |
| rating | DecimalField | Aggregated average (1-5) |
| created_by | ForeignKey | User who added product |
| created_at | DateTimeField | When product was added |
| updated_at | DateTimeField | Last modification time |

**Key Relationships:**

- `products` (reverse) from ProductImage

- `cartitem_set` (reverse) from CartItem

- `orderitem_set` (reverse) from OrderItem

- `rating_set` (reverse) from ProductRating



### catalog.models.ProductImage



Stores multiple images per product.



```python

class ProductImage(models.Model):

    product = models.ForeignKey(

        Product,

        on_delete=models.CASCADE,

        related_name='images'

    )

    image_url = models.URLField()

    is_primary = models.BooleanField(default=False)

    alt_text = models.CharField(max_length=200, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):

        return f"Image for {self.product.name}"

    

    class Meta:

        ordering = ['-is_primary', '-uploaded_at']

```



**Usage Pattern:**

```python

# Get primary image for product

primary_image = product.images.filter(is_primary=True).first()



# Get all images

all_images = product.images.all()



# Optimized query

from django.db.models import Prefetch

products = Product.objects.prefetch_related(

    Prefetch('images', queryset=ProductImage.objects.filter(is_primary=True))

)

```



## cart.models.Cart



Shopping cart with support for guests and users.



```python

class Cart(models.Model):

    user = models.ForeignKey(

        User,

        on_delete=models.CASCADE,

        null=True,

        blank=True,

        related_name='carts'

    )

    session_key = models.CharField(

        max_length=40,

        null=True,

        blank=True

    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    class Meta:

        constraints = [

            models.UniqueConstraint(

                fields=['user'],

                name='unique_user_cart',

                condition=models.Q(user__isnull=False)

            ),

            models.UniqueConstraint(

                fields=['session_key'],

                name='unique_session_cart',

                condition=models.Q(session_key__isnull=False)

            ),

        ]

    

    def get_total_items(self):

        """Sum of all item quantities"""

        return self.items.aggregate(

            total=Sum('quantity')

        )['total'] or 0

    

    def get_subtotal(self):

        """Sum of (quantity * price)"""

        return self.items.aggregate(

            subtotal=Sum(F('quantity') * F('product__price'))

        )['subtotal'] or 0

    

    def get_item_count(self):

        """Number of distinct products"""

        return self.items.count()

    

    def merge_carts(self, other_cart):

        """Merge another cart into this one"""

        for item in other_cart.items.all():

            existing = self.items.filter(product=item.product).first()

            if existing:

                existing.quantity += item.quantity

                existing.save()

            else:

                item.cart = self

                item.save()

        other_cart.delete()

    

    def clear(self):

        """Remove all items"""

        self.items.all().delete()

```



**Constraints:**

- At most one cart per user (when user != NULL)

- At most one cart per session key (when session_key != NULL)

- Prevents data corruption from duplicate carts



**Access Pattern:**

```python

from apps.cart.utils import get_or_create_cart



# Get or create cart (handles guest vs user)

cart = get_or_create_cart(request)

```



## cart.models.CartItem



Individual product in shopping cart.



```python

class CartItem(models.Model):

    cart = models.ForeignKey(

        Cart,

        on_delete=models.CASCADE,

        related_name='items'

    )

    product = models.ForeignKey(

        Product,

        on_delete=models.CASCADE

    )

    quantity = models.IntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    

    def __str__(self):

        return f"{self.product.name} x {self.quantity}"

    

    class Meta:

        unique_together = ['cart', 'product']

```



**Unique Constraint:**

- Each product appears at most once per cart

- Prevents duplicate CartItem entries

- Quantity field used for "add more" operations



### order.models.ShippingAddress



Delivery address for orders.



```python

class ShippingAddress(models.Model):

    user = models.ForeignKey(

        User,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='shipping_addresses'

    )

    full_name = models.CharField(max_length=100)

    phone_number = models.CharField(max_length=20)

    address = models.TextField()

    postal_code = models.CharField(max_length=20)

    city = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):

        return f"{self.full_name}, {self.city}"

    

    class Meta:

        verbose_name_plural = "Shipping Addresses"

```



### order.models.Order



Completed order/checkout transaction.



```python

class Order(models.Model):

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

    

    # Delivery timeline (seconds)

    PROCESSING_DURATION = 30

    EN_ROUTE_DURATION = 90  # Total: 120 seconds

    

    user = models.ForeignKey(

        User,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='orders'

    )

    cart = models.OneToOneField(

        Cart,

        on_delete=models.SET_NULL,

        null=True,

        blank=True

    )

    shipping_address = models.ForeignKey(

        ShippingAddress,

        on_delete=models.SET_NULL,

        null=True,

        blank=True

    )

    status = models.CharField(

        max_length=20,

        choices=Status.choices,

        default=Status.PENDING

    )

    delivery_status = models.CharField(

        max_length=20,

        choices=DeliveryStatus.choices,

        default=DeliveryStatus.PROCESSING

    )

    delivery_started_at = models.DateTimeField(

        null=True,

        blank=True,

        help_text="When delivery tracking started (order paid)"

    )

    total_price = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        default=0

    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):

        return f"Order #{self.id} ({self.status})"

    

    def calculate_total(self):

        """Recalculate total from OrderItems"""

        total = self.items.aggregate(

            total=Sum(F('quantity') * F('price'))

        )['total'] or 0

        self.total_price = total

        self.save()

        return total

    

    def start_delivery_tracking(self):

        """Initialize tracking when paid"""

        if not self.delivery_started_at:

            self.delivery_started_at = timezone.now()

            self.delivery_status = self.DeliveryStatus.PROCESSING

            self.save()

    

    def get_current_delivery_status(self):

        """Calculate status based on elapsed time"""

        if not self.delivery_started_at:

            return self.delivery_status, 0

        

        elapsed = (timezone.now() - self.delivery_started_at).total_seconds()

        

        if elapsed < self.PROCESSING_DURATION:

            remaining = self.PROCESSING_DURATION - elapsed

            return self.DeliveryStatus.PROCESSING, int(remaining)

        elif elapsed < (self.PROCESSING_DURATION + self.EN_ROUTE_DURATION):

            remaining = (self.PROCESSING_DURATION + self.EN_ROUTE_DURATION) - elapsed

            return self.DeliveryStatus.EN_ROUTE, int(remaining)

        else:

            return self.DeliveryStatus.DELIVERED, 0

    

    def get_delivery_progress_percentage(self):

        """Progress 0-100%"""

        if self.delivery_status == self.DeliveryStatus.DELIVERED:

            return 100

        

        total = self.PROCESSING_DURATION + self.EN_ROUTE_DURATION

        elapsed = (timezone.now() - self.delivery_started_at).total_seconds()

        return int(min((elapsed / total) * 100, 100))

    

    @classmethod

    def create_from_cart(cls, cart, shipping_address=None):

        """Convert Cart to Order (atomic with stock decrement)"""

        with transaction.atomic():

            order = cls.objects.create(

                user=cart.user,

                shipping_address=shipping_address

            )

            

            for item in cart.items.select_related('product'):

                # Lock product for race condition prevention

                product = Product.objects.select_for_update().get(

                    pk=item.product.pk

                )

                

                # Check stock

                if product.stock < item.quantity:

                    raise ValueError(

                        f"Insufficient stock for {product.name}"

                    )

                

                # Decrement stock atomically

                product.stock = F('stock') - item.quantity

                product.save()

                

                # Create snapshot

                OrderItem.objects.create(

                    order=order,

                    product=item.product,

                    quantity=item.quantity,

                    price=item.product.price  # Snapshot!

                )

        

        order.calculate_total()

        cart.clear()

        return order

```



**Delivery Timeline:**

- **PROCESSING**: 0-30 seconds (order being prepared)

- **EN_ROUTE**: 30-120 seconds (in transit)

- **DELIVERED**: 120+ seconds (arrived)



### order.models.OrderItem



Price snapshot of product at purchase time.



```python

class OrderItem(models.Model):

    order = models.ForeignKey(

        Order,

        on_delete=models.CASCADE,

        related_name='items'

    )

    product = models.ForeignKey(

        Product,

        on_delete=models.CASCADE,

        related_name='order_items'

    )

    quantity = models.IntegerField()

    price = models.DecimalField(

        max_digits=10,

        decimal_places=2,

        help_text="Price snapshot at purchase time"

    )

    

    def get_subtotal(self):

        return self.quantity * self.price

    

    def __str__(self):

        return f"{self.product.name} x {self.quantity}"

```



**Critical Design:**

- `price` field stores snapshot (not FK to Product.price)

- Decouples order history from current pricing

- If Product.price changes, OrderItem.price remains unchanged



### order.models.Payment



Mock payment record.



```python

class Payment(models.Model):

    class Method(models.TextChoices):

        CREDIT_CARD = "CREDIT_CARD", _("Credit Card")

        BANK_TRANSFER = "BANK_TRANSFER", _("Bank Transfer")

        E_WALLET = "E_WALLET", _("E-Wallet")

        CASH_ON_DELIVERY = "CASH_ON_DELIVERY", _("Cash on Delivery")

    

    class Status(models.TextChoices):

        PENDING = "PENDING", _("Pending")

        COMPLETED = "COMPLETED", _("Completed")

        FAILED = "FAILED", _("Failed")

    

    order = models.OneToOneField(

        Order,

        on_delete=models.CASCADE,

        related_name='payment'

    )

    method = models.CharField(

        max_length=20,

        choices=Method.choices

    )

    status = models.CharField(

        max_length=20,

        choices=Status.choices,

        default=Status.PENDING

    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    transaction_id = models.CharField(max_length=100, unique=True)

    payment_date = models.DateTimeField(null=True, blank=True)

    

    def __str__(self):

        return f"Payment for Order #{self.order.id}"

```



### order.models.ProductRating



User ratings for purchased products.



```python

class ProductRating(models.Model):

    user = models.ForeignKey(

        User,

        on_delete=models.CASCADE,

        related_name='product_ratings'

    )

    product = models.ForeignKey(

        Product,

        on_delete=models.CASCADE,

        related_name='ratings'

    )

    order_item = models.ForeignKey(

        OrderItem,

        on_delete=models.CASCADE,

        related_name='rating'

    )

    rating = models.IntegerField(

        choices=[(i, str(i)) for i in range(1, 6)]

    )

    review_text = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    

    def __str__(self):

        return f"{self.user.username} rated {self.product.name} {self.rating}*"

    

    class Meta:

        unique_together = ['user', 'product']

```



**Key Features:**

- Links to OrderItem (verifies purchase)

- One rating per user per product

- Signal updates Product.rating aggregate



## Query Optimization Examples



### Prevent N+1 Queries



```python

# Bad: N+1 queries

products = Product.objects.all()

for product in products:

    print(product.product_type.name)  # Query per product!



# Good: Use select_related

products = Product.objects.select_related('product_type')

for product in products:

    print(product.product_type.name)  # No additional queries

```



## Complex Queries with Aggregation



```python

# Get cart totals efficiently

cart = Cart.objects.annotate(

    item_count=Count('items'),

    subtotal=Sum(F('items__quantity') * F('items__product__price'))

).get(user=request.user)



# Get order statistics

orders = Order.objects.aggregate(

    total_orders=Count('id'),

    total_revenue=Sum('total_price'),

    avg_order_value=Avg('total_price')

)

```



## Prefetch Related



```python

# For reverse ForeignKey relationships

orders = Order.objects.prefetch_related(

    'items',

    'items__product',

    'payment'

)

```



## Migration Workflow



### Creating Migrations



```bash

# After model changes

python manage.py makemigrations



# Apply to database

python manage.py migrate



# Check status

python manage.py showmigrations

```



## Common Migration Issues



**Issue**: "No changes detected"

- Solution: Ensure model file was saved

- Check migration directory exists



**Issue**: "Target <app> XXXXX does not exist"

- Solution: Migration file is missing

- Recreate with `makemigrations`



---



**Next**: [API Endpoints](./04-api-endpoints.md)

