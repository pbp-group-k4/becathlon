# Development Guide

Best practices, workflows, and common tasks for developing Becathlon.

## Development Workflow

### Setting Up Your Environment

1. **Clone and activate virtual environment** (see Getting Started)
2. **Create `.env` file** for local configuration:
   ```
   DEBUG=True
   SECRET_KEY=development-key-change-in-production
   ALLOWED_HOSTS=localhost,127.0.0.1,testserver
   ```

3. **Run migrations and seed data**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python seed_product_types.py
   python manage.py createsuperuser
   ```

4. **Start development server**:
   ```bash
   python manage.py runserver
   ```

5. **Access**:
   - Homepage: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Common Development Tasks

### Adding a New Product

**Via Admin Panel:**
1. Navigate to http://127.0.0.1:8000/admin/
2. Click "Products" under Main app
3. Click "Add Product"
4. Fill in fields: name, description, price, category, stock
5. Save

**Via Django Shell:**
```bash
python manage.py shell
```

```python
from apps.main.models import Product, ProductType

# Create product
product = Product.objects.create(
    name="Trail Running Shoes",
    description="Perfect for off-road running",
    price=149.99,
    product_type=ProductType.objects.get(name="Running"),
    stock=50,
    brand="Nike",
    created_by=User.objects.get(username="admin")
)

# Add image
from apps.catalog.models import ProductImage

image = ProductImage.objects.create(
    product=product,
    image_url="https://example.com/shoe.jpg",
    is_primary=True,
    alt_text="Trail running shoe"
)

print(f"Created {product.name} with ID {product.id}")
```

### Testing Cart Functionality

```bash
python manage.py shell
```

```python
from apps.cart.utils import get_or_create_cart
from apps.main.models import Product
from django.test import RequestFactory

# Create mock request
factory = RequestFactory()
request = factory.get('/')
request.session = {}
request.user = None  # Guest user

# Test guest cart
cart = get_or_create_cart(request)
print(f"Guest cart: {cart}")
print(f"Items: {cart.get_total_items()}")

# Add product
product = Product.objects.first()
cart_item = cart.items.create(product=product, quantity=2)
print(f"Added {cart_item.quantity} x {product.name}")
print(f"Subtotal: ${cart.get_subtotal()}")
```

### Creating Test Data

```bash
python create_test_user.py
```

This creates:
- Test user: `testuser` / `password`
- Sample products across categories
- Pre-populated cart with items

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.cart

# Run specific test class
python manage.py test apps.order.tests.TestOrder

# Run with verbosity
python manage.py test --verbosity=2

# Run with coverage (if installed)
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Testing AJAX Endpoints

Use browser developer tools or curl:

```bash
# Get CSRF token from cookies
CSRF_TOKEN=$(curl -s -c /tmp/cookies.txt http://127.0.0.1:8000/ | grep -oP 'csrftoken=\K[^;]+')

# Test add to cart
curl -X POST http://127.0.0.1:8000/cart/add/1/ \
  -H "X-CSRFToken: $CSRF_TOKEN" \
  -H "Cookie: csrftoken=$CSRF_TOKEN" \
  -d "quantity=1" \
  -H "X-Requested-With: XMLHttpRequest"
```

Or use browser console:

```javascript
// Get CSRF token
const token = document.querySelector('[name=csrfmiddlewaretoken]').value;

// Test add to cart
fetch('/cart/add/1/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': token,
        'X-Requested-With': 'XMLHttpRequest'
    },
    body: new FormData(document.querySelector('form'))
})
.then(r => r.json())
.then(data => console.log(data));
```

## Code Patterns & Conventions

### Model Relationships

**Always use descriptive `related_name`:**
```python
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'  # ✓ Good
    )
    
    # Bad: relies on default 'cartitem_set'
    # cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
```

**Query with related_name:**
```python
# Use descriptive name
cart.items.all()  # ✓ Clear

# Avoid magic
cart.cartitem_set.all()  # ✗ Obscure
```

### Query Optimization

**Always use select_related for ForeignKey:**
```python
# ✓ Good: One query
items = CartItem.objects.select_related('product', 'cart')

# ✗ Bad: N queries (one per item)
items = CartItem.objects.all()
for item in items:
    print(item.product.name)  # Triggers query
```

**Always use prefetch_related for reverse relationships:**
```python
# ✓ Good
orders = Order.objects.prefetch_related('items', 'items__product')

# ✗ Bad: N queries
orders = Order.objects.all()
for order in orders:
    for item in order.items.all():  # Triggers query per order
        print(item.product.name)
```

### View Patterns

**Always check permissions:**
```python
@login_required  # ✓ Protect view
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders.html', {'orders': orders})
```

**Always use get_object_or_404:**
```python
# ✓ Good: Returns 404 automatically
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

# ✗ Bad: Manual error handling
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return HttpResponse("Not found", status=404)
```

### AJAX Endpoints

**Always return JSON with standard format:**
```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    try:
        cart = get_or_create_cart(request)
        product = get_object_or_404(Product, id=product_id)
        
        item, created = cart.items.get_or_create(
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            item.quantity += 1
            item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Added to cart',
            'cart_count': cart.get_item_count()
        })
    
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
```

## Debugging Techniques

### Print Debugging

```python
# In views.py
def some_view(request):
    cart = get_or_create_cart(request)
    print(f"DEBUG: Cart ID = {cart.id}")
    print(f"DEBUG: Cart items = {cart.items.count()}")
    print(f"DEBUG: Cart total = ${cart.get_subtotal()}")
