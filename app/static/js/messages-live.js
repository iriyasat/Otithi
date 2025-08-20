/**
 * Messages Live JavaScript - Real-time messaging functionality
 */

class MessagesLive {
    constructor() {
        this.currentConversation = null;
        this.conversations = [];
        this.unreadCount = 0;
        this.typingTimeout = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadConversations();
        this.startUnreadCountPolling();
    }

    bindEvents() {
        // Conversation list click events
        document.addEventListener('click', (e) => {
            if (e.target.closest('.conversation-item')) {
                const conversationItem = e.target.closest('.conversation-item');
                const participantId = conversationItem.dataset.participantId;
                if (participantId) {
                    this.loadConversation(participantId);
                    this.markConversationActive(conversationItem);
                }
            }
        });

        // Send message button
        const sendButton = document.getElementById('sendMessageBtn');
        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        // Message input enter key
        const messageInput = document.getElementById('messageInput');
        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });

            // Typing indicator
            messageInput.addEventListener('input', () => this.handleTyping());
        }

        // Search functionality
        const searchInput = document.getElementById('searchConversations');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.searchConversations(e.target.value));
        }
    }

    async loadConversations() {
        try {
            const response = await fetch('/messages/');
            if (response.ok) {
                const html = await response.text();
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // Extract conversations from the rendered HTML
                const conversationItems = doc.querySelectorAll('.conversation-item');
                this.conversations = Array.from(conversationItems).map(item => ({
                    userId: item.dataset.userId,
                    name: item.querySelector('.conversation-name')?.textContent || 'Unknown',
                    lastMessage: item.querySelector('.last-message')?.textContent || '',
                    unreadCount: parseInt(item.dataset.unreadCount || '0'),
                    timestamp: item.querySelector('.timestamp')?.textContent || ''
                }));

                this.renderConversations();
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }

    renderConversations() {
        const conversationsList = document.getElementById('conversationsList');
        if (!conversationsList) return;

        conversationsList.innerHTML = this.conversations.map(conv => `
            <div class="conversation-item ${conv.unreadCount > 0 ? 'unread' : ''}" 
                 data-user-id="${conv.userId}">
                <div class="conversation-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="conversation-content">
                    <div class="conversation-header">
                        <span class="conversation-name">${conv.name}</span>
                        <span class="timestamp">${conv.timestamp}</span>
                    </div>
                    <div class="last-message">${conv.lastMessage}</div>
                    ${conv.unreadCount > 0 ? `<span class="unread-badge">${conv.unreadCount}</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    async loadConversation(userId) {
        try {
            const response = await fetch(`/messages/conversation/${userId}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentConversation = userId;
                this.renderMessages(data.messages);
                this.showActiveChat();
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    }

    renderMessages(messages) {
        const messagesList = document.getElementById('messagesList');
        if (!messagesList) return;

        messagesList.innerHTML = messages.map(msg => `
            <div class="message-item ${msg.sender_id == this.getCurrentUserId() ? 'sent' : 'received'}">
                <div class="message-content">
                    <div class="message-text">${this.escapeHtml(msg.content)}</div>
                    <div class="message-time">${msg.created_at}</div>
                </div>
            </div>
        `).join('');
    }

    showActiveChat() {
        // Hide empty state and show active chat
        const emptyState = document.getElementById('chatEmptyState');
        const activeChat = document.getElementById('activeChat');
        
        if (emptyState) emptyState.style.display = 'none';
        if (activeChat) activeChat.style.display = 'block';
    }

    markConversationActive(conversationItem) {
        // Remove active class from all conversations
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to clicked conversation
        conversationItem.classList.add('active');
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const content = messageInput?.value.trim();
        
        if (!content || !this.currentConversation) return;

        try {
            const response = await fetch('/messages/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    receiver_id: this.currentConversation,
                    content: content,
                    listing_id: null
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Clear input
                messageInput.value = '';
                
                // Add message to UI
                this.addMessageToUI({
                    content: content,
                    created_at: new Date().toLocaleString(),
                    sender_id: this.getCurrentUserId()
                });
                
                // Scroll to bottom
                this.scrollToBottom();
                
                // Update unread count
                this.updateUnreadCount();
            } else {
                alert('Failed to send message: ' + (data.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Failed to send message. Please try again.');
        }
    }

    addMessageToUI(message) {
        const messagesContainer = document.getElementById('messagesContainer');
        if (!messagesContainer) return;

        const messageElement = document.createElement('div');
        messageElement.className = `message-item ${message.sender_id == this.getCurrentUserId() ? 'sent' : 'received'}`;
        messageElement.innerHTML = `
            <div class="message-content">
                <div class="message-text">${this.escapeHtml(message.content)}</div>
                <div class="message-time">${message.created_at}</div>
            </div>
        `;

        messagesContainer.appendChild(messageElement);
    }

    markConversationActive(userId) {
        // Remove active class from all conversations
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });

        // Add active class to current conversation
        const activeItem = document.querySelector(`[data-user-id="${userId}"]`);
        if (activeItem) {
            activeItem.classList.add('active');
        }
    }

    searchConversations(query) {
        const conversationItems = document.querySelectorAll('.conversation-item');
        
        conversationItems.forEach(item => {
            const name = item.querySelector('.conversation-name')?.textContent.toLowerCase() || '';
            const message = item.querySelector('.last-message')?.textContent.toLowerCase() || '';
            
            if (name.includes(query.toLowerCase()) || message.includes(query.toLowerCase())) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    handleTyping() {
        // Clear existing timeout
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }

        // Show typing indicator
        this.showTypingIndicator();

        // Hide typing indicator after delay
        this.typingTimeout = setTimeout(() => {
            this.hideTypingIndicator();
        }, 1000);
    }

    showTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.style.display = 'block';
        }
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.style.display = 'none';
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('messagesContainer');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    startUnreadCountPolling() {
        // Poll for unread count every 30 seconds
        setInterval(() => {
            this.updateUnreadCount();
        }, 30000);
    }

    async updateUnreadCount() {
        try {
            const response = await fetch('/messages/unread-count');
            const data = await response.json();
            
            if (data.success) {
                this.unreadCount = data.count;
                this.updateUnreadBadge();
            }
        } catch (error) {
            console.error('Error updating unread count:', error);
        }
    }

    updateUnreadBadge() {
        const badge = document.getElementById('messageBadge');
        if (badge) {
            if (this.unreadCount > 0) {
                badge.textContent = this.unreadCount;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    getCurrentUserId() {
        // This should be set by the template or retrieved from a data attribute
        const userIdElement = document.querySelector('[data-current-user-id]');
        return userIdElement ? userIdElement.dataset.currentUserId : null;
    }

    getCSRFToken() {
        const tokenField = document.getElementById('csrf-token-field');
        return tokenField ? tokenField.value : '';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MessagesLive();
});
