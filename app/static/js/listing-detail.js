/**
 * Listing Detail Page JavaScript
 * Handles image gallery, favorites, sharing, price calculation, and reviews
 */

class ListingDetail {
    constructor() {
        this.currentImageIndex = 0;
        this.listingImages = [];
        this.isInitialized = false;
        this.listingId = null;
        this.pricePerNight = 0;
        
        this.init();
    }
    
    init() {
        if (this.isInitialized) return;
        
        // Extract listing data from page
        this.extractListingData();
        
        // Initialize components
        this.initImageGallery();
        this.initFavoriteButton();
        this.initShareButton();
        this.initPriceCalculation();
        this.initStarRating();
        this.initKeyboardShortcuts();
        
        this.isInitialized = true;
        console.log('Listing detail page initialized');
    }
    
    extractListingData() {
        // Get listing ID from URL
        const urlParts = window.location.pathname.split('/');
        this.listingId = urlParts[urlParts.length - 1];
        
        // Get images from script tag or data attribute
        const imagesScript = document.querySelector('script[data-listing-images]');
        if (imagesScript) {
            try {
                this.listingImages = JSON.parse(imagesScript.textContent);
            } catch (e) {
                console.warn('Could not parse listing images:', e);
                this.listingImages = ['demo_listing_1.jpg'];
            }
        } else {
            // Fallback: extract from existing script
            const scripts = document.querySelectorAll('script');
            for (let script of scripts) {
                if (script.textContent.includes('listingImages')) {
                    try {
                        const match = script.textContent.match(/listingImages\s*=\s*(\[.*?\])/);
                        if (match) {
                            this.listingImages = JSON.parse(match[1]);
                        }
                    } catch (e) {
                        console.warn('Could not extract images from script:', e);
                    }
                    break;
                }
            }
        }
        
        // Get price per night
        const priceElement = document.querySelector('.price-amount');
        if (priceElement) {
            const priceText = priceElement.textContent.replace(/[^\d.]/g, '');
            this.pricePerNight = parseFloat(priceText) || 0;
        }
        
        console.log('Extracted listing data:', {
            listingId: this.listingId,
            images: this.listingImages,
            pricePerNight: this.pricePerNight
        });
    }
    
