# app/routes/messages.py
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from datetime import datetime
import json
from app.database import get_db_connection
from app.models import Message, User

# Create blueprint and SocketIO instance
messages_bp = Blueprint('messages', __name__)
socketio = None

def init_socketio(app):
    """Initialize SocketIO with the Flask app"""
    global socketio
    from flask_socketio import SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    register_socketio_events()
    return socketio

# Store online users
online_users = {}
user_rooms = {}

def register_socketio_events():
    """Register all SocketIO event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        if current_user.is_authenticated:
            user_id = str(current_user.id)
            online_users[user_id] = request.sid
            print(f"User {current_user.name} connected: {request.sid}")
            
            # Notify other users that this user is online
            emit('user_online', {'user_id': current_user.id}, broadcast=True, include_self=False)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        if current_user.is_authenticated:
            user_id = str(current_user.id)
            if user_id in online_users:
                del online_users[user_id]
            
            # Leave all rooms
            if user_id in user_rooms:
                for room in user_rooms[user_id]:
                    leave_room(room)
                del user_rooms[user_id]
            
            print(f"User {current_user.name} disconnected")
            
            # Notify other users that this user is offline
            emit('user_offline', {'user_id': current_user.id}, broadcast=True, include_self=False)
    
    @socketio.on('user_online')
    def handle_user_online(data):
        """Handle user coming online"""
        if current_user.is_authenticated:
            user_id = str(current_user.id)
            online_users[user_id] = request.sid
            emit('user_online', {'user_id': current_user.id}, broadcast=True, include_self=False)
    
    @socketio.on('join_conversation')
    def handle_join_conversation(data):
        """Handle user joining a conversation room"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        if not conversation_id:
            return
        
        room = f"conversation_{conversation_id}"
        join_room(room)
        
        # Track user rooms
        user_id = str(current_user.id)
        if user_id not in user_rooms:
            user_rooms[user_id] = set()
        user_rooms[user_id].add(room)
        
        print(f"User {current_user.name} joined conversation {conversation_id}")
    
    @socketio.on('leave_conversation')
    def handle_leave_conversation(data):
        """Handle user leaving a conversation room"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        if not conversation_id:
            return
        
        room = f"conversation_{conversation_id}"
        leave_room(room)
        
        # Remove from user rooms
        user_id = str(current_user.id)
        if user_id in user_rooms and room in user_rooms[user_id]:
            user_rooms[user_id].remove(room)
        
        print(f"User {current_user.name} left conversation {conversation_id}")
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle sending a new message"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        temp_id = data.get('temp_id')
        
        if not all([conversation_id, receiver_id, content]):
            emit('message_error', {'error': 'Missing required fields'})
            return
        
        try:
            # Save message to database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO messages (conversation_id, sender_id, receiver_id, content, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (conversation_id, current_user.id, receiver_id, content, datetime.now()))
            
            message_id = cursor.lastrowid
            conn.commit()
            
            # Get the complete message data
            cursor.execute("""
                SELECT m.*, u.name as sender_name, u.profile_photo as sender_photo
                FROM messages m
                JOIN users u ON m.sender_id = u.id
                WHERE m.id = %s
            """, (message_id,))
            
            message_data = cursor.fetchone()
            conn.close()
            
            if message_data:
                message = {
                    'id': message_data['id'],
                    'conversation_id': message_data['conversation_id'],
                    'sender_id': message_data['sender_id'],
                    'receiver_id': message_data['receiver_id'],
                    'content': message_data['content'],
                    'created_at': message_data['created_at'].isoformat(),
                    'status': 'sent'
                }
                
                sender = {
                    'id': current_user.id,
                    'name': message_data['sender_name'],
                    'profile_photo': message_data['sender_photo']
                }
                
                # Emit to conversation room
                room = f"conversation_{conversation_id}"
                emit('new_message', {
                    'message': message,
                    'conversation_id': conversation_id,
                    'sender': sender,
                    'temp_id': temp_id
                }, room=room)
                
                # Update message status to delivered
                emit('message_delivered', {'message_id': message_id}, room=request.sid)
                
                # Send notification to receiver if they're online but not in the room
                receiver_sid = online_users.get(str(receiver_id))
                if receiver_sid and receiver_sid not in rooms():
                    socketio.emit('new_message', {
                        'message': message,
                        'conversation_id': conversation_id,
                        'sender': sender
                    }, room=receiver_sid)
        
        except Exception as e:
            print(f"Error sending message: {e}")
            emit('message_error', {'error': 'Failed to send message', 'temp_id': temp_id})
    
    @socketio.on('typing_start')
    def handle_typing_start(data):
        """Handle user starting to type"""
        if not current_user.is_authenticated:
            return
        
        conversation_id = data.get('conversation_id')
        receiver_id = data.get('receiver_id')
        
        if not all([conversation_id, receiver_id]):
            return
        
        # Emit to the specific receiver
        receiver_sid = online_users.get(str(receiver_id))
        if receiver_sid:
            socketio.emit('user_typing', {
                'user_id': current_user.id,
                'conversation_id': conversation_id,
                'user': {
                    'name': current_user.name,
                    'profile_photo': current_user.profile_photo
                }
            }, room=receiver_sid)
    
    @socketio.on('typing_stop')
    def handle_typing_stop(data):
        """Handle user stopping typing"""
        if not current_user.is_authenticated:
            return
        
        receiver_id = data.get('receiver_id')
        
        if not receiver_id:
            return
        
        # Emit to the specific receiver
        receiver_sid = online_users.get(str(receiver_id))
        if receiver_sid:
            socketio.emit('user_stopped_typing', {
                'user_id': current_user.id
            }, room=receiver_sid)
    
    @socketio.on('message_read')
    def handle_message_read(data):
        """Handle message being read"""
        if not current_user.is_authenticated:
            return
        
        message_id = data.get('message_id')
        if not message_id:
            return
        
        try:
            # Update message as read in database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE messages 
                SET read_at = %s 
                WHERE id = %s AND receiver_id = %s
            """, (datetime.now(), message_id, current_user.id))
            
            # Get sender info to notify them
            cursor.execute("""
                SELECT sender_id FROM messages WHERE id = %s
            """, (message_id,))
            
            result = cursor.fetchone()
            conn.commit()
            conn.close()
            
            if result:
                sender_id = result['sender_id']
                sender_sid = online_users.get(str(sender_id))
                if sender_sid:
                    socketio.emit('message_read', {
                        'message_id': message_id
                    }, room=sender_sid)
        
        except Exception as e:
            print(f"Error marking message as read: {e}")

