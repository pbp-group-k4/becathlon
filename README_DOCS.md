# Becathlon Project Documentation

## Quick Links

Start here if you're new to Becathlon:

1. **[Getting Started](./docs/01-getting-started.md)** - Setup and installation
2. **[Architecture Overview](./docs/02-architecture-overview.md)** - Project structure
3. **[Database & Models](./docs/03-database-models.md)** - Data schema
4. **[API Endpoints](./docs/04-api-endpoints.md)** - All HTTP routes
5. **[Frontend Architecture](./docs/05-frontend-architecture.md)** - CSS, JS, templates
6. **[Development Guide](./docs/06-development-guide.md)** - Common workflows
7. **[Deployment Guide](./docs/07-deployment-guide.md)** - Production setup

## About Becathlon

Becathlon is a Django 5.2.5-powered e-commerce platform that recreates the shopping experience of a multisport retailer. It features a hybrid cart system, AJAX-driven interactions, and a modern glassmorphic design.

### Tech Stack
- **Backend**: Django 5.2.5
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Static Files**: WhiteNoise
- **Server**: Gunicorn

### Key Features
- Multi-app architecture with clear separation of concerns
- Hybrid cart system (session-based for guests, database-backed for users)
- Real-time delivery tracking simulation
- Product rating system
- Mock payment gateway
- AJAX-driven product interactions
- Glassmorphic design with dark theme

## Project Statistics

| Metric | Value |
|--------|-------|
| **Total Endpoints** | 40+ |
| **Django Apps** | 8 (main, auth, catalog, cart, order, profiles, stores, recommendation) |
| **Models** | 12+ |
| **Test Coverage** | Comprehensive |
| **Lines of CSS** | 1,179+ (catalog.css) |
| **Lines of JavaScript** | 1,000+ |

## Core Concepts

### Hybrid Cart System
- **Guest Carts**: Session-based, temporary
- **User Carts**: Persistent, account-linked
- **Merge on Login**: Automatically combines guest cart to user cart

### Price Snapshots
When orders are created, product prices are captured in `OrderItem.price` to preserve historical pricing even if product prices change later.

### Delivery Tracking
Orders simulate realistic delivery phases:
1. **PROCESSING** (0-30 seconds)
2. **EN_ROUTE** (30-120 seconds)
3. **DELIVERED** (120+ seconds)

### Rating System
Only users who purchased a product can rate it. Ratings are linked to `OrderItem` to verify purchase history.

## Development Workflow

### Quick Start
```bash
# Clone
git clone https://github.com/pbp-group-k4/becathlon.git
cd becathlon

# Setup
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python seed_product_types.py
python manage.py createsuperuser

# Run
python manage.py runserver
# Visit http://127.0.0.1:8000/
```

### Testing
```bash
python manage.py test
python manage.py test apps.cart  # Specific app
```

### Database
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py shell
```

## Project Structure

```
becathlon/
├── apps/                    # Django apps
│   ├── main/               # Homepage & products
│   ├── authentication/     # Login/signup
│   ├── catalog/            # Product browsing
│   ├── cart/               # Shopping cart
│   ├── order/              # Checkout & orders
│   ├── profiles/           # User profiles
│   ├── stores/             # Store locator
│   └── recommendation/     # Recommendations
├── becathlon/              # Project settings
├── docs/                   # This documentation
├── manage.py               # Django CLI
├── requirements.txt        # Dependencies
└── db.sqlite3              # Dev database
```

## Common Tasks

### Adding a Product
See [Development Guide](./docs/06-development-guide.md#adding-a-new-product)

### Creating an Order
See [Development Guide](./docs/06-development-guide.md#creating-an-order-programmatically)

### Querying Products Efficiently
See [Development Guide](./docs/06-development-guide.md#querying-products-efficiently)

### Debugging Issues
See [Development Guide](./docs/06-development-guide.md#common-pitfalls--solutions)

## Resources

### Django Documentation
- [Django 5.2 Docs](https://docs.djangoproject.com/en/5.2/)
- [Django ORM Reference](https://docs.djangoproject.com/en/5.2/topics/db/queries/)
- [Django Class-based Views](https://docs.djangoproject.com/en/5.2/topics/class-based-views/)

### Frontend
- [MDN Web Docs](https://developer.mozilla.org/)
- [CSS Tricks](https://css-tricks.com/)
- [JavaScript.info](https://javascript.info/)

## Getting Help

- Check the [Development Guide](./docs/06-development-guide.md) for common issues
- Review [API Endpoints](./docs/04-api-endpoints.md) for routing questions
- See [Database Models](./docs/03-database-models.md) for schema questions

## Team

- Muhammad Adra Prakoso
- Berguegou Briana Yadjam
- Zahran Musyaffa Ramadhan Mulya
- Gunata Prajna Putra Sakri
- Muhammad Vegard Fathul Islam
- Kent Wilbert Wijaya

## License

Internally developed for educational purposes.

## Last Updated

**October 28, 2025** - Complete documentation suite published to GitHub Pages

---

Navigate to the [Getting Started](./docs/01-getting-started.md) guide to begin development.