```

### Django Shell

```bash
python manage.py shell
```

```python
from apps.cart.models import Cart
from django.db import connection
from django.test.utils import CaptureQueriesContext

# Monitor queries
with CaptureQueriesContext(connection) as ctx:
    carts = Cart.objects.select_related('user')
    for cart in carts:
        print(cart.user.username)

print(f"Total queries: {len(ctx)}")
for query in ctx:
    print(query['sql'])
```

### Debug Toolbar (if installed)

```bash
pip install django-debug-toolbar
```

Add to `settings.py`:
```python
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']
```

Add to `urls.py`:
```python
if settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def checkout(request):
    logger.info(f"Checkout started for user {request.user}")
    
    try:
        # Process checkout
        logger.info(f"Order created: #{order.id}")
    except Exception as e:
        logger.error(f"Checkout failed: {str(e)}")
        raise
```

## Git Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/add-wishlist
# or
git checkout -b fix/cart-bug
# or
git checkout -b docs/update-readme
```

### Before Committing

```bash
# Run tests
python manage.py test

# Check code style
python -m flake8 apps/  # if linting configured

# Check migrations
python manage.py showmigrations

# Verify no secrets committed
grep -r "SECRET_KEY\|PASSWORD" apps/ --exclude-dir=migrations
```

### Committing Changes

```bash
# Stage changes
git add apps/cart/models.py apps/cart/tests.py

# Commit with clear message
git commit -m "feat: add cart item quantity validation

- Prevent adding more items than available stock
- Show error message to user
- Add unit tests for validation logic

Fixes #123"

# Push to remote
git push origin feature/add-wishlist
```

### Commit Message Format

**Format:** `<type>: <subject>`

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `refactor:` Code restructuring
- `test:` Test additions/fixes
- `perf:` Performance improvement
- `ci:` CI/CD changes
- `chore:` Build process, dependencies

**Examples:**
```
feat: implement product rating system
fix: prevent double-charging on checkout
docs: update API documentation
refactor: optimize cart queries
test: add test for delivery status calculation
perf: cache product images
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'apps'"

**Cause:** Python path not configured

**Solution:**
```python
# Check settings.py
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'apps'))  # ✓ Must be here
```

---

### Issue: Cart not persisting for logged-in users

**Cause:** Guest cart not transferred to user

**Solution:**
```python
# In authentication/views.py after successful login
from apps.cart.utils import transfer_guest_cart_to_user

def login_view(request):
    # ... login logic ...
    if user is not None:
        auth.login(request, user)
        transfer_guest_cart_to_user(request)  # ✓ Don't forget
        return redirect('/')
```

---

### Issue: "CSRF token missing" in AJAX

**Cause:** CSRF token not included in request

**Solution:**
```javascript
// Include in FormData
const formData = new FormData();
formData.append('quantity', 1);
formData.append('csrfmiddlewaretoken', 
    document.querySelector('[name=csrfmiddlewaretoken]').value);

fetch('/cart/add/1/', {
    method: 'POST',
    body: formData
});
```

---

### Issue: N+1 query problem (slow pages)

**Cause:** Missing select_related/prefetch_related

**Solution:**
```python
# Bad: 101 queries (1 main + 100 per item)
items = CartItem.objects.all()

# Good: 2 queries (1 main + 1 for related)
items = CartItem.objects.select_related('product', 'cart')
```

---

### Issue: "IntegrityError: UNIQUE constraint failed"

**Cause:** Trying to create duplicate cart/item

**Solution:**
```python
# ✓ Use get_or_create instead of create
cart_item, created = cart.items.get_or_create(
    product=product,
    defaults={'quantity': 1}
)

if not created:
    cart_item.quantity += 1
    cart_item.save()
```

---

### Issue: Product stock goes negative

**Cause:** No stock validation or race condition

**Solution:**
```python
# Use atomic transactions with select_for_update
from django.db import transaction

with transaction.atomic():
    product = Product.objects.select_for_update().get(id=product_id)
    
    if product.stock < quantity:
        raise ValueError("Insufficient stock")
    
    product.stock -= quantity
    product.save()
```

## Performance Tips

1. **Cache expensive queries:**
   ```python
   from django.core.cache import cache
   
   def get_featured_products():
       key = 'featured_products'
       products = cache.get(key)
       if products is None:
           products = Product.objects.all()[:12]
           cache.set(key, products, 3600)  # Cache for 1 hour
       return products
   ```

2. **Use select_related/prefetch_related:**
   ```python
   products = Product.objects.select_related(
       'product_type', 'created_by'
   ).prefetch_related('images')
   ```

3. **Use pagination for large lists:**
   ```python
   from django.core.paginator import Paginator
   
   paginator = Paginator(products, 20)  # 20 per page
   page_obj = paginator.get_page(request.GET.get('page'))
   ```

4. **Defer heavy fields:**
   ```python
   products = Product.objects.defer('description')  # Load later
   products = Product.objects.only('id', 'name', 'price')  # Load specific
   ```

5. **Use bulk operations:**
   ```python
   # Bad: 100 queries
   for product in products:
       product.stock -= 1
       product.save()
   
   # Good: 1 query
   Product.objects.bulk_update(products, ['stock'])
   ```

---

**Next**: [Deployment Guide](./07-deployment-guide.md)
