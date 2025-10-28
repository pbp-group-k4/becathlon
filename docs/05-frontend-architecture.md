# Frontend Architecture & Implementation

Comprehensive guide to Becathlon's frontend components, styling system, and JavaScript patterns.

## Frontend Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Markup | HTML5 | Semantic structure |
| Styling | CSS3 with CSS Variables | Design system & theming |
| Scripting | Vanilla JavaScript | AJAX, interactions |
| Libraries | jQuery (optional) | DOM manipulation |
| Framework | Bootstrap 5 (planned) | Grid and utilities |
| Icons | Font Awesome (optional) | UI icons |

## Design System

### CSS Variables (Root Theme)

```css
:root {
    /* Colors */
    --primary-black: #0a0a0a;
    --secondary-black: #1a1a1a;
    --accent-gray: #2a2a2a;
    --light-gray: #a0a0a0;
    --ultra-light: #f5f5f5;
    
    /* Accents */
    --accent-gold: #d4af37;      /* Primary CTAs */
    --accent-blue: #0066ff;      /* Links, interactive */
    --success-green: #10b981;
    --danger-red: #ef4444;
    --warning-orange: #f59e0b;
}
```

### Color Usage Guidelines

- **Primary Black (#0a0a0a)**: Page backgrounds, main containers
- **Accent Gold (#d4af37)**: Buttons, "Add to Cart", prominent CTAs
- **Accent Blue (#0066ff)**: Links, secondary actions
- **Green (#10b981)**: Success messages, checkmarks
- **Red (#ef4444)**: Error messages, destructive actions
- **Orange (#f59e0b)**: Warning states, alerts

## CSS Architecture

### File Organization

```
apps/
├── catalog/
│   └── static/catalog/css/
│       ├── catalog.css (1179 lines) - Modern modular approach
│       └── components.css - Reusable components
│
├── order/
│   └── templates/order/
│       └── checkout.html - Inline <style> block
│
├── cart/
│   └── static/cart/css/
│       └── cart.css - Cart-specific styles
│
└── main/
    ├── static/main/css/
    │   └── home.css - Homepage styles
    └── templates/
        └── base.html - Inline global styles
```

### Pattern Selection

**Use External CSS** (`apps/<app>/static/<app>/css/`) for:
- Catalog and product pages
- Reusable component libraries
- Large stylesheets (>500 lines)
- Multi-page consistency

**Use Inline Styles** (`<style>` in template) for:
- One-off pages (checkout, order confirmation)
- Self-contained layouts
- Production-quality forms (like checkout.html)
- Unique visual treatments

## CSS Components

### 1. Glassmorphism Pattern

```css
.card {
    background: rgba(26, 26, 26, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 4px;
}
```

**Used for:**
- Sidebar containers
- Modal overlays
- Card components
- Form containers

**Benefits:**
- Modern, sophisticated appearance
- Subtle depth with blur effect
- Consistent with design system

### 2. Text Gradients

```css
.heading {
    background: linear-gradient(to right, #ffffff, #a0a0a0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.05em;
}
```

**Used for:**
- Headings and titles
- Featured product names
- Call-to-action text

### 3. Button Styles

```css
/* Primary Button - Gold */
.btn-primary {
    background: var(--accent-gold);
    color: var(--primary-black);
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    transform: scale(1.05);
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}

/* Secondary Button - Outline */
.btn-secondary {
    background: transparent;
    color: var(--light-gray);
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.75rem 1.5rem;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-secondary:hover {
    border-color: var(--accent-gold);
    color: var(--ultra-light);
}
```

### 4. Product Grid Layout

```css
.product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 2rem;
    padding: 2rem 3rem;
}

@media (max-width: 1024px) {
    .product-grid {
        grid-template-columns: repeat(3, 1fr);
    }
}

@media (max-width: 768px) {
    .product-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        padding: 1rem;
    }
}

@media (max-width: 480px) {
    .product-grid {
        grid-template-columns: 1fr;
    }
}
```

**Features:**
- Responsive breakpoints (1200px, 1024px, 768px, 480px)
- Auto-fit columns with minimum width
- Mobile-first approach
- Maintains aspect ratio with gap

### 5. Sidebar Layout

```css
.catalog-wrapper {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 3rem;
}

.sidebar {
    background: rgba(26, 26, 26, 0.6);
    padding: 2rem;
    border-radius: 4px;
    height: fit-content;
    position: sticky;
    top: 100px;
}
```

**Features:**
- Fixed width sidebar (280px)
- Sticky positioning for filtering
- Responsive (stacks on mobile)

### 6. Form Styling

```css
.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--ultra-light);
    font-weight: 600;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

input[type="text"],
input[type="email"],
input[type="password"],
textarea,
select {
    width: 100%;
    padding: 0.75rem 1rem;
    background: rgba(26, 26, 26, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    color: var(--ultra-light);
    font-family: inherit;
    transition: all 0.3s ease;
}

input:focus,
textarea:focus,
select:focus {
    background: rgba(26, 26, 26, 1);
    border-color: var(--accent-gold);
    outline: none;
    box-shadow: 0 0 10px rgba(212, 175, 55, 0.2);
}

.form-error {
    color: var(--danger-red);
    font-size: 0.85rem;
    margin-top: 0.25rem;
}
```

## JavaScript Architecture

### Module Structure

Each app has dedicated JavaScript file(s):

```
apps/
├── catalog/static/catalog/js/
│   ├── catalog.js (360 lines)
│   │   ├── initCategoryFilters()
│   │   ├── initQuickView()
│   │   ├── initAjaxFilters()
│   │   └── Search & filter logic
│   └── index.js (if needed)
│
├── cart/static/cart/js/
│   ├── cart.js (274 lines)
│   │   ├── addToCart()
│   │   ├── removeFromCart()
│   │   ├── updateCartItem()
│   │   ├── refreshCartCount()
│   │   └── Notification system
│   └── index.js (if needed)
│
├── order/static/order/js/
│   ├── order_detail.js
│   │   ├── Delivery status polling
│   │   ├── Rating form handling
│   │   └── Timeline visualization
│   └── checkout.js (if needed)
│
└── main/static/main/js/
    ├── hero.js - Animations & hero section
    ├── product_detail.js - Gallery & variants
    └── global.js - Shared utilities
```

### Global Utilities

**CSRF Token Retrieval:**
```javascript
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split('; ')
               .find(row => row.startsWith('csrftoken='))
               ?.split('=')[1];
}
```

**Notification System:**
```javascript
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        notification.remove();
    }, 3000);
}
```

### AJAX Pattern

Standard fetch API pattern used throughout:

```javascript
function makeAjaxRequest(url, method = 'POST', data = null) {
    const formData = new FormData();
    
    if (data) {
        Object.entries(data).forEach(([key, value]) => {
            formData.append(key, value);
        });
    }
    
    formData.append('csrfmiddlewaretoken', getCSRFToken());
    
    return fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            throw new Error(data.error || 'Operation failed');
        }
        return data;
    })
    .catch(error => {
        console.error('AJAX Error:', error);
        showNotification(error.message, 'error');
        throw error;
    });
}
```

### Event Handling Pattern

```javascript
// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Event delegation for dynamic elements
    document.addEventListener('click', handleClick);
    document.addEventListener('change', handleChange);
    document.addEventListener('submit', handleSubmit);
}

function handleClick(event) {
    const target = event.target;
    
    if (target.matches('.add-to-cart-btn')) {
        handleAddToCart(event);
    }
    
    if (target.matches('.remove-item-btn')) {
        handleRemoveItem(event);
    }
    
    if (target.matches('.modal-close')) {
        handleCloseModal(event);
    }
}
```

## Template System

### Base Templates

**main/base.html** (Legacy)
```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Becathlon{% endblock %}</title>
    <style>
        /* Inline global styles */
    </style>
</head>
<body>
    {% include 'includes/nav.html' %}
    {% block content %}{% endblock %}
    {% include 'includes/footer.html' %}
</body>
</html>
```

**catalog/base_catalog.html** (Modern)
```html
{% extends 'base.html' %}
{% load static %}

{% block head_extra %}
    <link rel="stylesheet" href="{% static 'catalog/css/catalog.css' %}">
{% endblock %}

{% block content %}
    <div class="catalog-container">
        {% block catalog_content %}{% endblock %}
    </div>
    <script src="{% static 'catalog/js/catalog.js' %}"></script>
{% endblock %}
```

### Context Variables (Always Available)

```python
# From cart context processor
{
    'cart': Cart_instance,
    'cart_item_count': int,
    
    # From Django
    'user': User_instance,
    'user.is_authenticated': bool,
}
```

### Template Conventions

**Variable Naming:**
- Single item: `product`
- Collections: `products`
- Paginated: `page_obj`
- Forms: `form`
- Context flags: `is_admin`, `user_can_edit`

**Template Tags:**
```django
{% load static %}
{% load catalog_extras %}

<!-- Image with lazy loading -->
<img src="{% static 'images/placeholder.jpg' %}"
     data-src="{{ product.image_url }}"
     loading="lazy"
     alt="{{ product.name }}">

<!-- Form rendering -->
{% for field in form %}
    <div class="form-group">
        {{ field.label_tag }}
        {{ field }}
        {% if field.errors %}
            <div class="form-error">{{ field.errors }}</div>
        {% endif %}
    </div>
{% endfor %}

<!-- Conditional rendering -->
{% if user.is_authenticated %}
    <a href="{% url 'order:order_list' %}">My Orders</a>
{% else %}
    <a href="{% url 'auth:login' %}">Login</a>
{% endif %}
```

## Responsive Design

### Breakpoints

```css
/* Mobile first */
@media (min-width: 576px) {
    /* Small devices (landscape phones) */
}

@media (min-width: 768px) {
    /* Medium devices (tablets) */
}

@media (min-width: 992px) {
    /* Large devices (desktops) */
}

@media (min-width: 1200px) {
    /* Extra large devices (large desktops) */
}

@media (max-width: 480px) {
    /* Mobile (single column) */
}
```

### Responsive Typography

```css
html {
    font-size: 16px;
}

h1 {
    font-size: clamp(1.5rem, 5vw, 3rem);
}

p {
    font-size: clamp(0.875rem, 2vw, 1rem);
}
```

## Accessibility

### ARIA Attributes

```html
<!-- Screen reader labels -->
<button aria-label="Add product to cart">
    <span aria-hidden="true">+</span>
</button>

<!-- Live regions for updates -->
<div role="status" aria-live="polite" aria-atomic="true">
    {{ notification_message }}
</div>

<!-- Button groups -->
<div role="toolbar" aria-label="Product actions">
    <button>Add to Cart</button>
    <button>Save for Later</button>
</div>
```

### Color Contrast

- Text on dark backgrounds: Use `--ultra-light` (#f5f5f5)
- Text on light backgrounds: Use `--primary-black` (#0a0a0a)
- Minimum contrast ratio: 4.5:1 (WCAG AA)

### Keyboard Navigation

- Tab through interactive elements
- Enter/Space to activate buttons
- Escape to close modals
- Arrow keys for carousels

## Performance Optimization

### Image Loading

```html
<!-- Lazy load images -->
<img src="{% static 'placeholder.jpg' %}"
     data-src="{{ product.image_url }}"
     loading="lazy"
     alt="{{ product.name }}"
     width="300"
     height="300">
```

### CSS Optimization

- Use CSS variables for theming
- Minimize inline styles
- Leverage CSS grid and flexbox
- Avoid heavy animations on scroll

### JavaScript Optimization

- Event delegation instead of individual listeners
- Debounce/throttle frequent events
- Minimize DOM manipulation
- Use fetch instead of AJAX for modern browsers

### Caching

```javascript
// Cache DOM elements
const cartBadge = document.querySelector('.cart-badge');
const cartCount = document.querySelector('.cart-count');

// Reuse cached elements
function updateCartBadge(count) {
    cartCount.textContent = count;
    cartBadge.style.display = count > 0 ? 'block' : 'none';
}
```

---

**Next**: [Development Guide](./06-development-guide.md)
