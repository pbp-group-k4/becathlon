# Development Guide & Best Practices

Common workflows, patterns, and solutions for developing Becathlon.

## Setting Up Your Development Environment

### Initial Clone & Setup

```bash
# Clone repository
git clone https://github.com/pbp-group-k4/becathlon.git
cd becathlon

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py makemigrations
python manage.py migrate
python seed_product_types.py
python manage.py createsuperuser
```

### Running Development Server

```bash
python manage.py runserver
# Visit http://127.0.0.1:8000/
```

## Common Development Tasks

### Adding a New Product

```python
from apps.main.models import Product, ProductType
from apps.catalog.models import ProductImage

# Create product
product = Product.objects.create(
    name="Running Shoes Pro",
    description="High-performance running shoes",
    price=129.99,
    product_type=ProductType.objects.get(name="Running"),
    stock=50,
    brand="Nike",
    created_by=request.user
)

# Add images
ProductImage.objects.create(
    product=product,
    image_url="https://example.com/shoe1.jpg",
    is_primary=True,
    alt_text="Running shoe side view"
)
```

### Checking Cart State

```python
from apps.cart.utils import get_or_create_cart

cart = get_or_create_cart(request)
print(f"Items: {cart.get_total_items()}")
print(f"Subtotal: ${cart.get_subtotal()}")
print(f"Distinct products: {cart.get_item_count()}")

# View cart contents
for item in cart.items.all():
    print(f"{item.product.name}: {item.quantity} x ${item.product.price}")
```

### Creating an Order Programmatically

```python
from apps.order.models import Order, ShippingAddress
from apps.cart.utils import get_or_create_cart

# Get user's cart
cart = get_or_create_cart(request)

# Create shipping address
address = ShippingAddress.objects.create(
    user=request.user,
    full_name="John Doe",
    phone_number="08123456789",
    address="123 Main St",
    postal_code="12345",
    city="Jakarta"
)

# Convert cart to order
try:
    order = Order.create_from_cart(cart, address)
    print(f"Order created: #{order.id}")
except ValueError as e:
    print(f"Error: {e}")  # Stock insufficient
```

### Querying Products Efficiently

```python
from django.db.models import Prefetch, Avg
from apps.catalog.models import ProductImage

# Good: Avoids N+1 queries
products = Product.objects.select_related(
    'product_type',
    'created_by'
).prefetch_related(
    Prefetch(
        'images',
        queryset=ProductImage.objects.filter(is_primary=True)
    ),
    'ratings'
)

# With aggregation
products = products.annotate(
    avg_rating=Avg('ratings__rating')
)

for product in products:
    print(f"{product.name}: {product.avg_rating}*")
```

## Code Patterns & Conventions

### Model Methods Pattern

```python
class Cart(models.Model):
    # Calculation methods
    def get_total_items(self):
        """Return sum of all quantities"""
        return self.items.aggregate(
            total=Sum('quantity')
        )['total'] or 0
    
    # Utility methods
    def clear(self):
        """Remove all items"""
        self.items.all().delete()
    
    # Factory methods
    @classmethod
    def create_from_user(cls, user):
        return cls.objects.create(user=user)
    
    def __str__(self):
        return f"Cart for {self.user.username if self.user else 'guest'}"
```

### View Pattern (Function-Based)

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            return JsonResponse({
                'success': False,
                'error': 'Invalid quantity'
            }, status=400)
        
        cart = get_or_create_cart(request)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            item.quantity += quantity
            item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Added {product.name} to cart',
            'cart_count': cart.get_item_count()
        })
    
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

### Atomic Transaction Pattern

```python
from django.db import transaction
from django.db.models import F

@transaction.atomic
def process_checkout(cart, shipping_address):
    order = Order.objects.create(
        user=cart.user,
        shipping_address=shipping_address
    )
    
    for item in cart.items.select_related('product'):
        product = Product.objects.select_for_update().get(
            pk=item.product.pk
        )
        
        if product.stock < item.quantity:
            raise ValueError(f"Insufficient stock for {product.name}")
        
        # Atomic decrement
        product.stock = F('stock') - item.quantity
        product.save(update_fields=['stock'])
        
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price  # Snapshot
        )
    
    order.calculate_total()
    cart.clear()
    return order
```

