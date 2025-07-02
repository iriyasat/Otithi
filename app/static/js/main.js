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
    const userTypeCards = document.querySelectorAll('.user-type-card');
    userTypeCards.forEach(card => {
        card.addEventListener('click', function() {
            // Get the user type from the radio input inside this card
            const radioInput = this.querySelector('input[type="radio"]');
            if (radioInput) {
                // Remove active class from all cards
                userTypeCards.forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked card
                this.classList.add('active');
                
                // Check the corresponding radio button
                radioInput.checked = true;
            }
        });
    });

    // Initialize user type selection on page load
    // Set guest as default selected
    const guestCard = document.querySelector('.user-type-card');
    if (guestCard) {
        guestCard.classList.add('active');
        const guestRadio = guestCard.querySelector('input[type="radio"]');
        if (guestRadio) {
            guestRadio.checked = true;
        }
    }

    // View toggle functionality for explore page
    const viewToggleBtns = document.querySelectorAll('.view-btn');
    const listingsContainer = document.getElementById('listings-container');
    
    if (viewToggleBtns.length > 0 && listingsContainer) {
        viewToggleBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Prevent multiple rapid clicks
                if (this.classList.contains('switching')) return;
                
                // Remove active class from all buttons
                viewToggleBtns.forEach(b => {
                    b.classList.remove('active');
                    b.classList.remove('switching');
                });
                
                // Add switching state to prevent rapid clicks
                this.classList.add('switching');
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Get the view type
                const viewType = this.dataset.view;
                
                // Add fade out effect
                listingsContainer.style.opacity = '0.7';
                listingsContainer.style.transform = 'scale(0.98)';
                
                // After a short delay, change the view
                setTimeout(() => {
                    // Toggle the grid/list view
                    if (viewType === 'list') {
                        listingsContainer.classList.add('listings-list');
                        listingsContainer.classList.remove('listings-grid');
                    } else {
                        listingsContainer.classList.remove('listings-list');
                        listingsContainer.classList.add('listings-grid');
                    }
                    
                    // Fade back in with new layout
                    listingsContainer.style.opacity = '1';
                    listingsContainer.style.transform = 'scale(1)';
                    
                    // Remove switching state
                    this.classList.remove('switching');
                }, 150);
            });
        });
    }
});

// Global function for user type selection (backup for inline events)
function selectUserType(type, element) {
    // Remove active class from all cards
    document.querySelectorAll('.user-type-card').forEach(card => {
        card.classList.remove('active');
    });
    
    // Add active class to selected card
    element.classList.add('active');
    
    // Check the corresponding radio button
    const radioInput = document.getElementById(type);
    if (radioInput) {
        radioInput.checked = true;
    }
}

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

// File Upload Enhancement
function initFileUpload() {
    const fileInputs = document.querySelectorAll('.file-input');
    
    fileInputs.forEach(input => {
        const container = input.closest('.file-upload-container');
        const label = container.querySelector('.file-upload-label');
        const uploadContent = container.querySelector('.file-upload-content');
        const filePreview = container.querySelector('.file-preview');
        const previewImage = container.querySelector('.preview-image');
        const removeBtn = container.querySelector('.remove-file-btn');
        const mainText = container.querySelector('.upload-main-text');
        const subText = container.querySelector('.upload-sub-text');

        // Handle file selection
        input.addEventListener('change', function(e) {
            handleFileSelect(e.target.files[0]);
        });

        // Handle drag and drop
        label.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.add('drag-over');
            uploadContent.style.borderColor = 'var(--primary-500)';
            uploadContent.style.background = 'var(--primary-50)';
        });

        label.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.remove('drag-over');
            uploadContent.style.borderColor = 'var(--neutral-300)';
            uploadContent.style.background = 'var(--neutral-50)';
        });

        label.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            this.classList.remove('drag-over');
            uploadContent.style.borderColor = 'var(--neutral-300)';
            uploadContent.style.background = 'var(--neutral-50)';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        // Remove file button
        if (removeBtn) {
            removeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                removeFile();
            });
        }

        function handleFileSelect(file) {
            if (!file) return;

            // Validate file type
            if (!file.type.startsWith('image/')) {
                showNotification('Please select an image file', 'error');
                return;
            }

            // Validate file size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                showNotification('File size must be less than 5MB', 'error');
                return;
            }

            // Create preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                uploadContent.style.display = 'none';
                filePreview.style.display = 'block';
            };
            reader.readAsDataURL(file);

            // Update input
            const dt = new DataTransfer();
            dt.items.add(file);
            input.files = dt.files;
        }

        function removeFile() {
            input.value = '';
            previewImage.src = '';
            uploadContent.style.display = 'flex';
            filePreview.style.display = 'none';
        }
    });
}

