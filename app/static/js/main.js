// Main JavaScript file for Otithi

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Search form enhancements
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

    // Filter chips
    const filterChips = document.querySelectorAll('.filter-chip');
    filterChips.forEach(chip => {
        chip.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active from all chips
            filterChips.forEach(c => c.classList.remove('active'));
            
            // Add active to clicked chip
            this.classList.add('active');
        });
    });

    // Booking form validation
    const bookingForm = document.querySelector('.booking-card form');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const checkin = this.querySelector('input[name="checkin"]').value;
            const checkout = this.querySelector('input[name="checkout"]').value;
            
            if (!checkin || !checkout) {
                alert('Please select check-in and check-out dates.');
                return;
            }
            
            if (new Date(checkin) >= new Date(checkout)) {
                alert('Check-out date must be after check-in date.');
                return;
            }
            
            // Simulate booking process
            const button = this.querySelector('button[type="submit"]');
            const originalText = button.textContent;
            button.innerHTML = '<span class="loading"></span> Processing...';
            button.disabled = true;
            
            setTimeout(() => {
                alert('Booking request submitted successfully!');
                button.textContent = originalText;
                button.disabled = false;
            }, 2000);
        });
    }

    // Earnings calculator
    const calculatorButton = document.querySelector('button[type="button"]');
    if (calculatorButton && calculatorButton.textContent.includes('Calculate')) {
        calculatorButton.addEventListener('click', function() {
            const location = document.querySelector('input[placeholder*="address"]').value;
            const propertyType = this.closest('form').querySelector('select').value;
            
            if (!location.trim()) {
                alert('Please enter your location.');
                return;
            }
            
            // Simulate calculation
            this.innerHTML = '<span class="loading"></span> Calculating...';
            this.disabled = true;
            
            setTimeout(() => {
                const earnings = Math.floor(Math.random() * 20000) + 10000;
                const earningsDisplay = document.querySelector('.text-primary.fw-bold');
                if (earningsDisplay) {
                    earningsDisplay.textContent = `৳${earnings.toLocaleString()}`;
                }
                
                this.textContent = 'Calculate earnings';
                this.disabled = false;
            }, 1500);
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-update copyright year
    const footerParagraphs = document.querySelectorAll('footer p');
    footerParagraphs.forEach(p => {
        if (p.textContent.includes('©')) {
            const currentYear = new Date().getFullYear();
            p.innerHTML = p.innerHTML.replace(/\d{4}/, currentYear);
        }
    });

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // Email validation
            const emailFields = this.querySelectorAll('input[type="email"]');
            emailFields.forEach(field => {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (field.value && !emailRegex.test(field.value)) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else if (field.value) {
                    field.classList.remove('is-invalid');
                }
            });
            
            // Password confirmation
            const password = this.querySelector('input[name="password"]');
            const confirmPassword = this.querySelector('input[name="confirmPassword"]');
            if (password && confirmPassword && password.value !== confirmPassword.value) {
                confirmPassword.classList.add('is-invalid');
                isValid = false;
            } else if (confirmPassword) {
                confirmPassword.classList.remove('is-invalid');
            }
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    // Mobile menu enhancements
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const icon = this.querySelector('.navbar-toggler-icon');
            setTimeout(() => {
                if (this.getAttribute('aria-expanded') === 'true') {
                    icon.style.transform = 'rotate(90deg)';
                } else {
                    icon.style.transform = 'rotate(0deg)';
                }
            }, 10);
        });
    }

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img.lazy').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // User type selection for registration
    function selectUserType(type, element) {
        // Remove active class from all cards
        document.querySelectorAll('.user-type-card').forEach(card => {
            card.classList.remove('active');
        });
        
        // Add active class to selected card
        element.classList.add('active');
        
        // Check the corresponding radio button
        document.getElementById(type).checked = true;
    }

    // Initialize user type selection on page load
    // Set guest as default selected
    const guestCard = document.querySelector('.user-type-card');
    if (guestCard) {
        guestCard.classList.add('active');
    }
});

// Utility functions
function formatCurrency(amount) {
    return `৳${amount.toLocaleString()}`;
}

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// API helper functions
async function fetchListings(filters = {}) {
    try {
        const params = new URLSearchParams(filters);
        const response = await fetch(`/api/listings?${params}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching listings:', error);
        return [];
    }
}

// Export functions for use in other scripts
window.OtithiApp = {
    formatCurrency,
    showNotification,
    fetchListings
};
