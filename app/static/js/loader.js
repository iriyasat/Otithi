/**
 * Otithi JavaScript Loader
 * Handles dynamic loading of page-specific JavaScript modules
 */

// Page-specific script mappings
const PAGE_SCRIPTS = {
    // Booking pages
    '/booking': '/static/js/booking.js',
    '/my_bookings': '/static/js/booking.js',
    
    // Favorites pages
    '/favorites': '/static/js/favorites.js',
    
    // Maps functionality
    '/create_listing': '/static/js/maps.js',
    '/listing/': '/static/js/maps.js',
    
    // Admin pages
    '/admin': '/static/js/admin.js',
    '/admin/users': '/static/js/admin-verification.js'
};

/**
 * Load page-specific scripts based on current URL
 */
function loadPageSpecificScripts() {
    const currentPath = window.location.pathname;
    const scriptsToLoad = [];
    
    // Check for exact matches first
    for (const [path, script] of Object.entries(PAGE_SCRIPTS)) {
        if (currentPath === path || currentPath.startsWith(path)) {
            scriptsToLoad.push(script);
        }
    }
    
    // Load scripts sequentially
    scriptsToLoad.forEach(script => {
        loadScript(script);
    });
}

/**
 * Load a script dynamically
 * @param {string} src - Script source URL
 * @returns {Promise} Promise that resolves when script is loaded
 */
function loadScript(src) {
    return new Promise((resolve, reject) => {
        // Check if script is already loaded
        if (document.querySelector(`script[src="${src}"]`)) {
            resolve();
            return;
        }
        
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

/**
 * Initialize the loader
 */
document.addEventListener('DOMContentLoaded', function() {
    // Load page-specific scripts
    loadPageSpecificScripts();
    
    // Initialize any global functionality
    initializeGlobalFeatures();
});

/**
 * Initialize global features
 */
function initializeGlobalFeatures() {
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
}

// Export for use in other modules
window.OtithiLoader = {
    loadScript,
    loadPageSpecificScripts
}; 