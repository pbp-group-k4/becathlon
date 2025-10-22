# Ambient Lighting Customization Guide

## Overview
The product detail page now features YouTube-style ambient lighting that adapts to the dominant colors in the product image, creating an immersive visual experience.

## How It Works

### Automatic Color Extraction
The JavaScript in `apps/main/static/main/js/product_detail.js` automatically:
1. Loads the product image
2. Extracts the dominant color using HTML5 Canvas
3. Applies the color to create a subtle ambient glow effect
4. Falls back to neutral white if color extraction fails (CORS issues)

### CSS Variables Used

The ambient effect is controlled by **4 CSS custom properties**:

```css
--ambient-color: rgba(R, G, B, opacity)   /* Inner inset glow */
--ambient-glow: rgba(R, G, B, opacity)    /* Middle shadow layer */
--ambient-outer: rgba(R, G, B, opacity)   /* Outer glow effect */
--ambient-border: rgba(R, G, B, opacity)  /* Border highlight */
```

## Adjusting Brightness & Opacity

### Understanding the Values

Each `rgba()` color has 4 components:
- **R, G, B**: Red, Green, Blue values (0-255) - extracted from image
- **opacity**: Transparency (0.0 = invisible, 1.0 = fully opaque)

### Current Default Values

Located in `apps/main/static/main/js/product_detail.js` (lines ~70-73):

```javascript
container.style.setProperty('--ambient-color', `rgba(${r}, ${g}, ${b}, 0.12)`);
container.style.setProperty('--ambient-glow', `rgba(${r}, ${g}, ${b}, 0.15)`);
container.style.setProperty('--ambient-outer', `rgba(${r}, ${g}, ${b}, 0.08)`);
container.style.setProperty('--ambient-border', `rgba(${r}, ${g}, ${b}, 0.12)`);
```

### Customization Examples

#### Make Ambient Effect Brighter
Increase the **4th parameter** (opacity):

```javascript
// Original (subtle)
container.style.setProperty('--ambient-color', `rgba(${r}, ${g}, ${b}, 0.12)`);

// Brighter
container.style.setProperty('--ambient-color', `rgba(${r}, ${g}, ${b}, 0.25)`);

// Very bright
container.style.setProperty('--ambient-color', `rgba(${r}, ${g}, ${b}, 0.40)`);
```

#### Make Ambient Effect More Subtle
Decrease the opacity:

```javascript
// Very subtle
container.style.setProperty('--ambient-color', `rgba(${r}, ${g}, ${b}, 0.05)`);
container.style.setProperty('--ambient-glow', `rgba(${r}, ${g}, ${b}, 0.08)`);
```

#### Increase Outer Glow Radius
Modify the `box-shadow` blur radius in `product_detail.css`:

```css
.product-image.ambient-active {
    box-shadow: 
        inset 0 0 60px var(--ambient-color),      /* 60px = blur radius */
        0 20px 60px var(--ambient-glow),          /* 60px = blur radius */
        0 0 150px var(--ambient-outer);           /* Increase from 100px to 150px */
}
```

#### Adjust Border Brightness
Change border opacity independently:

```css
border: 1px solid var(--ambient-border);
/* Or set a fixed value: */
border: 1px solid rgba(255, 255, 255, 0.15);  /* Brighter white border */
```

## Quick Reference Table

| Property | Purpose | Default Opacity | Brightness Level |
|----------|---------|----------------|------------------|
| `--ambient-color` | Inner glow (inset) | 0.12 | Subtle |
| `--ambient-glow` | Middle shadow | 0.15 | Medium |
| `--ambient-outer` | Outer halo | 0.08 | Very subtle |
| `--ambient-border` | Border highlight | 0.12 | Subtle |

## Fallback Values

When color extraction fails (CORS errors), these fallback values are used:

```javascript
container.style.setProperty('--ambient-color', 'rgba(255, 255, 255, 0.05)');
container.style.setProperty('--ambient-glow', 'rgba(255, 255, 255, 0.08)');
container.style.setProperty('--ambient-outer', 'rgba(255, 255, 255, 0.04)');
container.style.setProperty('--ambient-border', 'rgba(255, 255, 255, 0.06)');
```

You can make these brighter by increasing the opacity values.

## Files to Edit

- **JavaScript (color extraction)**: `apps/main/static/main/js/product_detail.js`
- **CSS (shadow effects)**: `apps/main/static/main/css/product_detail.css`

## Testing Changes

1. Edit the opacity values in the JavaScript file
2. Refresh the page (Ctrl+Shift+R to bypass cache)
3. View different products to see how colors adapt
4. Adjust until you achieve the desired effect

## Recommended Settings

### Subtle (Current - YouTube-like)
```javascript
opacity: 0.12, 0.15, 0.08, 0.12
```

### Medium (More Visible)
```javascript
opacity: 0.20, 0.25, 0.15, 0.18
```

### Bold (Very Noticeable)
```javascript
opacity: 0.30, 0.35, 0.22, 0.25
```

### Minimal (Barely Visible)
```javascript
opacity: 0.05, 0.08, 0.04, 0.06
```
