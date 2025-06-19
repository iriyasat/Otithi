/*
===============================
অতিথি - Otithi Interactive JS
Modern Bangladesh-Inspired UI
===============================
*/

class OtithiApp {
    constructor() {
        this.init();
        this.bindEvents();
        this.initAnimations();
    }

    init() {
        console.log('🏠 অতিথি - Otithi App Initialized');
        
        // Set theme colors for dynamic use
        this.colors = {
            green: '#006A4E',
            red: '#F42A41',
            white: '#FFFFFF'
        };
    }

    bindEvents() {
        // Navbar scroll effect
        this.initNavbarScroll();
        
        // Search interactions
        this.initSearchFeatures();
        
        // Form enhancements
        this.initFormFeatures();
        
        // Button interactions
        this.initButtonAnimations();
    }

    initAnimations() {
        // Counter animations for stats
        this.initCounterAnimations();
        
        // Scroll animations
        this.initScrollAnimations();
    }

    // ==================== NAVBAR FUNCTIONALITY ====================
    initNavbarScroll() {
        const navbar = document.getElementById('mainNavbar');
        if (!navbar) return;

        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }

    // ==================== SEARCH FUNCTIONALITY ====================
    initSearchFeatures() {
        const searchForm = document.querySelector('.search-form');
        if (!searchForm) return;

        const searchFields = searchForm.querySelectorAll('.search-field');
        
        searchFields.forEach(field => {
            const input = field.querySelector('input');
            if (!input) return;

            // Focus animations
            input.addEventListener('focus', () => {
                field.classList.add('focused');
                this.animateSearchField(field, true);
            });

            input.addEventListener('blur', () => {
                if (!input.value) {
                    field.classList.remove('focused');
                    this.animateSearchField(field, false);
                }
            });
        });

        // Search form submission with loading state
        searchForm.addEventListener('submit', (e) => {
            this.handleSearchSubmit(e, searchForm);
        });
    }

    animateSearchField(field, focused) {
        const icon = field.querySelector('.search-icon i');
        if (icon) {
            if (focused) {
                icon.style.transform = 'scale(1.1)';
                icon.style.color = this.colors.green;
            } else {
                icon.style.transform = 'scale(1)';
                icon.style.color = '';
            }
        }
    }

    handleSearchSubmit(e, form) {
        const submitButton = form.querySelector('.search-button');
        if (!submitButton) return;

        // Show loading state
        const originalContent = submitButton.innerHTML;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        submitButton.disabled = true;

        // Restore after delay (form will redirect)
        setTimeout(() => {
            submitButton.innerHTML = originalContent;
            submitButton.disabled = false;
        }, 2000);
    }

    // ==================== FORM ENHANCEMENTS ====================
    initFormFeatures() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showValidationErrors(form);
                }
            });
        });
    }

    validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });

        return isValid;
    }

    showValidationErrors(form) {
        const firstInvalid = form.querySelector('.is-invalid');
        if (firstInvalid) {
            firstInvalid.focus();
            firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    // ==================== ANIMATIONS ====================
    initScrollAnimations() {
        const animatedElements = document.querySelectorAll('[data-aos]');
        
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('aos-animate');
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            animatedElements.forEach(el => observer.observe(el));
        }
    }

    initCounterAnimations() {
        const counters = document.querySelectorAll('.stat-number');
        
        const animateCounter = (counter) => {
            const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
            const duration = 2000;
            const increment = target / (duration / 16);
            let current = 0;

            const updateCounter = () => {
                current += increment;
                if (current < target) {
                    counter.textContent = Math.floor(current) + (counter.textContent.includes('+') ? '+' : '');
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target + (counter.textContent.includes('+') ? '+' : '');
                }
            };

            updateCounter();
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });

        counters.forEach(counter => observer.observe(counter));
    }

    // ==================== BUTTON ANIMATIONS ====================
    initButtonAnimations() {
        const buttons = document.querySelectorAll('.btn');
        
        buttons.forEach(button => {
            // Ripple effect
            button.addEventListener('click', (e) => {
                this.createRipple(e, button);
            });

            // Hover animations
            button.addEventListener('mouseenter', () => {
                button.style.transform = 'translateY(-2px)';
            });

            button.addEventListener('mouseleave', () => {
                button.style.transform = 'translateY(0)';
            });
        });
    }

    createRipple(e, button) {
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple 0.6s linear;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            pointer-events: none;
        `;

        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        button.appendChild(ripple);

        setTimeout(() => {
            ripple.remove();
        }, 600);
    }

    // ==================== UTILITY FUNCTIONS ====================
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
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
}

// CSS for additional animations
const additionalStyles = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .search-field.focused {
        background: rgba(0, 106, 78, 0.05);
        border-radius: 12px;
    }

    .aos-animate {
        animation: fadeInUp 0.6s ease-out;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    new OtithiApp();
});

// Navbar Scroll Effect
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar');
    
    function handleScroll() {
        if (window.scrollY > 20) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    }
    
    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Initial check
});

// Dropdown Menu Hover Effect
document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('mouseenter', function() {
            if (window.innerWidth >= 992) { // Only on desktop
                this.querySelector('.dropdown-menu').classList.add('show');
            }
        });
        
        dropdown.addEventListener('mouseleave', function() {
            if (window.innerWidth >= 992) { // Only on desktop
                this.querySelector('.dropdown-menu').classList.remove('show');
            }
        });
    });
});

// Flash Message Auto-Dismiss
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // Auto dismiss after 5 seconds
    });
});

// Form Validation Styling
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});

// Smooth Scroll for Anchor Links
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
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
});

// Image Loading Animation
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.classList.add('img-loaded');
        });
    });
});

// Mobile Menu Close on Click Outside
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenu) {
        document.addEventListener('click', function(event) {
            const isClickInside = mobileMenu.contains(event.target);
            const isMenuOpen = mobileMenu.classList.contains('show');
            const isToggler = event.target.closest('.navbar-toggler');
            
            if (!isClickInside && !isToggler && isMenuOpen) {
                const bsOffcanvas = bootstrap.Offcanvas.getInstance(mobileMenu);
                if (bsOffcanvas) {
                    bsOffcanvas.hide();
                }
            }
        });
    }
}); 