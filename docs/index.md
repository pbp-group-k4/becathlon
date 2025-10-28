---
layout: default
title: Becathlon Documentation
permalink: /
---

# Becathlon Project Documentation

Welcome to the **Becathlon** documentation. This is your complete guide to the Django 5.2.5 e-commerce platform that recreates the shopping experience of a multisport retailer.

## 📚 Documentation Guides

Start with these guides to understand and work with Becathlon:

| Guide | Description |
|-------|-------------|
| **[1. Getting Started](01-getting-started.md)** | Setup, installation, and first run |
| **[2. Architecture Overview](02-architecture-overview.md)** | Project structure and app organization |
| **[3. Database & Models](03-database-models.md)** | Complete data schema reference |
| **[4. API Endpoints](04-api-endpoints.md)** | All HTTP routes and endpoints |
| **[5. Frontend Architecture](05-frontend-architecture.md)** | CSS, JavaScript, and templates |
| **[6. Development Guide](06-development-guide.md)** | Common workflows and patterns |
| **[7. Deployment Guide](07-deployment-guide.md)** | Production setup and deployment |

## 🚀 Quick Start

Get up and running in 5 minutes:

```bash
# Clone the repository
git clone https://github.com/pbp-group-k4/becathlon.git
cd becathlon

# Setup virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Initialize database
python manage.py migrate
python seed_product_types.py
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Visit http://127.0.0.1:8000/
```

## 💻 Tech Stack

- **Backend**: Django 5.2.5
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Static Files**: WhiteNoise
- **Server**: Gunicorn

## 🎯 Key Features

- ✅ **Multi-app Architecture** - Clean separation of concerns
- ✅ **Hybrid Cart System** - Session-based for guests, persistent for users
- ✅ **AJAX Interactions** - Real-time product updates
- ✅ **Glassmorphic Design** - Modern dark theme with backdrop filters
- ✅ **Price Snapshots** - Historical pricing in orders
- ✅ **Rating System** - User reviews linked to purchases
- ✅ **Mock Payment Gateway** - Production-quality checkout experience
- ✅ **Delivery Tracking** - Real-time order status simulation

## 📊 Project Statistics

| Metric | Count |
|--------|-------|
| Django Apps | 8 |
| Models | 12+ |
| API Endpoints | 40+ |
| CSS Lines | 1,179+ |
| JavaScript Lines | 1,000+ |
| Test Coverage | Comprehensive |

## 🗂️ Project Structure

```
becathlon/
├── apps/                    # Django applications
│   ├── main/               # Homepage & core products
│   ├── authentication/     # User login/signup
│   ├── catalog/            # Product browsing & filtering
│   ├── cart/               # Shopping cart system
│   ├── order/              # Checkout & order management
│   ├── profiles/           # User profile management
│   ├── stores/             # Store locator
│   └── recommendation/     # Product recommendations
├── becathlon/              # Project configuration
├── docs/                   # Documentation (you are here!)
├── manage.py               # Django command-line tool
├── requirements.txt        # Python dependencies
└── db.sqlite3              # Development database
```

## 📖 How to Use This Documentation

1. **New to Becathlon?** Start with [Getting Started](01-getting-started.md)
2. **Understanding the system?** Read [Architecture Overview](02-architecture-overview.md)
3. **Working with models?** Check [Database & Models](03-database-models.md)
4. **Building APIs?** See [API Endpoints](04-api-endpoints.md)
5. **Frontend work?** Review [Frontend Architecture](05-frontend-architecture.md)
6. **Writing code?** Consult [Development Guide](06-development-guide.md)
7. **Deploying?** Follow [Deployment Guide](07-deployment-guide.md)

## 🔍 Common Questions

### Where do I start?
→ Read [Getting Started](01-getting-started.md)

### How is the cart system organized?
→ See the "Hybrid Cart System" section in [Architecture Overview](02-architecture-overview.md)

### What models exist?
→ Complete reference in [Database & Models](03-database-models.md)

### How do I add a new feature?
→ Follow patterns in [Development Guide](06-development-guide.md)

### Where are the API routes?
→ Full listing in [API Endpoints](04-api-endpoints.md)

## 👥 Team

- Muhammad Adra Prakoso
- Berguegou Briana Yadjam
- Zahran Musyaffa Ramadhan Mulya
- Gunata Prajna Putra Sakri
- Muhammad Vegard Fathul Islam
- Kent Wilbert Wijaya

## 📝 License

Internally developed for educational purposes.

---

**Last Updated**: October 28, 2025

**Status**: ✅ Production Ready

[View on GitHub](https://github.com/pbp-group-k4/becathlon/tree/docs/comprehensive-documentation)
