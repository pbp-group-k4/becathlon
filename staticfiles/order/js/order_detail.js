// CSRF Token helper
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Get data from JSON script tag
const orderData = JSON.parse(document.getElementById('order-data').textContent);
const csrftoken = getCookie('csrftoken');
const orderId = orderData.orderId;
let statusCheckInterval = null;
let ratedProductIds = orderData.ratedProductIds;

// Poll delivery status every 10 seconds
function startStatusPolling() {
    // Check immediately
    checkDeliveryStatus();
    
    // Then check every 10 seconds
    statusCheckInterval = setInterval(checkDeliveryStatus, 10000);
}

function checkDeliveryStatus() {
    fetch(`/order/${orderId}/status/`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateDeliveryUI(data);
            
            // Update rated products list
            ratedProductIds = data.rated_product_ids || [];
            
            // Show rating modal when delivered
            if (data.is_delivered && !hasShownRatingModal()) {
                showRatingModal();
                markRatingModalShown();
            }
            
            // Stop polling if delivered
            if (data.is_delivered && statusCheckInterval) {
                clearInterval(statusCheckInterval);
            }
        }
    })
    .catch(error => {
        console.error('Error checking delivery status:', error);
    });
}

function updateDeliveryUI(data) {
    // Update status badge
    const statusBadge = document.getElementById('delivery-status-badge');
    if (statusBadge) {
        statusBadge.textContent = data.delivery_status_display;
    }
    
    // Update progress bar
    const progressFill = document.getElementById('progress-fill');
    const progressPercentage = document.getElementById('progress-percentage');
    if (progressFill && progressPercentage) {
        progressFill.style.width = data.progress_percentage + '%';
        progressPercentage.textContent = data.progress_percentage + '%';
    }
    
    // Update stage classes
    const stages = {
        'PROCESSING': document.getElementById('stage-processing'),
        'EN_ROUTE': document.getElementById('stage-enroute'),
        'DELIVERED': document.getElementById('stage-delivered')
    };
    
    // Remove all active/completed classes first
    Object.values(stages).forEach(stage => {
        if (stage) {
            stage.classList.remove('active', 'completed');
        }
    });
    
    // Add appropriate classes based on current status
    if (data.delivery_status === 'PROCESSING') {
        stages.PROCESSING?.classList.add('active');
    } else if (data.delivery_status === 'EN_ROUTE') {
        stages.PROCESSING?.classList.add('completed');
        stages.EN_ROUTE?.classList.add('active');
    } else if (data.delivery_status === 'DELIVERED') {
        stages.PROCESSING?.classList.add('completed');
        stages.EN_ROUTE?.classList.add('completed');
        stages.DELIVERED?.classList.add('completed');
    }
    
    // Hidden timer (for realistic UX without countdown display)
}

// Rating Modal Functions
function showRatingModal() {
    const modal = document.getElementById('rating-modal');
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
        updateRatedProducts();
    }
}

