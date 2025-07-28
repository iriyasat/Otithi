/**
 * Otithi Main JavaScript
 * Main entry point and essential functionality
 */

// Import modular JavaScript files
document.addEventListener('DOMContentLoaded', function() {
    // Load core functionality
    loadScript('/static/js/core.js');
    
    // Load page-specific functionality
    loadPageSpecificScripts();
});

/**
 * Load page-specific scripts based on current page
 */
function loadPageSpecificScripts() {
    const currentPath = window.location.pathname;
    
    // Booking pages
    if (currentPath.includes('/booking') || currentPath.includes('/my_bookings')) {
        loadScript('/static/js/booking.js');
    }
    
    // Favorites pages
    if (currentPath.includes('/favorites')) {
        loadScript('/static/js/favorites.js');
    }
    
    // Maps functionality (create listing, listing details)
    if (currentPath.includes('/create_listing') || currentPath.includes('/listing/')) {
        loadScript('/static/js/maps.js');
    }
    
    // Admin pages
    if (currentPath.includes('/admin')) {
        loadScript('/static/js/admin.js');
        if (currentPath.includes('/users')) {
            loadScript('/static/js/admin-verification.js');
        }
    }
}

/**
 * Load script dynamically
 * @param {string} src - Script source URL
 */
function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

/**
 * User type selection for registration
 * @param {string} type - User type (guest, host)
 * @param {HTMLElement} element - The clicked element
 */
function selectUserType(type, element) {
    // Remove active class from all user type cards
    document.querySelectorAll('.user-type-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Add active class to selected card
    element.classList.add('active');
    
    // Update hidden input
    const userTypeInput = document.getElementById('user_type');
    if (userTypeInput) {
        userTypeInput.value = type;
    }
    
    // Update form validation
    updateUserTypeValidation(type);
}

/**
 * Update form validation based on user type
 * @param {string} type - Selected user type
 */
function updateUserTypeValidation(type) {
    const hostFields = document.querySelectorAll('.host-field');
    const guestFields = document.querySelectorAll('.guest-field');
    
    if (type === 'host') {
        hostFields.forEach(field => {
            field.style.display = 'block';
            field.querySelector('input')?.setAttribute('required', 'required');
        });
        guestFields.forEach(field => {
            field.style.display = 'none';
            field.querySelector('input')?.removeAttribute('required');
        });
    } else {
        hostFields.forEach(field => {
            field.style.display = 'none';
            field.querySelector('input')?.removeAttribute('required');
        });
        guestFields.forEach(field => {
            field.style.display = 'block';
            field.querySelector('input')?.setAttribute('required', 'required');
        });
    }
}

/**
 * Show terms and conditions modal
 * @param {Event} event - Click event
 */
function showTermsModal(event) {
    event.preventDefault();
    showModal('Terms and Conditions', getTermsContent());
}

/**
 * Show privacy policy modal
 * @param {Event} event - Click event
 */
function showPrivacyModal(event) {
    event.preventDefault();
    showModal('Privacy Policy', getPrivacyContent());
}

/**
 * Get terms and conditions content
 * @returns {string} HTML content for terms
 */
function getTermsContent() {
    return `
        <div class="terms-content">
            <h6>Terms and Conditions</h6>
            <p>By using Otithi, you agree to the following terms:</p>
            <ul>
                <li>You must be at least 18 years old to use our services</li>
                <li>You are responsible for the accuracy of your listing information</li>
                <li>You agree to treat other users with respect and courtesy</li>
                <li>We reserve the right to modify these terms at any time</li>
                <li>Violation of these terms may result in account suspension</li>
            </ul>
            <p>For complete terms, please contact our support team.</p>
        </div>
    `;
}

/**
 * Get privacy policy content
 * @returns {string} HTML content for privacy policy
 */
function getPrivacyContent() {
    return `
        <div class="privacy-content">
            <h6>Privacy Policy</h6>
            <p>Your privacy is important to us. This policy describes how we collect and use your information:</p>
            <ul>
                <li>We collect information you provide when creating an account</li>
                <li>We use cookies to improve your browsing experience</li>
                <li>We do not sell your personal information to third parties</li>
                <li>You can request deletion of your data at any time</li>
                <li>We implement security measures to protect your information</li>
            </ul>
            <p>For complete privacy policy, please contact our support team.</p>
        </div>
    `;
}

/**
 * Initialize filter chips functionality
 */
function initializeFilterChips() {
    const filterChips = document.querySelectorAll('.filter-chip');
    filterChips.forEach(chip => {
        chip.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active from all chips
            filterChips.forEach(c => c.classList.remove('active'));
            
            // Add active to clicked chip
            this.classList.add('active');
            
            // Apply filter
            const filterValue = this.dataset.filter;
            applyFilter(filterValue);
        });
    });
}

