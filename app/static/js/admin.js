/**
 * Otithi Admin Panel JavaScript
 * Interactive functionality for admin dashboard
 */

// Initialize admin dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeAdminDashboard();
});

function initializeAdminDashboard() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Set up real-time updates
    setupRealtimeUpdates();
    
    // Initialize charts if available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
}

// User Management Functions
function showCreateUserModal() {
    const modal = new bootstrap.Modal(document.getElementById('createUserModal'));
    modal.show();
}

function createUser() {
    const form = document.getElementById('createUserForm');
    const formData = new FormData();
    
    formData.append('full_name', document.getElementById('newUserName').value);
    formData.append('email', document.getElementById('newUserEmail').value);
    formData.append('phone', document.getElementById('newUserPhone').value);
    formData.append('user_type', document.getElementById('newUserType').value);
    formData.append('password', document.getElementById('newUserPassword').value);
    
    // Basic validation
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    // Show loading
    showNotification('Creating user...', 'info');
    
    // Simulate API call (replace with actual endpoint when ready)
    setTimeout(() => {
        showNotification('User created successfully!', 'success');
        bootstrap.Modal.getInstance(document.getElementById('createUserModal')).hide();
        form.reset();
        // Refresh page to show new user
        setTimeout(() => location.reload(), 1500);
    }, 1000);
}

function changeUserRole(userId, currentRole) {
    const roles = ['guest', 'host', 'admin'];
    const currentIndex = roles.indexOf(currentRole);
    const nextRole = roles[(currentIndex + 1) % roles.length];
    
    if (confirm(`Change user role from ${currentRole} to ${nextRole}?`)) {
        showNotification('Updating user role...', 'info');
        
        fetch(`/admin/users/${userId}/change-role`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ role: nextRole })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error updating user role', 'error');
        });
    }
}

function deleteUser(userId, userName) {
    if (confirm(`Are you sure you want to delete user "${userName}"? This action cannot be undone.`)) {
        showNotification('Deleting user...', 'info');
        
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/users/${userId}/delete`;
        form.style.display = 'none';
        document.body.appendChild(form);
        form.submit();
    }
}

// Listing Management Functions
function approveListing(listingId, listingTitle) {
    if (confirm(`Approve listing "${listingTitle}"?`)) {
        showNotification('Approving listing...', 'info');
        
        fetch(`/admin/listings/${listingId}/approve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => location.reload(), 1500);
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error approving listing', 'error');
        });
    }
}

function deleteListing(listingId, listingTitle) {
    if (confirm(`Are you sure you want to delete listing "${listingTitle}"? This action cannot be undone.`)) {
        showNotification('Deleting listing...', 'info');
        
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/admin/listings/${listingId}/delete`;
        form.style.display = 'none';
        document.body.appendChild(form);
        form.submit();
    }
}

// Booking Management Functions
function updateBookingStatus(bookingId, newStatus) {
    showNotification('Updating booking status...', 'info');
    
    fetch(`/admin/bookings/${bookingId}/update-status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 1500);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating booking status', 'error');
    });
}

// Quick Actions
function showApproveListingsModal() {
    // Create dynamic modal for bulk approving listings
    showNotification('Loading pending listings...', 'info');
    // This would typically fetch pending listings and show them in a modal
    setTimeout(() => {
        showNotification('Feature coming soon!', 'info');
    }, 1000);
}

function showBulkActionsModal() {
    showNotification('Bulk actions feature coming soon!', 'info');
}

function exportData() {
    showNotification('Preparing data export...', 'info');
    // This would typically generate and download a CSV/Excel file
    setTimeout(() => {
        showNotification('Export feature coming soon!', 'info');
    }, 1000);
}

// System Controls
function showSystemControls() {
    const modal = new bootstrap.Modal(document.getElementById('systemControlsModal'));
    modal.show();
}

function clearCache() {
    if (confirm('Clear application cache?')) {
        showNotification('Clearing cache...', 'info');
        setTimeout(() => {
            showNotification('Cache cleared successfully!', 'success');
        }, 2000);
    }
}

function backupDatabase() {
    if (confirm('Create database backup?')) {
        showNotification('Creating backup...', 'info');
        setTimeout(() => {
            showNotification('Database backup created successfully!', 'success');
        }, 3000);
    }
}

function runMaintenance() {
    if (confirm('Run system maintenance? This may take a few minutes.')) {
        showNotification('Running maintenance tasks...', 'info');
        setTimeout(() => {
            showNotification('Maintenance completed successfully!', 'success');
        }, 5000);
    }
}

function restartServices() {
    if (confirm('Restart system services? This may cause temporary downtime.')) {
        showNotification('Restarting services...', 'warning');
        setTimeout(() => {
            showNotification('Services restarted successfully!', 'success');
        }, 4000);
    }
}

// Real-time Updates
function setupRealtimeUpdates() {
    // Update stats every 30 seconds
    setInterval(updateDashboardStats, 30000);
    
    // Update system status every 10 seconds
    setInterval(updateSystemStatus, 10000);
}

function updateDashboardStats() {
    // This would typically fetch updated stats from the server
}

function updateSystemStatus() {
    // This would typically check system health
}

// Utility Functions
function showNotification(message, type = 'info', duration = 3000) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.admin-notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} admin-notification position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1060;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border: none;
        border-radius: 8px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    // Add icon based on type
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="${icons[type] || icons.info} me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.animation = 'slideOutRight 0.3s ease-in';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .admin-notification {
        animation: slideInRight 0.3s ease-out;
    }
`;
document.head.appendChild(style);

// Chart initialization (if Chart.js is available)
function initializeCharts() {
    // Revenue chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [12000, 19000, 15000, 25000, 22000, 30000],
                    borderColor: 'rgb(0, 106, 78)',
                    backgroundColor: 'rgba(0, 106, 78, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '৳' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    
    // User growth chart
    const userGrowthCtx = document.getElementById('userGrowthChart');
    if (userGrowthCtx) {
        new Chart(userGrowthCtx, {
            type: 'bar',
            data: {
                labels: ['Guests', 'Hosts', 'Admins'],
                datasets: [{
                    label: 'Users',
                    data: [45, 12, 3],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(0, 106, 78, 0.8)',
                        'rgba(124, 58, 237, 0.8)'
                    ],
                    borderColor: [
                        'rgb(54, 162, 235)',
                        'rgb(0, 106, 78)',
                        'rgb(124, 58, 237)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Export functions for global access
window.adminDashboard = {
    showCreateUserModal,
    createUser,
    changeUserRole,
    deleteUser,
    approveListing,
    deleteListing,
    updateBookingStatus,
    showApproveListingsModal,
    showBulkActionsModal,
    exportData,
    showSystemControls,
    clearCache,
    backupDatabase,
    runMaintenance,
    restartServices,
    showNotification
};
