/* ===== OTITHI LIVE MESSAGING SYSTEM ===== */
/* Real-time messaging with WebSocket support */

class LiveMessagingSystem {
    constructor() {
        this.socket = null;
        this.currentConversationId = null;
        this.currentReceiverId = null;
        this.currentUserId = window.currentUserId || null;
        this.typingTimeout = null;
        this.isTyping = false;
        this.messageSound = document.getElementById('messageSound');
        this.soundEnabled = localStorage.getItem('messageSoundEnabled') !== 'false';
        this.lastSeen = new Map();
        
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.bindEvents();
        this.loadConversations();
        this.setupNotifications();
    }
    
    /* ===== WEBSOCKET INITIALIZATION ===== */
    initializeSocket() {
        if (!this.currentUserId) {
            console.error('User ID not found');
            return;
        }
        
        this.socket = io();
        
        // Connection events
        this.socket.on('connect', () => {
            console.log('Connected to messaging server');
            this.updateConnectionStatus('connected');
            this.socket.emit('user_online', { user_id: this.currentUserId });
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from messaging server');
            this.updateConnectionStatus('disconnected');
        });
        
        this.socket.on('reconnect', () => {
            console.log('Reconnected to messaging server');
            this.updateConnectionStatus('connected');
            this.socket.emit('user_online', { user_id: this.currentUserId });
        });
        
        this.socket.on('reconnecting', () => {
            this.updateConnectionStatus('reconnecting');
        });
        
        // Message events
        this.socket.on('new_message', (data) => {
            this.handleNewMessage(data);
        });
        
        this.socket.on('message_delivered', (data) => {
            this.updateMessageStatus(data.message_id, 'delivered');
        });
        
        this.socket.on('message_read', (data) => {
            this.updateMessageStatus(data.message_id, 'read');
        });
        
        // Typing events
        this.socket.on('user_typing', (data) => {
            this.handleUserTyping(data);
        });
        
        this.socket.on('user_stopped_typing', (data) => {
            this.handleUserStoppedTyping(data);
        });
        
        // User status events
        this.socket.on('user_online', (data) => {
            this.updateUserOnlineStatus(data.user_id, true);
        });
        
        this.socket.on('user_offline', (data) => {
            this.updateUserOnlineStatus(data.user_id, false);
        });
    }
    
