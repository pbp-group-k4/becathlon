# Becathlon Authentication and Login System Documentation

## Table of Contents
1. [Overview](#overview)
2. [Database Models and Configuration](#database-models-and-configuration)
3. [Views and URL Routing](#views-and-url-routing)
4. [AJAX Implementation](#ajax-implementation)
5. [Security Features](#security-features)
6. [Cart Integration](#cart-integration)
7. [Architecture Diagrams](#architecture-diagrams)

---

## Overview

The Becathlon authentication system is built on Django's robust authentication framework, extended with custom user profiles and a dual-account type system (BUYER/SELLER). The system provides:

- User registration with custom profile creation
- Secure login/logout functionality
- Account type management (BUYER vs SELLER)
- Profile management with AJAX enhancements
- Seamless guest-to-user cart transfer
- Newsletter subscription management

---

## Database Models and Configuration

### 1. Database Configuration

**Location:** `becathlon/settings.py:110-150`

The application supports two database backends with automatic fallback:

#### PostgreSQL (Production)
```python
db_config = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': DB_NAME,           # From environment variable
    'USER': DB_USER,           # From environment variable
    'PASSWORD': DB_PASSWORD,   # From environment variable
    'HOST': DB_HOST,           # From environment variable
    'PORT': DB_PORT or '5432', # Default PostgreSQL port
    'ATOMIC_REQUESTS': False,  # Allow non-atomic operations
    'CONN_MAX_AGE': 0,         # Close connections immediately
}

# PostgreSQL schema support
if DB_SCHEMA:
    db_config['OPTIONS'] = {
        'options': f'-c search_path={DB_SCHEMA},public'
    }
```

**Environment Variables Required:**
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host address
- `DB_PORT`: Database port (optional, defaults to 5432)
- `SCHEMA`: PostgreSQL schema name (optional)

#### SQLite (Development Fallback)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

If PostgreSQL credentials are not provided, the system automatically falls back to SQLite for local development.

### 2. User Model Architecture

The authentication system uses Django's built-in `User` model extended with two profile models:

#### Base User Model
Django's `django.contrib.auth.models.User` provides:
- `username`: Unique identifier
- `email`: Email address
- `password`: Hashed password
- `first_name`, `last_name`: User's full name
- `is_active`, `is_staff`, `is_superuser`: Permission flags
- `date_joined`, `last_login`: Timestamps

#### Customer Model (Extended Profile)

**Location:** `apps/main/models.py:7-15`

```python
class Customer(models.Model):
    """Customer model extending User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - Customer"
```

**Relationship:** One-to-One with User
**Purpose:** Store customer-specific data (phone, address)
**Creation:** Automatically created during signup in `signup_view`

**Fields:**
- `user` (OneToOneField): Link to Django User
- `phone_number` (CharField): Customer's phone number (optional)
- `address` (TextField): Customer's address (optional)
- `created_at` (DateTimeField): Account creation timestamp

#### Profile Model (Account Management)

**Location:** `apps/profiles/models.py:4-30`

```python
class Profile(models.Model):
    ACCOUNT_TYPE_CHOICES = (
        ('BUYER', 'Buyer'),
        ('SELLER', 'Seller'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name="profile")
    first_name = models.CharField(max_length=100, blank=True)
    last_name  = models.CharField(max_length=100, blank=True)
    phone      = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    preferred_sports = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    newsletter_opt_in = models.BooleanField(default=False)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, default='BUYER')
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile({self.user.username})"

    def get_full_name(self):
        """Return the full name of the user."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.user.username
```

**Relationship:** One-to-One with User
**Purpose:** Manage account preferences and permissions

**Key Fields:**
- `account_type`: Determines user permissions
  - `BUYER`: Can browse and purchase products
  - `SELLER`: Can list products and manage store
- `newsletter_opt_in`: Email newsletter subscription flag
- `profile_picture`: User avatar (uploaded to `media/profile_pictures/`)
- `preferred_sports`: User's sports interests
- `created_at`, `updated_at`: Automatic timestamps

**Important Methods:**
- `get_full_name()`: Returns full name or username as fallback

### 3. Database Relationships

```
┌─────────────────┐
│  Django User    │
│  (Built-in)     │
└────────┬────────┘
         │
         ├──────────────────┐
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│    Customer     │  │    Profile      │
│  (main app)     │  │ (profiles app)  │
│                 │  │                 │
│ • phone_number  │  │ • account_type  │
│ • address       │  │ • newsletter    │
│ • created_at    │  │ • sports        │
└─────────────────┘  └─────────────────┘
```

### 4. Model Creation Flow

When a user signs up:

1. **User Creation** (via Django's `UserCreationForm`)
   - Username, email, password are saved to `User` model
   - Password is automatically hashed

2. **Customer Creation** (automatic)
   ```python
   Customer.objects.create(user=user)
   ```

3. **Profile Creation** (with account type)
   ```python
   profile, created = Profile.objects.get_or_create(user=user)
   profile.account_type = account_type
   profile.first_name = first_name
   profile.last_name = last_name
   profile.email = email
   profile.save()
   ```

### 5. Password Validation

**Location:** `becathlon/settings.py:156-169`

Django enforces four password validators:

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        # Prevents passwords similar to username/email
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        # Enforces minimum password length (default: 8 characters)
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        # Rejects common passwords (e.g., "password123")
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        # Prevents entirely numeric passwords
    },
]
```

### 6. Session Configuration

**Location:** `becathlon/settings.py:61-87`

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Enables sessions
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Auth handling
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

INSTALLED_APPS = [
    'django.contrib.sessions',  # Session support
    'django.contrib.auth',      # Authentication framework
    # ... other apps
]
```

Sessions are used for:
- User authentication state
- Guest cart storage (before login)
- CSRF token management
- Flash messages (via Django messages framework)

---

## Views and URL Routing

### 1. Authentication Views

**Location:** `apps/authentication/views.py`

#### signup_view (User Registration)

**URL:** `/auth/signup/`
**Method:** GET, POST
**Template:** `authentication/signup.html`

```python
def signup_view(request):
    """Handle user sign up"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create associated Customer profile
            Customer.objects.create(user=user)

            # Create or update Profile with account type
            account_type = form.cleaned_data.get('account_type', 'BUYER')
            first_name = form.cleaned_data.get('first_name', '')
            last_name = form.cleaned_data.get('last_name', '')
            email = form.cleaned_data.get('email', '')

            profile, created = Profile.objects.get_or_create(user=user)
            profile.account_type = account_type
            profile.first_name = first_name
            profile.last_name = last_name
            profile.email = email
            profile.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('auth:login')
    else:
        form = SignUpForm()
    return render(request, 'authentication/signup.html', {'form': form})
```

**Flow:**
1. User submits `SignUpForm` with:
   - Username, email, password1, password2
   - First name, last name
   - Account type (BUYER or SELLER)
2. Form validation checks:
   - Password strength (via `AUTH_PASSWORD_VALIDATORS`)
   - Username uniqueness
   - Email format
   - Password confirmation match
3. On valid form:
   - Creates `User` object
   - Creates `Customer` object (linked to user)
   - Creates/updates `Profile` object with account type
   - Displays success message
   - Redirects to login page

**Form Used:** `SignUpForm` (extends `UserCreationForm`)

**Location:** `apps/authentication/forms.py:6-21`

```python
class SignUpForm(UserCreationForm):
    """Custom sign up form"""
    email = forms.EmailField(max_length=254, required=True,
                            help_text='Required. Enter a valid email address.')
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    account_type = forms.ChoiceField(
        choices=[
            ('BUYER', 'Buyer - Browse and purchase items'),
            ('SELLER', 'Seller - Sell items on our marketplace')
        ],
        required=True,
        widget=forms.RadioSelect,
        help_text='Choose whether you want to buy items or sell items on the Becathlon marketplace.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'account_type',
                  'password1', 'password2')
```

#### login_view (User Authentication)

**URL:** `/auth/login/`
**Method:** GET, POST
**Template:** `authentication/login.html`

```python
def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Transfer guest cart to user cart
                transfer_guest_cart_to_user(request)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'authentication/login.html', {'form': form})
```

**Flow:**
1. User submits `AuthenticationForm` with username and password
2. `authenticate()` verifies credentials against database
3. On successful authentication:
   - Calls `login(request, user)` - creates session
   - Calls `transfer_guest_cart_to_user(request)` - merges carts
   - Displays welcome message
   - Redirects to home page
4. On failure:
   - Displays error message
   - Re-renders login form

**Form Used:** Django's built-in `AuthenticationForm`

**Cart Transfer Logic:** See [Cart Integration](#cart-integration) section

#### logout_view (Session Termination)

**URL:** `/auth/logout/`
**Method:** GET, POST
**Template:** None (redirects)

```python
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')
```

**Flow:**
1. Calls Django's `logout(request)`:
   - Clears session data
   - Removes authentication cookies
2. Displays logout success message
3. Redirects to home page

**Note:** Guest cart is preserved in session until browser closes

### 2. URL Configuration

**Location:** `apps/authentication/urls.py:1-10`

```python
from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
```

**URL Namespace:** `auth`

**Full URL Paths:**
- `/auth/signup/` → `signup_view` → Named route: `auth:signup`
- `/auth/login/` → `login_view` → Named route: `auth:login`
- `/auth/logout/` → `logout_view` → Named route: `auth:logout`

**Template Usage:**
```django
<a href="{% url 'auth:login' %}">Login</a>
<a href="{% url 'auth:signup' %}">Sign Up</a>
<a href="{% url 'auth:logout' %}">Logout</a>
```

### 3. Profile Management Views

**Location:** `apps/profiles/views.py`

These views handle user profile viewing and editing (requires authentication).

#### profile_detail (View Profile)

**URL:** `/profiles/`
**Decorator:** `@login_required`
**Template:** `profiles/profile_detail.html`

```python
@login_required
def detail(request):
    return render(request, "profiles/profile_detail.html", {"profile": request.user.profile})
```

**Access Control:**
- Only authenticated users can access
- Unauthenticated users redirected to `/auth/login/?next=/profiles/`

#### profile_edit (Update Profile)

**URL:** `/profiles/edit/`
**Decorator:** `@login_required`
**Method:** GET, POST
**Template:** `profiles/profile_edit.html`

```python
@login_required
def edit(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect("profiles:detail")
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors.as_json()}, status=400)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profiles/profile_edit.html", {"form": form})
```

**Features:**
- Dual response format (HTML or JSON)
- AJAX-aware (checks `X-Requested-With` header)
- Updates profile fields via `ProfileForm`

### 4. Dynamic URL Patterns

The authentication system doesn't use URL parameters directly, but integrates with other views that do:

#### Query Parameter Authentication Redirect

**Checkout View Example:**
```python
# In order/views.py
def checkout(request):
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to continue with checkout.')
        return redirect(f'/auth/login/?next=/order/checkout/')
    # ... checkout logic
```

**Flow:**
1. Unauthenticated user tries to access `/order/checkout/`
2. View redirects to `/auth/login/?next=/order/checkout/`
3. After successful login, user is redirected to original URL (`/order/checkout/`)

This is handled by Django's `@login_required` decorator automatically.

#### Dynamic Profile URLs

**Location:** `apps/profiles/urls.py`

```python
app_name = 'profiles'

urlpatterns = [
    path('', views.detail, name='detail'),
    path('edit/', views.edit, name='edit'),
    path('ajax/toggle-newsletter/', views.toggle_newsletter_ajax, name='toggle_newsletter_ajax'),
    path('ajax/switch-account-type/', views.switch_account_type_ajax, name='switch_account_type_ajax'),
]
```

**AJAX Endpoints:**
- `/profiles/ajax/toggle-newsletter/` - Toggle newsletter subscription
- `/profiles/ajax/switch-account-type/` - Switch between BUYER/SELLER

---

## AJAX Implementation

The authentication system extensively uses AJAX for dynamic, non-reloading updates to user profiles and account settings.

### 1. CSRF Token Management

All AJAX requests require CSRF protection. The system uses a JavaScript utility to extract the CSRF token from cookies.

**Location:** `apps/profiles/templates/profiles/profile_detail.html`

```javascript
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
}
```

**Usage in AJAX:**
```javascript
headers: {
    "X-CSRFToken": getCookie("csrftoken"),
    "X-Requested-With": "XMLHttpRequest",
}
```

### 2. Newsletter Toggle (AJAX)

**Backend View:** `apps/profiles/views.py:30-41`

```python
@login_required
def toggle_newsletter_ajax(request):
    if request.method != "POST" or request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return HttpResponseBadRequest("Invalid request")
    prof = request.user.profile
    prof.newsletter_opt_in = not prof.newsletter_opt_in
    prof.save(update_fields=["newsletter_opt_in"])
    return JsonResponse({
        "success": True,
        "data": {"newsletter_opt_in": prof.newsletter_opt_in},
        "error": None
    })
```

**Frontend Implementation:** `apps/profiles/templates/profiles/profile_detail.html:620-649`

```javascript
const toggle = document.getElementById("newsletter-toggle");
const statusSpan = document.getElementById("newsletter-status");

if (toggle) {
    toggle.addEventListener('change', async () => {
        const isSubscribed = toggle.checked;
        statusSpan.textContent = isSubscribed
            ? "✓ You're subscribed to our newsletter"
            : "You're not subscribed to our newsletter";

        try {
            const response = await fetch("{% url 'profiles:toggle_newsletter_ajax' %}", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: JSON.stringify({ newsletter_opt_in: isSubscribed }),
            });
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || "Update failed");
            }
            showToast('Newsletter preference updated', 'success');
        } catch (err) {
            console.error("Newsletter update failed:", err);
            // Rollback toggle state on error
            toggle.checked = !toggle.checked;
            statusSpan.textContent = isSubscribed
                ? "You're not subscribed to our newsletter"
                : "✓ You're subscribed to our newsletter";
            showToast('Failed to update newsletter preference', 'error');
        }
    });
}
```

**Features:**
- **Instant feedback:** UI updates immediately (optimistic update)
- **Error handling:** Rolls back changes if AJAX fails
- **Toast notifications:** Success/error messages via `showToast()`
- **Database update:** Only updates `newsletter_opt_in` field (efficient)

**Request Format:**
- **Method:** POST
- **Headers:**
  - `Content-Type: application/json`
  - `X-CSRFToken: <token>`
  - `X-Requested-With: XMLHttpRequest`
- **Body:** `{"newsletter_opt_in": true/false}`

**Response Format:**
```json
{
    "success": true,
    "data": {
        "newsletter_opt_in": true
    },
    "error": null
}
```

### 3. Account Type Switching (AJAX)

**Backend View:** `apps/profiles/views.py:44-83`

```python
@login_required
@require_POST
def switch_account_type_ajax(request):
    """Switch account type between BUYER and SELLER with warning about delisting products"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return HttpResponseBadRequest("Invalid request")

    profile = request.user.profile
    new_account_type = request.POST.get('account_type', '').upper()

    # Validate account type
    if new_account_type not in ['BUYER', 'SELLER']:
        return JsonResponse({'success': False, 'error': 'Invalid account type'}, status=400)

    # If switching TO BUYER, delist all products
    if new_account_type == 'BUYER' and profile.account_type == 'SELLER':
        # Delete all products created by this user
        Product.objects.filter(created_by=request.user).delete()
        profile.account_type = 'BUYER'
        profile.save()
        return JsonResponse({
            'success': True,
            'message': 'Account type switched to Buyer. All your listed products have been removed.',
            'account_type': profile.account_type
        })

    # If switching TO SELLER, just update
    if new_account_type == 'SELLER' and profile.account_type == 'BUYER':
        profile.account_type = 'SELLER'
        profile.save()
        return JsonResponse({
            'success': True,
            'message': 'Account type switched to Seller. You can now list products.',
            'account_type': profile.account_type
        })

    return JsonResponse({
        'success': False,
        'error': 'Account type already set'
    }, status=400)
```

**Important Business Logic:**
- **BUYER → SELLER:** Simple account upgrade, no data loss
- **SELLER → BUYER:** **DESTRUCTIVE** - deletes all products created by user
  - `Product.objects.filter(created_by=request.user).delete()`

**Frontend Implementation - Switch to SELLER:** `profile_detail.html:652-685`

```javascript
switchToSellerBtn.addEventListener('click', () => {
    showModal(
        'Upgrade to Seller Account',
        '<p>You are about to upgrade your account to a <strong>Seller</strong> account.</p>' +
        '<p>As a seller, you will be able to:</p>' +
        '<ul style="margin-left: 1.5rem; color: var(--light-gray);">' +
        '<li>List products on the Becathlon marketplace</li>' +
        '<li>Manage your store information</li>' +
        '<li>Track sales and orders</li>' +
        '</ul>' +
        '<p>Are you sure you want to continue?</p>',
        async () => {
            try {
                const response = await fetch("{% url 'profiles:switch_account_type_ajax' %}", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": getCookie("csrftoken"),
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: new URLSearchParams({
                        'account_type': 'SELLER'
                    })
                });
                const data = await response.json();
                if (data.success) {
                    showToast(data.message, 'success');
                    setTimeout(() => {
                        location.reload();  // Reload to update UI
                    }, 1500);
                } else {
                    showToast(data.error || 'Failed to switch account type', 'error');
                }
            } catch (err) {
                console.error("Account switch failed:", err);
                showToast('Failed to switch account type', 'error');
            }
        }
    );
});
```

**Frontend Implementation - Switch to BUYER:** `profile_detail.html:688-723`

```javascript
switchToBuyerBtn.addEventListener('click', () => {
    showModal(
        '⚠️ Downgrade to Buyer Account',
        '<p style="color: #ff6b6b; font-weight: 600;">Warning: This action cannot be undone!</p>' +
        '<p>Switching to a <strong>Buyer</strong> account will:</p>' +
        '<ul style="margin-left: 1.5rem; color: var(--light-gray);">' +
        '<li style="color: #ff6b6b;">❌ Remove all your listed products</li>' +
        '<li>Deactivate your seller account</li>' +
        '<li>You will no longer be able to manage your store</li>' +
        '</ul>' +
        '<p>Are you sure you want to continue?</p>',
        async () => {
            try {
                const response = await fetch("{% url 'profiles:switch_account_type_ajax' %}", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-CSRFToken": getCookie("csrftoken"),
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    body: new URLSearchParams({
                        'account_type': 'BUYER'
                    })
                });
                const data = await response.json();
                if (data.success) {
                    showToast(data.message, 'success');
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    showToast(data.error || 'Failed to switch account type', 'error');
                }
            } catch (err) {
                console.error("Account switch failed:", err);
                showToast('Failed to switch account type', 'error');
            }
        }
    );
});
```

**Features:**
- **Modal confirmation:** Prevents accidental account type changes
- **Warning for destructive action:** Red warning text when switching to BUYER
- **Page reload after success:** Ensures UI reflects new permissions
- **Toast notifications:** User feedback via `showToast()`

**Request Format:**
- **Method:** POST
- **Headers:**
  - `Content-Type: application/x-www-form-urlencoded`
  - `X-CSRFToken: <token>`
  - `X-Requested-With: XMLHttpRequest`
- **Body:** `account_type=SELLER` or `account_type=BUYER`

**Response Format:**
```json
{
    "success": true,
    "message": "Account type switched to Seller. You can now list products.",
    "account_type": "SELLER"
}
```

### 4. AJAX Request Pattern

All AJAX requests in the authentication system follow this pattern:

```javascript
// 1. Extract CSRF token
const csrftoken = getCookie("csrftoken");

// 2. Make fetch request
const response = await fetch(url, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",  // or application/x-www-form-urlencoded
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",  // Identifies AJAX request
    },
    body: JSON.stringify(data)  // or new URLSearchParams(data)
});

// 3. Parse JSON response
const result = await response.json();

// 4. Handle success/error
if (result.success) {
    showToast(result.message, 'success');
} else {
    showToast(result.error, 'error');
}
```

### 5. AJAX Validation

**Backend Validation:**
```python
# Check if request is AJAX
if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
    return HttpResponseBadRequest("Invalid request")

# Check HTTP method
if request.method != 'POST':
    return HttpResponseBadRequest("Invalid request")

# Check authentication
if not request.user.is_authenticated:
    return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)
```

**Frontend Error Handling:**
```javascript
try {
    const response = await fetch(url, options);
    const data = await response.json();

    if (!data.success) {
        throw new Error(data.error || "Request failed");
    }

    // Success handling
    showToast(data.message, 'success');

} catch (err) {
    console.error("Request failed:", err);
    showToast('Operation failed', 'error');
    // Rollback optimistic UI changes
}
```

---

## Security Features

### 1. CSRF Protection

**Configuration:** `becathlon/settings.py:36-56`

```python
# CSRF Trusted Origins (for production HTTPS)
CSRF_TRUSTED_ORIGINS = [
    'https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id',
    'https://pbp.cs.ui.ac.id',
    'https://muhammad.vegard.pbp.cs.ui.ac.id',
]

# Production security settings
if not DEBUG:
    SESSION_COOKIE_SECURE = True    # Only send session cookie over HTTPS
    CSRF_COOKIE_SECURE = True       # Only send CSRF cookie over HTTPS
    CSRF_COOKIE_SAMESITE = 'Lax'    # Prevent CSRF attacks
    SESSION_COOKIE_SAMESITE = 'Lax' # Prevent session hijacking
```

**CSRF Middleware:** `django.middleware.csrf.CsrfViewMiddleware` (line 85)

**How It Works:**
1. Django generates a CSRF token per user session
2. Token is stored in cookie (`csrftoken`)
3. Forms include token via `{% csrf_token %}` template tag
4. AJAX requests include token via `X-CSRFToken` header
5. Django validates token on POST requests
6. Invalid/missing token → 403 Forbidden

**Template Usage:**
```django
<form method="POST">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

**AJAX Usage:**
```javascript
headers: {
    "X-CSRFToken": getCookie("csrftoken"),
}
```

### 2. Password Security

**Hashing Algorithm:** PBKDF2 with SHA256 (Django default)

**Validation Rules:** `becathlon/settings.py:156-169`

| Validator | Purpose |
|-----------|---------|
| `UserAttributeSimilarityValidator` | Prevents passwords similar to username/email |
| `MinimumLengthValidator` | Enforces minimum 8 characters |
| `CommonPasswordValidator` | Blocks common passwords (e.g., "password123") |
| `NumericPasswordValidator` | Prevents entirely numeric passwords |

**Example Validation Errors:**
- "This password is too similar to the username."
- "This password is too short. It must contain at least 8 characters."
- "This password is too common."
- "This password is entirely numeric."

### 3. Production Security Headers

**Configuration:** `becathlon/settings.py:45-56`

```python
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True       # Enable browser XSS protection
    SECURE_CONTENT_TYPE_NOSNIFF = True     # Prevent MIME-sniffing
    X_FRAME_OPTIONS = 'DENY'               # Prevent clickjacking
```

**Middleware Stack (Security):**
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',      # Security headers
    'django.middleware.csrf.CsrfViewMiddleware',         # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Auth handling
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
]
```

### 4. Session Security

**Session Backend:** Database-backed sessions (Django default)

**Session Configuration:**
```python
INSTALLED_APPS = [
    'django.contrib.sessions',  # Session support
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
]
```

**Production Session Settings:**
```python
if not DEBUG:
    SESSION_COOKIE_SECURE = True     # HTTPS only
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

**Session Data Stored:**
- User authentication state (user ID)
- Guest cart data (for unauthenticated users)
- CSRF token
- Flash messages

### 5. Access Control

**Login Required Decorator:**
```python
from django.contrib.auth.decorators import login_required

@login_required
def protected_view(request):
    # Only authenticated users can access
    pass
```

**Used in:**
- `/profiles/` - Profile detail
- `/profiles/edit/` - Profile editing
- `/profiles/ajax/toggle-newsletter/` - Newsletter toggle
- `/profiles/ajax/switch-account-type/` - Account type switch
- `/order/checkout/` - Checkout process
- `/order/` - Order list
- All order-related views

**Redirect Behavior:**
- Unauthenticated users → `/auth/login/?next=<original-url>`
- After login → Redirect to `?next` URL or default (home)

### 6. SQL Injection Prevention

Django's ORM automatically prevents SQL injection by using parameterized queries.

**Safe (Django ORM):**
```python
# Automatically escaped
User.objects.get(username=username)
Product.objects.filter(created_by=request.user)
```

**Unsafe (Raw SQL - NOT used in this codebase):**
```python
# NEVER DO THIS
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### 7. XSS Prevention

Django templates automatically escape HTML by default.

**Auto-escaped:**
```django
<p>{{ user.username }}</p>
<!-- Output: &lt;script&gt;alert('xss')&lt;/script&gt; -->
```

**Manual escaping:**
```python
from django.utils.html import escape
safe_text = escape(user_input)
```

---

## Cart Integration

One of the most important features of the authentication system is seamless cart transfer when users log in.

### 1. Cart Model Structure

**Location:** `apps/cart/models.py:6-79`

```python
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='cart')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Design:**
- **Authenticated users:** `user` field is set, `session_key` is null
- **Guest users:** `session_key` is set (Django session ID), `user` is null
- **Dual identification:** Allows cart persistence before and after login

### 2. Cart Utility Functions

**Location:** `apps/cart/utils.py`

#### get_or_create_cart()

```python
def get_or_create_cart(request):
    """
    Get existing cart or create new one for user/session
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart
```

**Flow:**
1. Check if user is authenticated
2. **If authenticated:** Find/create cart by `user` field
3. **If not authenticated:**
   - Get session key (create session if needed)
   - Find/create cart by `session_key` field
4. Return cart object

#### transfer_guest_cart_to_user()

**Called automatically during login** (`apps/authentication/views.py:52`)

```python
def transfer_guest_cart_to_user(request):
    """
    Called after user login to merge guest cart into user cart
    """
    if not request.user.is_authenticated:
        return

    session_key = request.session.session_key
    if not session_key:
        return

    try:
        guest_cart = Cart.objects.get(session_key=session_key)
        user_cart, created = Cart.objects.get_or_create(user=request.user)

        if guest_cart != user_cart:
            user_cart.merge_carts(guest_cart)
    except Cart.DoesNotExist:
        pass
```

**Flow:**
1. Check if user is authenticated (should always be true when called from login)
2. Get current session key
3. Try to find guest cart by session key
4. Get or create user's cart
5. If carts are different, merge guest cart into user cart
6. Guest cart is deleted after merge (handled by `merge_carts()`)

### 3. Cart Merge Logic

The `merge_carts()` method (in `Cart` model) handles:

1. **Combining cart items:**
   - If product exists in both carts → increase quantity
   - If product only in guest cart → move to user cart
2. **Deleting guest cart:**
   - After merge, guest cart is deleted
3. **Preserving timestamps:**
   - User cart `updated_at` is updated

### 4. Login Flow with Cart Transfer

```
┌─────────────────────────────────────────────────────────────────┐
│  User adds products to cart as guest                            │
│  Cart: session_key="abc123", user=null                          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  User clicks "Login"                                             │
│  Redirected to /auth/login/                                      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  User submits credentials                                        │
│  authenticate() → login() → transfer_guest_cart_to_user()        │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  Cart merge:                                                     │
│  1. Find guest cart (session_key="abc123")                       │
│  2. Find/create user cart (user=User object)                     │
│  3. Merge items from guest cart → user cart                      │
│  4. Delete guest cart                                            │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  User redirected to home page                                    │
│  Cart now: user=User object, session_key=null                    │
│  All guest cart items preserved!                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Cart Context Processor

**Location:** `apps/cart/context_processors.py`

```python
def cart_context(request):
    """Add cart and cart item count to all template contexts"""
    cart = get_or_create_cart(request)
    return {
        'cart': cart,
        'cart_item_count': cart.items.count() if cart else 0,
    }
```

**Configuration:** `becathlon/settings.py:101`

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'apps.cart.context_processors.cart_context',  # Add cart to all templates
            ],
        },
    },
]
```

**Usage in Templates:**
```django
<!-- Available in ALL templates without passing explicitly -->
<a href="{% url 'cart:view' %}">
    Cart ({{ cart_item_count }})
</a>
```

---

## Architecture Diagrams

### 1. Authentication Flow Diagram

```
                    ┌──────────────┐
                    │ User Visits  │
                    │  Website     │
                    └──────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Already Have   │
                  │  Account?      │
                  └────┬───────┬───┘
                       │       │
                  YES  │       │  NO
                       │       │
                       ▼       ▼
            ┌──────────────┐ ┌──────────────┐
            │ /auth/login/ │ │/auth/signup/ │
            └──────┬───────┘ └──────┬───────┘
                   │                │
                   │                ▼
                   │      ┌─────────────────┐
                   │      │  SignUpForm     │
                   │      │  • username     │
                   │      │  • email        │
                   │      │  • password     │
                   │      │  • account_type │
                   │      └────────┬────────┘
                   │               │
                   │               ▼
                   │      ┌─────────────────┐
                   │      │  Create User    │
                   │      │  Create Customer│
                   │      │  Create Profile │
                   │      └────────┬────────┘
                   │               │
                   │               ▼
                   │      ┌─────────────────┐
                   │      │ Redirect to     │
                   │      │ /auth/login/    │
                   │      └────────┬────────┘
                   │               │
                   ◄───────────────┘
                   │
                   ▼
        ┌────────────────────┐
        │ AuthenticationForm │
        │  • username        │
        │  • password        │
        └──────────┬─────────┘
                   │
                   ▼
        ┌────────────────────┐
        │  authenticate()    │
        │  Verify password   │
        └──────────┬─────────┘
                   │
            ┌──────┴──────┐
            │             │
          VALID       INVALID
            │             │
            ▼             ▼
   ┌────────────────┐  ┌────────────────┐
   │   login(user)  │  │  Show Error    │
   │ Create session │  │  Re-render form│
   └────────┬───────┘  └────────────────┘
            │
            ▼
   ┌────────────────────┐
   │ transfer_guest_cart│
   │   _to_user()       │
   └────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │  Redirect to home  │
   │  User authenticated│
   └────────────────────┘
```

### 2. Database Schema Diagram

```
┌──────────────────────────────┐
│      django_user (Built-in)  │
├──────────────────────────────┤
│ id (PK)                      │
│ username                     │
│ email                        │
│ password (hashed)            │
│ first_name                   │
│ last_name                    │
│ is_active                    │
│ is_staff                     │
│ date_joined                  │
│ last_login                   │
└──────┬──────────────────┬────┘
       │                  │
       │                  │
       │ 1:1              │ 1:1
       │                  │
       ▼                  ▼
┌──────────────┐    ┌─────────────────────┐
│   Customer   │    │      Profile        │
├──────────────┤    ├─────────────────────┤
│ id (PK)      │    │ id (PK)             │
│ user_id (FK) │    │ user_id (FK)        │
│ phone_number │    │ first_name          │
│ address      │    │ last_name           │
│ created_at   │    │ phone               │
└──────────────┘    │ email               │
                    │ preferred_sports    │
                    │ profile_picture     │
                    │ newsletter_opt_in   │
                    │ account_type        │
                    │   (BUYER/SELLER)    │
                    │ created_at          │
                    │ updated_at          │
                    └─────────────────────┘

┌─────────────────────────────┐
│   django_session (Built-in) │
├─────────────────────────────┤
│ session_key (PK)            │
│ session_data (encrypted)    │
│ expire_date                 │
└─────────────────────────────┘
        │
        │ Used by
        │
        ▼
┌─────────────────┐
│      Cart       │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │──┐ Either user_id OR session_key
│ session_key     │──┘ is set (not both)
│ created_at      │
│ updated_at      │
└─────────────────┘
```

### 3. AJAX Request Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│              Frontend (JavaScript)                       │
└────────────────────┬─────────────────────────────────────┘
                     │
                     │ 1. User action (click, toggle)
                     │
                     ▼
          ┌──────────────────────┐
          │  getCookie()         │
          │  Extract CSRF token  │
          └──────────┬───────────┘
                     │
                     │ 2. Prepare request
                     │
                     ▼
          ┌──────────────────────────┐
          │  fetch(url, {            │
          │    method: "POST",       │
          │    headers: {            │
          │      X-CSRFToken,        │
          │      X-Requested-With    │
          │    },                    │
          │    body: data            │
          │  })                      │
          └──────────┬───────────────┘
                     │
                     │ 3. HTTP POST request
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│              Backend (Django View)                         │
├────────────────────────────────────────────────────────────┤
│  @login_required                                           │
│  def ajax_view(request):                                   │
│      # 4. Validate request                                 │
│      if not AJAX or not POST:                              │
│          return HttpResponseBadRequest()                   │
│                                                            │
│      # 5. Process data                                     │
│      profile = request.user.profile                        │
│      profile.field = new_value                             │
│      profile.save()                                        │
│                                                            │
│      # 6. Return JSON response                             │
│      return JsonResponse({                                 │
│          "success": True,                                  │
│          "data": {...},                                    │
│          "error": None                                     │
│      })                                                    │
└────────────────────┬───────────────────────────────────────┘
                     │
                     │ 7. JSON response
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│              Frontend (JavaScript)                         │
├────────────────────────────────────────────────────────────┤
│  const data = await response.json()                        │
│                                                            │
│  if (data.success) {                                       │
│      // 8. Update UI                                       │
│      showToast(data.message, 'success')                    │
│      location.reload() // if needed                        │
│  } else {                                                  │
│      // 9. Handle error                                    │
│      showToast(data.error, 'error')                        │
│      // Rollback optimistic UI changes                     │
│  }                                                         │
└────────────────────────────────────────────────────────────┘
```

### 4. Cart Transfer Flow Diagram

```
BEFORE LOGIN (Guest User)
┌─────────────────────────────────────┐
│  Session: abc123                    │
│                                     │
│  Cart:                              │
│    user_id: NULL                    │
│    session_key: "abc123"            │
│                                     │
│  CartItems:                         │
│    - Product A (qty: 2)             │
│    - Product B (qty: 1)             │
└─────────────────────────────────────┘

            │
            │ User logs in
            │ login_view() called
            │
            ▼

┌─────────────────────────────────────┐
│  transfer_guest_cart_to_user()      │
│                                     │
│  1. Find guest cart (session="abc") │
│  2. Find/create user cart (user=5)  │
│  3. Merge items:                    │
│     - Product A: 2 → user cart      │
│     - Product B: 1 → user cart      │
│  4. Delete guest cart               │
└─────────────────────────────────────┘

            │
            │
            ▼

AFTER LOGIN (Authenticated User)
┌─────────────────────────────────────┐
│  User ID: 5                         │
│                                     │
│  Cart:                              │
│    user_id: 5                       │
│    session_key: NULL                │
│                                     │
│  CartItems:                         │
│    - Product A (qty: 2)             │
│    - Product B (qty: 1)             │
│                                     │
│  ✓ All items preserved!             │
└─────────────────────────────────────┘
```

---

## Summary

The Becathlon authentication system is a well-architected Django application that provides:

### Key Features
- **Dual-profile system:** Customer + Profile models extend Django User
- **Account types:** BUYER and SELLER with different permissions
- **Secure authentication:** CSRF protection, password hashing, session security
- **AJAX enhancements:** Newsletter toggle, account type switching
- **Seamless cart transfer:** Guest carts automatically merge on login
- **Production-ready security:** HTTPS enforcement, secure cookies, XSS protection

### Technology Stack
- **Backend:** Django 5.2.5
- **Database:** PostgreSQL (production) / SQLite (development)
- **Frontend:** Vanilla JavaScript (Fetch API)
- **Session:** Database-backed sessions
- **Authentication:** Django's built-in auth framework

### File Locations Quick Reference
| Component | File Path |
|-----------|-----------|
| Authentication Views | `apps/authentication/views.py` |
| Authentication URLs | `apps/authentication/urls.py` |
| Signup Form | `apps/authentication/forms.py` |
| Customer Model | `apps/main/models.py` |
| Profile Model | `apps/profiles/models.py` |
| Profile Views | `apps/profiles/views.py` |
| Cart Utils | `apps/cart/utils.py` |
| Database Config | `becathlon/settings.py` |
| AJAX Implementation | `apps/profiles/templates/profiles/profile_detail.html` |

### Best Practices Followed
✅ Separation of concerns (apps for different features)
✅ DRY principle (reusable forms, utilities)
✅ Security-first approach (CSRF, password validation, HTTPS)
✅ User experience (cart preservation, AJAX updates)
✅ Production-ready configuration (environment variables, fallbacks)

---

**Documentation Version:** 1.0
**Last Updated:** 2025-11-08
**Author:** Becathlon Development Team
