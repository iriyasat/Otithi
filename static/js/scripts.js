// === Atithi JavaScript ===

// Initialize i18next
i18next.init({
    lng: localStorage.getItem('language') || 'en',
    fallbackLng: 'en',
    resources: {
        en: {
            translation: {
                // Logo
                'logo.text': 'Atithi',
                
                // Navigation
                'nav.home': 'Home',
                'nav.properties': 'Properties',
                'nav.destinations': 'Destinations',
                'nav.howItWorks': 'How It Works',
                'nav.contact': 'Contact',
                'nav.login': 'Login',
                'nav.register': 'Register',
                
                // Hero Section
                'hero.title': 'Discover Authentic Bangladesh',
                'hero.subtitle': 'Experience the warmth of local hospitality',
                'search.button': 'Search',
                
                // Properties Section
                'properties.title': 'Featured Properties',
                'properties.subtitle': 'Discover our most popular accommodations',
                'properties.viewAll': 'View All Properties',
                
                // Destinations Section
                'destinations.title': 'Popular Destinations',
                'destinations.subtitle': 'Explore the beauty of Bangladesh',
                
                // How It Works Section
                'howItWorks.title': 'How It Works',
                'howItWorks.subtitle': 'Simple steps to your perfect stay',
                'howItWorks.step1.title': 'Search',
                'howItWorks.step1.description': 'Find your perfect homestay',
                'howItWorks.step2.title': 'Book',
                'howItWorks.step2.description': 'Reserve with secure payment',
                'howItWorks.step3.title': 'Experience',
                'howItWorks.step3.description': 'Enjoy authentic Bangladesh',
                
                // Trust Section
                'trust.secure.title': 'Secure Payments',
                'trust.secure.description': 'bKash & Nagad integration',
                'trust.verified.title': 'Verified Hosts',
                'trust.verified.description': 'All hosts are verified',
                'trust.support.title': '24/7 Support',
                'trust.support.description': 'Always here to help',
                
                // Login Page
                'login.title': 'Welcome Back',
                'login.subtitle': 'Sign in to continue your journey',
                'login.email': 'Email',
                'login.password': 'Password',
                'login.remember': 'Remember me',
                'login.forgotPassword': 'Forgot Password?',
                'login.submit': 'Login',
                'login.or': 'or',
                'login.google': 'Continue with Google',
                'login.facebook': 'Continue with Facebook',
                'login.noAccount': "Don't have an account?",
                'login.register': 'Register',
                
                // Registration Page
                'register.title': 'Create Your Account',
                'register.subtitle': 'Join our community of travelers and hosts',
                'register.fullName': 'Full Name',
                'register.email': 'Email',
                'register.password': 'Password',
                'register.passwordHint': 'Must be at least 8 characters long',
                'register.confirmPassword': 'Confirm Password',
                'register.userType': 'I want to',
                'register.guest': 'Book Homestays',
                'register.host': 'List My Property',
                'register.terms': 'I agree to the Terms & Conditions',
                'register.submit': 'Create Account',
                'register.or': 'or',
                'register.google': 'Continue with Google',
                'register.facebook': 'Continue with Facebook',
                'register.haveAccount': 'Already have an account?',
                'register.login': 'Login',
                
                // Footer
                'footer.about.title': 'About Atithi',
                'footer.about.description': 'Connecting travelers with authentic Bangladeshi homestays',
                'footer.quickLinks.title': 'Quick Links',
                'footer.quickLinks.about': 'About Us',
                'footer.quickLinks.howItWorks': 'How It Works',
                'footer.quickLinks.safety': 'Safety',
                'footer.quickLinks.contact': 'Contact',
                'footer.payment.title': 'Payment Partners',
                'footer.newsletter.title': 'Newsletter',
                'footer.privacy': 'Privacy Policy',
                'footer.terms': 'Terms of Service'
            }
        },
        bn: {
            translation: {
                // Logo
                'logo.text': 'আতিথি',
                
                // Navigation
                'nav.home': 'হোম',
                'nav.properties': 'বাড়ি',
                'nav.destinations': 'গন্তব্য',
                'nav.howItWorks': 'কিভাবে কাজ করে',
                'nav.contact': 'যোগাযোগ',
                'nav.login': 'লগইন',
                'nav.register': 'রেজিস্টার',
                
                // Hero Section
                'hero.title': 'বাংলাদেশ আবিষ্কার করুন',
                'hero.subtitle': 'স্থানীয় আতিথেয়তা উপভোগ করুন',
                'search.button': 'অনুসন্ধান',
                
                // Properties Section
                'properties.title': 'বৈশিষ্ট্যযুক্ত বাড়ি',
                'properties.subtitle': 'আমাদের জনপ্রিয় বাসস্থান আবিষ্কার করুন',
                'properties.viewAll': 'সব বাড়ি দেখুন',
                
                // Destinations Section
                'destinations.title': 'জনপ্রিয় গন্তব্য',
                'destinations.subtitle': 'বাংলাদেশের সৌন্দর্য অন্বেষণ করুন',
                
                // How It Works Section
                'howItWorks.title': 'কিভাবে কাজ করে',
                'howItWorks.subtitle': 'আপনার নিখুঁত থাকার জন্য সহজ পদক্ষেপ',
                'howItWorks.step1.title': 'অনুসন্ধান',
                'howItWorks.step1.description': 'আপনার নিখুঁত বাড়ি খুঁজুন',
                'howItWorks.step2.title': 'বুকিং',
                'howItWorks.step2.description': 'নিরাপদ পেমেন্টের সাথে রিজার্ভ করুন',
                'howItWorks.step3.title': 'অভিজ্ঞতা',
                'howItWorks.step3.description': 'আসল বাংলাদেশ উপভোগ করুন',
                
                // Trust Section
                'trust.secure.title': 'নিরাপদ পেমেন্ট',
                'trust.secure.description': 'বিকাশ এবং নগদ ইন্টিগ্রেশন',
                'trust.verified.title': 'যাচাইকৃত হোস্ট',
                'trust.verified.description': 'সব হোস্ট যাচাইকৃত',
                'trust.support.title': '২৪/৭ সহায়তা',
                'trust.support.description': 'সবসময় আপনার পাশে',
                
                // Login Page
                'login.title': 'স্বাগতম',
                'login.subtitle': 'আপনার যাত্রা চালিয়ে যেতে সাইন ইন করুন',
                'login.email': 'ইমেইল',
                'login.password': 'পাসওয়ার্ড',
                'login.remember': 'মনে রাখুন',
                'login.forgotPassword': 'পাসওয়ার্ড ভুলে গেছেন?',
                'login.submit': 'লগইন',
                'login.or': 'অথবা',
                'login.google': 'গুগল দিয়ে চালিয়ে যান',
                'login.facebook': 'ফেসবুক দিয়ে চালিয়ে যান',
                'login.noAccount': 'অ্যাকাউন্ট নেই?',
                'login.register': 'রেজিস্টার',
                
                // Registration Page
                'register.title': 'অ্যাকাউন্ট তৈরি করুন',
                'register.subtitle': 'ভ্রমণকারী এবং হোস্টদের সম্প্রদায়ে যোগ দিন',
                'register.fullName': 'পূর্ণ নাম',
                'register.email': 'ইমেইল',
                'register.password': 'পাসওয়ার্ড',
                'register.passwordHint': 'অন্তত ৮টি অক্ষর হতে হবে',
                'register.confirmPassword': 'পাসওয়ার্ড নিশ্চিত করুন',
                'register.userType': 'আমি চাই',
                'register.guest': 'বাড়ি বুক করতে',
                'register.host': 'আমার বাড়ি তালিকাভুক্ত করতে',
                'register.terms': 'আমি শর্তাবলী মেনে নিচ্ছি',
                'register.submit': 'অ্যাকাউন্ট তৈরি করুন',
                'register.or': 'অথবা',
                'register.google': 'গুগল দিয়ে চালিয়ে যান',
                'register.facebook': 'ফেসবুক দিয়ে চালিয়ে যান',
                'register.haveAccount': 'ইতিমধ্যে অ্যাকাউন্ট আছে?',
                'register.login': 'লগইন',
                
                // Footer
                'footer.about.title': 'আতিথি সম্পর্কে',
                'footer.about.description': 'ভ্রমণকারীদের সাথে আসল বাংলাদেশি বাড়ি সংযোগ করছে',
                'footer.quickLinks.title': 'দ্রুত লিঙ্ক',
                'footer.quickLinks.about': 'আমাদের সম্পর্কে',
                'footer.quickLinks.howItWorks': 'কিভাবে কাজ করে',
                'footer.quickLinks.safety': 'নিরাপত্তা',
                'footer.quickLinks.contact': 'যোগাযোগ',
                'footer.payment.title': 'পেমেন্ট পার্টনার',
                'footer.newsletter.title': 'নিউজলেটার',
                'footer.privacy': 'গোপনীয়তা নীতি',
                'footer.terms': 'পরিষেবার শর্তাবলী'
            }
        }
    }
});

