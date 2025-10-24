// Cart JavaScript - Becathlon

// CSRF token setup for AJAX requests
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
}

// Show notification
function showNotification(message, type = 'success') {
    // Hide ALL notifications - just log to console
    console.log(`[${type.toUpperCase()}]:`, message);
    return; // Don't show any popups
    
    /* Original code kept for reference
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
    */
}

// Add to cart
function addToCart(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    fetch(`/cart/add/${productId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(async response => {
        const data = await response.json();

        if (data && data.success) {
            showNotification(data.message);
            refreshCartCount();
            refreshCartBadge();
        } else {
            const errorMessage = data?.error || 'Unable to add to cart';
            showNotification(errorMessage, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while adding to cart', 'error');
    });
}

// Update cart item quantity
function updateCartItem(itemId, quantity) {
    const formData = new FormData();
    formData.append('quantity', quantity);
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    const itemElement = document.querySelector(`[data-item-id="${itemId}"]`);
    if (itemElement) {
        itemElement.classList.add('loading');
    }

    fetch(`/cart/update/${itemId}/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (quantity === 0) {
                // Item removed
                if (itemElement) {
                    itemElement.remove();
                }
                // Check if cart is empty
                const cartItems = document.querySelectorAll('.cart-item');
                if (cartItems.length === 1) {
                    location.reload(); // Reload to show empty cart state
                }
            } else {
                // Update subtotal
                if (itemElement) {
                    const subtotalElement = itemElement.querySelector('.item-subtotal');
                    if (subtotalElement) {
                        subtotalElement.textContent = `$${data.item_subtotal.toFixed(2)}`;
                    }
                    itemElement.classList.remove('loading');
                }
            }
            refreshCartSummary();
            refreshCartCount();
            showNotification(data.message);
        } else {
            showNotification(data.error, 'error');
            if (itemElement) {
                itemElement.classList.remove('loading');
            }
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while updating cart', 'error');
        if (itemElement) {
            itemElement.classList.remove('loading');
        }
    });
}

// Update quantity (convenience function)
function updateQuantity(itemId, newQuantity) {
    if (newQuantity < 0) return;
    updateCartItem(itemId, newQuantity);
}

// Remove cart item
function removeCartItem(itemId) {
    if (!confirm('Are you sure you want to remove this item from your cart?')) {
        return;
    }

    updateCartItem(itemId, 0);
}

// Alias for backward compatibility
function removeItem(itemId) {
    removeCartItem(itemId);
}

// Clear entire cart
function clearCart() {
    if (!confirm('Are you sure you want to clear your entire cart?')) {
        return;
    }

    fetch('/cart/clear/', {
        method: 'POST',
        body: new FormData(),
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload(); // Reload to show empty cart
        } else {
            showNotification('Error clearing cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while clearing cart', 'error');
    });
}

// Refresh cart count in navbar
function refreshCartCount() {
    fetch('/cart/api/count/')
    .then(response => response.json())
    .then(data => {
        // Update cart badge if it exists
        const cartBadge = document.querySelector('.cart-badge');
        if (cartBadge) {
            cartBadge.textContent = data.count;
            cartBadge.style.display = data.count > 0 ? 'inline-flex' : 'none';
        }
    })
    .catch(error => console.error('Error refreshing cart count:', error));
}

// Refresh cart summary
function refreshCartSummary() {
    fetch('/cart/api/summary/')
    .then(response => response.json())
    .then(data => {
        // Update summary total
        const summaryTotal = document.querySelector('.summary-total');
        if (summaryTotal) {
            summaryTotal.textContent = `$${data.subtotal.toFixed(2)}`;
        }

        // Update item count
        const cartCount = document.querySelector('.cart-count');
        if (cartCount) {
            cartCount.textContent = `${data.total_items} item${data.total_items !== 1 ? 's' : ''}`;
        }
    })
    .catch(error => console.error('Error refreshing cart summary:', error));
}

// Refresh cart badge (placeholder for now)
function refreshCartBadge() {
    // This would update any cart badges in the navigation
    refreshCartCount();
}

// Handle quantity input changes with debouncing
let quantityTimeout;
function handleQuantityChange(input) {
    clearTimeout(quantityTimeout);
    const itemId = input.closest('.cart-item').dataset.itemId;
    const quantity = parseInt(input.value);

    if (isNaN(quantity) || quantity < 1) {
        input.value = 1;
        return;
    }

    quantityTimeout = setTimeout(() => {
        updateCartItem(itemId, quantity);
    }, 500); // Debounce for 500ms
}

// Initialize cart functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for quantity inputs (manual input change)
    document.querySelectorAll('.quantity-input').forEach(input => {
        input.addEventListener('change', function() {
            const itemId = this.getAttribute('data-item-id');
            const quantity = parseInt(this.value);
            if (itemId && !isNaN(quantity) && quantity >= 0) {
                updateCartItem(itemId, quantity);
            }
        });
    });

    // Add event listeners for decrease buttons
    document.querySelectorAll('.quantity-decrease').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            const currentQuantity = parseInt(this.getAttribute('data-quantity'));
            if (itemId && currentQuantity > 1) {
                updateQuantity(itemId, currentQuantity - 1);
            }
        });
    });

    // Add event listeners for increase buttons
    document.querySelectorAll('.quantity-increase').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            const currentQuantity = parseInt(this.getAttribute('data-quantity'));
            if (itemId) {
                updateQuantity(itemId, currentQuantity + 1);
            }
        });
    });

    // Add event listeners for remove buttons
    document.querySelectorAll('.remove-btn').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            if (itemId) {
                removeCartItem(itemId);
            }
        });
    });

    // Add event listener for clear cart button
    const clearCartBtn = document.querySelector('.btn-clear-cart');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', function() {
            clearCart();
        });
    }

    // Refresh cart count on page load
    refreshCartCount();
});