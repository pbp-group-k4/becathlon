# Architecture Overview



This document provides a comprehensive view of Becathlon's project structure, app organization, and data flow.



## Project Philosophy



Becathlon follows Django's "batteries included" philosophy with a multi-app architecture where each app has a specific responsibility:



- **Cohesion**: Each app contains models, views, templates, and tests related to a specific feature

- **Modularity**: Apps can be developed and tested independently

- **Reusability**: App structure allows for easy integration in other Django projects

- **Maintainability**: Clear separation of concerns makes code easier to understand and modify



## App Directory Structure



```

apps/

├── main/                    # Core product & homepage

│   ├── admin.py             # Django admin configuration

│   ├── apps.py              # App configuration

│   ├── models.py            # Product, ProductType, Customer

│   ├── views.py             # Home, product detail, AJAX endpoints

│   ├── urls.py              # URL routing

│   ├── tests.py             # Test suite

│   ├── migrations/          # Database migrations

│   ├── templates/main/      # HTML templates

│   └── static/main/         # CSS, JS, images

│

├── authentication/          # User registration & login

│   ├── forms.py             # Custom sign-up form

│   ├── models.py            # Extensions to User model

│   ├── views.py             # Sign up, login, logout

│   ├── urls.py              # Auth URL routes

│   └── templates/auth/      # Auth pages

│

├── catalog/                 # Product browsing & filtering

│   ├── models.py            # ProductImage model

│   ├── views.py             # Product listing, filtering

│   ├── urls.py              # Catalog routes

│   ├── forms.py             # Filter forms

│   ├── templatetags/        # Custom template tags

│   ├── static/catalog/      # Modern CSS & JS

│   └── templates/catalog/   # Product pages

│

├── cart/                    # Shopping cart

│   ├── models.py            # Cart, CartItem

│   ├── views.py             # Cart operations

│   ├── utils.py             # Helper functions

│   ├── context_processors.py # Global context

│   ├── urls.py              # Cart routes

│   └── templates/cart/      # Cart template

│

├── order/                   # Orders & checkout

│   ├── models.py            # Order, OrderItem, Payment

│   ├── views.py             # Checkout, confirmation

│   ├── forms.py             # Shipping, payment forms

│   ├── urls.py              # Order routes

│   ├── templates/order/     # Checkout pages

│   └── tests/               # Dedicated test directory

│

├── profiles/                # User profiles (planned)

│   ├── models.py            # User profile extensions

│   ├── views.py             # Profile views

│   └── templates/profiles/  # Profile pages

│

├── stores/                  # Store locator (planned)

│   ├── models.py            # Store locations

│   ├── views.py             # Store finder

│   ├── fixtures/            # Pre-loaded store data

│   └── templates/stores/    # Store pages

│

└── recommendation/          # Recommendations (placeholder)

    ├── models.py            # Recommendation logic

    ├── views.py             # Recommendation views

    └── templates/           # Recommendation templates

```



## Django Settings Configuration



### Path Configuration (`becathlon/settings.py`)



```python

import sys

from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent



# Critical: Add apps to Python path

sys.path.insert(0, str(BASE_DIR / 'apps'))

```



This allows imports like:

```python

from apps.main.models import Product

from apps.cart.utils import get_or_create_cart

```



## Installed Apps Order



Apps are listed in dependency order (dependencies flow downward):



```python

INSTALLED_APPS = [

    # Django built-ins

    'django.contrib.admin',

    'django.contrib.auth',

    'django.contrib.contenttypes',

    'django.contrib.sessions',

    'django.contrib.messages',

    'django.contrib.staticfiles',

    

    # Project apps (order matters!)

    'apps.main.apps.MainConfig',              # Base models

    'apps.authentication.apps.AuthenticationConfig',

    'apps.catalog.apps.CatalogConfig',        # Extends main

    'apps.cart.apps.CartConfig',              # Uses main + auth

    'apps.profiles.apps.ProfilesConfig',      # User extensions

    'apps.stores.apps.StoresConfig',          # Standalone

    'apps.recommendation.apps.RecommendationConfig',

    'apps.order.apps.OrderConfig',            # Uses cart + main

]

```