// Language Switcher
function initLanguageSwitcher() {
    const langButtons = document.querySelectorAll('.lang-btn');
    
    langButtons.forEach(button => {
        button.addEventListener('click', function() {
            const lang = this.dataset.lang;
            
            // Update active state
            langButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Change language
            i18next.changeLanguage(lang, (err, t) => {
                if (err) return console.error('Error changing language:', err);
                
                // Save language preference
                localStorage.setItem('language', lang);
                
                // Update all translatable elements
                document.querySelectorAll('[data-i18n]').forEach(element => {
                    const key = element.dataset.i18n;
                    element.textContent = t(key);
                });
                
                // Update HTML lang attribute
                document.documentElement.lang = lang;
            });
        });
    });
    
    // Set initial language
    const currentLang = localStorage.getItem('language') || 'en';
    const activeButton = document.querySelector(`.lang-btn[data-lang="${currentLang}"]`);
    if (activeButton) {
        activeButton.click();
    }
}

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all modules
    initMobileMenu();
    initForms();
    initDashboard();
    initDateInputs();
    initLanguageSwitcher();
    initAdminDashboard();
});

// Mobile Menu Toggle
function initMobileMenu() {
    const hamburger = document.getElementById('hamburger');
    const navMenu = document.getElementById('navMenu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!hamburger.contains(event.target) && !navMenu.contains(event.target)) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    }
}

// Form Handling
function initForms() {
    // Login form
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Registration form
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegistration);
    }

    // Search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }

    // Password toggle functionality
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    });
}

