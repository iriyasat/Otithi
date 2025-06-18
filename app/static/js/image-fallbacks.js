/**
 * Image Fallback Handler for Othiti Platform
 * Handles image loading errors and provides graceful fallbacks
 */

class OtithiImageHandler {
    constructor() {
        this.init();
    }

    init() {
        // Handle image errors on page load
        this.setupImageErrorHandlers();
        
        // Handle dynamically loaded images
        this.observeImageChanges();
    }

    setupImageErrorHandlers() {
        // Handle avatar images
        document.querySelectorAll('img[src*="profiles/"], img[src*="default_avatar"]').forEach(img => {
            img.addEventListener('error', (e) => this.handleAvatarError(e.target));
        });

        // Handle listing images
        document.querySelectorAll('img[src*="listings/"], img[src*="default_listing"]').forEach(img => {
            img.addEventListener('error', (e) => this.handleListingError(e.target));
        });

        // Handle general image errors
        document.querySelectorAll('img').forEach(img => {
            if (!img.hasAttribute('data-fallback-handled')) {
                img.addEventListener('error', (e) => this.handleGeneralError(e.target));
            }
        });
    }

    handleAvatarError(img) {
        if (img.hasAttribute('data-fallback-applied')) return;
        
        img.setAttribute('data-fallback-applied', 'true');
        
        // Try default avatar first
        if (!img.src.includes('default_avatar.png')) {
            img.src = '/static/images/ui/default_avatar.png';
            return;
        }

        // If default avatar also fails, create a text-based fallback
        this.createAvatarFallback(img);
    }

    handleListingError(img) {
        if (img.hasAttribute('data-fallback-applied')) return;
        
        img.setAttribute('data-fallback-applied', 'true');
        
        // Try default listing image first
        if (!img.src.includes('default_listing.jpg')) {
            img.src = '/static/images/ui/default_listing.jpg';
            return;
        }

        // If default listing also fails, create a placeholder
        this.createListingFallback(img);
    }

    handleGeneralError(img) {
        if (img.hasAttribute('data-fallback-applied')) return;
        
        img.setAttribute('data-fallback-applied', 'true');
        
        // Create a generic placeholder
        this.createGenericFallback(img);
    }

    createAvatarFallback(img) {
        const fallback = document.createElement('div');
        fallback.className = 'avatar-fallback';
        fallback.style.width = img.offsetWidth + 'px';
        fallback.style.height = img.offsetHeight + 'px';
        
        // Get user initial from alt text or use 'U'
        const initial = img.alt ? img.alt.charAt(0).toUpperCase() : 'U';
        fallback.textContent = initial;
        
        img.parentNode.replaceChild(fallback, img);
    }

    createListingFallback(img) {
        const fallback = document.createElement('div');
        fallback.className = 'listing-image-fallback listing-image';
        fallback.style.width = img.offsetWidth + 'px';
        fallback.style.height = img.offsetHeight + 'px';
        
        fallback.innerHTML = '<i class="fas fa-home"></i>';
        
        img.parentNode.replaceChild(fallback, img);
    }

    createGenericFallback(img) {
        const fallback = document.createElement('div');
        fallback.className = 'image-placeholder';
        fallback.style.width = img.offsetWidth + 'px';
        fallback.style.height = img.offsetHeight + 'px';
        
        fallback.innerHTML = '<i class="fas fa-image"></i>';
        
        img.parentNode.replaceChild(fallback, img);
    }

    observeImageChanges() {
        // Use MutationObserver to handle dynamically added images
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        const images = node.tagName === 'IMG' ? [node] : node.querySelectorAll('img');
                        images.forEach(img => {
                            if (!img.hasAttribute('data-fallback-handled')) {
                                img.setAttribute('data-fallback-handled', 'true');
                                
                                if (img.src.includes('profiles/') || img.src.includes('default_avatar')) {
                                    img.addEventListener('error', (e) => this.handleAvatarError(e.target));
                                } else if (img.src.includes('listings/') || img.src.includes('default_listing')) {
                                    img.addEventListener('error', (e) => this.handleListingError(e.target));
                                } else {
                                    img.addEventListener('error', (e) => this.handleGeneralError(e.target));
                                }
                            }
                        });
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Utility method to preload images
    preloadImage(src) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => resolve(img);
            img.onerror = reject;
            img.src = src;
        });
    }

    // Method to check if an image exists
    async imageExists(src) {
        try {
            await this.preloadImage(src);
            return true;
        } catch {
            return false;
        }
    }
}

// Initialize the image handler when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new OtithiImageHandler();
});

// Also make it globally available
window.OtithiImageHandler = OtithiImageHandler; 