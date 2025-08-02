/**
 * Admin Panel JavaScript - Enhanced Admin Functionality
 * Provides modern admin panel features with improved UX
 */

class AdminPanel {
    constructor() {
        this.currentSort = {
            column: null,
            direction: 'asc'
        };
        this.init();
    }

    // Initialize admin panel functionality
    init() {
        this.initializeUserManagement();
        this.initializeDeleteForms();
        this.initializeNotifications();
        this.initializeAnimations();
    }

    // User management functionality
    initializeUserManagement() {
        // User verification toggle
        document.querySelectorAll('.verification-toggle').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const userId = button.dataset.userId;
                const isCurrentlyVerified = button.querySelector('i').classList.contains('fa-times-circle');
                this.toggleUserVerification(userId, isCurrentlyVerified);
            });
        });

        // User search functionality
        const userSearch = document.getElementById('userSearch');
        if (userSearch) {
            userSearch.addEventListener('input', (e) => {
                this.filterUsers(e.target.value);
            });
        }

        // Table sorting
        document.querySelectorAll('th[data-sortable]').forEach(header => {
            header.addEventListener('click', () => {
                this.sortTable(header);
            });
        });
    }

    // Toggle user verification status
    toggleUserVerification(userId, isCurrentlyVerified) {
        const button = document.querySelector(`[data-user-id="${userId}"]`);
        const icon = button.querySelector('i');
        const badge = document.querySelector(`tr:has([data-user-id="${userId}"]) .admin-badge`);
        
        // Show loading state
        button.disabled = true;
        icon.className = 'fas fa-spinner fa-spin';
        
        // Simulate API call (replace with actual endpoint)
        fetch(`/admin/users/${userId}/toggle-verification`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI based on new verification status
                const newVerified = !isCurrentlyVerified;
                
                // Update button icon and title
                icon.className = `fas fa-${newVerified ? 'times-circle' : 'check-circle'}`;
                button.title = newVerified ? 'Unverify User' : 'Verify User';
                
                // Update badge
                if (badge) {
                    badge.className = `admin-badge admin-badge-${newVerified ? 'success' : 'warning'}`;
                    badge.innerHTML = `<i class="fas fa-${newVerified ? 'check-circle' : 'clock'}"></i> ${newVerified ? 'Verified' : 'Unverified'}`;
                }
                
                this.showNotification(
                    `User ${newVerified ? 'verified' : 'unverified'} successfully`, 
                    'success'
                );
            } else {
                throw new Error(data.message || 'Failed to update verification status');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Failed to update verification status', 'error');
            
            // Reset icon
            icon.className = `fas fa-${isCurrentlyVerified ? 'times-circle' : 'check-circle'}`;
        })
        .finally(() => {
            button.disabled = false;
        });
    }

    // Filter users in table
    filterUsers(searchTerm) {
        const table = document.getElementById('usersTable');
        if (!table) return;

        const rows = table.querySelectorAll('tbody tr');
        const term = searchTerm.toLowerCase().trim();

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            let matchFound = false;

            cells.forEach(cell => {
                const text = cell.textContent.toLowerCase();
                if (text.includes(term)) {
                    matchFound = true;
                }
            });

            row.style.display = matchFound ? '' : 'none';
        });

        // Show "no results" message if needed
        const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
        this.toggleNoResultsMessage(table, visibleRows.length === 0 && term !== '');
    }

    // Sort table by column
    sortTable(header) {
        const table = header.closest('table');
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const columnIndex = Array.from(header.parentNode.children).indexOf(header);
        
        // Determine sort direction
        const isCurrentColumn = this.currentSort.column === columnIndex;
        const direction = isCurrentColumn && this.currentSort.direction === 'asc' ? 'desc' : 'asc';
        
        // Update sort state
        this.currentSort = { column: columnIndex, direction };
        
        // Clear previous sort indicators
        header.parentNode.querySelectorAll('th').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        
        // Add sort indicator
        header.classList.add(`sort-${direction}`);
        
        // Sort rows
        rows.sort((a, b) => {
            const aText = a.cells[columnIndex].textContent.trim();
            const bText = b.cells[columnIndex].textContent.trim();
            
            // Handle numeric sorting for certain columns
            const isNumeric = !isNaN(aText) && !isNaN(bText);
            
            let comparison;
            if (isNumeric) {
                comparison = parseFloat(aText) - parseFloat(bText);
            } else {
                comparison = aText.localeCompare(bText);
            }
            
            return direction === 'asc' ? comparison : -comparison;
        });
        
        // Reorder rows in DOM
        rows.forEach(row => tbody.appendChild(row));
        
        // Add animation
        tbody.classList.add('admin-fade-in');
        setTimeout(() => tbody.classList.remove('admin-fade-in'), 500);
    }

    // Initialize delete form confirmation
    initializeDeleteForms() {
        document.querySelectorAll('[data-action="delete"]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const itemName = link.dataset.itemName || 'this item';
                
                if (confirm(`Are you sure you want to delete "${itemName}"? This action cannot be undone.`)) {
                    // Add loading state
                    const originalText = link.innerHTML;
                    link.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                    link.style.pointerEvents = 'none';
                    
                    // Navigate to delete URL
                    window.location.href = link.href;
                }
            });
        });
    }

    // Show notification
    showNotification(message, type = 'info', duration = 5000) {
        // Remove existing notifications
        document.querySelectorAll('.admin-notification').forEach(n => n.remove());
        
        const notification = document.createElement('div');
        notification.className = `admin-notification admin-notification-${type}`;
        notification.innerHTML = `
            <div class="admin-notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span class="admin-notification-message">${message}</span>
                <button class="admin-notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after duration
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, duration);
    }

    // Get notification icon based on type
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Initialize animations
    initializeAnimations() {
        // Add fade-in animation to cards
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('admin-fade-in');
                }
            });
        });

        document.querySelectorAll('.admin-card, .admin-stat-card').forEach(card => {
            observer.observe(card);
        });
    }

    // Show/hide no results message
    toggleNoResultsMessage(table, show) {
        let noResultsRow = table.querySelector('.no-results-row');
        
        if (show && !noResultsRow) {
            const tbody = table.querySelector('tbody');
            const columnCount = table.querySelectorAll('thead th').length;
            
            noResultsRow = document.createElement('tr');
            noResultsRow.className = 'no-results-row';
            noResultsRow.innerHTML = `
                <td colspan="${columnCount}" class="admin-text-center" style="padding: 2rem;">
                    <i class="fas fa-search" style="font-size: 2rem; color: #6c757d; margin-bottom: 1rem;"></i>
                    <p style="color: #6c757d; margin: 0;">No results found for your search.</p>
                </td>
            `;
            
            tbody.appendChild(noResultsRow);
        } else if (!show && noResultsRow) {
            noResultsRow.remove();
        }
    }

    // Get CSRF token for forms
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
}

// Global functions for backward compatibility
window.toggleUserVerification = function(userId, isVerified) {
    if (window.adminPanel) {
        window.adminPanel.toggleUserVerification(userId, isVerified);
    }
};

// Initialize admin panel when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.adminPanel = new AdminPanel();
});

// Add notification styles dynamically
const notificationStyles = document.createElement('style');
notificationStyles.textContent = `
    .admin-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideInRight 0.3s ease-out;
    }
    
    .admin-notification-success {
        background: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
    }
    
    .admin-notification-error {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        color: #721c24;
    }
    
    .admin-notification-warning {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        color: #856404;
    }
    
    .admin-notification-info {
        background: #d1ecf1;
        border-left: 4px solid #17a2b8;
        color: #0c5460;
    }
    
    .admin-notification-content {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        gap: 8px;
    }
    
    .admin-notification-message {
        flex: 1;
        font-weight: 500;
    }
    
    .admin-notification-close {
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        opacity: 0.7;
        transition: opacity 0.2s;
    }
    
    .admin-notification-close:hover {
        opacity: 1;
    }
    
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
`;
document.head.appendChild(notificationStyles);