// Search Handler
function handleSearch(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const searchData = {
        location: formData.get('location'),
        checkin: formData.get('checkin'),
        checkout: formData.get('checkout'),
        guests: formData.get('guests')
    };
    
    console.log('Search Data:', searchData);
    
    // In a real app, this would make an API call
    // For now, we'll just show an alert
    alert(`Searching for properties in ${searchData.location}`);
    
    // Redirect to a results page (in a real app)
    // window.location.href = `/search?location=${searchData.location}`;
}

// Login Handler
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({ email, password, remember })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store user data
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Show success message
            showToast('Login successful!', 'success');
            
            // Redirect to the appropriate dashboard
            window.location.href = data.redirect_url;
        } else {
            showToast(data.message || 'Login failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('An error occurred. Please try again.', 'error');
    }
}

// Handle registration form submission
function handleRegistration(event) {
    event.preventDefault();
    
    const form = document.getElementById('registerForm');
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    
    // Basic validation
    const requiredFields = ['name', 'email', 'password', 'confirmPassword', 'userType'];
    for (const field of requiredFields) {
        const input = form.querySelector(`[name="${field}"]`);
        if (!input.value.trim()) {
            showToast('error', 'Please fill in all required fields');
            return;
        }
    }
    
    // Password validation
    const password = form.querySelector('[name="password"]').value;
    const confirmPassword = form.querySelector('[name="confirmPassword"]').value;
    
    if (password !== confirmPassword) {
        showToast('error', 'Passwords do not match');
        return;
    }
    
    if (password.length < 8) {
        showToast('error', 'Password must be at least 8 characters long');
        return;
    }
    
    // Terms and conditions validation
    const termsCheckbox = form.querySelector('[name="terms"]');
    if (!termsCheckbox.checked) {
        showToast('error', 'Please accept the terms and conditions');
        return;
    }
    
    // Get CSRF token
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    // Show loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';
    
    // Get user type
    const userType = document.getElementById('userType').value;
    
    // Prepare registration data
    const registrationData = {
        name: form.querySelector('[name="name"]').value,
        email: form.querySelector('[name="email"]').value,
        password: password,
        userType: userType,
        preferred_language: document.documentElement.lang || 'en'
    };
    
    // Send registration request
    fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify(registrationData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Store user data
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Show success message
            showToast('success', data.message);
            
            // Redirect to appropriate dashboard
            window.location.href = data.redirect_url;
        } else {
            showToast('error', data.message);
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    })
    .catch(error => {
        console.error('Registration error:', error);
        showToast('error', 'An error occurred during registration');
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalBtnText;
    });
}

