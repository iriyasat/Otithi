/**
 * Otithi Configuration
 * Centralized configuration for API keys and settings
 */

// Google Maps API Configuration (only declare if not already declared)
if (typeof GOOGLE_MAPS_CONFIG === 'undefined') {
    const GOOGLE_MAPS_CONFIG = {
        API_KEY: 'AIzaSyAOyKOo-evauWLjq9IJfG-xhOWcRpBpqdw',
        LIBRARIES: ['places'],
        DEFAULT_LOCATION: { lat: 23.8103, lng: 90.4125 }, // Dhaka, Bangladesh
        BANGLADESH_BOUNDS: {
            north: 26.5,
            south: 20.5,
            east: 93.0,
            west: 88.0
        }
    };
    // Make it globally available
    window.GOOGLE_MAPS_CONFIG = GOOGLE_MAPS_CONFIG;
}

// Application Configuration (only declare if not already declared)
if (typeof APP_CONFIG === 'undefined') {
    const APP_CONFIG = {
        CURRENCY: 'BDT',
        CURRENCY_SYMBOL: '৳',
        SERVICE_FEE_PERCENTAGE: 0.15, // 15%
        MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
        MAX_IMAGES: 5,
        ALLOWED_IMAGE_TYPES: ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp']
    };
    // Make it globally available
    window.APP_CONFIG = APP_CONFIG;
}

// API Endpoints (only declare if not already declared)
if (typeof API_ENDPOINTS === 'undefined') {
    const API_ENDPOINTS = {
        LISTINGS: '/api/listings',
        BOOKINGS: '/api/bookings',
        FAVORITES: '/api/favorites',
        USERS: '/api/users',
        ADMIN: '/api/admin'
    };
    // Make it globally available
    window.API_ENDPOINTS = API_ENDPOINTS;
}

// Export configuration for use in other modules
window.OtithiConfig = {
    GOOGLE_MAPS: window.GOOGLE_MAPS_CONFIG || {},
    APP: window.APP_CONFIG || {},
    API: window.API_ENDPOINTS || {}
}; 