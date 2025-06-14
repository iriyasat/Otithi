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
        const [properties, users, bookings] = await Promise.all([
            apiRequest('/api/admin/properties'),
            apiRequest('/api/admin/users'),
            apiRequest('/api/admin/bookings')
        ]);
        
        updatePropertiesList(properties.properties);
        updateUsersList(users.users);
        updateBookingsList(bookings.bookings);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Error loading dashboard data', 'error');
    }
}

// Update toggleUserStatus function
async function toggleUserStatus(userId) {
    try {
        const response = await apiRequest(`/api/admin/users/${userId}/toggle-status`, 'POST');
        if (response.status === 'success') {
            showNotification(response.message, 'success');
            loadDashboardData(); // Reload data to update UI
        } else {
            showNotification(response.message, 'error');
        }
    } catch (error) {
        console.error('Error toggling user status:', error);
        showNotification('Error updating user status', 'error');
    }
}

// Update deleteProperty function
async function deleteProperty(propertyId) {
    if (!confirm('Are you sure you want to delete this property?')) {
        return;
    }
    
    try {
        const response = await apiRequest(`/api/admin/properties/${propertyId}`, 'DELETE');
        if (response.status === 'success') {
            showNotification(response.message, 'success');
            loadDashboardData(); // Reload data to update UI
        } else {
            showNotification(response.message, 'error');
        }
    } catch (error) {
        console.error('Error deleting property:', error);
        showNotification('Error deleting property', 'error');
    }
}

// Update updateBookingStatus function
async function updateBookingStatus(bookingId, status) {
    try {
        const response = await apiRequest(`/api/admin/bookings/${bookingId}/status`, 'PUT', { status });
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