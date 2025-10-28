# Getting Started with Becathlon

This guide walks you through setting up the Becathlon project for local development.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git
- Virtual environment (venv or virtualenv)
- Basic Django knowledge

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/pbp-group-k4/becathlon.git
cd becathlon
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
- Django 5.2.5 - Web framework
- Pillow 12.0.0 - Image processing
- psycopg2-binary 2.9.9 - PostgreSQL adapter
- WhiteNoise 6.6.0 - Static file serving
- Gunicorn 21.2.0 - Production server
- dj-database-url 2.1.0 - Database URL parsing

### 4. Database Setup

Initialize the database and apply migrations:

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Load product categories
python seed_product_types.py

# Create superuser for admin access
python manage.py createsuperuser
```

When prompted for superuser credentials, use:
- Username: `admin`
- Email: `admin@example.com`
- Password: Choose a secure password

### 5. Create Test Data (Optional)

```bash
python create_test_user.py
```

This creates:
- Test customer account
- Sample products in each category
- Pre-populated shopping carts

### 6. Run Development Server

```bash
python manage.py runserver
```

The application is now accessible at:
- **Homepage**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Verification Checklist

After setup, verify everything is working:

- [ ] Homepage loads without errors
- [ ] Admin panel accessible with superuser credentials
- [ ] Product categories visible on homepage
- [ ] Cart functionality works (add/remove items)
- [ ] Can add items to cart as guest (no login required)
- [ ] Can login with test user account
- [ ] Checkout flow starts (though mock payment only)

## Database Overview

### Development Database
- **Location**: `db.sqlite3` (SQLite)
- **Reset**: Delete file and re-run migrations (fresh start)

### Production Database
- **Type**: PostgreSQL
- **Connection**: Via `DATABASE_URL` environment variable
- **Format**: `postgres://user:password@host:5432/dbname`

## Environment Variables

Create a `.env` file (not committed) for local overrides:

```bash
# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (optional, defaults to SQLite)
# DATABASE_URL=postgres://user:password@localhost/becathlon

# Static files
STATIC_ROOT=staticfiles
STATIC_URL=/static/
```

Load with `python-dotenv`:
```bash
pip install python-dotenv
```

Then in settings.py:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Project Structure

```
becathlon/
├── apps/
│   ├── main/              # Core homepage & products
│   ├── authentication/    # Login/signup
│   ├── catalog/           # Product browsing & filtering
│   ├── cart/              # Shopping cart
│   ├── order/             # Checkout & orders
│   ├── profiles/          # User profiles
│   ├── stores/            # Store locator
│   └── recommendation/    # Recommendations
├── becathlon/             # Project config
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI config
├── manage.py              # Django management
├── requirements.txt       # Python dependencies
└── db.sqlite3             # Development database
```

## Key Applications

### main
Handles homepage, product display, and basic AJAX operations.
- Models: Product, ProductType, Customer
- Views: Home page, product detail
- AJAX: Get/add/delete products

### catalog
Advanced product browsing with filtering and search.
- Models: ProductImage (extends main.Product)
- Views: Product listings, category filtering
- AJAX: Dynamic filtering, quick views

### cart
Hybrid cart system supporting guests and users.
- Models: Cart, CartItem
- Views: Cart display, add/remove items
- Utilities: Cart creation, guest-to-user migration

### order
Checkout flow and order management.
- Models: Order, OrderItem, ShippingAddress, Payment, ProductRating
- Views: Checkout, confirmation, order history
- Features: Price snapshots, delivery tracking, ratings

### authentication
User registration and login.
- Views: Signup, login, logout
- Forms: Custom registration form
- Integration: Cart merge on login

## Common Commands

### Django CLI

```bash
# Create new app
python manage.py startapp <app_name>

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Interactive shell
python manage.py shell

# Run tests
python manage.py test

# Run specific test
python manage.py test apps.cart.tests

# Collect static files
python manage.py collectstatic --no-input
```

### Debugging

```bash
# Check SQL queries (development only)
python manage.py shell
>>> from django.db import connection
>>> from django.test.utils import CaptureQueriesContext
>>> with CaptureQueriesContext(connection) as ctx:
>>>     products = Product.objects.all()[:5]
>>> print(len(ctx), "queries")

# Django debug toolbar (if installed)
pip install django-debug-toolbar
```

## Troubleshooting

### ModuleNotFoundError: No module named 'apps'

**Problem**: Python can't find the apps package
**Solution**: Check `becathlon/settings.py` line 20:
```python
sys.path.insert(0, str(BASE_DIR / 'apps'))
```

### Migration Conflicts

**Problem**: Migration dependency issues
**Solution**: Reset migrations (dev only):
```bash
python reset_migrations.py
python manage.py makemigrations
python manage.py migrate
```

### Static Files Not Loading

**Problem**: CSS/JS don't load in development
**Solution**: Ensure WhiteNoise is installed:
```bash
pip install whitenoise
```

### Database Locked (SQLite)

**Problem**: "database is locked" error
**Solution**: 
1. Close any other connections to db.sqlite3
2. Restart Django server
3. Or switch to PostgreSQL for development

### CSRF Token Errors

**Problem**: "CSRF token missing" on AJAX
**Solution**: Include CSRF token in request:
```javascript
const token = document.querySelector('[name=csrfmiddlewaretoken]').value;
fetch('/api/cart/add/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': token,
        'X-Requested-With': 'XMLHttpRequest'
    }
});
```

## Next Steps

1. **Explore the Admin Panel**: Add products, manage categories
2. **Read [Architecture Overview](./02-architecture-overview.md)**: Understand app structure
3. **Review [API Endpoints](./04-api-endpoints.md)**: See available routes
4. **Check [Development Guide](./06-development-guide.md)**: Learn workflows

## Resources

- [Django Documentation](https://docs.djangoproject.com/en/5.2/)
- [Django ORM Query Reference](https://docs.djangoproject.com/en/5.2/topics/db/queries/)
- [Django URL Dispatcher](https://docs.djangoproject.com/en/5.2/topics/http/urls/)
- [Django Class-based Views](https://docs.djangoproject.com/en/5.2/topics/class-based-views/)

## Getting Help

- Check `IMPLEMENTATION.md` for feature details
- Review existing tests for usage examples
- Consult `.github/copilot-instructions.md` for conventions
- Open an issue on GitHub for blockers

---

**Next**: [Architecture Overview](./02-architecture-overview.md)
