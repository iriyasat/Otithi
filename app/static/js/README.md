# Otithi JavaScript Architecture

This directory contains the modular JavaScript files for the Otithi application. The JavaScript has been separated into logical modules for better maintainability and performance.

## File Structure

```
js/
├── config.js            # Centralized configuration and API keys
├── core.js              # Essential initialization and utility functions
├── loader.js            # Dynamic script loading and global features
├── main.js              # Main entry point and page-specific logic
├── booking.js           # Booking management functionality
├── favorites.js         # Favorites management functionality
├── maps.js              # Google Maps integration
├── admin.js             # Admin panel functionality
├── admin-verification.js # Admin user verification functionality
└── README.md           # This documentation file
```

## Module Descriptions

### `config.js`
**Purpose**: Centralized configuration and API keys
**Features**:
- Google Maps API configuration
- Application settings (currency, file limits, etc.)
- API endpoint definitions
- Environment-specific configurations

### `core.js`
**Purpose**: Essential initialization and utility functions
**Features**:
- Core initialization system
- Tooltip initialization
- Search functionality
- Listing interactions
- Form validations
- Notification system
- File upload functionality
- Modal system
- Utility functions (currency formatting, API calls)

### `loader.js`
**Purpose**: Dynamic script loading and global features
**Features**:
- Page-specific script loading
- Global feature initialization
- Smooth scrolling
- Form validation
- Lazy loading for images
- Mobile menu enhancements

### `main.js`
**Purpose**: Main entry point and page-specific logic
**Features**:
- User type selection
- Filter chips functionality
- View toggle functionality
- Terms and privacy modals
- Page-specific script loading coordination

### `booking.js`
**Purpose**: Booking management and interactions
**Features**:
- Booking form validation
- Booking actions (cancel, modify, etc.)
- Booking calendar functionality
- Booking details display
- Refund requests
- Booking total calculations

### `favorites.js`
**Purpose**: Favorites management and interactions
**Features**:
- Favorite button functionality
- Favorites page management
- Favorite filters and sorting
- Bulk operations
- Export and share functionality

### `maps.js`
**Purpose**: Google Maps integration and location functionality
**Features**:
- Google Maps initialization
- Location search
- Property map display
- Address parsing
- Geocoding functionality
- Route calculation

### `admin.js`
**Purpose**: Admin panel functionality
**Features**:
- User management
- Listing management
- Booking management
- System controls
- Dashboard statistics
- Real-time updates

### `admin-verification.js`
**Purpose**: Admin user verification functionality
**Features**:
- User verification toggle
- Verification status updates
- AJAX communication with backend

## Loading Order

1. **Bootstrap** - External library
2. **config.js** - Configuration and API keys
3. **core.js** - Essential functionality
4. **loader.js** - Dynamic loading system
5. **main.js** - Main entry point
6. **Page-specific modules** - Loaded dynamically based on current page

## Usage

### Automatic Loading
The system automatically loads page-specific scripts based on the current URL:

- `/booking` or `/my_bookings` → `booking.js`
- `/favorites` → `favorites.js`
- `/create_listing` or `/listing/` → `maps.js`
- `/admin` → `admin.js`
- `/admin/users` → `admin-verification.js`

### Manual Loading
To manually load a script:

```javascript
// Using the loader
window.OtithiLoader.loadScript('/static/js/booking.js');

// Or using the core function
loadScript('/static/js/booking.js');
```

### Adding New Modules

1. Create the new module file in the `js/` directory
2. Add the module to the `PAGE_SCRIPTS` mapping in `loader.js`
3. Ensure the module follows the initialization pattern:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    initializeModule();
});

function initializeModule() {
    // Module initialization code
}
```

## Best Practices

### Module Structure
Each module should follow this structure:

```javascript
/**
 * Module Name
 * Brief description of functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeModule();
});

function initializeModule() {
    // Initialize all module functionality
}

// Module-specific functions
function moduleFunction() {
    // Function implementation
}
```

### Error Handling
Always include error handling for:
- API calls
- File operations
- User interactions
- Network requests

### Performance
- Use event delegation where appropriate
- Implement lazy loading for heavy functionality
- Minimize DOM queries
- Use efficient selectors

### Accessibility
- Ensure keyboard navigation works
- Provide ARIA labels where needed
- Support screen readers
- Maintain focus management

## Dependencies

### External Libraries
- **Bootstrap 5.1.3** - UI framework
- **Google Maps API** - Maps functionality (loaded dynamically)

### Internal Dependencies
- `core.js` provides utility functions used by other modules
- `loader.js` manages dynamic loading
- `main.js` coordinates page-specific functionality

## Development

### Adding Features
1. Identify the appropriate module for the feature
2. Add the feature following the module's structure
3. Update documentation if needed
4. Test across different pages

### Debugging
- Check browser console for errors
- Verify script loading order
- Ensure dependencies are available
- Test on different devices/browsers

### Testing
- Test each module independently
- Test module interactions
- Test on different page types
- Test with different user roles

## Migration Notes

### From Inline Scripts
All inline scripts have been removed from HTML templates and moved to appropriate modules:

- Booking functionality → `booking.js`
- Favorites functionality → `favorites.js`
- Maps functionality → `maps.js`
- Admin functionality → `admin.js`

### From Monolithic main.js
The original `main.js` has been split into:
- Core functionality → `core.js`
- Page-specific logic → `main.js`
- Global features → `loader.js`

## Performance Benefits

1. **Reduced Initial Load**: Only core scripts load initially
2. **On-Demand Loading**: Page-specific scripts load when needed
3. **Better Caching**: Modules can be cached independently
4. **Parallel Loading**: Multiple modules can load simultaneously
5. **Reduced Memory**: Unused functionality doesn't load

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- ES6+ features used
- Fallbacks for older browsers where needed
- Progressive enhancement approach 