function closeRatingModal() {
    const modal = document.getElementById('rating-modal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

function hasShownRatingModal() {
    return sessionStorage.getItem(`rating-modal-shown-${orderId}`) === 'true';
}

function markRatingModalShown() {
    sessionStorage.setItem(`rating-modal-shown-${orderId}`, 'true');
}

function updateRatedProducts() {
    ratedProductIds.forEach(productId => {
        const card = document.querySelector(`.rating-product-card[data-product-id="${productId}"]`);
        if (card) {
            card.classList.add('rated');
            const statusDiv = card.querySelector('.rating-status');
            if (statusDiv) {
                statusDiv.textContent = '✓ Already Rated';
                statusDiv.classList.add('show', 'success');
            }
        }
    });
}

// Star Rating Functions
function setRating(productId, rating) {
    // Update hidden input
    const hiddenInput = document.querySelector(`.selected-rating[data-product-id="${productId}"]`);
    if (hiddenInput) {
        hiddenInput.value = rating;
    }
    
    // Update star visuals
    const starRating = document.querySelector(`.star-rating[data-product-id="${productId}"]`);
    if (starRating) {
        const stars = starRating.querySelectorAll('.star-btn');
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }
    
    // Enable submit button
    const submitBtn = document.querySelector(`.submit-rating-btn[data-product-id="${productId}"]`);
    if (submitBtn) {
        submitBtn.disabled = false;
    }
}

function submitRating(productId) {
    const ratingValue = document.querySelector(`.selected-rating[data-product-id="${productId}"]`)?.value;
    const reviewText = document.querySelector(`.rating-review-input[data-product-id="${productId}"]`)?.value || '';
    const statusDiv = document.querySelector(`.rating-status[data-product-id="${productId}"]`);
    const submitBtn = document.querySelector(`.submit-rating-btn[data-product-id="${productId}"]`);
    
    if (!ratingValue || ratingValue === '0') {
        if (statusDiv) {
            statusDiv.textContent = 'Please select a rating';
            statusDiv.classList.add('show', 'error');
            statusDiv.classList.remove('success');
            setTimeout(() => statusDiv.classList.remove('show'), 3000);
        }
        return;
    }
    
    // Disable button during submission
    if (submitBtn) submitBtn.disabled = true;
    
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('rating', ratingValue);
    formData.append('review', reviewText);
    
    fetch(`/order/${orderId}/rate/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (statusDiv) {
                statusDiv.textContent = '✓ ' + data.message;
                statusDiv.classList.add('show', 'success');
                statusDiv.classList.remove('error');
            }
            
            // Mark as rated
            ratedProductIds.push(productId);
            const card = document.querySelector(`.rating-product-card[data-product-id="${productId}"]`);
            if (card) card.classList.add('rated');
            
            // Check if all products rated
            checkAllProductsRated();
        } else {
            if (statusDiv) {
                statusDiv.textContent = data.error || 'Failed to submit rating';
                statusDiv.classList.add('show', 'error');
                statusDiv.classList.remove('success');
            }
            if (submitBtn) submitBtn.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error submitting rating:', error);
        if (statusDiv) {
            statusDiv.textContent = 'Network error. Please try again.';
            statusDiv.classList.add('show', 'error');
            statusDiv.classList.remove('success');
        }
        if (submitBtn) submitBtn.disabled = false;
    });
}

function checkAllProductsRated() {
    const allCards = document.querySelectorAll('.rating-product-card');
    const allRated = Array.from(allCards).every(card => card.classList.contains('rated'));
    
    if (allRated) {
        setTimeout(() => {
            alert('Thank you for rating all products! 🌟');
            closeRatingModal();
        }, 1500);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Set initial progress bar width
    const progressFill = document.getElementById('progress-fill');
    if (progressFill) {
        const initialProgress = progressFill.getAttribute('data-initial-progress');
        if (initialProgress) {
            progressFill.style.width = initialProgress + '%';
        }
    }
    
    // Start polling if delivery tracking is active
    const deliveryTracking = document.getElementById('delivery-tracking');
    if (deliveryTracking) {
        startStatusPolling();
    }
    
    // Modal close handlers
    const modalOverlay = document.getElementById('rating-modal-overlay');
    const modalClose = document.getElementById('rating-modal-close');
    
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeRatingModal);
    }
    
    if (modalClose) {
        modalClose.addEventListener('click', closeRatingModal);
    }
    
    // Star rating click handlers
    document.querySelectorAll('.star-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const rating = parseInt(this.getAttribute('data-rating'));
            setRating(productId, rating);
        });
    });
    
    // Submit rating button handlers
    document.querySelectorAll('.submit-rating-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            submitRating(productId);
        });
    });
    
    // Update already rated products
    updateRatedProducts();
});

// Clean up interval on page unload
window.addEventListener('beforeunload', function() {
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
});
