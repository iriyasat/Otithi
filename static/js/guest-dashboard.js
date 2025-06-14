// Helper function to get CSRF token
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Helper function for API requests
async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': getCSRFToken()
        },
        credentials: 'same-origin'
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    const response = await fetch(url, options);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

// Update loadDashboardData function
async function loadDashboardData() {
    try {
        const [bookings, savedProperties, reviews] = await Promise.all([
            apiRequest('/api/guest/bookings'),
            apiRequest('/api/guest/saved-properties'),
            apiRequest('/api/guest/reviews')
        ]);
        
        updateBookingsList(bookings.bookings);
        updateSavedPropertiesList(savedProperties.properties);
        updateReviewsList(reviews.reviews);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading dashboard data', 'error');
    }
}

// Update toggleSavedProperty function
async function toggleSavedProperty(propertyId) {
    try {
        const response = await apiRequest(`/api/guest/saved-properties/${propertyId}`, 'POST');
        if (response.status === 'success') {
            showNotification(response.message, 'success');
            loadDashboardData(); // Reload data to update UI
        } else {
            showNotification(response.message, 'error');
        }
    } catch (error) {
        console.error('Error toggling saved property:', error);
        showNotification('Error updating saved property', 'error');
    }
}

// Update submitReview function
async function submitReview(propertyId, rating, comment) {
    try {
        const response = await apiRequest(`/api/properties/${propertyId}/reviews`, 'POST', {
            rating,
            comment_en: comment,
            comment_bn: comment // You might want to add separate Bengali comment field
        });
        
        if (response.status === 'success') {
            showNotification(response.message, 'success');
            loadDashboardData(); // Reload data to update UI
        } else {
            showNotification(response.message, 'error');
        }
    } catch (error) {
        console.error('Error submitting review:', error);
        showNotification('Error submitting review', 'error');
    }
} 