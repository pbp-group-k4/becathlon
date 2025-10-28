# Becathlon Project Documentation

Welcome to the comprehensive Becathlon project documentation. This documentation covers the complete Django e-commerce platform inspired by Decathlon's UX and functionality.

## Quick Navigation

- **[Getting Started](./docs/01-getting-started.md)** - Setup, installation, and initial configuration
- **[Architecture Overview](./docs/02-architecture-overview.md)** - Project structure and app organization
- **[Database & Models](./docs/03-database-models.md)** - Complete schema, relationships, and ORM patterns
- **[API Endpoints](./docs/04-api-endpoints.md)** - All available routes and AJAX endpoints
- **[Frontend Architecture](./docs/05-frontend-architecture.md)** - CSS, JavaScript, and template system
- **[Development Guide](./docs/06-development-guide.md)** - Common workflows and best practices
- **[Deployment Guide](./docs/07-deployment-guide.md)** - Production setup and configuration

## Project Overview

**Becathlon** is a Django 5.2.5-powered e-commerce storefront that recreates the shopping experience of a multisport retailer. It features:

- Multi-app architecture with clear separation of concerns
- Hybrid cart system (session-based for guests, database-backed for users)
- AJAX-driven interactions for seamless user experience
- Glassmorphic design with modern CSS and vanilla JavaScript
- Real-time delivery tracking simulation
- Product rating system with order history integration
- Mock payment gateway supporting multiple methods

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Django 5.2.5 |
| Database | SQLite (dev), PostgreSQL (prod) |
| Frontend | HTML5, CSS3, Vanilla JS/jQuery |
| Static Files | WhiteNoise |
| Server | Gunicorn |
| Hosting | PWS (Python Web Service) |

## Key Features

### Shopping Experience
- Browse sports equipment across multiple categories
- Advanced product filtering and search
- Quick product previews with modal views
- Shopping cart with quantity management
- Persistent cart for logged-in users
- Checkout with shipping address and payment method selection

### User Management
- Registration and authentication
- User profiles (planned dual-role system)
- Order history and tracking
- Product ratings and reviews
- Personalized recommendations (placeholder)

### Admin Features
- Django admin for product management
- Stock tracking and inventory
- Order management and status updates
- User account administration

## Core Concepts

### Hybrid Cart System
- **Guest Carts**: Session-based, temporary storage in database
- **User Carts**: Persistent, linked to user account
- **Merge on Login**: Guest cart automatically merged when user logs in

### Price Snapshots
When an order is created, product prices are captured at that moment in `OrderItem.price`. This preserves historical pricing even if product prices change later.

### Delivery Tracking
Orders simulate realistic delivery phases:
1. **PROCESSING** (0-30 seconds)
2. **EN_ROUTE** (30-120 seconds)
3. **DELIVERED** (120+ seconds)

### Rating System
- Only users who purchased a product can rate it
- Ratings linked to `OrderItem` to verify purchase
- Product `rating` field updated with aggregated average

## Directory Structure

```
becathlon/
├── apps/                           # Django apps
│   ├── main/                       # Homepage, products
│   ├── authentication/             # Login/signup
│   ├── catalog/                    # Product browsing
│   ├── cart/                       # Shopping cart
│   ├── order/                      # Checkout, orders
│   ├── profiles/                   # User profiles (planned)
│   ├── recommendation/             # Recommendations (placeholder)
│   └── stores/                     # Store locator (planned)
├── becathlon/                      # Project settings
├── docs/                           # This documentation
├── staticfiles/                    # Collected static files
├── manage.py                       # Django CLI
├── requirements.txt                # Python dependencies
└── db.sqlite3                      # Development database
```

## Getting Help

### Documentation Files
Each section of documentation includes practical examples and common patterns.

### Common Issues
Refer to the [Development Guide](./docs/06-development-guide.md#common-pitfalls) for solutions to frequent problems.

### Code Examples
Throughout the documentation, code examples show Django patterns and AJAX implementations.

## Contributing

When modifying this documentation:
1. Update relevant `.md` file in the `docs/` directory
2. Follow the existing structure and formatting
3. Include code examples where appropriate
4. Keep descriptions clear and accessible

## Latest Updates

- **Project Status**: Active development
- **Test Coverage**: Comprehensive across all apps
- **Documentation**: Continuously updated
- **Production Deployment**: Live at pbp.cs.ui.ac.id

---

**Last Updated**: October 2025
**Django Version**: 5.2.5
**Documentation Version**: 1.0