    /* ===== EVENT BINDING ===== */
    bindEvents() {
        // Search functionality
        const searchToggle = document.getElementById('searchToggle');
        const searchInput = document.getElementById('searchMessages');
        
        searchToggle?.addEventListener('click', this.toggleSearch.bind(this));
        searchInput?.addEventListener('input', this.handleSearch.bind(this));
        
        // Filter tabs
        document.querySelectorAll('.filter-tab').forEach(tab => {
            tab.addEventListener('click', this.handleFilterTab.bind(this));
        });
        
        // Conversation selection
        document.addEventListener('click', (e) => {
            const conversationItem = e.target.closest('.conversation-item');
            if (conversationItem) {
                this.selectConversation(conversationItem);
            }
        });
        
        // Message form
        const messageForm = document.getElementById('messageForm');
        messageForm?.addEventListener('submit', this.handleSendMessage.bind(this));
        
        // Message input typing detection
        const messageInput = document.getElementById('messageInput');
        messageInput?.addEventListener('input', this.handleTyping.bind(this));
        messageInput?.addEventListener('keypress', this.handleKeyPress.bind(this));
        messageInput?.addEventListener('blur', this.handleStopTyping.bind(this));
        
        // File attachment
        const attachmentBtn = document.getElementById('attachmentBtn');
        const fileInput = document.getElementById('fileInput');
        
        attachmentBtn?.addEventListener('click', () => fileInput?.click());
        fileInput?.addEventListener('change', this.handleFileUpload.bind(this));
        
        // Chat actions
        document.getElementById('chatInfo')?.addEventListener('click', this.toggleInfoPanel.bind(this));
        document.getElementById('chatArchive')?.addEventListener('click', this.archiveConversation.bind(this));
        document.getElementById('chatBlock')?.addEventListener('click', this.showBlockModal.bind(this));
        
        // Modal actions
        document.getElementById('confirmBlockUser')?.addEventListener('click', this.blockUser.bind(this));
        document.getElementById('submitReport')?.addEventListener('click', this.reportUser.bind(this));
        
        // Mark all as read
        document.getElementById('markAllRead')?.addEventListener('click', this.markAllAsRead.bind(this));
        
        // Close modals
        document.querySelectorAll('[data-modal-close]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                modal?.style.setProperty('display', 'none');
            });
        });
        
        // Toast close
        document.getElementById('toastClose')?.addEventListener('click', this.hideToast.bind(this));
    }
    
    /* ===== REAL-TIME MESSAGE HANDLING ===== */
    handleNewMessage(data) {
        const { message, conversation_id, sender } = data;
        
        // Play sound notification
        if (this.soundEnabled && sender.id !== this.currentUserId) {
            this.playNotificationSound();
        }
        
        // Update conversation list
        this.updateConversationList(data);
        
        // Add message to current chat if it's the active conversation
        if (conversation_id === this.currentConversationId) {
            this.appendMessage(message, false);
            this.scrollToBottom();
            
            // Mark as read immediately if chat is open
            this.markMessageAsRead(message.id);
        } else {
            // Show notification for other conversations
            this.showNotificationToast(`New message from ${sender.name}`);
            this.updateUnreadCount(conversation_id, 1);
        }
        
        // Update browser title with unread count
        this.updatePageTitle();
    }
    
    handleUserTyping(data) {
        if (data.user_id === this.currentReceiverId && data.conversation_id === this.currentConversationId) {
            this.showTypingIndicator(data.user);
        }
    }
    
    handleUserStoppedTyping(data) {
        if (data.user_id === this.currentReceiverId) {
            this.hideTypingIndicator();
        }
    }
    
    handleTyping() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (message && this.currentConversationId && !this.isTyping) {
            this.isTyping = true;
            this.socket.emit('typing_start', {
                conversation_id: this.currentConversationId,
                receiver_id: this.currentReceiverId
            });
            
            messageInput.setAttribute('data-typing', 'true');
        }
        
        // Clear existing timeout
        clearTimeout(this.typingTimeout);
        
        // Set new timeout to stop typing
        this.typingTimeout = setTimeout(() => {
            this.handleStopTyping();
        }, 2000);
    }
    
    handleStopTyping() {
        if (this.isTyping) {
            this.isTyping = false;
            this.socket.emit('typing_stop', {
                conversation_id: this.currentConversationId,
                receiver_id: this.currentReceiverId
            });
            
            const messageInput = document.getElementById('messageInput');
            messageInput.removeAttribute('data-typing');
        }
        
        clearTimeout(this.typingTimeout);
    }
    
    handleKeyPress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.handleSendMessage(e);
        }
    }
    
    /* ===== MESSAGE SENDING ===== */
    async handleSendMessage(e) {
        e.preventDefault();
        
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message || !this.currentConversationId) return;
        
        // Stop typing indicator
        this.handleStopTyping();
        
        // Create temporary message object
        const tempMessage = {
            id: 'temp_' + Date.now(),
            content: message,
            sender_id: this.currentUserId,
            created_at: new Date().toISOString(),
            status: 'sending'
        };
        
        // Add message to chat immediately
        this.appendMessage(tempMessage, true);
        
        // Clear input
        messageInput.value = '';
        this.updateCharCounter();
        this.scrollToBottom();
        
        try {
            // Send via WebSocket
            this.socket.emit('send_message', {
                conversation_id: this.currentConversationId,
                receiver_id: this.currentReceiverId,
                content: message,
                temp_id: tempMessage.id
            });
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.updateMessageStatus(tempMessage.id, 'failed');
            this.showToast('Failed to send message', 'error');
        }
    }
    
    /* ===== CONVERSATION MANAGEMENT ===== */
    async loadConversations() {
        try {
            const response = await fetch('/api/conversations');
            const data = await response.json();
            
            if (data.success) {
                this.renderConversations(data.conversations);
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
        }
    }
    
    selectConversation(conversationElement) {
        const conversationId = conversationElement.dataset.conversationId;
        const participantId = conversationElement.dataset.participantId;
        
        if (conversationId === this.currentConversationId) return;
        
        // Update active states
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        conversationElement.classList.add('active');
        
        // Join conversation room
        if (this.currentConversationId) {
            this.socket.emit('leave_conversation', { conversation_id: this.currentConversationId });
        }
        
        this.currentConversationId = conversationId;
        this.currentReceiverId = participantId;
        
        this.socket.emit('join_conversation', { conversation_id: conversationId });
        
        // Load conversation messages
        this.loadConversationMessages(conversationId);
        
        // Update UI
        this.showActiveChat();
        this.updateChatHeader(conversationElement);
        
        // Mark conversation as read
        this.markConversationAsRead(conversationId);
    }
    
    async loadConversationMessages(conversationId) {
        try {
            const response = await fetch(`/api/conversations/${conversationId}/messages`);
            const data = await response.json();
            
            if (data.success) {
                this.renderMessages(data.messages);
                this.scrollToBottom();
            }
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    }
    
    /* ===== UI UPDATES ===== */
    renderConversations(conversations) {
        const conversationsList = document.getElementById('conversationsList');
        if (!conversationsList) return;
        
        conversationsList.innerHTML = conversations.map(conv => `
            <div class="conversation-item ${conv.unread_count > 0 ? 'unread' : ''}" 
                 data-conversation-id="${conv.id}"
                 data-participant-id="${conv.other_participant.id}"
                 data-online="${conv.other_participant.is_online}">
                
                <div class="conversation-avatar">
                    ${conv.other_participant.profile_photo ? 
                        `<img src="/static/uploads/profiles/${conv.other_participant.profile_photo}" 
                             alt="${conv.other_participant.name}">` :
                        `<div class="avatar-placeholder">
                            ${conv.other_participant.name.charAt(0).toUpperCase()}
                        </div>`
                    }
                    ${conv.other_participant.is_online ? '<span class="online-indicator"></span>' : ''}
                </div>
                
                <div class="conversation-content">
                    <div class="conversation-header">
                        <h4 class="participant-name">${conv.other_participant.name}</h4>
                        <span class="conversation-time">${this.formatTime(conv.last_message_time)}</span>
                    </div>
                    
                    <div class="conversation-preview">
                        <p class="last-message">
                            ${conv.last_message ? 
                                (conv.last_message.sender_id === this.currentUserId ? 'You: ' : '') +
                                this.truncateText(conv.last_message.content, 50) :
                                'No messages yet'
                            }
                        </p>
                        ${conv.unread_count > 0 ? 
                            `<span class="unread-badge">${conv.unread_count}</span>` : ''
                        }
                    </div>
                    
                    ${conv.listing ? `
                        <div class="conversation-context">
                            <i class="icon-home"></i>
                            <span>${this.truncateText(conv.listing.title, 30)}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }
    
    renderMessages(messages) {
        const messagesList = document.getElementById('messagesList');
        if (!messagesList) return;
        
        messagesList.innerHTML = messages.map(message => 
            this.createMessageHTML(message)
        ).join('');
    }
    
    appendMessage(message, isSent = false) {
        const messagesList = document.getElementById('messagesList');
        if (!messagesList) return;
        
        const messageHTML = this.createMessageHTML(message, isSent);
        messagesList.insertAdjacentHTML('beforeend', messageHTML);
    }
    
    createMessageHTML(message, isSent = null) {
        const isFromCurrentUser = isSent !== null ? isSent : (message.sender_id === this.currentUserId);
        const messageClass = isFromCurrentUser ? 'sent' : 'received';
        const statusClass = message.status || 'sent';
        
        return `
            <div class="message ${messageClass} ${statusClass}" data-message-id="${message.id}">
                ${!isFromCurrentUser ? `
                    <div class="message-avatar">
                        <img src="/static/uploads/profiles/default.jpg" alt="User">
                    </div>
                ` : ''}
                
                <div class="message-content">
                    <div class="message-bubble">
                        ${this.formatMessageContent(message.content)}
                    </div>
                    
                    <div class="message-meta">
                        <span class="message-time">${this.formatTime(message.created_at)}</span>
                        ${isFromCurrentUser ? `
                            <span class="message-status ${statusClass}">
                                ${this.getStatusIcon(statusClass)}
                            </span>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    showActiveChat() {
        document.getElementById('chatEmptyState').style.display = 'none';
        document.getElementById('activeChat').style.display = 'flex';
    }
    
    updateChatHeader(conversationElement) {
        const participantName = conversationElement.querySelector('.participant-name').textContent;
        const avatar = conversationElement.querySelector('.conversation-avatar img, .avatar-placeholder');
        const isOnline = conversationElement.dataset.online === 'true';
        
        document.getElementById('chatParticipantName').textContent = participantName;
        
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (isOnline) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'Online';
        } else {
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Offline';
        }
        
        // Update avatar
        const chatAvatar = document.getElementById('chatAvatar');
        if (avatar.tagName === 'IMG') {
            chatAvatar.src = avatar.src;
            chatAvatar.alt = participantName;
        } else {
            chatAvatar.src = '/static/uploads/profiles/default.jpg';
            chatAvatar.alt = participantName;
        }
    }
    
    showTypingIndicator(user) {
        const typingIndicator = document.getElementById('typingIndicator');
        const typingStatus = document.getElementById('typingStatus');
        const typingAvatar = document.getElementById('typingAvatar');
        
        if (typingAvatar && user.profile_photo) {
            typingAvatar.src = `/static/uploads/profiles/${user.profile_photo}`;
        }
        
        typingIndicator.style.display = 'flex';
        typingStatus.style.display = 'inline';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        const typingStatus = document.getElementById('typingStatus');
        
        typingIndicator.style.display = 'none';
        typingStatus.style.display = 'none';
    }
    
    updateMessageStatus(messageId, status) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            const statusElement = messageElement.querySelector('.message-status');
            if (statusElement) {
                statusElement.className = `message-status ${status}`;
                statusElement.innerHTML = this.getStatusIcon(status);
            }
        }
    }
    
    updateUserOnlineStatus(userId, isOnline) {
        const conversations = document.querySelectorAll(`[data-participant-id="${userId}"]`);
        conversations.forEach(conv => {
            const indicator = conv.querySelector('.online-indicator');
            conv.dataset.online = isOnline;
            
            if (isOnline) {
                if (!indicator) {
                    const avatar = conv.querySelector('.conversation-avatar');
                    avatar.insertAdjacentHTML('beforeend', '<span class="online-indicator"></span>');
                }
            } else {
                indicator?.remove();
            }
        });
        
        // Update current chat if it's the same user
        if (userId === this.currentReceiverId) {
            const statusDot = document.getElementById('statusDot');
            const statusText = document.getElementById('statusText');
            
            if (isOnline) {
                statusDot.className = 'status-dot online';
                statusText.textContent = 'Online';
            } else {
                statusDot.className = 'status-dot offline';
                statusText.textContent = 'Offline';
            }
        }
    }
    
    updateConnectionStatus(status) {
        const connectionStatus = document.getElementById('connectionStatus');
        const statusText = connectionStatus.querySelector('.status-text');
        const statusDot = connectionStatus.querySelector('.status-dot');
        
        connectionStatus.className = `connection-status ${status}`;
        
        switch (status) {
            case 'connected':
                statusText.textContent = 'Connected';
                statusDot.className = 'status-dot online';
                setTimeout(() => {
                    connectionStatus.style.display = 'none';
                }, 2000);
                break;
            case 'disconnected':
                statusText.textContent = 'Disconnected';
                statusDot.className = 'status-dot offline';
                connectionStatus.style.display = 'block';
                break;
            case 'reconnecting':
                statusText.textContent = 'Reconnecting...';
                statusDot.className = 'status-dot typing';
                connectionStatus.style.display = 'block';
                break;
        }
    }
    
    /* ===== UTILITY FUNCTIONS ===== */
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) {
            return date.toLocaleTimeString('en-US', { 
                hour: 'numeric', 
                minute: '2-digit',
                hour12: true 
            });
        } else if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return date.toLocaleDateString('en-US', { weekday: 'short' });
        } else {
            return date.toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric' 
            });
        }
    }
    
    formatMessageContent(content) {
        // Basic HTML escaping and URL detection
        return content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n/g, '<br>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    }
    
    getStatusIcon(status) {
        switch (status) {
            case 'sending':
                return '<i class="icon-clock"></i>';
            case 'sent':
                return '<i class="icon-check"></i>';
            case 'delivered':
                return '<i class="icon-check-check"></i>';
            case 'read':
                return '<i class="icon-check-check" style="color: var(--primary-500);"></i>';
            case 'failed':
                return '<i class="icon-x-circle"></i>';
            default:
                return '<i class="icon-check"></i>';
        }
    }
    
    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('messagesContainer');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
    
    /* ===== NOTIFICATION FUNCTIONS ===== */
    setupNotifications() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
    
    playNotificationSound() {
        if (this.messageSound && this.soundEnabled) {
            this.messageSound.currentTime = 0;
            this.messageSound.play().catch(e => {
                console.log('Could not play notification sound:', e);
            });
        }
    }
    
    showNotificationToast(message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('Otithi', {
                body: message,
                icon: '/static/img/logo.png'
            });
        }
        
        this.showToast(message, 'info');
    }
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        
        toast.className = `toast ${type}`;
        toastMessage.textContent = message;
        toast.style.display = 'block';
        
        setTimeout(() => {
            this.hideToast();
        }, 5000);
    }
    
    hideToast() {
        const toast = document.getElementById('toast');
        toast.style.display = 'none';
    }
    
    /* ===== SEARCH AND FILTER ===== */
    toggleSearch() {
        const searchContainer = document.getElementById('searchContainer');
        const searchInput = document.getElementById('searchMessages');
        
        if (searchContainer.style.display === 'none') {
            searchContainer.style.display = 'block';
            searchInput.focus();
        } else {
            searchContainer.style.display = 'none';
            searchInput.value = '';
            this.handleSearch({ target: { value: '' } });
        }
    }
    
    handleSearch(e) {
        const query = e.target.value.toLowerCase();
        const conversations = document.querySelectorAll('.conversation-item');
        
        conversations.forEach(conv => {
            const name = conv.querySelector('.participant-name').textContent.toLowerCase();
            const lastMessage = conv.querySelector('.last-message').textContent.toLowerCase();
            
            if (name.includes(query) || lastMessage.includes(query)) {
                conv.style.display = 'flex';
            } else {
                conv.style.display = 'none';
            }
        });
    }
    
    handleFilterTab(e) {
        const tab = e.target;
        const filter = tab.dataset.filter;
        
        // Update active tab
        document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Filter conversations
        const conversations = document.querySelectorAll('.conversation-item');
        conversations.forEach(conv => {
            switch (filter) {
                case 'all':
                    conv.style.display = 'flex';
                    break;
                case 'unread':
                    conv.style.display = conv.classList.contains('unread') ? 'flex' : 'none';
                    break;
                case 'archived':
                    // Implement archived conversations filter
                    break;
            }
        });
    }
    
    /* ===== ADDITIONAL FEATURES ===== */
    updateCharCounter() {
        const messageInput = document.getElementById('messageInput');
        const charCounter = document.getElementById('charCounter');
        
        if (messageInput && charCounter) {
            const length = messageInput.value.length;
            charCounter.textContent = `${length}/2000`;
            
            if (length > 1800) {
                charCounter.style.color = 'var(--accent-coral)';
            } else {
                charCounter.style.color = 'var(--neutral-500)';
            }
        }
    }
    
    async markMessageAsRead(messageId) {
        try {
            await fetch(`/api/messages/${messageId}/read`, { method: 'POST' });
            this.socket.emit('message_read', { message_id: messageId });
        } catch (error) {
            console.error('Error marking message as read:', error);
        }
    }
    
    async markConversationAsRead(conversationId) {
        try {
            await fetch(`/api/conversations/${conversationId}/read`, { method: 'POST' });
        } catch (error) {
            console.error('Error marking conversation as read:', error);
        }
    }
    
    async markAllAsRead() {
        try {
            await fetch('/api/conversations/read-all', { method: 'POST' });
            document.querySelectorAll('.conversation-item.unread').forEach(conv => {
                conv.classList.remove('unread');
                const badge = conv.querySelector('.unread-badge');
                badge?.remove();
            });
            this.showToast('All conversations marked as read', 'success');
        } catch (error) {
            console.error('Error marking all as read:', error);
            this.showToast('Failed to mark all as read', 'error');
        }
    }
    
    // Add other methods like file upload, modals, etc.
    handleFileUpload(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        // Implement file upload functionality
        console.log('File upload not implemented yet:', file.name);
    }
    
    toggleInfoPanel() {
        const infoPanel = document.getElementById('infoPanel');
        infoPanel.style.display = infoPanel.style.display === 'none' ? 'flex' : 'none';
    }
    
    showBlockModal() {
        document.getElementById('blockUserModal').style.display = 'flex';
    }
    
    async blockUser() {
        // Implement block user functionality
        console.log('Block user not implemented yet');
    }
    
    async reportUser() {
        // Implement report user functionality
        console.log('Report user not implemented yet');
    }
    
    async archiveConversation() {
        // Implement archive conversation functionality
        console.log('Archive conversation not implemented yet');
    }
    
    updatePageTitle() {
        const unreadCount = document.querySelectorAll('.conversation-item.unread').length;
        const baseTitle = 'Otithi - Messages';
        document.title = unreadCount > 0 ? `(${unreadCount}) ${baseTitle}` : baseTitle;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.messagingSystem = new LiveMessagingSystem();
});

