/**
 * OTITHI - Main JavaScript
 * Modern interactive features and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // =========================
    // Navbar Scroll Effect
    // =========================
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // =========================
    // Smooth Scrolling for Anchor Links
    // =========================
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

    // =========================
    // Animate Elements on Scroll
    // =========================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
            }
        });
    }, observerOptions);

    // Observe cards and sections
    document.querySelectorAll('.card, .dashboard-card, .listing-card, .hero-content').forEach(el => {
        observer.observe(el);
    });

    // =========================
    // Form Enhancements
    // =========================
    document.querySelectorAll('.form-control, .form-select').forEach(input => {
        // Add floating label effect
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });

        // Auto-resize textareas
        if (input.tagName === 'TEXTAREA') {
            input.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });
        }
    });

    // =========================
    // Button Loading States
    // =========================
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
            }
        });
    });

    // =========================
    // Card Hover Effects
    // =========================
    document.querySelectorAll('.card, .listing-card, .dashboard-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // =========================
    // Image Lazy Loading
    // =========================
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }

    // =========================
    // Toast Notifications
    // =========================
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = `
            top: 100px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }

    // =========================
    // Search Enhancement
    // =========================
    const searchInput = document.querySelector('input[type="search"], input[name="search"]');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Add search functionality here
                console.log('Searching for:', this.value);
            }, 300);
        });
    }

    // =========================
    // Modal Enhancements
    // =========================
    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(trigger => {
        trigger.addEventListener('click', function() {
            const target = this.getAttribute('data-bs-target');
            const modal = document.querySelector(target);
            if (modal) {
                modal.classList.add('show');
            }
        });
    });

    // =========================
    // Table Enhancements
    // =========================
    document.querySelectorAll('.table tbody tr').forEach(row => {
        row.addEventListener('click', function() {
            // Remove active class from other rows
            this.parentElement.querySelectorAll('tr').forEach(r => {
                r.classList.remove('table-active');
            });
            // Add active class to clicked row
            this.classList.add('table-active');
        });
    });

    // =========================
    // Pagination Enhancement
    // =========================
    document.querySelectorAll('.pagination .page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            if (page) {
                // Add pagination functionality here
                console.log('Navigating to page:', page);
            }
        });
    });

    // =========================
    // File Upload Enhancement
    // =========================
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const label = this.nextElementSibling;
                if (label && label.tagName === 'LABEL') {
                    label.textContent = file.name;
                }
                
                // Show preview for images
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const preview = document.createElement('img');
                        preview.src = e.target.result;
                        preview.style.cssText = 'max-width: 200px; max-height: 200px; object-fit: cover; border-radius: 8px; margin-top: 10px;';
                        input.parentNode.appendChild(preview);
                    };
                    reader.readAsDataURL(file);
                }
            }
        });
    });

    // =========================
    // Keyboard Shortcuts
    // =========================
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[name="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals/dropdowns
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                modal.classList.remove('show');
                modal.style.display = 'none';
            });
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });

    // =========================
    // Performance Optimization
    // =========================
    
    // Debounce function for performance
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Optimize scroll events
    const optimizedScrollHandler = debounce(function() {
        // Scroll-based animations and effects
    }, 16); // ~60fps

    window.addEventListener('scroll', optimizedScrollHandler);

    // =========================
    // Accessibility Enhancements
    // =========================
    
    // Skip to main content
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'sr-only sr-only-focusable position-absolute';
    skipLink.style.cssText = 'top: 10px; left: 10px; z-index: 9999; background: var(--bd-green); color: white; padding: 10px; text-decoration: none; border-radius: 4px;';
    
    document.body.insertBefore(skipLink, document.body.firstChild);

    // Focus management for modals
    document.querySelectorAll('[data-bs-toggle="modal"]').forEach(trigger => {
        trigger.addEventListener('click', function() {
            const target = this.getAttribute('data-bs-target');
            const modal = document.querySelector(target);
            if (modal) {
                const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
                if (focusableElements.length > 0) {
                    focusableElements[0].focus();
                }
            }
        });
    });

    // =========================
    // Error Handling
    // =========================
    window.addEventListener('error', function(e) {
        console.error('JavaScript Error:', e.error);
        showToast('An error occurred. Please refresh the page.', 'danger');
    });

    // =========================
    // Initialize Tooltips
    // =========================
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // =========================
    // Initialize Popovers
    // =========================
    if (typeof bootstrap !== 'undefined') {
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }

    console.log('OTITHI JavaScript initialized successfully!');
}); 