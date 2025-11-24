# Django Backend Mobile API Integration

This document describes the changes made to the Becathlon Django backend to support the Flutter mobile application.

## Changes Summary

### 1. CORS Configuration

Added `django-cors-headers` to enable cross-origin requests from the Flutter mobile app.

**Files Modified:**
- `becathlon/settings.py` - Added CORS configuration
- `requirements.txt` - Added `django-cors-headers==4.3.1`

**Changes in settings.py:**
```python
INSTALLED_APPS = [
    ...
    'corsheaders',  # Add for mobile API
    ...
]

MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',  # Add CORS middleware for mobile API
    ...
]

# CORS Settings for Mobile API
CORS_ALLOW_ALL_ORIGINS = True  # For development - restrict in production
CORS_ALLOW_CREDENTIALS = True
```

### 2. Authentication API Endpoints

Modified `apps/authentication/views.py` to handle both web (HTML) and mobile (JSON) requests.

**Endpoints:**
- `POST /auth/login/` - Handles both web form and mobile JSON login
- `POST /auth/signup/` - Handles both web form and mobile JSON registration
- `POST /auth/logout/` - Handles both web and mobile logout

**How it works:**
- Views detect request content type (`application/json` for mobile)
- Returns appropriate response (HTML redirect for web, JSON for mobile)

**Mobile Response Format:**
```json
// Login Success
{
    "status": true,
    "message": "Login successful!",
    "username": "user123",
    "email": "user@example.com",
    "account_type": "BUYER"
}

// Error Response
{
    "status": false,
    "message": "Invalid username or password"
}
```

### 3. Catalog API Endpoints

Added mobile-specific product endpoints to `apps/catalog/views.py`.

**Endpoints:**
- `GET /catalog/mobile/products/` - Get all products with filtering
- `GET /catalog/mobile/products/<id>/` - Get single product detail
- `GET /catalog/mobile/categories/` - Get all categories

**Query Parameters for /catalog/mobile/products/:**
- `category` - Filter by category name
- `search` - Search in product name/description
- `in_stock_only=true` - Only show products in stock
- `min_price` - Minimum price filter
- `max_price` - Maximum price filter
- `sort_by` - Sort options: `newest`, `price_low`, `price_high`, `name_asc`, `name_desc`
- `limit` - Limit number of results

**Response Format (Django pk/fields format):**
```json
[
    {
        "pk": 1,
        "fields": {
            "name": "Product Name",
            "description": "Product description",
            "price": "99.99",
            "category": "Sports",
            "brand": "Brand Name",
            "image": "https://image-url.com",
            "stock": 10,
            "rating": "4.5"
        }
    }
]
```

## Installation & Deployment

### Local Development

1. Install new dependency:
```bash
pip install django-cors-headers==4.3.1
```

2. Run migrations (if any):
```bash
python manage.py migrate
```

3. Start server:
```bash
python manage.py runserver
```

### Production Deployment

1. Update `requirements.txt` on server
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Collect static files:
```bash
python manage.py collectstatic --noinput
```

4. Restart application server

## Security Considerations

### CSRF Protection

Mobile API endpoints use `@csrf_exempt` decorator because:
- Mobile apps can't handle CSRF tokens the same way browsers do
- Authentication is handled via session cookies with `pbp_django_auth`

### CORS in Production

Currently set to `CORS_ALLOW_ALL_ORIGINS = True` for development. For production, restrict to specific origins:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://your-app-domain.com',
]
```

## Testing Mobile API

### Using cURL

Login:
```bash
curl -X POST https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

Get Products:
```bash
curl -X GET "https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/catalog/mobile/products/"
```

Search Products:
```bash
curl -X GET "https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/catalog/mobile/products/?search=football"
```

### Using Flutter App

The Flutter app is pre-configured to use:
- Production URL: `https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id`
- Uses `pbp_django_auth` package for authentication
- Automatic session management with cookies

## Backward Compatibility

All changes are backward compatible:
- Existing web views continue to work unchanged
- Mobile endpoints are separate routes
- No breaking changes to existing functionality

## Files Changed

1. `becathlon/settings.py` - CORS configuration
2. `requirements.txt` - Added django-cors-headers
3. `apps/authentication/views.py` - Added mobile JSON handling
4. `apps/catalog/views.py` - Added mobile product endpoints
5. `apps/catalog/urls.py` - Added mobile URL patterns

## Future Enhancements

Consider adding:
1. API versioning (`/api/v1/products/`)
2. Rate limiting for mobile endpoints
3. Token-based authentication (JWT) as alternative to sessions
4. Pagination for product lists
5. API documentation (Swagger/OpenAPI)
6. Mobile-specific error codes and messages
