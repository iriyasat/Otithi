/**
 * Otithi Core JavaScript
 * Essential initialization and utility functions
 */

// Core initialization
document.addEventListener('DOMContentLoaded', function() {
    initializeCore();
});

function initializeCore() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize listing interactions
    initializeListingInteractions();
    
    // Initialize form validations
    initializeFormValidations();
    
    // Initialize notifications
    initializeNotifications();
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize search form functionality
 */
function initializeSearch() {
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = this.querySelector('input[name="query"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
}

/**
 * Initialize listing card interactions
 */
function initializeListingInteractions() {
    // Listing card click handlers
    const listingCards = document.querySelectorAll('.listing-card');
    listingCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't navigate if clicking on heart button
            if (e.target.closest('.btn')) {
                return;
            }
            
            const listingId = this.dataset.listingId || 1;
            window.location.href = `/listing/${listingId}`;
        });
    });

    // Heart button toggle
    const heartButtons = document.querySelectorAll('.btn[title*="wishlist"], .btn[title*="Save"]');
    heartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const icon = this.querySelector('i');
            if (icon.classList.contains('bi-heart')) {
                icon.classList.remove('bi-heart');
                icon.classList.add('bi-heart-fill');
                this.classList.add('text-danger');
            } else {
                icon.classList.remove('bi-heart-fill');
                icon.classList.add('bi-heart');
                this.classList.remove('text-danger');
            }
        });
    });
}

/**
 * Initialize form validations
 */
function initializeFormValidations() {
    // Booking form validation
    const bookingForm = document.querySelector('.booking-card form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const checkin = this.querySelector('input[name="checkin"]').value;
            const checkout = this.querySelector('input[name="checkout"]').value;
            
            if (!checkin || !checkout) {
                showNotification('Please select check-in and check-out dates.', 'error');
                return;
            }
            
            if (new Date(checkin) >= new Date(checkout)) {
                showNotification('Check-out date must be after check-in date.', 'error');
                return;
            }
            
            // Simulate booking process
            const button = this.querySelector('button[type="submit"]');
            const originalText = button.textContent;
            button.innerHTML = '<span class="loading"></span> Processing...';
            button.disabled = true;
            
            setTimeout(() => {
                showNotification('Booking request submitted successfully!', 'success');
                button.textContent = originalText;
                button.disabled = false;
            }, 2000);
        });
    }
}

/**
 * Initialize notification system
 */
function initializeNotifications() {
    // Create notification container if it doesn't exist
    if (!document.getElementById('notification-container')) {
        const notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(notificationContainer);
    }
}

/**
 * Show notification message
 * @param {string} message - The message to display
 * @param {string} type - The type of notification (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 3000) {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    notification.style.cssText = `
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: none;
        border-radius: 8px;
    `;

    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    container.appendChild(notification);

    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);

    // Remove on close button click
    notification.querySelector('.btn-close').addEventListener('click', () => {
        notification.remove();
    });
}

/**
 * Format currency for display
 * @param {number} amount - The amount to format
 * @param {string} currency - The currency code
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount, currency = null) {
    const config = window.OtithiConfig?.APP || {};
    const currencyCode = currency || config.CURRENCY || 'BDT';
    const currencySymbol = config.CURRENCY_SYMBOL || '৳';
    
    return new Intl.NumberFormat('en-BD', {
        style: 'currency',
        currency: currencyCode
    }).format(amount);
}

/**
 * Fetch listings with filters
 * @param {Object} filters - Filter parameters
 * @returns {Promise} Promise that resolves to listings data
 */
async function fetchListings(filters = {}) {
    try {
        const config = window.OtithiConfig?.API || {};
        const endpoint = config.LISTINGS || '/api/listings';
        const queryString = new URLSearchParams(filters).toString();
        const response = await fetch(`${endpoint}?${queryString}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching listings:', error);
        showNotification('Error loading listings', 'error');
        return [];
    }
}

/**
 * Toggle favorite status for a listing
 * @param {number} listingId - The listing ID
 * @returns {Promise} Promise that resolves to the updated favorite status
 */
async function toggleFavorite(listingId) {
    try {
        const config = window.OtithiConfig?.API || {};
        const endpoint = config.LISTINGS || '/api/listings';
        const response = await fetch(`${endpoint}/${listingId}/favorite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        showNotification(data.message, data.success ? 'success' : 'error');
        return data;
    } catch (error) {
        console.error('Error toggling favorite:', error);
        showNotification('Error updating favorite status', 'error');
        return { success: false, message: 'Error updating favorite status' };
    }
}

/**
 * Initialize file upload functionality
 */
function initFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            const previewContainer = this.parentNode.querySelector('.file-preview') || 
                                   this.parentNode.querySelector('.image-preview');
            
            if (previewContainer) {
                previewContainer.innerHTML = '';
                
                files.forEach(file => {
                    if (file.type.startsWith('image/')) {
                        const reader = new FileReader();
                        reader.onload = function(e) {
                            const preview = document.createElement('div');
                            preview.className = 'file-preview-item';
                            preview.style.cssText = `
                                display: inline-block;
                                margin: 5px;
                                position: relative;
                            `;
                            
                            preview.innerHTML = `
                                <img src="${e.target.result}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 4px;">
                                <button type="button" class="btn-close" style="position: absolute; top: -5px; right: -5px; background: white; border-radius: 50%; width: 20px; height: 20px; border: 1px solid #ddd;"></button>
                            `;
                            
                            previewContainer.appendChild(preview);
                            
                            // Remove file on close button click
                            preview.querySelector('.btn-close').addEventListener('click', function() {
                                preview.remove();
                                // Remove file from input
                                const dt = new DataTransfer();
                                const input = previewContainer.parentNode.querySelector('input[type="file"]');
                                const { files } = input;
                                
                                for (let i = 0; i < files.length; i++) {
                                    const f = files[i];
                                    if (f !== file) {
                                        dt.items.add(f);
                                    }
                                }
                                
                                input.files = dt.files;
                            });
                        };
                        reader.readAsDataURL(file);
                    }
                });
            }
        });
    });
}

/**
 * Show modal with custom content
 * @param {string} title - Modal title
 * @param {string} content - Modal content
 */
function showModal(title, content) {
    const modalHtml = `
        <div class="modal fade" id="customModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if any
    const existingModal = document.getElementById('customModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Add new modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('customModal'));
    modal.show();
}

/**
 * Close modal
 */
function closeModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('customModal'));
    if (modal) {
        modal.hide();
    }
} 