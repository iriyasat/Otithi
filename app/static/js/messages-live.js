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
        
        // Update character counter
        this.updateCharCounter();
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
    
    // Placeholder functions for additional features
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
    
    updateConversationList(data) {
        // Update the conversation list with new message data
        const { conversation_id, message, sender } = data;
        const conversationElement = document.querySelector(`[data-conversation-id="${conversation_id}"]`);
        
        if (conversationElement) {
            const lastMessage = conversationElement.querySelector('.last-message');
            const time = conversationElement.querySelector('.conversation-time');
            
            if (lastMessage) {
                const prefix = sender.id === this.currentUserId ? 'You: ' : '';
                lastMessage.textContent = prefix + this.truncateText(message.content, 50);
            }
            
            if (time) {
                time.textContent = this.formatTime(message.created_at);
            }
            
            // Move conversation to top
            const parent = conversationElement.parentNode;
            parent.insertBefore(conversationElement, parent.firstChild);
        }
    }
    
    updateUnreadCount(conversationId, increment) {
        const conversationElement = document.querySelector(`[data-conversation-id="${conversationId}"]`);
        if (conversationElement && conversationId !== this.currentConversationId) {
            conversationElement.classList.add('unread');
            
            let badge = conversationElement.querySelector('.unread-badge');
            if (!badge) {
                badge = document.createElement('span');
                badge.className = 'unread-badge';
                conversationElement.querySelector('.conversation-preview').appendChild(badge);
            }
            
            const currentCount = parseInt(badge.textContent) || 0;
            badge.textContent = currentCount + increment;
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    if (window.currentUserId) {
        window.messagingSystem = new LiveMessagingSystem();
    }
});

// Handle message input character counter
document.addEventListener('input', (e) => {
    if (e.target.id === 'messageInput') {
        window.messagingSystem?.updateCharCounter();
    }
});