# HTTP Routes for messages

@messages_bp.route('/messages')
@login_required
def messages():
    """Render messages page"""
    return render_template('messages.html')

@messages_bp.route('/api/conversations')
@login_required
def get_conversations():
    """Get user's conversations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get conversations with last message and unread count
        cursor.execute("""
            SELECT DISTINCT
                CASE 
                    WHEN m.sender_id = %s THEN m.receiver_id 
                    ELSE m.sender_id 
                END as other_user_id,
                MAX(m.created_at) as last_message_time,
                (SELECT message_content FROM messages m2 
                 WHERE (m2.sender_id = %s OR m2.receiver_id = %s)
                 AND (m2.sender_id = other_user_id OR m2.receiver_id = other_user_id)
                 ORDER BY m2.created_at DESC LIMIT 1) as last_message_content,
                (SELECT sender_id FROM messages m3 
                 WHERE (m3.sender_id = %s OR m3.receiver_id = %s)
                 AND (m3.sender_id = other_user_id OR m3.receiver_id = other_user_id)
                 ORDER BY m3.created_at DESC LIMIT 1) as last_sender_id,
                COUNT(CASE WHEN m.receiver_id = %s AND m.read_at IS NULL THEN 1 END) as unread_count
            FROM messages m
            WHERE m.sender_id = %s OR m.receiver_id = %s
            GROUP BY other_user_id
            ORDER BY last_message_time DESC
        """, (current_user.id, current_user.id, current_user.id, 
              current_user.id, current_user.id, current_user.id, 
              current_user.id, current_user.id))
        
        conversations_data = cursor.fetchall()
        conversations = []
        
        for conv in conversations_data:
            # Get other user details
            cursor.execute("""
                SELECT u.user_id, u.name, u.email, ud.profile_photo, ud.user_type 
                FROM users u 
                LEFT JOIN user_details ud ON u.user_id = ud.user_id 
                WHERE u.user_id = %s
            """, (conv['other_user_id'],))
            
            other_user = cursor.fetchone()
            
            if other_user:
                # Check if user is online
                is_online = str(other_user['user_id']) in online_users
                
                conversation = {
                    'id': f"{min(current_user.id, other_user['user_id'])}_{max(current_user.id, other_user['user_id'])}",
                    'other_participant': {
                        'id': other_user['user_id'],
                        'name': other_user['name'],
                        'profile_photo': other_user['profile_photo'],
                        'user_type': other_user['user_type'],
                        'is_online': is_online
                    },
                    'last_message': {
                        'content': conv['last_message_content'],
                        'sender_id': conv['last_sender_id']
                    } if conv['last_message_content'] else None,
                    'last_message_time': conv['last_message_time'].isoformat() if conv['last_message_time'] else None,
                    'unread_count': conv['unread_count']
                }
                conversations.append(conversation)
        
        conn.close()
        return jsonify({'success': True, 'conversations': conversations})
    
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messages_bp.route('/api/conversations/<conversation_id>/messages')
@login_required
def get_conversation_messages(conversation_id):
    """Get messages for a specific conversation"""
    try:
        # Parse conversation ID to get user IDs
        user_ids = conversation_id.split('_')
        if len(user_ids) != 2:
            return jsonify({'success': False, 'error': 'Invalid conversation ID'}), 400
        
        user1_id, user2_id = map(int, user_ids)
        
        # Verify current user is part of the conversation
        if current_user.id not in [user1_id, user2_id]:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get messages between these users
        cursor.execute("""
            SELECT m.*, u.name as sender_name, u.profile_photo as sender_photo
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE (m.sender_id = %s AND m.receiver_id = %s)
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.created_at ASC
            LIMIT 50
        """, (user1_id, user2_id, user2_id, user1_id))
        
        messages_data = cursor.fetchall()
        
        messages = []
        for msg in messages_data:
            message = {
                'id': msg['id'],
                'sender_id': msg['sender_id'],
                'receiver_id': msg['receiver_id'],
                'content': msg['content'],
                'created_at': msg['created_at'].isoformat(),
                'read_at': msg['read_at'].isoformat() if msg['read_at'] else None,
                'sender_name': msg['sender_name'],
                'sender_photo': msg['sender_photo']
            }
            messages.append(message)
        
        conn.close()
        return jsonify({'success': True, 'messages': messages})
    
    except Exception as e:
        print(f"Error getting messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messages_bp.route('/api/messages/<int:message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mark a message as read"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages 
            SET read_at = %s 
            WHERE id = %s AND receiver_id = %s
        """, (datetime.now(), message_id, current_user.id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error marking message as read: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messages_bp.route('/api/conversations/<conversation_id>/read', methods=['POST'])
@login_required
def mark_conversation_read(conversation_id):
    """Mark all messages in a conversation as read"""
    try:
        # Parse conversation ID to get user IDs
        user_ids = conversation_id.split('_')
        if len(user_ids) != 2:
            return jsonify({'success': False, 'error': 'Invalid conversation ID'}), 400
        
        user1_id, user2_id = map(int, user_ids)
        other_user_id = user2_id if current_user.id == user1_id else user1_id
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages 
            SET read_at = %s 
            WHERE sender_id = %s AND receiver_id = %s AND read_at IS NULL
        """, (datetime.now(), other_user_id, current_user.id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error marking conversation as read: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messages_bp.route('/api/conversations/read-all', methods=['POST'])
@login_required
def mark_all_conversations_read():
    """Mark all conversations as read"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages 
            SET read_at = %s 
            WHERE receiver_id = %s AND read_at IS NULL
        """, (datetime.now(), current_user.id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"Error marking all conversations as read: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messages_bp.route('/api/users/<int:user_id>')
@login_required
def get_user_info(user_id):
    """Get user information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, profile_photo, user_type 
            FROM users WHERE id = %s
        """, (user_id,))
        
        user_data = cursor.fetchone()
        conn.close()
        
        if not user_data:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Check if user is online
        is_online = str(user_id) in online_users
        
        user = {
            'id': user_data['id'],
            'name': user_data['name'],
            'email': user_data['email'],
            'profile_photo': user_data['profile_photo'],
            'user_type': user_data['user_type'],
            'is_online': is_online
        }
        
        return jsonify(user)
    
    except Exception as e:
        print(f"Error getting user info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
