# Django Backend Mobile API Integration

This document describes the mobile API endpoints and configuration for the Becathlon Django backend to support Flutter mobile application integration.

## Overview

The Becathlon API provides RESTful endpoints for mobile clients to:
- Authenticate users (login, register, logout)
- Browse and search products
- Filter by category, price, and stock
- View product details and images
- Access product categories

## Architecture & Configuration

### 1. CORS & Cross-Origin Support

`django-cors-headers` is configured to enable cross-origin requests from the Flutter mobile app.

**Configuration in `becathlon/settings.py`:**
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Must be early in middleware stack
    ...
]

# CORS Settings for Mobile API
CORS_ALLOW_ALL_ORIGINS = True  # For development - restrict in production
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://10.0.2.2:8000',  # Android emulator bridge
]

# Production settings
if not DEBUG:
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SAMESITE = 'None'
```

**Why CORS is needed:**
- Mobile apps cannot handle CSRF tokens like browsers do
- Cross-origin requests required for mobile → backend communication
- Session cookies with `pbp_django_auth` handle authentication

### 2. Authentication API Endpoints

**Location:** `apps/authentication/views.py`  
**Pattern:** Follows PBP (Platform Bersama Penyelenggara) Django authentication tutorial pattern

#### POST `/auth/flutter/login/`
Handle Flutter app user login.

**Request Format:**
```
POST /auth/flutter/login/ HTTP/1.1
Content-Type: application/x-www-form-urlencoded

username=testuser&password=testpass123
```

**Success Response (200):**
```json
{
    "status": true,
    "message": "Login successful!",
    "username": "testuser"
}
```

**Error Response (401):**
```json
{
    "status": false,
    "message": "Login failed, please check your username or password."
}
```

**Key Points:**
- Uses `@csrf_exempt` decorator for mobile access
- Uses POST data (form-encoded) to match PBP tutorial pattern
- Returns Django session cookie for authenticated requests
- Supports both active and inactive accounts with appropriate error messages

---

#### POST `/auth/flutter/register/`
Handle Flutter app user registration.

**Request Format:**
```
POST /auth/flutter/register/ HTTP/1.1
Content-Type: application/json

