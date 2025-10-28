# Frontend Architecture & Implementation

Comprehensive guide to Becathlon's frontend design system, CSS architecture, JavaScript patterns, and template hierarchy.

## Design System

### CSS Variables (Custom Properties)

```css
:root {
    /* Color Palette */
    --primary-black: #0a0a0a;           /* Page background */
    --secondary-black: #1a1a1a;         /* Card backgrounds */
    --accent-gray: #2a2a2a;             /* Accent elements */
    --light-gray: #a0a0a0;              /* Text secondary */
    --ultra-light: #f5f5f5;             /* Text primary */
    
    /* Accent Colors */
    --accent-gold: #d4af37;             /* Primary CTAs, highlights */
    --accent-blue: #0066ff;             /* Links, interactive */
    
    /* Status Colors */
    --success-green: #10b981;           /* Success states */
    --danger-red: #ef4444;              /* Errors */
    --warning-orange: #f59e0b;          /* Warnings */
}
```

### Typography

```css
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-weight: 300;
    color: var(--ultra-light);
    letter-spacing: 0.05em;
}

h1, h2, h3 {
    font-weight: 600;
    letter-spacing: 0.05em;
}

/* Text gradient (headings) */
.gradient-text {
    background: linear-gradient(to right, #fff, #aaa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
```

### Glassmorphism Effects

```css
.glass-container {
    background: rgba(26, 26, 26, 0.6);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 4px;
}

.glass-panel {
    background: rgba(10, 10, 10, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
```

### Button Styles

**Primary Button (CTAs):**
```css
.btn-primary {
    background-color: var(--accent-gold);
    color: var(--primary-black);
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 16px rgba(212, 175, 55, 0.3);
}
```

## Module Pattern Examples

### cart.js Pattern

```javascript
function addToCart(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    
    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken(),
        },
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message);
            refreshCartCount();
        }
    });
}
```

## Performance Optimization

- Lazy loading for images: `loading="lazy"`
- Debounced search/filter events
- Event delegation for dynamic elements
- CSS containment for sidebars
- Transform animations (GPU accelerated)

## Accessibility

- Semantic HTML (nav, main, article)
- ARIA labels and roles
- Keyboard navigation support
- Skip links
- Alt text for images
- Form labels associated with inputs

---

**Next**: [Development Guide](./06-development-guide.md)
