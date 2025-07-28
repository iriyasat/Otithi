/**
 * Otithi Configuration
 * Centralized configuration for API keys and settings
 */

// Google Maps API Configuration
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

// Application Configuration
const APP_CONFIG = {
    CURRENCY: 'BDT',
    CURRENCY_SYMBOL: '৳',
    SERVICE_FEE_PERCENTAGE: 0.15, // 15%
    MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
    MAX_IMAGES: 5,
    ALLOWED_IMAGE_TYPES: ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp']
};

// API Endpoints
const API_ENDPOINTS = {
    LISTINGS: '/api/listings',
    BOOKINGS: '/api/bookings',
    FAVORITES: '/api/favorites',
    USERS: '/api/users',
    ADMIN: '/api/admin'
};

// Export configuration for use in other modules
window.OtithiConfig = {
    GOOGLE_MAPS: GOOGLE_MAPS_CONFIG,
    APP: APP_CONFIG,
    API: API_ENDPOINTS
}; 