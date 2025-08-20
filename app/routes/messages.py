from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Message, User

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

@messages_bp.route('/')
@login_required
def messages():
    """Messages page - show all conversations"""
    try:
        # Get user's conversations
        conversations_data = Message.get_user_conversations(current_user.id)
        
        # Process conversations to get user details
        conversations = []
        for conv_data in conversations_data:
            other_user_id = conv_data['other_user_id']
            other_user = User.get(other_user_id)
            
            if other_user:
                conversation = {
                    'conversation_id': f"{min(current_user.id, other_user_id)}_{max(current_user.id, other_user_id)}",
                    'other_participant': {
                        'user_id': other_user.id,
                        'name': other_user.name,
                        'profile_photo': other_user.profile_photo,
                        'is_online': False  # TODO: Implement online status
                    },
                    'last_message': {
                        'content': conv_data['last_message_content'] or 'No messages yet',
                        'sender_id': conv_data['last_sender_id']
                    },
                    'last_message_time': conv_data['last_message_time'].strftime('%Y-%m-%d %H:%M') if conv_data['last_message_time'] else 'Never',
                    'unread_count': conv_data['unread_count'] or 0,
                    'listing': None  # TODO: Add listing context if available
                }
                conversations.append(conversation)
        
        return render_template('messages.html', 
                             user=current_user,
                             conversations=conversations)
                             
    except Exception as e:
        print(f"Error loading messages: {e}")
        flash('Error loading messages.', 'error')
        return render_template('messages.html', 
                             user=current_user,
                             conversations=[])

@messages_bp.route('/conversation/<int:other_user_id>')
@login_required
def get_conversation(other_user_id):
    """Get messages for a specific conversation"""
    try:
        messages = Message.get_conversation_messages(current_user.id, other_user_id)
        
        # Mark messages as read
        Message.mark_conversation_as_read(current_user.id, other_user_id, current_user.id)
        
        # Convert messages to dict format
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'sender_id': msg.sender_id,
                'content': msg.content,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_read': msg.is_read,
                'sender_name': msg.sender_name,
                'sender_photo': msg.sender_photo
            })
        
        return jsonify({
            'success': True,
            'messages': messages_data
        })
        
    except Exception as e:
        print(f"Error getting conversation: {e}")
        return jsonify({
            'success': False,
            'message': 'Error loading conversation'
        })

@messages_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Send a new message"""
    try:
        data = request.get_json()
        receiver_id = data.get('receiver_id')
        content = data.get('content')
        listing_id = data.get('listing_id')
        booking_id = data.get('booking_id')
        
        if not receiver_id or not content:
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            })
        
        # Create the message
        message = Message.create(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            content=content,
            listing_id=listing_id,
            booking_id=booking_id
        )
        
        if message:
            return jsonify({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
                    'sender_name': current_user.name
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send message'
            })
            
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({
            'success': False,
            'message': 'Error sending message'
        })

@messages_bp.route('/unread-count')
@login_required
def get_unread_count():
    """Get unread message count for the current user"""
    try:
        count = Message.get_unread_count(current_user.id)
        return jsonify({
            'success': True,
            'count': count
        })
    except Exception as e:
        print(f"Error getting unread count: {e}")
        return jsonify({
            'success': False,
            'count': 0
        })