// Initialize file upload when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initFileUpload();
});

// Terms and Privacy Policy Modal Functions
function showTermsModal(event) {
    event.preventDefault();
    showModal('Terms of Service', getTermsContent());
}

function showPrivacyModal(event) {
    event.preventDefault();
    showModal('Privacy Policy', getPrivacyContent());
}

function showModal(title, content) {
    // Create modal HTML
    const modalHTML = `
        <div class="modal-overlay" onclick="closeModal()">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3 class="modal-title">${title}</h3>
                    <button class="modal-close" onclick="closeModal()">×</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" onclick="closeModal()">Close</button>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
        document.body.style.overflow = 'auto';
    }
}

function getTermsContent() {
    return `
        <div class="terms-content">
            <h4>1. Acceptance of Terms</h4>
            <p>By using Otithi, you agree to be bound by these Terms of Service and all applicable laws and regulations.</p>
            
            <h4>2. Service Description</h4>
            <p>Otithi is a platform that connects travelers with local hosts in Bangladesh, facilitating short-term accommodation bookings.</p>
            
            <h4>3. User Accounts</h4>
            <p>You must create an account to use our services. You are responsible for maintaining the security of your account credentials.</p>
            
            <h4>4. Booking and Payments</h4>
            <p>All bookings are subject to host approval. Payment processing is handled securely through our platform.</p>
            
            <h4>5. Host Responsibilities</h4>
            <p>Hosts must provide accurate listing information and maintain their properties to the standards described.</p>
            
            <h4>6. Guest Responsibilities</h4>
            <p>Guests must respect host properties and follow house rules as outlined in each listing.</p>
            
            <h4>7. Cancellation Policy</h4>
            <p>Cancellation policies vary by listing. Please review the specific policy before booking.</p>
            
            <h4>8. Limitation of Liability</h4>
            <p>Otithi acts as a platform and is not responsible for the conduct of hosts or guests.</p>
        </div>
    `;
}

function getPrivacyContent() {
    return `
        <div class="privacy-content">
            <h4>1. Information We Collect</h4>
            <p>We collect information you provide when creating an account, making bookings, and using our services.</p>
            
            <h4>2. How We Use Your Information</h4>
            <p>Your information is used to facilitate bookings, improve our services, and communicate with you about your account.</p>
            
            <h4>3. Information Sharing</h4>
            <p>We share necessary information between hosts and guests to facilitate bookings. We do not sell your personal information.</p>
            
            <h4>4. Data Security</h4>
            <p>We implement appropriate security measures to protect your personal information against unauthorized access.</p>
            
            <h4>5. Cookies</h4>
            <p>We use cookies to enhance your experience and analyze website usage.</p>
            
            <h4>6. Your Rights</h4>
            <p>You have the right to access, update, or delete your personal information at any time.</p>
            
            <h4>7. Contact Us</h4>
            <p>If you have questions about this Privacy Policy, please contact us at privacy@otithi.com</p>
        </div>
    `;
}

// Favorite toggle function for listings
function toggleFavorite(listingId) {
    // Get the button that was clicked
    const button = event.target.closest('.favorite-btn');
    if (!button) return;
    
    const icon = button.querySelector('i');
    const isCurrentlyFavorited = icon.classList.contains('bi-heart-fill');
    
    // Toggle the icon
    if (isCurrentlyFavorited) {
        icon.classList.remove('bi-heart-fill');
        icon.classList.add('bi-heart');
        button.classList.remove('favorited');
    } else {
        icon.classList.remove('bi-heart');
        icon.classList.add('bi-heart-fill');
        button.classList.add('favorited');
    }
    
    // Here you would typically make an AJAX request to save the favorite state
    // For now, we'll just update the UI
    console.log(`Toggled favorite for listing ${listingId}`);
    
    // Optional: Add animation feedback
    button.style.transform = 'scale(1.2)';
    setTimeout(() => {
        button.style.transform = 'scale(1)';
    }, 150);
}