### Context Processors



Global context available in all templates:



```python

TEMPLATES = [

    {

        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'CONTEXT_PROCESSORS': [

            'django.template.context_processors.debug',

            'django.template.context_processors.request',

            'django.contrib.auth.context_processors.auth',

            'apps.cart.context_processors.cart_context',  # Global cart

        ],

    },

]

```



The cart context processor adds:

- `cart`: Cart object (guest or user)

- `cart_item_count`: Total items in cart



## Data Flow Architecture



```

┌─────────────────────────────────────┐

│     User Authentication             │

│  (apps.authentication)              │

└──────────────┬──────────────────────┘

               │

        ┌──────▼──────┐

        │  User/Guest │

        └──────┬──────┘

               │

    ┌──────────┴──────────┐

    │                     │

┌───▼────────┐    ┌──────▼──────┐

│  Homepage  │    │   Catalog   │

│ (main app) │    │ (catalog)   │

└───┬────────┘    └──────┬──────┘

    │                    │

    └──────────┬─────────┘

               │

        ┌──────▼──────┐

        │   Products  │

        │ (main.models)│

        └──────┬──────┘

               │

        ┌──────▼────────────┐

        │  Product Images   │

        │(catalog.models)   │

        └──────┬────────────┘

               │

        ┌──────▼──────────────────┐

        │   Add to Cart AJAX      │

        │  (cart app)             │

        └──────┬──────────────────┘

               │

        ┌──────▼──────────┐

        │ Shopping Cart   │

        │ (session/DB)    │

        └──────┬──────────┘

               │

        ┌──────▼──────────┐

        │  Cart Display   │

        │ (cart app)      │

        └──────┬──────────┘

               │

        ┌──────▼─────────────┐

        │  Checkout AJAX     │

        │  (order app)       │

        └──────┬─────────────┘

               │

        ┌──────▼─────────────────────┐

        │  Order Creation             │

        │  - Create Order record      │

        │  - Create OrderItems        │

        │  - Capture prices           │

        │  - Decrement stock          │

        │  - Create Payment mock      │

        └──────┬─────────────────────┘

               │

        ┌──────▼──────────┐

        │ Order History   │

        │ (order app)     │

        └──────┬──────────┘

               │

        ┌──────▼──────────┐

        │  Ratings        │

        │  (order models) │

        └─────────────────┘

```



## Request/Response Cycle



### Page Request Flow



```

1. User Request

   ↓

2. Django URL Router (urls.py)

   ↓

3. App View (views.py)

   ├─ Query Database

   ├─ Apply Business Logic

   └─ Pass Context to Template

   ↓

4. Template Rendering

   ├─ Inherit Base Template

   ├─ Include App-Specific HTML

   └─ Inject Context Variables

   ↓

5. Response to Browser

   ├─ HTML Content

   ├─ CSS Links

   └─ JavaScript

```



### AJAX Request Flow



```

1. JavaScript Event (click, submit)

   ↓

2. Fetch/XMLHttpRequest to API Endpoint

   ├─ POST method

   ├─ CSRF token included

   └─ JSON/FormData payload

   ↓

3. Django View

   ├─ Validate CSRF

   ├─ Query Database

   ├─ Execute Business Logic

   └─ Return JSON Response

   ↓

4. JavaScript Handler

   ├─ Parse JSON Response

   ├─ Update DOM elements

   └─ Show user feedback

```



## App Dependencies



### Dependency Graph



```

django.contrib (built-in)

    ↓

main

    ├─ authentication

    ├─ catalog (extends via ProductImage)

    ├─ cart (uses Product)

    ├─ profiles

    └─ order (uses Product + Cart)



authentication

    └─ profiles

    └─ cart (user reference)



catalog

    ├─ cart (shows product images)

    └─ order (product listings)



cart

    └─ order (converts to)



order

    ├─ cart (creates from)

    ├─ main (products)

    └─ authentication (user orders)



recommendation

    ├─ main (product suggestions)

    └─ order (usage patterns)



stores

    └─ (standalone)

```



