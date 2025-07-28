/**
 * Otithi Favorites JavaScript
 * Favorites management and interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeFavorites();
});

function initializeFavorites() {
    // Initialize favorite buttons
    initializeFavoriteButtons();
    
    // Initialize favorites page functionality
    initializeFavoritesPage();
    
    // Initialize favorite filters
    initializeFavoriteFilters();
}

/**
 * Initialize favorite button functionality
 */
function initializeFavoriteButtons() {
    const favoriteButtons = document.querySelectorAll('.favorite-btn, .btn[title*="wishlist"], .btn[title*="Save"]');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const listingId = this.dataset.listingId;
            const heartIcon = this.querySelector('i');
            
            if (!listingId) {
                console.error('No listing ID found on favorite button');
                return;
            }
            
            // Toggle favorite status
            toggleFavoriteStatus(button, listingId, heartIcon);
        });
    });
}

/**
 * Initialize favorites page functionality
 */
function initializeFavoritesPage() {
    const favoriteButtons = document.querySelectorAll('.favorite-btn');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const listingId = this.dataset.listingId;
            const heartIcon = this.querySelector('i');
            
            // Remove from favorites (since this is the favorites page)
            if (confirm('Remove this listing from your favorites?')) {
                removeFromFavorites(button, listingId);
            }
        });
    });
}

/**
 * Initialize favorite filters
 */
function initializeFavoriteFilters() {
    const filterButtons = document.querySelectorAll('.favorite-filter');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const filter = this.dataset.filter;
            
            // Remove active from all filter buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active to clicked button
            this.classList.add('active');
            
            // Filter favorites
            filterFavorites(filter);
        });
    });
}

/**
 * Toggle favorite status for a listing
 * @param {HTMLElement} button - The favorite button element
 * @param {number} listingId - The listing ID
 * @param {HTMLElement} heartIcon - The heart icon element
 */
