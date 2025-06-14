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
        const [properties, bookings, reviews] = await Promise.all([
            apiRequest('/api/host/properties'),
            apiRequest('/api/host/bookings'),
            apiRequest('/api/host/reviews')
        ]);
        
        updatePropertiesList(properties.properties);
        updateBookingsList(bookings.bookings);
        updateReviewsList(reviews.reviews);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading dashboard data', 'error');
    }
}

// Update uploadPropertyImage function
async function uploadPropertyImage(propertyId, file, isPrimary = false) {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('is_primary', isPrimary);
    
    try {
        const response = await fetch(`/api/properties/${propertyId}/images`, {
            method: 'POST',
            headers: {
                'X-CSRF-Token': getCSRFToken()
            },
            body: formData,
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.status === 'success') {
            showNotification(data.message, 'success');
            loadDashboardData(); // Reload data to update UI
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        console.error('Error uploading image:', error);
        showNotification('Error uploading image', 'error');
    }
}

// Update deletePropertyImage function
async function deletePropertyImage(propertyId, imageId) {
    try {
        const response = await apiRequest(`/api/properties/${propertyId}/images/${imageId}`, 'DELETE');
        if (response.status === 'success') {
            showNotification(response.message, 'success');
            loadDashboardData(); // Reload data to update UI
        } else {
            showNotification(response.message, 'error');
        }
    } catch (error) {
        console.error('Error deleting image:', error);
        showNotification('Error deleting image', 'error');
    }
}

// Update updateBookingStatus function
async function updateBookingStatus(bookingId, status) {
    try {
        const response = await apiRequest(`/api/bookings/${bookingId}/status`, 'PUT', { status });
        if (response.status === 'success') {
            showNotification(response.message, 'success');
            loadDashboardData(); // Reload data to update UI
        } else {
            showNotification(response.message, 'error');
        }
    } catch (error) {
        console.error('Error updating booking status:', error);
        showNotification('Error updating booking status', 'error');
    }
} 