## URL Namespace Structure



All URLs follow consistent patterns:



```

/                              → main.home

/auth/

  ├─ login/                   → authentication.login

  ├─ logout/                  → authentication.logout

  └─ signup/                  → authentication.signup



/catalog/

  ├─ (empty)                  → catalog.catalog_home

  ├─ category/<slug>/         → catalog.category_products

  ├─ product/<id>/            → catalog.product_detail

  └─ api/

      ├─ filter/              → catalog.api_filter_products

      └─ quick-view/          → catalog.api_product_quick_view



/cart/

  ├─ (empty)                  → cart.cart_view

  ├─ add/<id>/                → cart.add_to_cart

  ├─ update/<id>/             → cart.update_cart_item

  ├─ remove/<id>/             → cart.remove_from_cart

  ├─ clear/                   → cart.clear_cart

  ├─ checkout/                → cart.checkout_view (redirects)

  └─ api/

      ├─ summary/             → cart.api_cart_summary

      └─ count/               → cart.api_cart_count



/order/

  ├─ (empty)                  → order.order_list

  ├─ checkout/                → order.checkout_view

  ├─ checkout/success/<id>/   → order.checkout_success

  ├─ <id>/                    → order.order_detail

  └─ <id>/

      ├─ status/              → order.check_delivery_status (AJAX)

      └─ rate/                → order.submit_rating (AJAX)



/profiles/

  ├─ (empty)                  → profiles.profile_view

  └─ edit/                    → profiles.profile_edit



/stores/

  ├─ (empty)                  → stores.store_list

  └─ <id>/                    → stores.store_detail



/recommendation/

  └─ (empty)                  → recommendation.recommendations



/admin/                        → Django admin panel

```



## Critical Design Patterns



### 1. Hybrid Cart System



**Guest Carts** (session-based):

- Stored in database but linked via `session_key`

- Temporary, auto-deleted after session expires

- No user authentication required



**User Carts** (persistent):

- Linked to user account via ForeignKey

- Persists across sessions

- Survives logout/login cycles



**Merge on Login**:

- After successful login, guest cart merged into user cart

- Function: `apps.cart.utils.transfer_guest_cart_to_user()`

- Preserves quantities and products



### 2. Price Snapshots



When creating Order from Cart:

1. Copy CartItem quantity

2. **Capture current Product.price** in OrderItem.price

3. Store as separate field (not ForeignKey)

4. Decrement Product.stock atomically



Result: Historical pricing preserved even if Product.price changes later.



### 3. AJAX Pattern



All AJAX endpoints return consistent JSON:

```json

{

  "success": true|false,

  "data": {...},

  "message": "string",

  "error": "string"

}

```



Error handling standardized across frontend JavaScript.



### 4. Query Optimization



Always use:

- `select_related()` for ForeignKey relationships

- `prefetch_related()` for reverse ForeignKey and ManyToMany

- `values()` / `values_list()` for specific fields

- `only()` / `defer()` for large models



### 5. Authentication Integration



- Django's built-in User model extended (not replaced)

- Customer model provides optional extensions

- Permissions checked via `@login_required` decorator

- Admin panel uses Django admin for management



## Static Files Architecture



### Development



Django serves static files directly:

```

/static/<app>/css/

/static/<app>/js/

/static/<app>/images/

```



### Production



WhiteNoise serves static files from collected directory:

```

/staticfiles/<app>/css/

/staticfiles/<app>/js/

```



Collect with:

```bash

python manage.py collectstatic --no-input

```



## Middleware Stack



```

SecurityMiddleware

    ↓

WhiteNoiseMiddleware (production static files)

    ↓

SessionMiddleware

    ↓

AuthenticationMiddleware

    ↓

MessageMiddleware

    ↓

(Custom middleware can be added here)

```



## Testing Architecture



Each app has `tests.py` containing:

- Model tests

- View tests

- Integration tests



Run all tests:

```bash

python manage.py test

```



Run specific app:

```bash

python manage.py test apps.cart

```



---



**Next**: [Database & Models](./03-database-models.md)