/**
 * Apply filter to listings
 * @param {string} filterValue - Filter value to apply
 */
function applyFilter(filterValue) {
    const listings = document.querySelectorAll('.listing-card');
    
    listings.forEach(listing => {
        let shouldShow = true;
        
        switch (filterValue) {
            case 'all':
                shouldShow = true;
                break;
            case 'available':
                const availability = listing.dataset.availability;
                shouldShow = availability === 'available';
                break;
            case 'price-low':
                const price = parseFloat(listing.dataset.price);
                shouldShow = price <= 1000;
                break;
            case 'price-high':
                const priceHigh = parseFloat(listing.dataset.price);
                shouldShow = priceHigh > 1000;
                break;
            case 'rating-high':
                const rating = parseFloat(listing.dataset.rating);
                shouldShow = rating >= 4.0;
                break;
            default:
                shouldShow = true;
        }
        
        if (shouldShow) {
            listing.style.display = 'block';
            listing.style.opacity = '1';
        } else {
            listing.style.display = 'none';
        }
    });
    
    // Update results count
    updateResultsCount();
}

/**
 * Update results count display
 */
function updateResultsCount() {
    const visibleListings = document.querySelectorAll('.listing-card[style*="display: block"], .listing-card:not([style*="display: none"])');
    const countElement = document.querySelector('.results-count');
    
    if (countElement) {
        countElement.textContent = visibleListings.length;
    }
}

/**
 * Initialize view toggle functionality
 */
function initializeViewToggle() {
    const viewButtons = document.querySelectorAll('.view-btn');
    const listingsGrid = document.querySelector('.listings-grid');
    
    viewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active from all buttons
            viewButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active to clicked button
            this.classList.add('active');
            
            // Apply view
            const viewType = this.dataset.view;
            applyView(viewType);
        });
    });
}

/**
 * Apply view type to listings
 * @param {string} viewType - View type to apply
 */
function applyView(viewType) {
    const listingsGrid = document.querySelector('.listings-grid');
    
    if (!listingsGrid) return;
    
    switch (viewType) {
        case 'grid':
            listingsGrid.className = 'listings-grid grid-view';
            break;
        case 'list':
            listingsGrid.className = 'listings-grid list-view';
            break;
        case 'map':
            // Show map view (implement map functionality)
            showMapView();
            break;
        default:
            listingsGrid.className = 'listings-grid grid-view';
    }
}

/**
 * Show map view of listings
 */
function showMapView() {
    // This would integrate with the maps.js functionality
    // For now, just show a placeholder
    const listingsContainer = document.querySelector('.listings-container');
    if (listingsContainer) {
        listingsContainer.innerHTML = `
            <div class="map-view-placeholder">
                <h4>Map View</h4>
                <p>Map view functionality will be implemented here.</p>
            </div>
        `;
    }
}

// Initialize additional functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize filter chips
    initializeFilterChips();
    
    // Initialize view toggle
    initializeViewToggle();
    
    // Initialize file upload if present
    if (document.querySelector('input[type="file"]')) {
        initFileUpload();
    }
});
