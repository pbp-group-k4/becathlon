// Catalog JavaScript - Becathlon

document.addEventListener('DOMContentLoaded', function() {
    // Category Filter Toggle and Search
    initCategoryFilters();
    
    // Quick View Modal
    initQuickView();
    
    // AJAX Filtering (optional enhancement)
    // Can be expanded for dynamic filtering without page reload
    initAjaxFilters();
});

// Category Filter Toggle and Search Functionality
function initCategoryFilters() {
    const toggleBtn = document.getElementById('category-toggle');
    const filtersWrapper = document.getElementById('category-filters');
    const searchInput = document.getElementById('category-search-input');
    const checkboxes = document.querySelectorAll('.category-filters input[type="checkbox"]');
    const selectedCountSpan = document.getElementById('selected-count');
    const noResultsDiv = document.getElementById('no-category-results');
    
    if (!toggleBtn || !filtersWrapper) return;
    
    // Toggle dropdown
    toggleBtn.addEventListener('click', function() {
        const isExpanded = filtersWrapper.classList.toggle('expanded');
        toggleBtn.classList.toggle('expanded');
        
        // Focus search input when opening
        if (isExpanded && searchInput) {
            setTimeout(() => searchInput.focus(), 100);
        }
    });
    
    // Update selected count
    function updateSelectedCount() {
        const checkedCount = document.querySelectorAll('.category-filters input[type="checkbox"]:checked').length;
        if (selectedCountSpan) {
            selectedCountSpan.textContent = `${checkedCount} selected`;
        }
    }
    
    // Listen to checkbox changes
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateSelectedCount);
    });
    
    // Category search functionality
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            const categoryLabels = document.querySelectorAll('.filter-checkbox');
            let visibleCount = 0;
            
            categoryLabels.forEach(label => {
                const categoryName = label.getAttribute('data-category-name') || '';
                const categoryText = label.textContent.toLowerCase();
                
                if (categoryName.includes(searchTerm) || categoryText.includes(searchTerm)) {
                    label.classList.remove('hidden');
                    visibleCount++;
                } else {
                    label.classList.add('hidden');
                }
            });
            
            // Show/hide no results message
            if (noResultsDiv) {
                noResultsDiv.style.display = visibleCount === 0 ? 'block' : 'none';
            }
        });
    }
    
    // Initialize selected count on load
    updateSelectedCount();
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!toggleBtn.contains(e.target) && !filtersWrapper.contains(e.target)) {
            filtersWrapper.classList.remove('expanded');
            toggleBtn.classList.remove('expanded');
        }
    });
}

// Quick View Modal Functionality
function initQuickView() {
    const modal = document.getElementById('quick-view-modal');
    if (!modal) return;
    
    const modalContent = document.getElementById('quick-view-content');
    const closeBtn = modal.querySelector('.modal-close');
    const quickViewButtons = document.querySelectorAll('.btn-quick-view');
    
    // Open modal on quick view button click
    quickViewButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            if (!productId) return;
            
            // Show modal with loading state
            modal.classList.add('active');
            modalContent.innerHTML = '<div class="loading">Loading product details...</div>';
            
            try {
                // Fetch product data via AJAX
                const response = await fetch(`/catalog/api/product/${productId}/quick-view/`);
                
                if (!response.ok) {
                    throw new Error('Failed to load product');
                }
                
                const product = await response.json();

                // Build quick view content
                const quickViewHTML = buildQuickViewHTML(product);
                modalContent.innerHTML = quickViewHTML;
                attachQuickViewActions(modalContent, product);

            } catch (error) {
                console.error('Error loading quick view:', error);
                // Just close the modal silently instead of showing error
                modal.classList.remove('active');
                return;
            }
        });
    });
    
    // Close modal on close button click
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.classList.remove('active');
        });
    }
    
    // Close modal on outside click
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
    
    // Close modal on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            modal.classList.remove('active');
        }
    });
}

// Build Quick View HTML
function buildQuickViewHTML(product) {
    const stockStatus = product.in_stock 
        ? `<span class="stock-indicator in-stock">✓ In Stock (${product.stock})</span>`
        : `<span class="stock-indicator out-of-stock">✗ Out of Stock</span>`;
    
    let imagesHTML = '';
    if (product.images && product.images.length > 0) {
        imagesHTML = product.images.map(img => 
            `<img src="${img}" alt="${product.name}" style="max-width: 100%; height: auto; margin-bottom: 1rem;">`
        ).join('');
    } else {
        imagesHTML = '<div class="no-image-large">No Image Available</div>';
    }
    
    return `
        <div class="quick-view-container">
            <div class="quick-view-images">
                ${imagesHTML}
            </div>
            <div class="quick-view-info">
                <div class="product-category-badge">${product.product_type}</div>
                <h2 style="margin: 1rem 0; color: var(--ultra-light);">${product.name}</h2>
                <div class="product-price-large" style="margin-bottom: 1rem;">$${product.price}</div>
                <div style="margin-bottom: 1.5rem;">
                    ${stockStatus}
                </div>
                <p style="color: var(--light-gray); line-height: 1.8; margin-bottom: 1.5rem;">
                    ${product.description}
                </p>
                <div style="display: flex; gap: 1rem;">
                    <a href="/catalog/product/${product.id}/" class="btn-view" style="flex: 1; text-decoration: none;">
                        View Full Details
                    </a>
                    <button class="btn-add-cart" type="button" data-action="quick-view-add" style="flex: 1;" ${!product.in_stock ? 'disabled' : ''}>
                        ${product.in_stock ? 'Add to Cart' : 'Out of Stock'}
                    </button>
                </div>
            </div>
        </div>
    `;
}