// Dashboard Functions
function initDashboard() {
    // Check if user is logged in
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    
    // Update user name in dashboard
    const userNameElement = document.getElementById('userName');
    const userFirstNameElement = document.getElementById('userFirstName');
    
    if (userNameElement && user.name) {
        userNameElement.textContent = user.name;
    }
    
    if (userFirstNameElement && user.firstName) {
        userFirstNameElement.textContent = user.firstName;
    }
    
    // Logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(event) {
            event.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                localStorage.removeItem('user');
                window.location.href = '/';
            }
        });
    }
    
    // Handle user menu on mobile
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        userMenu.addEventListener('click', function(event) {
            if (window.innerWidth <= 768) {
                event.stopPropagation();
                this.classList.toggle('active');
            }
        });
    }
}

// Initialize date inputs with min date as today
function initDateInputs() {
    const today = new Date().toISOString().split('T')[0];
    
    const checkinInput = document.querySelector('input[name="checkin"]');
    const checkoutInput = document.querySelector('input[name="checkout"]');
    
    if (checkinInput) {
        checkinInput.min = today;
        
        // Update checkout min date when checkin changes
        checkinInput.addEventListener('change', function() {
            const checkinDate = new Date(this.value);
            checkinDate.setDate(checkinDate.getDate() + 1);
            const minCheckout = checkinDate.toISOString().split('T')[0];
            
            if (checkoutInput) {
                checkoutInput.min = minCheckout;
                
                // Clear checkout if it's before new min date
                if (checkoutInput.value && checkoutInput.value < minCheckout) {
                    checkoutInput.value = '';
                }
            }
        });
    }
    
    if (checkoutInput) {
        checkoutInput.min = today;
    }
}

// Utility function to format currency in BDT
function formatCurrency(amount) {
    return `৳ ${amount.toLocaleString('en-BD')}`;
}

// Utility function to show toast notifications
function showToast(type = 'info', message) {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Add styles
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS animation for toasts
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Example API configuration for future use
const API_CONFIG = {
    baseURL: 'http://localhost:5000/api',  // Update this when you set up Flask
    headers: {
        'Content-Type': 'application/json'
    }
};

// Example API function for future use
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_CONFIG.baseURL}${endpoint}`, {
            ...options,
            headers: {
                ...API_CONFIG.headers,
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Call Failed:', error);
        throw error;
    }
}

// Example: How to use the API function
/*
async function loginUser(email, password) {
    try {
        const data = await apiCall('/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        // Store auth token
        localStorage.setItem('authToken', data.token);
        
        return data;
    } catch (error) {
        showToast('Login failed. Please try again.', 'error');
    }
}
*/

// Admin Dashboard
function initAdminDashboard() {
    // Mobile Navigation Toggle
    const adminNavToggle = document.getElementById('adminNavToggle');
    const adminNav = document.querySelector('.admin-nav');
    
    if (adminNavToggle) {
        adminNavToggle.addEventListener('click', () => {
            adminNav.classList.toggle('show');
        });
    }

    // Profile Dropdown
    const adminProfile = document.querySelector('.admin-profile');
    const adminDropdown = document.getElementById('adminDropdown');
    
    if (adminProfile && adminDropdown) {
        adminProfile.addEventListener('click', (e) => {
            e.stopPropagation();
            adminDropdown.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!adminProfile.contains(e.target) && !adminDropdown.contains(e.target)) {
                adminDropdown.classList.remove('show');
            }
        });
    }

    // Notifications
    const notifications = document.querySelector('.admin-notifications');
    if (notifications) {
        notifications.addEventListener('click', () => {
            // TODO: Implement notifications panel
            console.log('Notifications clicked');
        });
    }

    // Search
    const searchInput = document.querySelector('.admin-search input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            // TODO: Implement search functionality
            console.log('Search:', e.target.value);
        });
    }
}

// Global logout handler
function handleLogout() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    
    fetch('/api/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        credentials: 'include'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Clear local storage
            localStorage.removeItem('user');
            sessionStorage.clear();
            
            // Show success message
            showToast('success', data.message);
            
            // Redirect to the URL provided by the server
            window.location.href = data.redirect || '/';
        } else {
            showToast('error', data.message || 'Logout failed');
        }
    })
    .catch(error => {
        console.error('Logout error:', error);
        showToast('error', 'An error occurred during logout');
    });
}