{
    "username": "newuser",
    "password": "securepass123",
    "password2": "securepass123"
}
```

**Success Response (201):**
```json
{
    "status": true,
    "message": "Registration successful!",
    "username": "newuser"
}
```

**Error Responses (400):**
```json
{
    "status": false,
    "message": "Username and password are required"
}
```

```json
{
    "status": false,
    "message": "Passwords do not match"
}
```

```json
{
    "status": false,
    "message": "Username already exists"
}
```

**Key Points:**
- Accepts JSON request body
- Validates password confirmation match
- Creates associated Customer and Profile objects
- Auto-sets `account_type` to 'BUYER' for new users
- Uses `@csrf_exempt` decorator

---

#### POST `/auth/flutter/logout/`
Handle Flutter app user logout.

**Request Format:**
```
POST /auth/flutter/logout/ HTTP/1.1
```

**Success Response (200):**
```json
{
    "status": true,
    "message": "Logout successful"
}
```

**Error Response (500):**
```json
{
    "status": false,
    "message": "Error message details"
}
```

**Key Points:**
- Clears session cookie
- Uses `@csrf_exempt` decorator
- Always succeeds if session exists

### 3. Catalog API Endpoints

**Location:** `apps/catalog/views.py`  
**Route Pattern:** `/catalog/mobile/...`

#### GET `/catalog/mobile/products/`
Retrieve all products with optional filtering, sorting, and search.

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `search` | string | Search in product name/description | `?search=football` |
| `category` | string | Filter by product type name (case-insensitive) | `?category=Running` |
| `in_stock_only` | boolean | Only show products with stock > 0 | `?in_stock_only=true` |
| `min_price` | float | Minimum price filter | `?min_price=50.00` |
| `max_price` | float | Maximum price filter | `?max_price=200.00` |
| `sort_by` | string | Sort options: `newest`, `price_low`, `price_high`, `name_asc`, `name_desc` | `?sort_by=price_low` |
| `limit` | integer | Limit number of results | `?limit=20` |

**Example Request:**
```
GET /catalog/mobile/products/?category=Running&in_stock_only=true&sort_by=price_low&limit=20
```

**Success Response (200):**
```json
[
    {
        "pk": 1,
        "fields": {
            "name": "Running Shoes Pro",
            "description": "Professional running shoes with advanced cushioning",
            "price": "149.99",
            "category": "Running",
            "brand": "Nike",
            "image": "https://example.com/image.jpg",
            "stock": 25,
            "rating": "4.50"
        }
    },
    {
        "pk": 2,
        "fields": {
            "name": "Runner's Jacket",
            "description": "Lightweight and breathable running jacket",
            "price": "89.99",
            "category": "Running",
            "brand": "Adidas",
            "image": "https://example.com/jacket.jpg",
            "stock": 12,
            "rating": "4.25"
        }
    }
]
```

**Error Response (500):**
```json
{
    "status": false,
    "message": "Error message details"
}
```

**Response Format Notes:**
- Uses Django's pk/fields format for consistency
- `price` and `rating` returned as strings (format from database)
- `image` returns the primary product image URL
- `stock` is an integer >= 0
- Empty results return empty array `[]`

---

#### GET `/catalog/mobile/products/<int:product_id>/`
Retrieve detailed information for a single product.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `product_id` | integer | Unique product identifier |

**Example Request:**
```
GET /catalog/mobile/products/1/
```

**Success Response (200):**
```json
{
    "pk": 1,
    "fields": {
        "name": "Running Shoes Pro",
        "description": "Professional running shoes with advanced cushioning",
        "price": "149.99",
        "category": "Running",
        "brand": "Nike",
        "image": "https://example.com/image-primary.jpg",
        "images": [
            "https://example.com/image-primary.jpg",
            "https://example.com/image-angle1.jpg",
            "https://example.com/image-angle2.jpg"
        ],
        "stock": 25,
        "rating": "4.50",
        "in_stock": true
    }
}
```

**Not Found Response (404):**
```json
{
    "status": false,
    "message": "Product not found"
}
```

**Error Response (500):**
```json
{
    "status": false,
    "message": "Error message details"
}
```

**Response Format Notes:**
- `image` returns the primary/first image URL
- `images` array includes all product images for gallery views
- `in_stock` boolean is convenience field (true if stock > 0)
- All ProductImage objects included (not filtered by is_primary)

---

#### GET `/catalog/mobile/categories/`
Retrieve all available product categories/types.

**Example Request:**
```
GET /catalog/mobile/categories/
```

**Success Response (200):**
```json
[
    {
        "id": 1,
        "name": "Running",
        "description": "Running shoes and apparel",
        "product_count": 45
    },
    {
        "id": 2,
        "name": "Cycling",
        "description": "Bikes, gear, and accessories",
        "product_count": 32
    },
    {
        "id": 3,
        "name": "Swimming",
        "description": "Swimwear and swimming equipment",
        "product_count": 28
    }
]
```

**Error Response (500):**
```json
{
    "status": false,
    "message": "Error message details"
}
```

**Response Format Notes:**
- Returns all ProductType objects
- `product_count` is calculated count of products in category
- Sorted by insertion order (no specific sort applied)
- Empty if no categories exist

---

## 4. Cart API Endpoints (Flutter)

**Location:** `apps/cart/views.py`  
**Route Pattern:** `/cart/flutter/...`

These endpoints are CSRF-exempt (`@csrf_exempt`) and support both guest (session-key) or authenticated users (session cookie returned by `/auth/flutter/login/`). Use form-encoded `quantity` data for POSTs (`Content-Type: application/x-www-form-urlencoded`).

Endpoint summary:
- GET `/cart/flutter/` — Retrieve cart summary and items
- POST `/cart/flutter/add/<product_id>/` — Add a product (path param `product_id`, body: `quantity`)
- POST `/cart/flutter/update/<item_id>/` — Update quantity for cart item (path param `item_id`, body: `quantity`). If quantity <= 0 the item is removed.
- POST `/cart/flutter/remove/<item_id>/` — Remove a cart item (path param `item_id`)
- POST `/cart/flutter/clear/` — Clear the whole cart
- GET `/cart/flutter/count/` — Return total item count
- GET/POST `/cart/flutter/checkout/` — Starts the checkout flow; requires authenticated user

Minimal examples (development):

Login (create session cookie):
```bash
curl -c cookie-jar.txt -X POST http://localhost:8000/auth/flutter/login/ \
    -d "username=testuser&password=testpass123"