async function toggleFavoriteStatus(button, listingId, heartIcon) {
    try {
        const config = window.OtithiConfig?.API || {};
        const endpoint = config.LISTINGS || '/api/listings';
        const response = await fetch(`${endpoint}/${listingId}/favorite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Update button appearance
            if (data.isFavorite) {
                heartIcon.classList.remove('bi-heart');
                heartIcon.classList.add('bi-heart-fill');
                button.classList.add('text-danger');
                button.title = 'Remove from favorites';
            } else {
                heartIcon.classList.remove('bi-heart-fill');
                heartIcon.classList.add('bi-heart');
                button.classList.remove('text-danger');
                button.title = 'Add to favorites';
            }
            
            showNotification(data.message, 'success');
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        console.error('Error toggling favorite:', error);
        showNotification('Error updating favorite status', 'error');
    }
}

/**
 * Remove listing from favorites
 * @param {HTMLElement} button - The favorite button element
 * @param {number} listingId - The listing ID
 */
async function removeFromFavorites(button, listingId) {
    try {
        const config = window.OtithiConfig?.API || {};
        const endpoint = config.LISTINGS || '/api/listings';
        const response = await fetch(`${endpoint}/${listingId}/favorite`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Animate removal
            const card = button.closest('.col-lg-4, .col-md-6, .listing-card');
            if (card) {
                card.style.opacity = '0.5';
                card.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    card.remove();
                    
                    // Check if no more favorites
                    const remainingCards = document.querySelectorAll('.listing-card');
                    if (remainingCards.length === 0) {
                        location.reload(); // Reload to show empty state
                    }
                }, 300);
            }
            
            showNotification('Removed from favorites', 'success');
        } else {
            showNotification(data.message || 'Failed to remove from favorites', 'error');
        }
    } catch (error) {
        console.error('Error removing from favorites:', error);
        showNotification('Error removing from favorites', 'error');
    }
}

/**
 * Filter favorites by criteria
 * @param {string} filter - The filter criteria
 */
function filterFavorites(filter) {
    const favoriteCards = document.querySelectorAll('.listing-card');
    
    favoriteCards.forEach(card => {
        let shouldShow = true;
        
        switch (filter) {
            case 'all':
                shouldShow = true;
                break;
            case 'available':
                const availability = card.dataset.availability;
                shouldShow = availability === 'available';
                break;
            case 'recent':
                const addedDate = new Date(card.dataset.addedDate);
                const oneWeekAgo = new Date();
                oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
                shouldShow = addedDate >= oneWeekAgo;
                break;
            case 'price-low':
                const price = parseFloat(card.dataset.price);
                shouldShow = price <= 1000; // Adjust threshold as needed
                break;
            case 'price-high':
                const priceHigh = parseFloat(card.dataset.price);
                shouldShow = priceHigh > 1000; // Adjust threshold as needed
                break;
            default:
                shouldShow = true;
        }
        
        if (shouldShow) {
            card.style.display = 'block';
            card.style.opacity = '1';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Update results count
    updateFavoritesCount();
}

/**
 * Update favorites count display
 */
function updateFavoritesCount() {
    const visibleCards = document.querySelectorAll('.listing-card[style*="display: block"], .listing-card:not([style*="display: none"])');
    const countElement = document.querySelector('.favorites-count');
    
    if (countElement) {
        countElement.textContent = visibleCards.length;
    }
}

/**
 * Sort favorites by criteria
 * @param {string} sortBy - The sorting criteria
 */
function sortFavorites(sortBy) {
    const favoritesContainer = document.querySelector('.favorites-grid, .listings-grid');
    const favoriteCards = Array.from(document.querySelectorAll('.listing-card'));
    
    if (!favoritesContainer) return;
    
    favoriteCards.sort((a, b) => {
        switch (sortBy) {
            case 'price-low':
                return parseFloat(a.dataset.price) - parseFloat(b.dataset.price);
            case 'price-high':
                return parseFloat(b.dataset.price) - parseFloat(a.dataset.price);
            case 'rating':
                return parseFloat(b.dataset.rating) - parseFloat(a.dataset.rating);
            case 'date-added':
                return new Date(b.dataset.addedDate) - new Date(a.dataset.addedDate);
            case 'name':
                return a.dataset.title.localeCompare(b.dataset.title);
            default:
                return 0;
        }
    });
    
    // Reorder cards in DOM
    favoriteCards.forEach(card => {
        favoritesContainer.appendChild(card);
    });
}

/**
 * Export favorites to CSV
 */
function exportFavorites() {
    const favoriteCards = document.querySelectorAll('.listing-card');
    const csvData = [];
    
    // Add header
    csvData.push(['Title', 'Location', 'Price', 'Rating', 'Added Date']);
    
    // Add data
    favoriteCards.forEach(card => {
        csvData.push([
            card.dataset.title || '',
            card.dataset.location || '',
            card.dataset.price || '',
            card.dataset.rating || '',
            card.dataset.addedDate || ''
        ]);
    });
    
    // Create CSV content
    const csvContent = csvData.map(row => row.join(',')).join('\n');
    
    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'favorites.csv';
    a.click();
    
    // Cleanup
    window.URL.revokeObjectURL(url);
    
    showNotification('Favorites exported successfully', 'success');
}

/**
 * Share favorites
 */
function shareFavorites() {
    const favoriteCards = document.querySelectorAll('.listing-card');
    const favoriteIds = Array.from(favoriteCards).map(card => card.dataset.listingId);
    
    if (favoriteIds.length === 0) {
        showNotification('No favorites to share', 'warning');
        return;
    }
    
    const shareUrl = `${window.location.origin}/favorites?shared=true&ids=${favoriteIds.join(',')}`;
    
    if (navigator.share) {
        navigator.share({
            title: 'My Favorite Listings',
            text: 'Check out my favorite listings on Otithi!',
            url: shareUrl
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(shareUrl).then(() => {
            showNotification('Share link copied to clipboard', 'success');
        }).catch(() => {
            showNotification('Failed to copy share link', 'error');
        });
    }
}

/**
 * Bulk remove favorites
 */
function bulkRemoveFavorites() {
    const selectedCards = document.querySelectorAll('.listing-card input[type="checkbox"]:checked');
    
    if (selectedCards.length === 0) {
        showNotification('Please select favorites to remove', 'warning');
        return;
    }
    
    if (confirm(`Are you sure you want to remove ${selectedCards.length} favorites?`)) {
        const promises = Array.from(selectedCards).map(checkbox => {
            const card = checkbox.closest('.listing-card');
            const listingId = card.dataset.listingId;
            
            return fetch(`/api/listings/${listingId}/favorite`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
        });
        
        Promise.all(promises).then(() => {
            showNotification(`${selectedCards.length} favorites removed`, 'success');
            location.reload();
        }).catch(error => {
            console.error('Error removing favorites:', error);
            showNotification('Error removing favorites', 'error');
        });
    }
}

/**
 * Initialize bulk selection
 */
function initializeBulkSelection() {
    const selectAllCheckbox = document.querySelector('#select-all-favorites');
    const favoriteCheckboxes = document.querySelectorAll('.listing-card input[type="checkbox"]');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            favoriteCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
        });
    }
    
    favoriteCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const checkedCount = document.querySelectorAll('.listing-card input[type="checkbox"]:checked').length;
            const totalCount = favoriteCheckboxes.length;
            
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = checkedCount === totalCount;
                selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < totalCount;
            }
        });
    });
} 