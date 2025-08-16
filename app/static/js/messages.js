// Traditional Messaging System - No WebSocket/SocketIO
// Simple, reliable messaging with periodic polling

class TraditionalMessagingSystem {
    constructor() {
        this.currentConversationId = null;
        this.currentOtherUserId = null;
        this.conversations = [];
        this.currentMessages = [];
        this.pollInterval = null;
        this.pollIntervalMs = 5000; // Poll every 5 seconds
        
        this.init();
    }

    init() {
        console.log('🔄 Initializing Traditional Messaging System');
        
        // Initialize DOM elements
        this.initializeElements();
        
        // Load initial data
        this.loadConversations();
        
        // Setup periodic polling for new messages
        this.startPolling();
        
        // Setup event listeners
        this.setupEventListeners();
    }
    
    initializeElements() {
        this.conversationsList = document.getElementById('conversationsList');
        this.chatArea = document.getElementById('chatArea');
        this.messagesList = document.getElementById('messagesList');
        this.messageForm = document.getElementById('messageForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
    }
    
    setupEventListeners() {
        // Send message form
        if (this.messageForm) {
            this.messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }
        
        // Send button
        if (this.sendButton) {
            this.sendButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }
        
        // Enter key to send
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
        
        // Filter tabs
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.handleFilterTab(e));
        });
        
        // Mark all as read
        const markAllReadBtn = document.getElementById('markAllRead');
        if (markAllReadBtn) {
            markAllReadBtn.addEventListener('click', () => this.markAllAsRead());
        }
        
        // Search functionality
        const searchToggle = document.getElementById('searchToggle');
        if (searchToggle) {
            searchToggle.addEventListener('click', () => this.toggleSearch());
        }
        
        const searchInput = document.getElementById('searchMessages');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.handleSearch(e));
        }
    }
    
    startPolling() {
        // Poll for new conversations every 5 seconds
        this.pollInterval = setInterval(() => {
            this.loadConversations();
            
            // If viewing a conversation, poll for new messages
            if (this.currentConversationId) {
                this.loadMessages(this.currentConversationId, false); // Silent load
            }
        }, this.pollIntervalMs);
        
        console.log(`📡 Started polling every ${this.pollIntervalMs / 1000} seconds`);
    }
    
    stopPolling() {
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
            this.pollInterval = null;
            console.log('⏹️ Stopped polling');
        }
    }
    
    async loadConversations() {
        try {
            const response = await fetch('/api/conversations', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success) {
                this.conversations = result.conversations;
                this.renderConversations();
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }
    
    renderConversations() {
        if (!this.conversationsList) return;
        
        if (this.conversations.length === 0) {
            this.conversationsList.innerHTML = `
                <div class="empty-conversations">
                    <div class="empty-icon">💬</div>
                    <h3>No conversations yet</h3>
                    <p>Start messaging with hosts or guests to see your conversations here.</p>
                </div>
            `;
            return;
        }
        
        this.conversationsList.innerHTML = this.conversations.map(conv => {
            const isUnread = conv.unread_count > 0;
            const lastMessage = conv.last_message.content || 'No messages yet';
            const truncatedMessage = lastMessage.length > 50 ? lastMessage.substring(0, 50) + '...' : lastMessage;
            
            return `
                <div class="conversation-item ${isUnread ? 'unread' : ''} ${this.currentConversationId === conv.id ? 'active' : ''}" 
                     data-conversation-id="${conv.id}" 
                     data-other-user-id="${conv.other_participant.id}">
                    
                    <div class="conversation-avatar">
                        <img src="${conv.other_participant.profile_photo || '/static/img/default-avatar.png'}" 
                             alt="${conv.other_participant.name}">
                    </div>
                    
                    <div class="conversation-content">
                        <div class="conversation-header">
                            <h4 class="participant-name">${conv.other_participant.name}</h4>
                            <span class="conversation-time">${this.formatTime(conv.last_message.timestamp)}</span>
                        </div>
                        
                        <div class="conversation-preview">
                            <p class="last-message">${truncatedMessage}</p>
                            ${isUnread ? `<span class="unread-badge">${conv.unread_count}</span>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        // Add click listeners to conversation items
        this.conversationsList.querySelectorAll('.conversation-item').forEach(item => {
            item.addEventListener('click', () => this.selectConversation(item));
        });
    }
    
    async selectConversation(conversationElement) {
        const conversationId = conversationElement.dataset.conversationId;
        const otherUserId = conversationElement.dataset.otherUserId;
        
        // Update active conversation
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        conversationElement.classList.add('active');
        
        this.currentConversationId = conversationId;
        this.currentOtherUserId = parseInt(otherUserId);
        
        // Load messages for this conversation
        await this.loadMessages(conversationId);
        
        // Mark conversation as read
        this.markConversationAsRead(conversationId);
        
        // Remove unread indicators
        conversationElement.classList.remove('unread');
        const unreadBadge = conversationElement.querySelector('.unread-badge');
        if (unreadBadge) {
            unreadBadge.remove();
        }
    }
    
    async loadMessages(conversationId, showLoader = true) {
        try {
            if (showLoader) {
                this.showChatLoader();
            }
            
            const response = await fetch(`/api/conversations/${conversationId}/messages`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success) {
                this.currentMessages = result.messages;
                this.renderMessages(showLoader);
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            if (showLoader) {
                this.showChatError('Failed to load messages');
            }
        }
    }
    
    renderMessages(scrollToBottom = true) {
        if (!this.messagesList) return;
        
        this.messagesList.innerHTML = this.currentMessages.map(msg => {
            const isFromCurrentUser = msg.sender_id === window.currentUserId;
            const messageClass = isFromCurrentUser ? 'sent' : 'received';
            
            return `
                <div class="message ${messageClass}" data-message-id="${msg.id}">
                    ${!isFromCurrentUser ? `
                        <div class="message-avatar">
                            <img src="${msg.sender_photo || '/static/img/default-avatar.png'}" 
                                 alt="${msg.sender_name}">
                        </div>
                    ` : ''}
                    
                    <div class="message-content">
                        <div class="message-bubble">
                            ${msg.content}
                        </div>
                        <div class="message-meta">
                            <span class="message-time">${this.formatTime(msg.timestamp)}</span>
                            ${isFromCurrentUser ? `<span class="message-status">${msg.is_read ? 'Read' : 'Sent'}</span>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        if (scrollToBottom) {
            this.scrollToBottom();
        }
        
        // Show chat interface
        this.showActiveChat();
    }
    
    async sendMessage() {
        if (!this.currentOtherUserId || !this.messageInput) return;
        
        const content = this.messageInput.value.trim();
        if (!content) return;
        
        // Disable send button
        if (this.sendButton) {
            this.sendButton.disabled = true;
        }
        
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            
            const response = await fetch('/api/messages/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    receiver_id: this.currentOtherUserId,
                    content: content
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success) {
                // Clear input
                this.messageInput.value = '';
                
                // Add message to current messages
                this.currentMessages.push(result.message);
                this.renderMessages();
                
                // Refresh conversations to update last message
                this.loadConversations();
                
                this.showToast('Message sent', 'success');
            } else {
                throw new Error(result.error || 'Failed to send message');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showToast('Failed to send message', 'error');
        } finally {
            // Re-enable send button
            if (this.sendButton) {
                this.sendButton.disabled = false;
            }
        }
    }
    
    async markConversationAsRead(conversationId) {
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            await fetch(`/api/conversations/${conversationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });
        } catch (error) {
            console.error('Error marking conversation as read:', error);
        }
    }
    
    async markAllAsRead() {
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
            const response = await fetch('/api/conversations/read-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            if (result.success) {
                // Remove unread indicators
                document.querySelectorAll('.conversation-item.unread').forEach(conv => {
                    conv.classList.remove('unread');
                    const badge = conv.querySelector('.unread-badge');
                    if (badge) badge.remove();
                });
                
                this.showToast(result.message || 'All conversations marked as read', 'success');
            }
        } catch (error) {
            console.error('Error marking all as read:', error);
            this.showToast('Failed to mark all as read', 'error');
        }
    }
    
    // UI Helper Methods
    showChatLoader() {
        if (this.chatArea) {
            this.chatArea.innerHTML = `
                <div class="chat-loading">
                    <div class="loading-spinner"></div>
                    <p>Loading messages...</p>
                </div>
            `;
        }
    }
    
    showChatError(message) {
        if (this.chatArea) {
            this.chatArea.innerHTML = `
                <div class="chat-error">
                    <div class="error-icon">⚠️</div>
                    <h3>Error</h3>
                    <p>${message}</p>
                    <button onclick="window.messagingSystem.loadConversations()" class="btn-primary">Retry</button>
                </div>
            `;
        }
    }
    
    showActiveChat() {
        if (this.chatArea) {
            this.chatArea.classList.remove('chat-empty');
            this.chatArea.classList.add('chat-active');
        }
    }
    
    scrollToBottom() {
        if (this.messagesList) {
            this.messagesList.scrollTop = this.messagesList.scrollHeight;
        }
    }
    
    formatTime(timestamp) {
        if (!timestamp) return '';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        // Less than 1 minute
        if (diff < 60000) {
            return 'Just now';
        }
        
        // Less than 1 hour
        if (diff < 3600000) {
            const minutes = Math.floor(diff / 60000);
            return `${minutes}m ago`;
        }
        
        // Less than 24 hours
        if (diff < 86400000) {
            const hours = Math.floor(diff / 3600000);
            return `${hours}h ago`;
        }
        
        // More than 24 hours
        return date.toLocaleDateString();
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('toast-show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('toast-show');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
    
    // Search and filter functionality
    toggleSearch() {
        const searchContainer = document.getElementById('searchContainer');
        if (searchContainer) {
            const isVisible = searchContainer.style.display !== 'none';
            searchContainer.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible) {
                const searchInput = document.getElementById('searchMessages');
                if (searchInput) searchInput.focus();
            }
        }
    }
    
    handleSearch(event) {
        const query = event.target.value.toLowerCase();
        const conversations = document.querySelectorAll('.conversation-item');
        
        conversations.forEach(conv => {
            const name = conv.querySelector('.participant-name').textContent.toLowerCase();
            const message = conv.querySelector('.last-message').textContent.toLowerCase();
            
            if (name.includes(query) || message.includes(query)) {
                conv.style.display = 'flex';
            } else {
                conv.style.display = 'none';
            }
        });
    }
    
    handleFilterTab(event) {
        const filter = event.target.dataset.filter;
        
        // Update active tab
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Filter conversations
        this.filterConversations(filter);
    }
    
    filterConversations(filter) {
        const conversations = document.querySelectorAll('.conversation-item');
        
        conversations.forEach(conv => {
            switch (filter) {
                case 'unread':
                    conv.style.display = conv.classList.contains('unread') ? 'flex' : 'none';
                    break;
                case 'archived':
                    // Implement archived functionality if needed
                    conv.style.display = 'none';
                    break;
                default: // 'all'
                    conv.style.display = 'flex';
            }
        });
    }
    
    // Cleanup method
    destroy() {
        this.stopPolling();
        console.log('🗑️ Traditional messaging system destroyed');
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('conversationsList')) {
        window.messagingSystem = new TraditionalMessagingSystem();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.messagingSystem) {
        window.messagingSystem.destroy();
    }
});