```

Add to cart (form-encoded POST):
```bash
curl -b cookie-jar.txt -X POST http://localhost:8000/cart/flutter/add/1/ \
    -d "quantity=2"
```

Get cart summary:
```bash
curl -X GET http://localhost:8000/cart/flutter/
```

Update an item (reduce to 1):
```bash
curl -b cookie-jar.txt -X POST http://localhost:8000/cart/flutter/update/1/ \
    -d "quantity=1"
```

Example responses:
```json
{ "success": true, "message": "Item added to cart" }
```
```json
{
    "total_items": 2,
    "subtotal": 299.98,
    "item_count": 2,
    "items": [
        {"id": 1, "product_id": 1, "product_name": "Running Shoes Pro", "quantity": 2, "price": 149.99, "subtotal": 299.98}
    ]
}
```

Notes:
- For guests: the server will set a session cookie on first contact — persist and reuse it.
- For authenticated users: use `/auth/flutter/login/` to obtain a session cookie (persisted) used for subsequent cart operations.
- The `checkout` endpoint requires authentication; the server replies with an error for guests.
- Endpoints return `success` booleans and `message` strings for action feedback.

## 5. Order API Endpoints (Flutter)

**Location:** `apps/order/views.py`  
**Route Pattern:** `/order/flutter/...`

These endpoints are CSRF-exempt (`@csrf_exempt`) and require authenticated users.

#### POST `/order/flutter/checkout/`
Handle checkout and order creation for Flutter app.

**Request Format:**
```json
{
    "full_name": "John Doe",
    "phone_number": "+628123456789",
    "address_line1": "Jl. Contoh No. 123",
    "address_line2": "Blok A",
    "city": "Jakarta",
    "state": "DKI Jakarta",
    "postal_code": "12345",
    "country": "Indonesia",
    "payment_method": "CREDIT_CARD"
}
```

**Success Response (201):**
```json
{
    "status": true,
    "message": "Order created successfully",
    "order_id": 123
}
```

**Error Response (400, 401, 500):**
```json
{
    "status": false,
    "message": "Error message details",
    "errors": {
        "field_name": "Validation error message"
    }
}
```
**Key Points:**
- Requires authenticated user.
- Accepts JSON request body for shipping address and payment method.
- Validates all shipping address fields and payment method.
- Decrements product stock atomically.

#### GET `/order/flutter/list/`
Retrieve a list of all orders for the authenticated user.

**Example Request:**
```
GET /order/flutter/list/
```

**Success Response (200):**
```json
{
    "status": true,
    "orders": [
        {
            "id": 123,
            "status": "PAID",
            "delivery_status": "EN_ROUTE",
            "delivery_status_display": "En Route",
            "total_price": 150.00,
            "created_at": "2025-12-02 10:30:00",
            "item_count": 2
        },
        {
            "id": 124,
            "status": "PAID",
            "delivery_status": "PROCESSING",
            "delivery_status_display": "Processing",
            "total_price": 25.50,
            "created_at": "2025-12-01 15:00:00",
            "item_count": 1
        }
    ]
}
```

**Error Response (401):**
```json
{
    "status": false,
    "message": "User not authenticated"
}
```
**Key Points:**
- Requires authenticated user.
- Returns a list of simplified order objects.
- `delivery_status_display` provides a human-readable status.

#### GET `/order/flutter/<int:order_id>/`
Retrieve detailed information for a specific order.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `order_id` | integer | Unique order identifier |

**Example Request:**
```
GET /order/flutter/123/
```

**Success Response (200):**
```json
{
    "status": true,
    "order": {
        "id": 123,
        "status": "PAID",
        "delivery_status": "EN_ROUTE",
        "delivery_status_display": "En Route",
        "total_price": 150.00,
        "created_at": "2025-12-02 10:30:00",
        "items": [
            {
                "product_id": 1,
                "product_name": "Running Shoes Pro",
                "quantity": 1,
                "price": 149.99,
                "subtotal": 149.99,
                "image_url": "https://example.com/running_shoes.jpg"
            },
            {
                "product_id": 5,
                "product_name": "Sport Socks",
                "quantity": 2,
                "price": 0.01,
                "subtotal": 0.02,
                "image_url": "https://example.com/sport_socks.jpg"
            }
        ],
        "shipping_address": {
            "full_name": "John Doe",
            "phone_number": "+628123456789",
            "address": "Jl. Contoh No. 123, Jakarta, 12345, Indonesia"
        },
        "rated_product_ids": [1]
    }
}
```

**Error Response (401, 404):**
```json
{
    "status": false,
    "message": "User not authenticated"
}
```
```json
{
    "status": false,
    "message": "Order not found"
}
```
**Key Points:**
- Requires authenticated user.
- Provides comprehensive details about the order, its items, and shipping address.
- `rated_product_ids` indicates which products in the order the user has already rated.

#### GET `/order/flutter/<int:order_id>/status/`
Check the current delivery status of a specific order.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `order_id` | integer | Unique order identifier |

**Example Request:**
```
GET /order/flutter/123/status/
```

**Success Response (200):**
```json
{
    "status": true,
    "delivery_status": "EN_ROUTE",
    "delivery_status_display": "En Route",
    "progress_percentage": 50,
    "seconds_remaining": 60,
    "is_delivered": false
}
```

**Error Response (401, 404):**
```json
{
    "status": false,
    "message": "User not authenticated"
}
```
```json
{
    "status": false,
    "message": "Order not found"
}
```
**Key Points:**
- Requires authenticated user.
- Provides real-time delivery status, progress, and estimated time remaining.

#### POST `/order/flutter/<int:order_id>/rate/`
Submit or update a product rating for a delivered order.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `order_id` | integer | Unique order identifier |

**Request Format:**
```json
{
    "product_id": 1,
    "rating": 4,
    "review": "Great product, very comfortable!"
}
```

**Success Response (200):**
```json
{
    "status": true,
    "message": "Rating submitted successfully!",
    "new_aggregate_rating": 4.25
}
```

**Error Response (400, 401, 404, 500):**
```json
{
    "status": false,
    "message": "Error message details"
}
```
**Key Points:**
- Requires authenticated user.
- Order must be in `DELIVERED` status.
- `product_id`, `rating` (1-5) are required; `review` is optional.
- Updates the aggregate rating of the product.

## Testing Mobile API

### Using cURL

**Login (Development):**
```bash
curl -X POST http://localhost:8000/auth/flutter/login/ \
  -d "username=testuser&password=testpass123"
