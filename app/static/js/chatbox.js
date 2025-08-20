/**
 * Modern Chatbox JavaScript - Floating Copilot Studio Integration
 * Handles toggle functionality, state persistence, and user interactions
 */

class OtithiChatbox {
    constructor() {
        this.isOpen = false;
        this.isLoading = false;
        this.hasError = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        
        // Storage keys for persistence (must be defined before generateSessionId)
        this.STORAGE_KEYS = {
            CHAT_STATE: 'otithi_chat_state',
            SESSION_ID: 'otithi_chat_session',
            LAST_ACTIVITY: 'otithi_chat_activity'
        };
        
        this.sessionId = this.generateSessionId();
        
        // DOM elements
        this.container = null;
        this.toggle = null;
        this.window = null;
        this.iframe = null;
        this.loading = null;
        this.error = null;
        
        this.init();
    }
    
    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }
    
    setup() {
        this.createChatboxHTML();
        this.bindEvents();
        this.restoreState();
        this.addPulseAnimation();
        this.setupPeriodicSave();
    }
    
    generateSessionId() {
        // Try to restore existing session first
        const existingSessionId = localStorage.getItem(this.STORAGE_KEYS.SESSION_ID);
        const lastActivity = parseInt(localStorage.getItem(this.STORAGE_KEYS.LAST_ACTIVITY) || '0');
        const timeSinceLastActivity = Date.now() - lastActivity;
        
        // If session is recent (within 4 hours), reuse it
        if (existingSessionId && timeSinceLastActivity < 4 * 60 * 60 * 1000) {
            return existingSessionId;
        }
        
        // Generate new session ID
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(2, 15);
        const sessionId = `otithi_${timestamp}_${random}`;
        
        // Save the new session ID
        localStorage.setItem(this.STORAGE_KEYS.SESSION_ID, sessionId);
        
        return sessionId;
    }
    
    updateIframeWithSession() {
        // Update iframe URL to include session information if needed
        if (this.iframe && this.iframe.src) {
            const url = new URL(this.iframe.src);
            url.searchParams.set('sessionId', this.sessionId);
            url.searchParams.set('timestamp', Date.now().toString());
            
            // Only update if URL actually changed to avoid unnecessary reloads
            if (this.iframe.src !== url.toString()) {
                this.iframe.src = url.toString();
            }
        }
    }
    
    createChatboxHTML() {
        // Create the main container
        this.container = document.createElement('div');
        this.container.className = 'chatbox-container';
        this.container.innerHTML = `
            <!-- Toggle Button -->
            <button class="chatbox-toggle" id="chatboxToggle" aria-label="Open Otithi Tour Guide">
                💬
            </button>
            
            <!-- Chatbox Window -->
            <div class="chatbox-window" id="chatboxWindow">
                <!-- Header -->
                <div class="chatbox-header">
                    <button class="chatbox-close" id="chatboxClose" aria-label="Close chat">
                        ×
                    </button>
                </div>
                
                <!-- Content -->
                <div class="chatbox-content">
                    <!-- Loading State -->
                    <div class="chatbox-loading" id="chatboxLoading">
                        <div class="chatbox-spinner"></div>
                        <div>Loading your tour guide...</div>
                    </div>
                    
                    <!-- Error State -->
                    <div class="chatbox-error" id="chatboxError" style="display: none;">
                        <div class="chatbox-error-icon">🚫</div>
                        <div><strong>Connection Error</strong></div>
                        <div style="font-size: 14px; margin: 8px 0;">
                            Unable to load the tour guide. Please check your internet connection.
                        </div>
                        <button class="chatbox-retry" onclick="otithiChatbox.retryLoad()">
                            Try Again
                        </button>
                    </div>
                    
                    <!-- Copilot Studio Iframe -->
                    <iframe 
                        class="chatbox-iframe" 
                        id="chatboxIframe"
                        src="https://copilotstudio.microsoft.com/environments/Default-9e0adbba-24b8-4ac6-804f-cb243f135ac2/bots/cr908_otithiTourGuide/webchat?__version__=2" 
                        frameborder="0"
                        allow="microphone; camera"
                        title="Otithi Tour Guide"
                        style="display: none;">
                    </iframe>
                </div>
            </div>
        `;
        
        // Append to body
        document.body.appendChild(this.container);
        
        // Get references to DOM elements
        this.toggle = document.getElementById('chatboxToggle');
        this.window = document.getElementById('chatboxWindow');
        this.iframe = document.getElementById('chatboxIframe');
        this.loading = document.getElementById('chatboxLoading');
        this.error = document.getElementById('chatboxError');
        this.closeBtn = document.getElementById('chatboxClose');
    }
    
    bindEvents() {
        // Toggle button click
        this.toggle.addEventListener('click', () => this.toggleChatbox());
        
        // Close button click
        this.closeBtn.addEventListener('click', () => this.closeChatbox());
        
        // Iframe load events
        this.iframe.addEventListener('load', () => this.handleIframeLoad());
        this.iframe.addEventListener('error', () => this.handleIframeError());
        
        // Click outside to close (optional)
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.container.contains(e.target)) {
                // Uncomment the line below if you want to close on outside click
                // this.closeChatbox();
            }
        });
        
        // Keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeChatbox();
            }
        });
        
        // Window resize handling for mobile
        window.addEventListener('resize', () => this.handleResize());
    }
    
    toggleChatbox() {
        if (this.isOpen) {
            this.closeChatbox();
        } else {
            this.openChatbox();
        }
    }
    
    openChatbox() {
        this.isOpen = true;
        this.window.classList.add('show');
        this.toggle.classList.add('open');
        this.toggle.innerHTML = '×';
        this.toggle.classList.remove('pulse');
        
        // Start loading iframe if not already loaded
        if (!this.iframe.src || this.hasError) {
            this.loadIframe();
        }
        
        // Save state
        this.saveState();
        
        // Track analytics
        this.trackEvent('chatbox_opened');
        
        // Focus management for accessibility
        this.iframe.focus();
    }
    
    closeChatbox() {
        this.isOpen = false;
        this.window.classList.remove('show');
        this.toggle.classList.remove('open');
        this.toggle.innerHTML = '💬';
        
        // Save state
        this.saveState();
        
        // Track analytics
        this.trackEvent('chatbox_closed');
    }
    
    loadIframe() {
        this.isLoading = true;
        this.hasError = false;
        this.loading.style.display = 'flex';
        this.error.style.display = 'none';
        this.iframe.style.display = 'none';
        
        // Build iframe URL with session information
        const baseUrl = 'https://copilotstudio.microsoft.com/environments/Default-9e0adbba-24b8-4ac6-804f-cb243f135ac2/bots/cr908_otithiTourGuide/webchat';
        const url = new URL(baseUrl);
        url.searchParams.set('__version__', '2');
        url.searchParams.set('sessionId', this.sessionId);
        url.searchParams.set('timestamp', Date.now().toString());
        
        // Set iframe source (trigger load)
        this.iframe.src = url.toString();
        
        // Set timeout for loading
        this.loadTimeout = setTimeout(() => {
            if (this.isLoading) {
                this.handleIframeError();
            }
        }, 15000); // 15 second timeout
    }
    
    handleIframeLoad() {
        console.log('Otithi Tour Guide loaded successfully');
        
        clearTimeout(this.loadTimeout);
        this.isLoading = false;
        this.hasError = false;
        this.retryCount = 0;
        
        this.loading.style.display = 'none';
        this.error.style.display = 'none';
        this.iframe.style.display = 'block';
        
        this.trackEvent('chatbox_iframe_loaded');
    }
    
    handleIframeError() {
        console.error('Failed to load Otithi Tour Guide');
        
        clearTimeout(this.loadTimeout);
        this.isLoading = false;
        this.hasError = true;
        
        this.loading.style.display = 'none';
        this.iframe.style.display = 'none';
        this.error.style.display = 'flex';
        
        this.trackEvent('chatbox_iframe_error', { retryCount: this.retryCount });
    }
    
    retryLoad() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log(`Retrying to load Otithi Tour Guide (attempt ${this.retryCount})`);
            this.loadIframe();
        } else {
            console.error('Max retry attempts reached for Otithi Tour Guide');
            this.trackEvent('chatbox_max_retries_reached');
        }
    }
    
    addPulseAnimation() {
        // Add pulse animation after page load to draw attention
        setTimeout(() => {
            if (!this.isOpen) {
                this.toggle.classList.add('pulse');
                // Remove pulse after 6 seconds
                setTimeout(() => {
                    this.toggle.classList.remove('pulse');
                }, 6000);
            }
        }, 3000); // Start pulse after 3 seconds
    }
    
    saveState() {
        try {
            const state = {
                isOpen: this.isOpen,
                sessionId: this.sessionId,
                lastActivity: Date.now(),
                iframeLoaded: this.iframe && this.iframe.src
            };
            
            localStorage.setItem(this.STORAGE_KEYS.CHAT_STATE, JSON.stringify(state));
            localStorage.setItem(this.STORAGE_KEYS.SESSION_ID, this.sessionId);
            localStorage.setItem(this.STORAGE_KEYS.LAST_ACTIVITY, Date.now().toString());
            
            // Also save to sessionStorage for tab-specific persistence
            sessionStorage.setItem(this.STORAGE_KEYS.CHAT_STATE, JSON.stringify(state));
        } catch (e) {
            console.warn('Unable to save chatbox state to localStorage:', e);
        }
    }
    
    restoreState() {
        try {
            // First check sessionStorage for tab-specific state
            let savedState = sessionStorage.getItem(this.STORAGE_KEYS.CHAT_STATE);
            
            // If no session state, check localStorage for persistent state
            if (!savedState) {
                savedState = localStorage.getItem(this.STORAGE_KEYS.CHAT_STATE);
            }
            
            if (savedState) {
                const state = JSON.parse(savedState);
                const lastActivity = parseInt(localStorage.getItem(this.STORAGE_KEYS.LAST_ACTIVITY) || '0');
                const timeSinceLastActivity = Date.now() - lastActivity;
                
                // Only restore if activity was recent (within 1 hour)
                if (timeSinceLastActivity < 60 * 60 * 1000) {
                    this.sessionId = state.sessionId || this.sessionId;
                    
                    if (state.isOpen) {
                        // Small delay to ensure everything is ready
                        setTimeout(() => this.openChatbox(), 500);
                    }
                }
            }
        } catch (e) {
            console.warn('Unable to restore chatbox state from storage:', e);
        }
    }
    
    setupPeriodicSave() {
        // Save state periodically to prevent data loss
        setInterval(() => {
            if (this.isOpen) {
                this.saveState();
            }
        }, 30000); // Save every 30 seconds when open
        
        // Save state when page is about to unload
        window.addEventListener('beforeunload', () => {
            this.saveState();
        });
        
        // Save state when page becomes hidden (tab switch)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.saveState();
            }
        });
        
        // Listen for storage changes from other tabs
        window.addEventListener('storage', (e) => {
            if (e.key === this.STORAGE_KEYS.CHAT_STATE) {
                this.handleCrossTabSync(e);
            }
        });
    }
    
    handleCrossTabSync(event) {
        try {
            if (event.newValue) {
                const newState = JSON.parse(event.newValue);
                const currentTime = Date.now();
                const timeDiff = Math.abs(currentTime - newState.lastActivity);
                
                // Only sync if the change is recent (within 5 seconds)
                if (timeDiff < 5000) {
                    if (newState.isOpen && !this.isOpen) {
                        // Another tab opened the chatbox
                        this.openChatbox();
                    } else if (!newState.isOpen && this.isOpen) {
                        // Another tab closed the chatbox
                        this.closeChatbox();
                    }
                    
                    // Update session ID if needed
                    if (newState.sessionId && newState.sessionId !== this.sessionId) {
                        this.sessionId = newState.sessionId;
                    }
                }
            }
        } catch (e) {
            console.warn('Error handling cross-tab chatbox sync:', e);
        }
    }
    
    handleResize() {
        // Handle mobile responsiveness
        if (window.innerWidth <= 768 && this.isOpen) {
            // Adjust positioning for mobile if needed
            this.window.style.bottom = '80px';
        }
    }
    
    trackEvent(eventName, data = {}) {
        // Track analytics events (integrate with your analytics service)
        try {
            if (typeof gtag !== 'undefined') {
                gtag('event', eventName, {
                    event_category: 'Otithi_Chatbox',
                    ...data
                });
            }
            
            // Console log for development
            console.log(`Chatbox Event: ${eventName}`, data);
        } catch (e) {
            console.warn('Analytics tracking failed:', e);
        }
    }
    
    // Public methods for external control
    open() {
        this.openChatbox();
    }
    
    close() {
        this.closeChatbox();
    }
    
    toggle() {
        this.toggleChatbox();
    }
    
    isVisible() {
        return this.isOpen;
    }
}

// Global function for legacy support
function toggleChatbox() {
    if (window.otithiChatbox) {
        window.otithiChatbox.toggle();
    }
}

// Initialize chatbox when script loads
window.otithiChatbox = new OtithiChatbox();

// Expose for debugging in development
if (typeof console !== 'undefined') {
    console.log('Otithi Chatbox initialized successfully');
}
