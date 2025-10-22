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
    }
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
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

    // Quantity decrease button
    const decreaseBtn = document.querySelector('.quantity-decrease');
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function() {
            changeQuantity(-1);
        });
    }

    // Quantity increase button
    const increaseBtn = document.querySelector('.quantity-increase');
    if (increaseBtn) {
        increaseBtn.addEventListener('click', function() {
            changeQuantity(1);
        });
    }

    // Add to cart button
    const addToCartBtn = document.querySelector('.btn-add-to-cart');
    if (addToCartBtn) {
        addToCartBtn.addEventListener('click', function() {
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
    }
});