```

**Login (Production):**
```bash
curl -X POST https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/auth/flutter/login/ \
  -d "username=testuser&password=testpass123" \
  --ssl-no-revoke
```

**Register (Development):**
```bash
curl -X POST http://localhost:8000/auth/flutter/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username":"newuser123",
    "password":"securepass123",
    "password2":"securepass123"
  }'
```

**Register (Production):**
```bash
curl -X POST https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/auth/flutter/register/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"newuser123\",\"password\":\"rahasia123\",\"password2\":\"rahasia123\"}" \
  --ssl-no-revoke
```

**Get All Products (Development):**
```bash
curl -X GET "http://localhost:8000/catalog/mobile/products/"
```

**Get All Products (Production):**
```bash
curl -X GET "https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/catalog/mobile/products/" \
  --ssl-no-revoke
```

**Search Products (Production):**
```bash
curl -X GET "https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/catalog/mobile/products/?search=running" \
  --ssl-no-revoke
```

**Filter by Category and Price (Production):**
```bash
curl -X GET "https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/catalog/mobile/products/?category=Running&min_price=50&max_price=200&sort_by=price_low" \
  --ssl-no-revoke
```

**Get Single Product Detail (Production):**
```bash
curl -X GET "https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/catalog/mobile/products/1/" \
  --ssl-no-revoke
```

**Get All Categories (Production):**
```bash
curl -X GET "https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/catalog/mobile/categories/" \
  --ssl-no-revoke
```

### Using Flutter App

The Flutter app integrates with this backend using:
- **pbp_django_auth** package for session-based authentication
- **Automatic session management** with cookies
- **CORS headers** to bypass browser restrictions

### Typical Flutter Integration:**
```dart
// Login example
final response = await http.post(
  Uri.parse('https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/auth/flutter/login/'),
  body: {
    'username': 'testuser',
    'password': 'testpass123',
  },
);