    // Image Gallery Functions
    initImageGallery() {
        // Add click handlers to images
        const galleryImages = document.querySelectorAll('.photo-gallery img, .photo-overlay');
        galleryImages.forEach((element, index) => {
            element.addEventListener('click', () => this.openImageModal(index));
        });
        
        // Modal controls
        const modal = document.getElementById('imageModal');
        const closeBtn = modal?.querySelector('.modal-close');
        const prevBtn = modal?.querySelector('.modal-prev');
        const nextBtn = modal?.querySelector('.modal-next');
        
        if (closeBtn) closeBtn.addEventListener('click', () => this.closeImageModal());
        if (prevBtn) prevBtn.addEventListener('click', () => this.prevImage());
        if (nextBtn) nextBtn.addEventListener('click', () => this.nextImage());
        
        // Close on background click
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.closeImageModal();
            });
        }
    }
    
    openImageModal(index) {
        this.currentImageIndex = index;
        const modal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        const counter = document.getElementById('imageCounter');
        
        if (!modal || !modalImage) return;
        
        const imagePath = this.listingImages[this.currentImageIndex];
        const imageUrl = imagePath === 'demo_listing_1.jpg' 
            ? `/static/img/demo_listing_1.jpg`
            : `/static/uploads/listings/${imagePath}`;
        
        modalImage.src = imageUrl;
        if (counter) {
            counter.textContent = `${this.currentImageIndex + 1} / ${this.listingImages.length}`;
        }
        
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
    
    closeImageModal() {
        const modal = document.getElementById('imageModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }
    
    nextImage() {
        this.currentImageIndex = (this.currentImageIndex + 1) % this.listingImages.length;
        this.openImageModal(this.currentImageIndex);
    }
    
    prevImage() {
        this.currentImageIndex = (this.currentImageIndex - 1 + this.listingImages.length) % this.listingImages.length;
        this.openImageModal(this.currentImageIndex);
    }
    
    // Favorite Button Functions
    initFavoriteButton() {
        const favoriteBtn = document.querySelector('.action-button:has(.bi-heart)');
        if (!favoriteBtn) return;
        
        // Check if already favorited
        this.updateFavoriteStatus();
        
        favoriteBtn.addEventListener('click', () => this.toggleFavorite());
    }
    
    async toggleFavorite() {
        const favoriteBtn = document.querySelector('.action-button:has(.bi-heart)');
        const heartIcon = favoriteBtn?.querySelector('i');
        
        if (!favoriteBtn || !heartIcon) return;
        
        const isFavorited = favoriteBtn.classList.contains('favorited');
        
        try {
            // Update UI immediately for better UX
            this.updateFavoriteUI(!isFavorited);
            
            // Make API call
            const response = await fetch('/api/favorites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    listing_id: this.listingId,
                    action: isFavorited ? 'remove' : 'add'
                })
            });
            
            if (!response.ok) {
                // Revert UI if API call failed
                this.updateFavoriteUI(isFavorited);
                
                if (response.status === 401) {
                    this.showLoginPrompt('Please log in to save favorites');
                } else {
                    this.showNotification('Error updating favorites', 'error');
                }
                return;
            }
            
            const result = await response.json();
            this.showNotification(
                isFavorited ? 'Removed from favorites' : 'Added to favorites',
                'success'
            );
            
        } catch (error) {
            console.error('Error toggling favorite:', error);
            // Revert UI
            this.updateFavoriteUI(isFavorited);
            this.showNotification('Error updating favorites', 'error');
        }
    }
    
    updateFavoriteUI(isFavorited) {
        const favoriteBtn = document.querySelector('.action-button:has(.bi-heart)');
        const heartIcon = favoriteBtn?.querySelector('i');
        const btnText = favoriteBtn?.querySelector('span') || favoriteBtn?.childNodes[1];
        
        if (!favoriteBtn || !heartIcon) return;
        
        if (isFavorited) {
            favoriteBtn.classList.add('favorited');
            heartIcon.classList.remove('bi-heart');
            heartIcon.classList.add('bi-heart-fill');
            if (btnText) btnText.textContent = ' Saved';
        } else {
            favoriteBtn.classList.remove('favorited');
            heartIcon.classList.remove('bi-heart-fill');
            heartIcon.classList.add('bi-heart');
            if (btnText) btnText.textContent = ' Save';
        }
    }
    
    async updateFavoriteStatus() {
        try {
            const response = await fetch(`/api/favorites/check/${this.listingId}`, {
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                this.updateFavoriteUI(result.is_favorited);
            }
        } catch (error) {
            console.error('Error checking favorite status:', error);
        }
    }
    
    // Share Button Functions
    initShareButton() {
        const shareBtn = document.querySelector('.action-button:has(.bi-share)');
        if (!shareBtn) return;
        
        shareBtn.addEventListener('click', () => this.handleShare());
    }
    
    async handleShare() {
        const shareData = {
            title: document.title,
            text: `Check out this amazing place: ${document.querySelector('.listing-title')?.textContent}`,
            url: window.location.href
        };
        
        try {
            // Try native sharing first (mobile devices)
            if (navigator.share) {
                await navigator.share(shareData);
                this.showNotification('Shared successfully!', 'success');
                return;
            }
            
            // Fallback to share modal
            this.showShareModal(shareData);
            
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Error sharing:', error);
                this.showShareModal(shareData);
            }
        }
    }
    
    showShareModal(shareData) {
        // Create share modal
        const modal = document.createElement('div');
        modal.className = 'share-modal';
        modal.innerHTML = `
            <div class="share-modal-content">
                <div class="share-header">
                    <h3>Share this listing</h3>
                    <button class="share-close">&times;</button>
                </div>
                <div class="share-options">
                    <button class="share-option" data-platform="copy">
                        <i class="bi bi-clipboard"></i>
                        Copy Link
                    </button>
                    <button class="share-option" data-platform="facebook">
                        <i class="bi bi-facebook"></i>
                        Facebook
                    </button>
                    <button class="share-option" data-platform="twitter">
                        <i class="bi bi-twitter"></i>
                        Twitter
                    </button>
                    <button class="share-option" data-platform="whatsapp">
                        <i class="bi bi-whatsapp"></i>
                        WhatsApp
                    </button>
                    <button class="share-option" data-platform="email">
                        <i class="bi bi-envelope"></i>
                        Email
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add styles
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1001;
        `;
        
        const content = modal.querySelector('.share-modal-content');
        content.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 24px;
            max-width: 400px;
            width: 90%;
        `;
        
        // Add event listeners
        modal.querySelector('.share-close').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
        
        modal.querySelectorAll('.share-option').forEach(option => {
            option.addEventListener('click', () => {
                const platform = option.dataset.platform;
                this.shareToplatform(platform, shareData);
                document.body.removeChild(modal);
            });
        });
    }
    
    async shareToplatform(platform, shareData) {
        const url = encodeURIComponent(shareData.url);
        const text = encodeURIComponent(shareData.text);
        const title = encodeURIComponent(shareData.title);
        
        switch (platform) {
            case 'copy':
                try {
                    await navigator.clipboard.writeText(shareData.url);
                    this.showNotification('Link copied to clipboard!', 'success');
                } catch (error) {
                    console.error('Failed to copy:', error);
                    this.showNotification('Failed to copy link', 'error');
                }
                break;
                
            case 'facebook':
                window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank');
                break;
                
            case 'twitter':
                window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, '_blank');
                break;
                
            case 'whatsapp':
                window.open(`https://wa.me/?text=${text}%20${url}`, '_blank');
                break;
                
            case 'email':
                window.location.href = `mailto:?subject=${title}&body=${text}%0A%0A${shareData.url}`;
                break;
        }
    }
    
    // Price Calculation Functions
    initPriceCalculation() {
        const checkInInput = document.querySelector('input[name="check_in"]');
        const checkOutInput = document.querySelector('input[name="check_out"]');
        
        if (checkInInput) {
            checkInInput.addEventListener('change', () => this.updatePriceCalculation());
        }
        if (checkOutInput) {
            checkOutInput.addEventListener('change', () => this.updatePriceCalculation());
        }
        
        // Initial calculation
        this.updatePriceCalculation();
    }
    
    updatePriceCalculation() {
        const checkInInput = document.querySelector('input[name="check_in"]');
        const checkOutInput = document.querySelector('input[name="check_out"]');
        const priceBreakdown = document.getElementById('price-breakdown');
        const pricePlaceholder = document.getElementById('price-placeholder');
        
        if (!checkInInput || !checkOutInput || !priceBreakdown || !pricePlaceholder) return;
        
        if (checkInInput.value && checkOutInput.value) {
            const checkIn = new Date(checkInInput.value);
            const checkOut = new Date(checkOutInput.value);
            
            if (checkOut > checkIn) {
                const nights = Math.ceil((checkOut - checkIn) / (1000 * 60 * 60 * 24));
                const basePrice = this.pricePerNight * nights;
                const serviceFee = basePrice * 0.15; // 15% service fee
                const total = basePrice + serviceFee;
                
                // Update the display
                const nightsText = document.getElementById('nights-text');
                const basePriceEl = document.getElementById('base-price');
                const serviceFeeEl = document.getElementById('service-fee');
                const totalPriceEl = document.getElementById('total-price');
                
                if (nightsText) nightsText.textContent = `৳${this.pricePerNight} x ${nights} night${nights > 1 ? 's' : ''}`;
                if (basePriceEl) basePriceEl.textContent = `৳${basePrice.toFixed(2)}`;
                if (serviceFeeEl) serviceFeeEl.textContent = `৳${serviceFee.toFixed(2)}`;
                if (totalPriceEl) totalPriceEl.textContent = `৳${total.toFixed(2)}`;
                
                // Show price breakdown, hide placeholder
                priceBreakdown.style.display = 'block';
                pricePlaceholder.style.display = 'none';
            } else {
                // Hide price breakdown, show placeholder
                priceBreakdown.style.display = 'none';
                pricePlaceholder.style.display = 'block';
            }
        } else {
            // Hide price breakdown, show placeholder
            priceBreakdown.style.display = 'none';
            pricePlaceholder.style.display = 'block';
        }
    }
    
    // Star Rating Functions
    initStarRating() {
        const starLabels = document.querySelectorAll('.star-rating');
        const ratingInputs = document.querySelectorAll('input[name="rating"]');
        
        if (starLabels.length === 0) return;
        
        starLabels.forEach((label, index) => {
            label.addEventListener('mouseover', () => {
                this.highlightStars(index, starLabels);
            });
            
            label.addEventListener('click', () => {
                if (ratingInputs[index]) {
                    ratingInputs[index].checked = true;
                }
                this.setStarRating(index, starLabels);
            });
        });
        
        // Reset stars on mouse leave if no rating selected
        const starContainer = starLabels[0]?.parentNode;
        if (starContainer) {
            starContainer.addEventListener('mouseleave', () => {
                const selectedRating = document.querySelector('input[name="rating"]:checked');
                if (selectedRating) {
                    const selectedIndex = parseInt(selectedRating.value) - 1;
                    this.setStarRating(selectedIndex, starLabels);
                } else {
                    this.resetStars(starLabels);
                }
            });
        }
    }
    
    highlightStars(index, starLabels) {
        starLabels.forEach((label, i) => {
            if (i <= index) {
                label.style.color = '#FFD700';
            } else {
                label.style.color = '#ddd';
            }
        });
    }
    
    setStarRating(index, starLabels) {
        starLabels.forEach((label, i) => {
            if (i <= index) {
                label.style.color = '#FFD700';
                label.classList.add('active');
            } else {
                label.style.color = '#ddd';
                label.classList.remove('active');
            }
        });
    }
    
    resetStars(starLabels) {
        starLabels.forEach(label => {
            label.style.color = '#ddd';
            label.classList.remove('active');
        });
    }
    
    // Keyboard Shortcuts
    initKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            const modal = document.getElementById('imageModal');
            if (modal && modal.style.display === 'block') {
                switch (e.key) {
                    case 'Escape':
                        this.closeImageModal();
                        break;
                    case 'ArrowLeft':
                        this.prevImage();
                        break;
                    case 'ArrowRight':
                        this.nextImage();
                        break;
                }
            }
        });
    }
    
    // Utility Functions
    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Style the notification
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 1002;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (notification.parentNode) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
    
    showLoginPrompt(message) {
        this.showNotification(message, 'info');
        setTimeout(() => {
            window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
        }, 2000);
    }
}

// Global functions for backward compatibility
window.openImageModal = function(index) {
    if (window.listingDetailInstance) {
        window.listingDetailInstance.openImageModal(index);
    }
};

window.closeImageModal = function() {
    if (window.listingDetailInstance) {
        window.listingDetailInstance.closeImageModal();
    }
};

window.nextImage = function() {
    if (window.listingDetailInstance) {
        window.listingDetailInstance.nextImage();
    }
};

window.prevImage = function() {
    if (window.listingDetailInstance) {
        window.listingDetailInstance.prevImage();
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on listing detail pages
    if (window.location.pathname.includes('/listings/')) {
        window.listingDetailInstance = new ListingDetail();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ListingDetail;
}