// Handle message input character counter
document.addEventListener('input', (e) => {
    if (e.target.id === 'messageInput') {
        window.messagingSystem?.updateCharCounter();
    }
});
        const messageInput = document.getElementById('messageInput');
        messageInput?.addEventListener('input', this.handleMessageInput.bind(this));
        messageInput?.addEventListener('keydown', this.handleKeyDown.bind(this));
        messageInput?.addEventListener('focus', this.markAsRead.bind(this));
        
        // Chat actions
        document.getElementById('chatInfo')?.addEventListener('click', this.toggleInfoPanel.bind(this));
        document.getElementById('closeInfoPanel')?.addEventListener('click', this.closeInfoPanel.bind(this));
        document.getElementById('chatArchive')?.addEventListener('click', this.archiveConversation.bind(this));
        document.getElementById('chatBlock')?.addEventListener('click', this.showBlockModal.bind(this));
        
        // Mark all as read
        document.getElementById('markAllRead')?.addEventListener('click', this.markAllAsRead.bind(this));
        
        // File attachment
        document.getElementById('attachmentBtn')?.addEventListener('click', this.triggerFileUpload.bind(this));
        
        // Info panel actions
        document.getElementById('archiveConversation')?.addEventListener('click', this.archiveConversation.bind(this));
        document.getElementById('blockUser')?.addEventListener('click', this.showBlockModal.bind(this));
        document.getElementById('reportUser')?.addEventListener('click', this.showReportModal.bind(this));
        
        // Modal actions
        document.getElementById('confirmBlockUser')?.addEventListener('click', this.blockUser.bind(this));
        document.getElementById('submitReport')?.addEventListener('click', this.submitReport.bind(this));
        
        // Window visibility change
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        // Scroll to load more messages
        const messagesContainer = document.getElementById('messagesContainer');
        messagesContainer?.addEventListener('scroll', this.handleScroll.bind(this));
    }
    
    /* ===== WEBSOCKET CONNECTION ===== */
    initializeWebSocket() {
        if (typeof WebSocket === 'undefined') {
            console.log('WebSocket not supported, falling back to polling');
            return;
        }
        
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/messages`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.sendHeartbeat();
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.ws.onclose = () => {
                console.log('WebSocket disconnected, attempting to reconnect...');
                setTimeout(() => this.initializeWebSocket(), 5000);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            // Send heartbeat every 30 seconds
            setInterval(() => this.sendHeartbeat(), 30000);
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }
    
    sendHeartbeat() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'heartbeat' }));
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'new_message':
                this.handleNewMessage(data.message);
                break;
            case 'message_read':
                this.handleMessageRead(data.messageId);
                break;
            case 'user_typing':
                this.handleUserTyping(data.userId, data.conversationId);
                break;
            case 'user_stopped_typing':
                this.handleUserStoppedTyping(data.userId);
                break;
            case 'user_online':
                this.handleUserOnlineStatus(data.userId, true);
                break;
            case 'user_offline':
                this.handleUserOnlineStatus(data.userId, false);
                break;
        }
    }
    
    /* ===== MESSAGE POLLING (FALLBACK) ===== */
    setupMessagePolling() {
        // Poll for new messages every 10 seconds if WebSocket is not available
        this.messagePollingInterval = setInterval(() => {
            if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
                this.pollForNewMessages();
            }
        }, 10000);
    }
    
    async pollForNewMessages() {
        if (!this.currentConversationId) return;
        
        try {
            const response = await fetch(`/api/messages/${this.currentConversationId}/poll`, {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(message => this.handleNewMessage(message));
                }
            }
        } catch (error) {
            console.error('Error polling for messages:', error);
        }
    }
    
    /* ===== SEARCH FUNCTIONALITY ===== */
    toggleSearch() {
        const searchContainer = document.getElementById('searchContainer');
        const searchInput = document.getElementById('searchMessages');
        
        if (searchContainer.style.display === 'none') {
            searchContainer.style.display = 'block';
            searchInput.focus();
        } else {
            searchContainer.style.display = 'none';
            searchInput.value = '';
            this.loadConversations(); // Reset filter
        }
    }
    
    handleSearch(event) {
        const query = event.target.value.toLowerCase().trim();
        const conversations = document.querySelectorAll('.conversation-item');
        
        conversations.forEach(conversation => {
            const participantName = conversation.querySelector('.participant-name').textContent.toLowerCase();
            const lastMessage = conversation.querySelector('.last-message').textContent.toLowerCase();
            
            if (participantName.includes(query) || lastMessage.includes(query)) {
                conversation.style.display = 'flex';
            } else {
                conversation.style.display = 'none';
            }
        });
    }
    
    /* ===== FILTER TABS ===== */
    handleFilterTab(event) {
        const tabs = document.querySelectorAll('.filter-tab');
        tabs.forEach(tab => tab.classList.remove('active'));
        event.target.classList.add('active');
        
        const filter = event.target.dataset.filter;
        this.filterConversations(filter);
    }
    
    filterConversations(filter) {
        const conversations = document.querySelectorAll('.conversation-item');
        
        conversations.forEach(conversation => {
            switch (filter) {
                case 'all':
                    conversation.style.display = 'flex';
                    break;
                case 'unread':
                    if (conversation.classList.contains('unread')) {
                        conversation.style.display = 'flex';
                    } else {
                        conversation.style.display = 'none';
                    }
                    break;
                case 'archived':
                    // Implement archived conversations filter
                    conversation.style.display = 'none';
                    break;
            }
        });
    }
    
    /* ===== CONVERSATION MANAGEMENT ===== */
    async loadConversations() {
        try {
            const response = await fetch('/api/conversations', {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.renderConversations(data.conversations);
            }
        } catch (error) {
            console.error('Error loading conversations:', error);
            this.showToast('Failed to load conversations', 'error');
        }
    }
    
    renderConversations(conversations) {
        const conversationsList = document.getElementById('conversationsList');
        if (!conversationsList) return;
        
        if (conversations.length === 0) {
            conversationsList.innerHTML = `
                <div class="empty-conversations">
                    <div class="empty-icon">
                        <i class="icon-message-circle"></i>
                    </div>
                    <h3>No conversations yet</h3>
                    <p>Start messaging with hosts or guests to see your conversations here.</p>
                </div>
            `;
            return;
        }
        
        const conversationsHTML = conversations.map(conversation => {
            const unreadClass = conversation.unread_count > 0 ? 'unread' : '';
            const unreadBadge = conversation.unread_count > 0 ? 
                `<span class="unread-badge">${conversation.unread_count}</span>` : '';
            
            return `
                <div class="conversation-item ${unreadClass}" 
                     data-conversation-id="${conversation.conversation_id}"
                     data-participant-id="${conversation.other_participant.user_id}">
                    
                    <div class="conversation-avatar">
                        ${conversation.other_participant.profile_photo ? 
                            `<img src="/static/uploads/profiles/${conversation.other_participant.profile_photo}" 
                                 alt="${conversation.other_participant.name}">` :
                            `<div class="avatar-placeholder">
                                ${conversation.other_participant.name.charAt(0).toUpperCase()}
                             </div>`
                        }
                        ${conversation.other_participant.is_online ? 
                            '<span class="online-indicator"></span>' : ''}
                    </div>
                    
                    <div class="conversation-content">
                        <div class="conversation-header">
                            <h4 class="participant-name">${conversation.other_participant.name}</h4>
                            <span class="conversation-time">${this.formatTime(conversation.last_message_time)}</span>
                        </div>
                        
                        <div class="conversation-preview">
                            <p class="last-message">
                                ${conversation.last_message.sender_id === currentUserId ? 
                                    '<span class="message-sender">You:</span>' : ''}
                                ${this.truncateText(conversation.last_message.content, 50)}
                            </p>
                            ${unreadBadge}
                        </div>
                        
                        ${conversation.listing ? `
                        <div class="conversation-context">
                            <i class="icon-home"></i>
                            <span>${this.truncateText(conversation.listing.title, 30)}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        conversationsList.innerHTML = conversationsHTML;
    }
    
    async selectConversation(conversationElement) {
        // Remove active class from all conversations
        document.querySelectorAll('.conversation-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to selected conversation
        conversationElement.classList.add('active');
        conversationElement.classList.remove('unread');
        
        // Get conversation data
        this.currentConversationId = conversationElement.dataset.conversationId;
        this.currentReceiverId = conversationElement.dataset.participantId;
        
        // Update UI
        document.getElementById('conversationId').value = this.currentConversationId;
        document.getElementById('receiverId').value = this.currentReceiverId;
        
        // Show active chat
        document.getElementById('chatEmptyState').style.display = 'none';
        document.getElementById('activeChat').style.display = 'flex';
        
        // Load participant info
        await this.loadParticipantInfo(this.currentReceiverId);
        
        // Load messages
        await this.loadMessages(this.currentConversationId);
        
        // Mark messages as read
        await this.markAsRead();
        
        // Focus message input
        document.getElementById('messageInput').focus();
    }
    
    async loadParticipantInfo(userId) {
        try {
            const response = await fetch(`/api/users/${userId}`, {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const user = await response.json();
                this.updateChatHeader(user);
                this.updateInfoPanel(user);
            }
        } catch (error) {
            console.error('Error loading participant info:', error);
        }
    }
    
    updateChatHeader(user) {
        const chatAvatar = document.getElementById('chatAvatar');
        const chatParticipantName = document.getElementById('chatParticipantName');
        const chatParticipantStatus = document.getElementById('chatParticipantStatus');
        const chatOnlineStatus = document.getElementById('chatOnlineStatus');
        
        if (user.profile_photo) {
            chatAvatar.src = `/static/uploads/profiles/${user.profile_photo}`;
            chatAvatar.alt = user.name;
        } else {
            chatAvatar.src = '/static/img/default-avatar.png';
        }
        
        chatParticipantName.textContent = user.name;
        chatParticipantStatus.textContent = user.is_online ? 'Online' : `Last seen ${this.formatTime(user.last_seen)}`;
        
        if (user.is_online) {
            chatOnlineStatus.style.display = 'block';
        } else {
            chatOnlineStatus.style.display = 'none';
        }
    }
    
    updateInfoPanel(user) {
        const infoAvatar = document.getElementById('infoAvatar');
        const infoName = document.getElementById('infoName');
        const infoUserType = document.getElementById('infoUserType');
        
        if (user.profile_photo) {
            infoAvatar.src = `/static/uploads/profiles/${user.profile_photo}`;
        } else {
            infoAvatar.src = '/static/img/default-avatar.png';
        }
        
        infoName.textContent = user.name;
        infoUserType.textContent = user.user_type.charAt(0).toUpperCase() + user.user_type.slice(1);
    }
    
    /* ===== MESSAGE MANAGEMENT ===== */
    async loadMessages(conversationId, page = 1) {
        if (!conversationId) return;
        
        try {
            const response = await fetch(`/api/messages/${conversationId}?page=${page}`, {
                method: 'GET',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                const data = await response.json();
                this.renderMessages(data.messages, page === 1);
                
                if (page === 1) {
                    this.scrollToBottom();
                }
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            this.showToast('Failed to load messages', 'error');
        }
    }
    
    renderMessages(messages, clearFirst = true) {
        const messagesList = document.getElementById('messagesList');
        if (!messagesList) return;
        
        if (clearFirst) {
            messagesList.innerHTML = '';
        }
        
        const messagesHTML = messages.map(message => this.createMessageHTML(message)).join('');
        
        if (clearFirst) {
            messagesList.innerHTML = messagesHTML;
        } else {
            messagesList.insertAdjacentHTML('afterbegin', messagesHTML);
        }
    }
    
    createMessageHTML(message) {
        const isCurrentUser = message.sender_id === parseInt(currentUserId);
        const messageClass = isCurrentUser ? 'sent' : 'received';
        const avatar = message.sender.profile_photo ? 
            `/static/uploads/profiles/${message.sender.profile_photo}` : 
            '/static/img/default-avatar.png';
        
        let messageContent = '';
        
        switch (message.message_type) {
            case 'text':
                messageContent = `<div class="message-bubble">${this.escapeHtml(message.message_content)}</div>`;
                break;
            case 'image':
                messageContent = `
                    <div class="message-bubble">
                        <div class="message-image">
                            <img src="/static/uploads/messages/${message.attachment_filename}" 
                                 alt="Shared image" onclick="this.classList.toggle('fullscreen')">
                        </div>
                    </div>
                `;
                break;
            case 'file':
                messageContent = `
                    <div class="message-bubble">
                        <div class="message-file">
                            <div class="file-icon">
                                <i class="icon-file"></i>
                            </div>
                            <div class="file-details">
                                <div class="file-name">${message.attachment_filename}</div>
                                <div class="file-size">${this.formatFileSize(message.attachment_size)}</div>
                            </div>
                        </div>
                    </div>
                `;
                break;
        }
        
        return `
            <div class="message ${messageClass}" data-message-id="${message.message_id}">
                <div class="message-avatar">
                    <img src="${avatar}" alt="${message.sender.name}">
                </div>
                <div class="message-content">
                    ${messageContent}
                    <div class="message-meta">
                        <span class="message-time">${this.formatTime(message.created_at)}</span>
                        ${isCurrentUser ? `<span class="message-status">${message.is_read ? '✓✓' : '✓'}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    handleNewMessage(message) {
        if (message.conversation_id === this.currentConversationId) {
            // Add message to current conversation
            const messageHTML = this.createMessageHTML(message);
            const messagesList = document.getElementById('messagesList');
            messagesList.insertAdjacentHTML('beforeend', messageHTML);
            this.scrollToBottom();
            
            // Mark as read if chat is active
            if (document.visibilityState === 'visible') {
                this.markAsRead();
            }
        }
        
        // Update conversation list
        this.updateConversationPreview(message);
        
        // Show notification if not in current conversation or tab is not visible
        if (message.conversation_id !== this.currentConversationId || document.visibilityState !== 'visible') {
            this.showNotification(message);
        }
    }
    
    updateConversationPreview(message) {
        const conversationItem = document.querySelector(`[data-conversation-id="${message.conversation_id}"]`);
        if (!conversationItem) return;
        
        const lastMessageElement = conversationItem.querySelector('.last-message');
        const conversationTime = conversationItem.querySelector('.conversation-time');
        const unreadBadge = conversationItem.querySelector('.unread-badge');
        
        // Update last message preview
        const prefix = message.sender_id === parseInt(currentUserId) ? 'You: ' : '';
        lastMessageElement.innerHTML = prefix + this.truncateText(message.message_content, 50);
        
        // Update time
        conversationTime.textContent = this.formatTime(message.created_at);
        
        // Update unread count
        if (message.sender_id !== parseInt(currentUserId)) {
            conversationItem.classList.add('unread');
            
            let currentCount = this.unreadCounts.get(message.conversation_id) || 0;
            currentCount++;
            this.unreadCounts.set(message.conversation_id, currentCount);
            
            if (unreadBadge) {
                unreadBadge.textContent = currentCount;
            } else {
                const previewElement = conversationItem.querySelector('.conversation-preview');
                previewElement.insertAdjacentHTML('beforeend', `<span class="unread-badge">${currentCount}</span>`);
            }
        }
        
        // Move conversation to top
        const conversationsList = document.getElementById('conversationsList');
        conversationsList.insertBefore(conversationItem, conversationsList.firstChild);
    }
    
    /* ===== MESSAGE SENDING ===== */
    async handleSendMessage(event) {
        event.preventDefault();
        
        const messageInput = document.getElementById('messageInput');
        const messageContent = messageInput.value.trim();
        
        if (!messageContent || !this.currentConversationId) return;
        
        const sendBtn = document.getElementById('sendBtn');
        sendBtn.disabled = true;
        
        try {
            const response = await fetch('/api/messages/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    conversation_id: this.currentConversationId,
                    receiver_id: this.currentReceiverId,
                    message_content: messageContent,
                    message_type: 'text'
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                messageInput.value = '';
                this.updateCharCounter();
                this.autoResizeTextarea(messageInput);
                
                // Add message to UI immediately for better UX
                this.handleNewMessage(data.message);
                
                // Send via WebSocket for real-time delivery
                if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({
                        type: 'send_message',
                        message: data.message
                    }));
                }
            } else {
                this.showToast('Failed to send message', 'error');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showToast('Failed to send message', 'error');
        } finally {
            sendBtn.disabled = false;
        }
    }
    
    handleMessageInput(event) {
        const input = event.target;
        this.updateCharCounter();
        this.autoResizeTextarea(input);
        this.handleTypingIndicator();
    }
    
    handleKeyDown(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            document.getElementById('messageForm').dispatchEvent(new Event('submit'));
        }
    }
    
    updateCharCounter() {
        const messageInput = document.getElementById('messageInput');
        const charCounter = document.getElementById('charCounter');
        const currentLength = messageInput.value.length;
        const maxLength = 2000;
        
        charCounter.textContent = `${currentLength}/${maxLength}`;
        
        if (currentLength > maxLength * 0.9) {
            charCounter.style.color = 'var(--accent-coral)';
        } else {
            charCounter.style.color = 'var(--neutral-500)';
        }
    }
    
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    /* ===== TYPING INDICATOR ===== */
    handleTypingIndicator() {
        if (!this.currentConversationId) return;
        
        // Send typing indicator
        if (!this.isTyping) {
            this.isTyping = true;
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'user_typing',
                    conversation_id: this.currentConversationId
                }));
            }
        }
        
        // Clear existing timeout
        clearTimeout(this.typingTimeout);
        
        // Set new timeout to stop typing
        this.typingTimeout = setTimeout(() => {
            this.isTyping = false;
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({
                    type: 'user_stopped_typing',
                    conversation_id: this.currentConversationId
                }));
            }
        }, 2000);
    }
    
    handleUserTyping(userId, conversationId) {
        if (conversationId === this.currentConversationId && userId !== parseInt(currentUserId)) {
            this.showTypingIndicator();
        }
    }
    
    handleUserStoppedTyping(userId) {
        if (userId !== parseInt(currentUserId)) {
            this.hideTypingIndicator();
        }
    }
    
    showTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        const typingAvatar = document.getElementById('typingAvatar');
        const chatAvatar = document.getElementById('chatAvatar');
        
        if (chatAvatar && typingAvatar) {
            typingAvatar.src = chatAvatar.src;
        }
        
        typingIndicator.style.display = 'flex';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        typingIndicator.style.display = 'none';
    }
    
    /* ===== FILE UPLOAD ===== */
    setupFileUpload() {
        const fileInput = document.getElementById('fileInput');
        fileInput?.addEventListener('change', this.handleFileUpload.bind(this));
    }
    
    triggerFileUpload() {
        document.getElementById('fileInput').click();
    }
    
    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file || !this.currentConversationId) return;
        
        // Validate file
        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showToast('File size must be less than 10MB', 'error');
            return;
        }
        
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 
                             'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
        if (!allowedTypes.includes(file.type)) {
            this.showToast('File type not supported', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        formData.append('conversation_id', this.currentConversationId);
        formData.append('receiver_id', this.currentReceiverId);
        formData.append('message_type', file.type.startsWith('image/') ? 'image' : 'file');
        
        try {
            this.showLoading();
            
            const response = await fetch('/api/messages/upload', {
                method: 'POST',
                credentials: 'same-origin',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                this.handleNewMessage(data.message);
                event.target.value = ''; // Clear file input
            } else {
                this.showToast('Failed to upload file', 'error');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            this.showToast('Failed to upload file', 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    /* ===== CONVERSATION ACTIONS ===== */
    async markAsRead() {
        if (!this.currentConversationId) return;
        
        try {
            await fetch(`/api/messages/${this.currentConversationId}/read`, {
                method: 'POST',
                credentials: 'same-origin'
            });
            
            // Update UI
            const conversationItem = document.querySelector(`[data-conversation-id="${this.currentConversationId}"]`);
            conversationItem?.classList.remove('unread');
            
            const unreadBadge = conversationItem?.querySelector('.unread-badge');
            unreadBadge?.remove();
            
            this.unreadCounts.delete(this.currentConversationId);
        } catch (error) {
            console.error('Error marking messages as read:', error);
        }
    }
    
    async markAllAsRead() {
        try {
            const response = await fetch('/api/messages/mark-all-read', {
                method: 'POST',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Update UI
                document.querySelectorAll('.conversation-item').forEach(item => {
                    item.classList.remove('unread');
                    item.querySelector('.unread-badge')?.remove();
                });
                
                this.unreadCounts.clear();
                this.showToast('All messages marked as read', 'success');
            }
        } catch (error) {
            console.error('Error marking all messages as read:', error);
            this.showToast('Failed to mark messages as read', 'error');
        }
    }
    
    async archiveConversation() {
        if (!this.currentConversationId) return;
        
        try {
            const response = await fetch(`/api/conversations/${this.currentConversationId}/archive`, {
                method: 'POST',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Remove from UI
                const conversationItem = document.querySelector(`[data-conversation-id="${this.currentConversationId}"]`);
                conversationItem?.remove();
                
                // Reset chat area
                this.resetChatArea();
                
                this.showToast('Conversation archived', 'success');
            }
        } catch (error) {
            console.error('Error archiving conversation:', error);
            this.showToast('Failed to archive conversation', 'error');
        }
    }
    
    async blockUser() {
        if (!this.currentReceiverId) return;
        
        try {
            const response = await fetch(`/api/users/${this.currentReceiverId}/block`, {
                method: 'POST',
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Remove conversation from UI
                const conversationItem = document.querySelector(`[data-participant-id="${this.currentReceiverId}"]`);
                conversationItem?.remove();
                
                // Reset chat area
                this.resetChatArea();
                
                this.showToast('User blocked successfully', 'success');
                this.hideModal('blockUserModal');
            }
        } catch (error) {
            console.error('Error blocking user:', error);
            this.showToast('Failed to block user', 'error');
        }
    }
    
    async submitReport() {
        const reason = document.getElementById('reportReason').value;
        const details = document.getElementById('reportDetails').value;
        
        if (!reason || !this.currentReceiverId) return;
        
        try {
            const response = await fetch('/api/users/report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    reported_user_id: this.currentReceiverId,
                    reason: reason,
                    details: details
                })
            });
            
            if (response.ok) {
                this.showToast('Report submitted successfully', 'success');
                this.hideModal('reportUserModal');
                
                // Reset form
                document.getElementById('reportForm').reset();
            }
        } catch (error) {
            console.error('Error submitting report:', error);
            this.showToast('Failed to submit report', 'error');
        }
    }
    
    resetChatArea() {
        document.getElementById('chatEmptyState').style.display = 'flex';
        document.getElementById('activeChat').style.display = 'none';
        this.currentConversationId = null;
        this.currentReceiverId = null;
    }
    
    /* ===== UI HELPERS ===== */
    toggleInfoPanel() {
        const infoPanel = document.getElementById('infoPanel');
        const isOpen = infoPanel.style.display === 'block';
        
        if (isOpen) {
            this.closeInfoPanel();
        } else {
            infoPanel.style.display = 'block';
            // Update grid layout for desktop
            if (window.innerWidth > 1024) {
                document.querySelector('.messages-grid').style.gridTemplateColumns = '380px 1fr 320px';
            }
        }
    }
    
    closeInfoPanel() {
        const infoPanel = document.getElementById('infoPanel');
        infoPanel.style.display = 'none';
        
        // Reset grid layout
        if (window.innerWidth > 1024) {
            document.querySelector('.messages-grid').style.gridTemplateColumns = '380px 1fr auto';
        }
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('messagesContainer');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
    
    handleScroll(event) {
        const container = event.target;
        if (container.scrollTop === 0) {
            // Load more messages when scrolled to top
            // Implement pagination here
        }
    }
    
    handleVisibilityChange() {
        if (document.visibilityState === 'visible' && this.currentConversationId) {
            this.markAsRead();
        }
    }
    
    /* ===== MODAL MANAGEMENT ===== */
    setupModals() {
        // Close modal when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.hideModal(e.target.id);
            }
        });
        
        // Close modal buttons
        document.querySelectorAll('[data-modal-close]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) {
                    this.hideModal(modal.id);
                }
            });
        });
    }
    
    showBlockModal() {
        this.showModal('blockUserModal');
    }
    
    showReportModal() {
        this.showModal('reportUserModal');
    }
    
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }
    
    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }
    
    /* ===== LOADING STATE ===== */
    showLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
    }
    
    hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
    
    /* ===== TOAST NOTIFICATIONS ===== */
    setupToast() {
        document.getElementById('toastClose')?.addEventListener('click', this.hideToast.bind(this));
    }
    
    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        
        if (toast && toastMessage) {
            toastMessage.textContent = message;
            toast.className = `toast ${type}`;
            toast.style.display = 'block';
            
            // Auto hide after 5 seconds
            setTimeout(() => this.hideToast(), 5000);
        }
    }
    
    hideToast() {
        const toast = document.getElementById('toast');
        if (toast) {
            toast.style.display = 'none';
        }
    }
    
    /* ===== NOTIFICATIONS ===== */
    showNotification(message) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(`New message from ${message.sender.name}`, {
                body: message.message_content,
                icon: '/static/img/otithi-icon.png',
                tag: `message-${message.message_id}`
            });
        } else if ('Notification' in window && Notification.permission !== 'denied') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.showNotification(message);
                }
            });
        }
    }
    
    /* ===== UTILITY FUNCTIONS ===== */
    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes}m ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours}h ago`;
        } else if (diffInSeconds < 604800) {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days}d ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    handleUserOnlineStatus(userId, isOnline) {
        // Update online indicators for the user
        document.querySelectorAll(`[data-participant-id="${userId}"] .online-indicator`).forEach(indicator => {
            indicator.style.display = isOnline ? 'block' : 'none';
        });
        
        // Update chat header if it's the current conversation
        if (parseInt(this.currentReceiverId) === userId) {
            const chatOnlineStatus = document.getElementById('chatOnlineStatus');
            const chatParticipantStatus = document.getElementById('chatParticipantStatus');
            
            if (chatOnlineStatus) {
                chatOnlineStatus.style.display = isOnline ? 'block' : 'none';
            }
            
            if (chatParticipantStatus) {
                chatParticipantStatus.textContent = isOnline ? 'Online' : 'Offline';
            }
        }
    }
    
    handleMessageRead(messageId) {
        // Update message status in UI
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            const statusElement = messageElement.querySelector('.message-status');
            if (statusElement) {
                statusElement.textContent = '✓✓';
            }
        }
    }
}

// Initialize messaging system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Make sure currentUserId is available globally
    if (typeof currentUserId === 'undefined') {
        console.error('currentUserId is not defined. Please ensure it is set in the template.');
        return;
    }
    
    new MessagingSystem();
});

// Handle responsive behavior
window.addEventListener('resize', () => {
    const messagesGrid = document.querySelector('.messages-grid');
    const infoPanel = document.getElementById('infoPanel');
    
    if (window.innerWidth <= 1024 && infoPanel.style.display === 'block') {
        infoPanel.classList.add('open');
        messagesGrid.style.gridTemplateColumns = '380px 1fr';
    } else if (window.innerWidth > 1024) {
        infoPanel.classList.remove('open');
        if (infoPanel.style.display === 'block') {
            messagesGrid.style.gridTemplateColumns = '380px 1fr 320px';
        } else {
            messagesGrid.style.gridTemplateColumns = '380px 1fr auto';
        }
    }
});
