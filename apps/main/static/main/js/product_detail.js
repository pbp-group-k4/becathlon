// Product Detail Page JavaScript - Becathlon

// Quantity selector functions
function changeQuantity(delta) {
    const input = document.getElementById('product-quantity');
    if (!input) return;
    
    const currentValue = parseInt(input.value);
    const newValue = currentValue + delta;
    const max = parseInt(input.max);
    const min = parseInt(input.min);

    if (newValue >= min && newValue <= max) {
        input.value = newValue;
        // Trigger input event to ensure consistency
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

// YouTube-style ambient lighting effect
function applyAmbientLighting() {
    const productImage = document.querySelector('.product-image');
    const img = productImage ? productImage.querySelector('img') : null;
    
    if (!img || !productImage) return;
    
    // Wait for image to load
    if (!img.complete) {
        img.addEventListener('load', () => extractAndApplyColor(img, productImage));
    } else {
        extractAndApplyColor(img, productImage);
    }
}

function extractAndApplyColor(img, container) {
    try {
        // Create a canvas to extract dominant color
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas size (smaller for performance)
        canvas.width = 100;
        canvas.height = 100;
        
        // Draw image scaled down
        ctx.drawImage(img, 0, 0, 100, 100);
        
        // Get image data - this will throw an error if CORS is not allowed
        const imageData = ctx.getImageData(0, 0, 100, 100).data;
        
        // Calculate weighted average color (focusing on mid-tones)
        let r = 0, g = 0, b = 0, count = 0;
        
        for (let i = 0; i < imageData.length; i += 4) {
            const pixelR = imageData[i];
            const pixelG = imageData[i + 1];
            const pixelB = imageData[i + 2];
            const pixelA = imageData[i + 3];
            
            // Skip transparent pixels
            if (pixelA < 128) continue;
            
            // Calculate brightness
            const brightness = (pixelR + pixelG + pixelB) / 3;
            
            // Focus on mid-tone colors (avoid pure black and pure white)
            if (brightness > 20 && brightness < 235) {
                r += pixelR;
                g += pixelG;
                b += pixelB;
                count++;
            }
        }
        
        if (count > 0) {
            r = Math.floor(r / count);
            g = Math.floor(g / count);
            b = Math.floor(b / count);
            
            // Boost saturation slightly for more vibrant glow
            const max = Math.max(r, g, b);
            const min = Math.min(r, g, b);
            const saturation = max > 0 ? ((max - min) / max) : 0;
            
            // If color is too desaturated (close to grey), try to enhance it
            if (saturation < 0.1) {
                // Fall back to subtle white glow for neutral/grey images
                container.style.setProperty('--ambient-glow', 'rgba(255, 255, 255, 0.12)');
                container.style.setProperty('--ambient-outer', 'rgba(255, 255, 255, 0.08)');
                container.style.setProperty('--ambient-far', 'rgba(255, 255, 255, 0.04)');
            } else {
                // Apply the extracted color for vibrant glow
                container.style.setProperty('--ambient-glow', `rgba(${r}, ${g}, ${b}, 0.15)`);
                container.style.setProperty('--ambient-outer', `rgba(${r}, ${g}, ${b}, 0.10)`);
                container.style.setProperty('--ambient-far', `rgba(${r}, ${g}, ${b}, 0.05)`);
            }
            
            // Add the ambient-active class
            container.classList.add('ambient-active');
        } else {
            // No suitable pixels found, use white glow
            applyWhiteGlow(container);
        }
    } catch (e) {
        // CORS error or other image processing error
        console.log('Could not extract color from image (likely CORS restricted):', e.message);
        // Apply a subtle white glow as fallback
        applyWhiteGlow(container);
    }
}

function applyWhiteGlow(container) {
    container.style.setProperty('--ambient-glow', 'rgba(255, 255, 255, 0.12)');
    container.style.setProperty('--ambient-outer', 'rgba(255, 255, 255, 0.08)');
    container.style.setProperty('--ambient-far', 'rgba(255, 255, 255, 0.04)');
    container.classList.add('ambient-active');
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Apply ambient lighting effect
    applyAmbientLighting();
    
    // Quantity input validation
    const quantityInput = document.getElementById('product-quantity');
    if (quantityInput) {
        quantityInput.addEventListener('input', function() {
            const value = parseInt(this.value);
            const min = parseInt(this.min);
            const max = parseInt(this.max);

            if (isNaN(value) || value < min) this.value = min;
            if (value > max) this.value = max;
        });
    }

    // Quantity decrease button - with multiple event listener approaches for reliability
    const decreaseBtn = document.querySelector('.quantity-decrease');
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            changeQuantity(-1);
        });
        // Ensure button is always clickable
        decreaseBtn.style.pointerEvents = 'auto';
    }

    // Quantity increase button - with multiple event listener approaches for reliability
    const increaseBtn = document.querySelector('.quantity-increase');
    if (increaseBtn) {
        increaseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            changeQuantity(1);
        });
        // Ensure button is always clickable
        increaseBtn.style.pointerEvents = 'auto';
    }

    // Add to cart button
    const addToCartBtn = document.querySelector('.btn-add-to-cart');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const productId = this.getAttribute('data-product-id');
            const quantityElem = document.getElementById('product-quantity');
            const quantity = quantityElem ? parseInt(quantityElem.value) : 1;
            
            // Call addToCart function from cart.js
            if (typeof addToCart === 'function') {
                addToCart(productId, quantity);
            } else {
                console.error('addToCart function not found. Make sure cart.js is loaded.');
            }
        });
        // Ensure button is always clickable
        addToCartBtn.style.pointerEvents = 'auto';
    }
});