function attachQuickViewActions(container, product) {
    const addButton = container.querySelector('[data-action="quick-view-add"]');
    if (!addButton || !product.in_stock) {
        return;
    }

    addButton.addEventListener('click', () => {
        if (typeof addToCart === 'function') {
            addToCart(product.id, 1);
        }
    });
}

// AJAX Filtering (optional enhancement for dynamic updates)
function initAjaxFilters() {
    // This is a placeholder for future AJAX filtering implementation
    // Currently, the app uses traditional form submission
    // This can be expanded to provide seamless filtering without page reloads
    
    const filterForm = document.getElementById('filter-form');
    if (!filterForm) return;
    
    // Example: Add debounced search
    const searchInput = filterForm.querySelector('input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Could implement AJAX search here
                // For now, just submit the form
                // filterForm.submit();
            }, 500);
        });
    }
}

// Image Gallery for Product Detail
function changeMainImage(imageUrl, thumbnail) {
    const mainImage = document.getElementById('main-product-image');
    if (mainImage) {
        mainImage.src = imageUrl;
        
        // Update active thumbnail
        document.querySelectorAll('.thumbnail').forEach(thumb => {
            thumb.classList.remove('active');
        });
        if (thumbnail) {
            thumbnail.classList.add('active');
        }
    }
}

// AJAX Product Filtering (Advanced - for future implementation)
async function filterProducts(filters) {
    try {
        const params = new URLSearchParams();
        
        // Build query parameters
        if (filters.categories && filters.categories.length > 0) {
            filters.categories.forEach(cat => params.append('category_ids[]', cat));
        }
        if (filters.min_price) params.append('min_price', filters.min_price);
        if (filters.max_price) params.append('max_price', filters.max_price);
        if (filters.in_stock_only) params.append('in_stock_only', 'true');
        if (filters.search) params.append('search', filters.search);
        if (filters.sort_by) params.append('sort_by', filters.sort_by);
        if (filters.page) params.append('page', filters.page);
        
        const response = await fetch(`/catalog/api/filter/?${params.toString()}`);
        
        if (!response.ok) {
            throw new Error('Failed to filter products');
        }
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('Error filtering products:', error);
        return null;
    }
}

// Update products grid with AJAX results
function updateProductsGrid(data) {
    const grid = document.getElementById('products-grid');
    if (!grid || !data || !data.products) return;
    
    // Clear current products
    grid.innerHTML = '';
    
    if (data.products.length === 0) {
        grid.innerHTML = `
            <div class="no-products">
                <p>No products found matching your criteria.</p>
                <a href="/catalog/" class="btn-clear">Clear Filters</a>
            </div>
        `;
        return;
    }
    
    // Add new products
    data.products.forEach(product => {
        const productCard = buildProductCard(product);
        grid.appendChild(productCard);
    });
    
    // Re-initialize quick view buttons
    initQuickView();
}

// Build product card element
function buildProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    
    const stockBadge = product.stock === 0 
        ? '<span class="stock-badge out-of-stock">Out of Stock</span>'
        : product.stock < 10 
        ? '<span class="stock-badge low-stock">Low Stock</span>'
        : '';
    
    const stockText = product.stock > 0
        ? `<span class="in-stock">${product.stock} in stock</span>`
        : `<span class="out-of-stock">Out of stock</span>`;
    
    const imageHTML = product.image_url
        ? `<img src="${product.image_url}" alt="${product.name}">`
        : '<div class="no-image">No Image</div>';
    
    card.innerHTML = `
        <div class="product-image">
            ${imageHTML}
            <span class="product-badge">${product.product_type}</span>
            ${stockBadge}
        </div>
        <div class="product-info">
            <h3 class="product-name">${product.name}</h3>
            <p class="product-price">$${product.price}</p>
            <div class="product-stock">
                ${stockText}
            </div>
            <div class="product-actions">
                <a href="${product.url}" class="btn-view">View Details</a>
                <button class="btn-quick-view" data-product-id="${product.id}">Quick View</button>
            </div>
        </div>
    `;
    
    return card;
}

// Price range slider (future enhancement)
function initPriceSlider() {
    // Placeholder for price range slider implementation
    // Could use libraries like noUiSlider for better UX
}

// Export functions for use in templates
window.changeMainImage = changeMainImage;
window.filterProducts = filterProducts;
