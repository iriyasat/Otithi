# app/routes/messages.py - Traditional Messaging System (No WebSocket)
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
import json
from app.database import get_db_connection
from app.models import Message, User

# Create blueprint for traditional messaging
messages_bp = Blueprint('messages', __name__)

def init_socketio(app):
    """Dummy function to maintain compatibility - SocketIO disabled"""
    print("📱 SocketIO disabled - using traditional messaging system")
    return None

# Main messages page route
@messages_bp.route('/')
@messages_bp.route('/messages')
@login_required
def messages():
    """Main messages page - Traditional messaging interface"""
    return render_template('messages.html')

# API Routes for Traditional Messaging

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
                COUNT(CASE WHEN m.receiver_id = %s AND m.is_read = 0 THEN 1 END) as unread_count
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
                conversation = {
                    'id': f"{min(current_user.id, other_user['user_id'])}_{max(current_user.id, other_user['user_id'])}",
                    'other_participant': {
                        'id': other_user['user_id'],
                        'name': other_user['name'],
                        'profile_photo': other_user['profile_photo'],
                        'user_type': other_user['user_type'],
                        'is_online': False  # No online status in traditional mode
                    },
                    'last_message': {
                        'content': conv['last_message_content'],
                        'timestamp': conv['last_message_time'].isoformat() if conv['last_message_time'] else '',
                        'is_from_current_user': conv['last_sender_id'] == current_user.id
                    },
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
        
        other_user_id = int(user_ids[1]) if int(user_ids[0]) == current_user.id else int(user_ids[0])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get messages between current user and other user
        cursor.execute("""
            SELECT m.*, u.name as sender_name, ud.profile_photo as sender_photo
            FROM messages m
            JOIN users u ON m.sender_id = u.user_id
            LEFT JOIN user_details ud ON u.user_id = ud.user_id
            WHERE (m.sender_id = %s AND m.receiver_id = %s)
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.created_at ASC
        """, (current_user.id, other_user_id, other_user_id, current_user.id))
        
        messages_data = cursor.fetchall()
        messages = []
        
        for msg in messages_data:
            message = {
                'id': msg['message_id'],
                'content': msg['message_content'],
                'sender_id': msg['sender_id'],
                'sender_name': msg['sender_name'],
                'sender_photo': msg['sender_photo'],
                'timestamp': msg['created_at'].isoformat(),
                'is_read': bool(msg['is_read']),
                'message_type': msg['message_type']
            }
            messages.append(message)
        
        # Mark messages as read
        cursor.execute("""
            UPDATE messages 
            SET is_read = 1, read_at = %s 
            WHERE sender_id = %s AND receiver_id = %s AND is_read = 0
        """, (datetime.now(), other_user_id, current_user.id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'messages': messages})
    
    except Exception as e:
        print(f"Error getting conversation messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messages_bp.route('/api/messages/send', methods=['POST'])
@login_required
def send_message():
    """Send a new message"""
    try:
        data = request.get_json()
        if not data or 'receiver_id' not in data or 'content' not in data:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        receiver_id = int(data['receiver_id'])
        content = data['content'].strip()
        
        if not content:
            return jsonify({'success': False, 'error': 'Message content cannot be empty'}), 400
        
        # Verify receiver exists
        receiver = User.get(receiver_id)
        if not receiver:
            return jsonify({'success': False, 'error': 'Receiver not found'}), 404
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert new message
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, message_content, message_type, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (current_user.id, receiver_id, content, 'text', datetime.now()))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': {
                'id': message_id,
                'content': content,
                'sender_id': current_user.id,
                'sender_name': current_user.name,
                'receiver_id': receiver_id,
                'timestamp': datetime.now().isoformat(),
                'is_read': False
            }
        })
    
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@messages_bp.route('/api/conversations/<conversation_id>/read', methods=['POST'])
@login_required
def mark_conversation_read(conversation_id):
    """Mark conversation as read"""
    try:
        # Parse conversation ID to get user IDs
        user_ids = conversation_id.split('_')
        if len(user_ids) != 2:
            return jsonify({'success': False, 'error': 'Invalid conversation ID'}), 400
        
        other_user_id = int(user_ids[1]) if int(user_ids[0]) == current_user.id else int(user_ids[0])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE messages 
            SET is_read = 1, read_at = %s 
            WHERE sender_id = %s AND receiver_id = %s AND is_read = 0
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
        print(f"Mark all conversations read called by user {current_user.id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if there are any unread messages
        cursor.execute("""
            SELECT COUNT(*) as unread_count
            FROM messages 
            WHERE receiver_id = %s AND is_read = 0
        """, (current_user.id,))
        
        result = cursor.fetchone()
        unread_count = result['unread_count'] if result else 0
        print(f"Found {unread_count} unread messages for user {current_user.id}")
        
        if unread_count > 0:
            # Update messages to mark as read
            cursor.execute("""
                UPDATE messages 
                SET is_read = 1, read_at = %s 
                WHERE receiver_id = %s AND is_read = 0
            """, (datetime.now(), current_user.id))
            
            affected_rows = cursor.rowcount
            print(f"Marked {affected_rows} messages as read")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Marked {unread_count} conversations as read'
        })
    
    except Exception as e:
        print(f"Error marking all conversations as read: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@messages_bp.route('/api/users/<int:user_id>')
@login_required
def get_user_info(user_id):
    """Get user information"""
    try:
        user = User.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'profile_photo': user.profile_photo,
                'user_type': user.user_type
            }
        })
    
    except Exception as e:
        print(f"Error getting user info: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