## Testing Patterns

### Model Tests

```python
from django.test import TestCase
from apps.main.models import Product, ProductType

class ProductTestCase(TestCase):
    def setUp(self):
        self.category = ProductType.objects.create(
            name="Running",
            description="Running shoes"
        )
        self.product = Product.objects.create(
            name="Test Shoe",
            description="Test",
            price=99.99,
            product_type=self.category,
            stock=10,
            created_by=User.objects.create_user('testuser')
        )
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Shoe")
        self.assertEqual(self.product.stock, 10)
    
    def test_product_string(self):
        expected = "Test Shoe - Running"
        self.assertEqual(str(self.product), expected)
```

### View Tests

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User

class CartViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.product = self.create_product()
    
    def test_add_to_cart_success(self):
        response = self.client.post(
            f'/cart/add/{self.product.id}/',
            {'quantity': 1}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
    
    def test_cart_view_requires_auth(self):
        response = self.client.get('/cart/')
        self.assertEqual(response.status_code, 200)  # Works for guests
```

## Debugging Tips

### Django Debug Toolbar

```bash
pip install django-debug-toolbar
```

Add to `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']
```

### Query Logging

```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    products = Product.objects.all()[:5]

print(f"{len(ctx)} queries executed")
for query in ctx:
    print(query['sql'])
```

### Browser Console Debugging

```javascript
// Check cart state
fetch('/cart/api/summary/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCSRFToken(),
    }
}).then(r => r.json()).then(console.log);

// Test AJAX endpoint
fetch('/api/products/', {
    method: 'POST',
    body: new URLSearchParams({page: 1}),
    headers: {'X-CSRFToken': getCSRFToken()}
}).then(r => r.json()).then(console.log);
```

## Common Pitfalls & Solutions

### Issue: ModuleNotFoundError for 'apps.*'

**Cause**: `sys.path` not configured correctly

**Solution**: Check `becathlon/settings.py` line 20:
```python
sys.path.insert(0, str(BASE_DIR / 'apps'))
```

### Issue: Cart not persisting after login

**Cause**: Guest cart not merged to user cart

**Solution**: Ensure `transfer_guest_cart_to_user()` is called after login:
```python
# In authentication/views.py
if form.is_valid():
    user = form.save()
    login(request, user)
    transfer_guest_cart_to_user(request)  # Add this
    return redirect('home')
```

### Issue: CSRF token errors on AJAX

**Cause**: Token not included in request

**Solution**: Include token in headers:
```javascript
fetch(url, {
    method: 'POST',
    headers: {
        'X-CSRFToken': getCSRFToken(),
    },
});
```

### Issue: N+1 query problem

**Cause**: Missing `select_related()` or `prefetch_related()`

**Solution**: Use proper query optimization:
```python
# Bad: N+1 queries
for product in Product.objects.all():
    print(product.product_type.name)

# Good: Single query
for product in Product.objects.select_related('product_type'):
    print(product.product_type.name)
```

### Issue: Database locked (SQLite)

**Cause**: Multiple connections to db.sqlite3

**Solution**: 
1. Close other connections
2. Restart Django server
3. Consider using PostgreSQL for development

## Performance Optimization Tips

1. **Database**: Use `select_related()`, `prefetch_related()`, and aggregation
2. **Caching**: Cache expensive queries with `@cache_page` decorator
3. **Images**: Use lazy loading and responsive images
4. **Frontend**: Debounce search, minimize AJAX calls
5. **Static Files**: WhiteNoise compression in production
6. **ORM**: Use F() expressions for atomic operations

## Git Workflow

### Creating Feature Branch

```bash
git checkout -b feature/cart-improvements
```

### Before Committing

```bash
# Run tests
python manage.py test

# Format code (if configured)
black .
isort . --profile=black

# Check for issues
flake8 .
```

### Committing Changes

```bash
git add .
git commit -m "feat: add cart quantity validation"
git push origin feature/cart-improvements
```

---

**Next**: [Deployment Guide](./07-deployment-guide.md)