// Get products with filters
final response = await http.get(
  Uri.parse('https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/catalog/mobile/products/?category=Running&limit=20'),
);
```

### Production API Base URL
- **URL:** `https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id`
- **All endpoints** should be prefixed with this URL

## Installation & Deployment

### Local Development Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run migrations:**
```bash
python manage.py migrate
```

3. **Create test data:**
```bash
# Seed product types
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'becathlon.settings'); import django; django.setup(); exec(open('seed_product_types.py').read())"

# Create superuser (for admin)
python manage.py createsuperuser
```

4. **Start development server:**
```bash
python manage.py runserver
```
   - Web access: `http://127.0.0.1:8000/`
   - Mobile API accessible at same URL (CORS enabled for all origins in dev)

### Production Deployment

1. **Update dependencies on server:**
```bash
pip install -r requirements.txt
```

2. **Run migrations:**
```bash
python manage.py migrate
```

3. **Collect static files:**
```bash
python manage.py collectstatic --noinput
```

4. **Set environment variables:**
   - `DEBUG=False`
   - `ALLOWED_HOSTS` (comma-separated)
   - `SECRET_KEY` (strong random string)
   - `DB_*` (PostgreSQL credentials if using production DB)

5. **Restart application server** (via your hosting provider's process manager)

## Security Considerations

### CSRF Protection Strategy

Mobile API endpoints use `@csrf_exempt` decorator because:
- Mobile apps cannot request and include CSRF tokens like browsers
- PBP tutorial pattern relies on session cookies for authentication, not CSRF tokens
- Cross-origin requests from mobile clients need CORS support (not CSRF)

**Trade-offs:**
- ✅ Required for mobile client authentication
- ⚠️ Requires strong CORS configuration in production
- ✅ Still uses session authentication (not less secure than form-based)

### CORS in Production

**Current Development Setting:**
```python
CORS_ALLOW_ALL_ORIGINS = True  # ⚠️ NOT SAFE FOR PRODUCTION
```

**Recommended Production Setting:**
```python
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://your-flutter-app-domain.com',  # Your mobile app's API calls
    'https://your-web-domain.com',  # Web frontend if separate
]
```

**Also set for production:**
```python
if not DEBUG:
    CSRF_COOKIE_SAMESITE = 'None'  # Allow cross-origin cookies
    SESSION_COOKIE_SAMESITE = 'None'  # Allow cross-origin sessions
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

### Authentication Best Practices

1. **Session Management:**
   - Django session cookie handles authentication
   - Flutter app automatically sends cookies with requests (when configured with `pbp_django_auth`)
   - Sessions expire based on Django settings (default: 2 weeks)

2. **Password Storage:**
   - All passwords hashed using Django's built-in PBKDF2 + SHA256
   - Validated against common patterns (no default, sequential, etc.)

3. **Account Types:**
   - Currently all users created as 'BUYER' by default
   - Future: Planned dual-role system (Customer vs Store profiles)

## Data Model Reference

### Product Response Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| pk | int | Product ID | 1 |
| name | string | Product name | "Running Shoes Pro" |
| description | string | Product description | "Professional running shoes..." |
| price | string | Price (string from DB) | "149.99" |
| category | string | ProductType name | "Running" |
| brand | string | Brand name | "Nike" |
| image | string (URL) | Primary product image | "https://example.com/img.jpg" |
| images | array | All product images | (only in detail endpoint) |
| stock | int | Current quantity | 25 |
| rating | string | Average rating | "4.50" |
| in_stock | bool | Stock status | true (only in detail endpoint) |

### Category Response Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| id | int | Category ID | 1 |
| name | string | Category name | "Running" |
| description | string | Category description | "Running shoes..." |
| product_count | int | Products in category | 45 |

## API Response Status Codes

| Code | Meaning | When | Example |
|------|---------|------|---------|
| 200 | OK | Successful GET/product found | All product list/detail requests |
| 201 | Created | Successful registration | `POST /auth/flutter/register/` |
| 400 | Bad Request | Invalid input | Missing required fields, invalid prices |
| 401 | Unauthorized | Login failed/invalid credentials | Wrong password, account disabled |
| 404 | Not Found | Resource doesn't exist | Non-existent product ID |
| 500 | Internal Server Error | Unexpected error | Database errors, server crash |

## Error Response Format

All error responses follow this format:
```json
{
    "status": false,
    "message": "Human-readable error description"
}
```

## Implementation Files & Architecture

### Core Files Modified

| File | Changes | Purpose |
|------|---------|---------|
| `becathlon/settings.py` | Added CORS configuration, middleware, SAMESITE settings | Enable cross-origin mobile API access |
| `apps/authentication/views.py` | Added `flutter_login`, `flutter_register`, `flutter_logout` views | Mobile authentication endpoints |
| `apps/authentication/urls.py` | Added Flutter mobile authentication routes | URL routing for mobile auth |
| `apps/catalog/views.py` | Added `mobile_products_list`, `mobile_product_detail`, `mobile_categories_list` views | Mobile product browsing |
| `apps/catalog/urls.py` | Added mobile API URL patterns | URL routing for mobile catalog |
| `apps/order/views.py` | Added `flutter_checkout`, `flutter_order_list`, `flutter_order_detail`, `flutter_check_delivery_status`, `flutter_submit_rating` views | Mobile order management endpoints |
| `apps/order/urls.py` | Added Flutter mobile order routes | URL routing for mobile order |
| `requirements.txt` | Added `django-cors-headers==4.3.1` | Enable CORS support |

### Data Flow Architecture

```
Mobile Client (Flutter)
    ↓ (HTTP Request + Session Cookie)
Django Middleware (CORS check)
    ↓
Authentication/Catalog Views
    ↓ (Database query)
Django ORM
    ↓ (Product/User data)
Views (JSON Response)
    ↓ (HTTP Response)
Mobile Client (Parse JSON)
```

### URL Namespace Structure

```
/auth/flutter/login/        → flutter_login (POST)
/auth/flutter/register/     → flutter_register (POST)
/auth/flutter/logout/       → flutter_logout (POST)

/catalog/mobile/products/            → mobile_products_list (GET)
/catalog/mobile/products/<id>/       → mobile_product_detail (GET)
/catalog/mobile/categories/          → mobile_categories_list (GET)

/cart/flutter/                      → flutter_cart_view (GET)
/cart/flutter/add/<product_id>/     → flutter_add_to_cart (POST)
/cart/flutter/update/<item_id>/     → flutter_update_cart_item (POST)
/cart/flutter/remove/<item_id>/     → flutter_remove_from_cart (POST)
/cart/flutter/clear/                → flutter_clear_cart (POST)
/cart/flutter/count/                → flutter_cart_count (GET)
/cart/flutter/checkout/             → flutter_checkout_view (POST)

/order/flutter/checkout/            → flutter_checkout (POST)
/order/flutter/list/                → flutter_order_list (GET)
/order/flutter/<int:order_id>/      → flutter_order_detail (GET)
/order/flutter/<int:order_id>/status/ → flutter_check_delivery_status (GET)
/order/flutter/<int:order_id>/rate/ → flutter_submit_rating (POST)
```

## Query Optimization

All mobile endpoints use Django's `select_related()` and `prefetch_related()` for efficient database queries:

```python
# Products list uses:
products = Product.objects.select_related('product_type').prefetch_related(
    Prefetch('images', queryset=ProductImage.objects.filter(is_primary=True))
)

# Product detail uses:
product = Product.objects.select_related('product_type').prefetch_related('images').get(id=product_id)
```

This prevents N+1 query problems when fetching related data (product types, images).

## Backward Compatibility

All changes are **fully backward compatible**:
- ✅ Existing web views unchanged
- ✅ Mobile endpoints are separate routes
- ✅ No breaking changes to existing functionality
- ✅ Session authentication works for both web and mobile

## Planned Future Enhancements

1. **User Profile API** - Retrieve and update user profile information
2. **Order History** - View past orders and order details (Partially implemented now with flutter_order_list and flutter_order_detail)
3. **Wishlist API** - Save favorite products
4. **API Versioning** - Support `/api/v1/`, `/api/v2/` for future updates
5. **Rate Limiting** - Protect against abuse (per IP/user)
6. **JWT Authentication** - Token-based auth alternative to sessions
7. **Pagination** - Proper page-based pagination for large product lists
8. **OpenAPI/Swagger** - Auto-generated API documentation
