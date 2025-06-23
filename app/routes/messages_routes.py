from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
from ..models import User, Message, Conversation, Listing, Booking
from ..forms import MessageForm
from .. import db

messages_bp = Blueprint('messages', __name__, url_prefix='/messages')

@messages_bp.route('/')
@login_required
def messages():
    """User's messages/conversations with pagination"""
    page = request.args.get('page', 1, type=int)
    
    # Get user's conversations
    conversations = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) | (Conversation.user2_id == current_user.id)
    ).order_by(Conversation.updated_at.desc()).all()
    
    # Get paginated conversations
    pagination = Conversation.query.filter(
        (Conversation.user1_id == current_user.id) | (Conversation.user2_id == current_user.id)
    ).order_by(Conversation.updated_at.desc())\
     .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('messages/messages.html', pagination=pagination)

# Add route without trailing slash to handle redirects gracefully
@messages_bp.route('')
@login_required
def messages_redirect():
    """Redirect /messages to /messages/"""
    return redirect(url_for('messages.messages'))

@messages_bp.route('/conversation/<int:conversation_id>')
@login_required
def conversation(conversation_id):
    """View a specific conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Ensure user is part of this conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('messages.messages'))
    
    # Get the other user in the conversation
    other_user = conversation.user2 if conversation.user1_id == current_user.id else conversation.user1
    
    # Get messages for this conversation
    messages = Message.query.filter_by(conversation_id=conversation_id)\
        .order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    unread_messages = Message.query.filter_by(
        conversation_id=conversation_id,
        recipient_id=current_user.id,
        is_read=False
    ).all()
    
    for message in unread_messages:
        message.is_read = True
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    
    form = MessageForm()
    
    return render_template('messages/conversation.html', 
                         conversation=conversation,
                         other_user=other_user,
                         messages=messages,
                         form=form)

@messages_bp.route('/send/<int:conversation_id>', methods=['POST'])
@login_required
def send_message(conversation_id):
    """Send a message in a conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Ensure user is part of this conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('messages.messages'))
    
    form = MessageForm()
    
    if form.validate_on_submit():
        # Determine recipient
        recipient_id = conversation.user2_id if conversation.user1_id == current_user.id else conversation.user1_id
        
        new_message = Message(
            conversation_id=conversation_id,
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=form.content.data
        )
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        try:
            db.session.add(new_message)
            db.session.commit()
            flash('Message sent successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error sending message. Please try again.', 'error')
    
    return redirect(url_for('messages.conversation', conversation_id=conversation_id))

@messages_bp.route('/start-conversation/<int:user_id>', methods=['GET', 'POST'])
@login_required
def start_conversation(user_id):
    """Start a new conversation with a user"""
    if user_id == current_user.id:
        flash('You cannot start a conversation with yourself.', 'error')
        return redirect(url_for('messages.messages'))
    
    other_user = User.query.get_or_404(user_id)
    
    # Check if conversation already exists
    existing_conversation = Conversation.query.filter(
        ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
        ((Conversation.user1_id == user_id) & (Conversation.user2_id == current_user.id))
    ).first()
    
    if existing_conversation:
        return redirect(url_for('messages.conversation', conversation_id=existing_conversation.id))
    
    form = MessageForm()
    
    if form.validate_on_submit():
        # Create new conversation
        new_conversation = Conversation(
            user1_id=current_user.id,
            user2_id=user_id
        )
        
        try:
            db.session.add(new_conversation)
            db.session.flush()  # Get the conversation ID
            
            # Create first message
            new_message = Message(
                conversation_id=new_conversation.id,
                sender_id=current_user.id,
                recipient_id=user_id,
                content=form.content.data
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            flash('Conversation started successfully!', 'success')
            return redirect(url_for('messages.conversation', conversation_id=new_conversation.id))
        except Exception as e:
            db.session.rollback()
            flash('Error starting conversation. Please try again.', 'error')
    
    return render_template('messages/start_conversation.html', form=form, other_user=other_user)

@messages_bp.route('/contact-host/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def contact_host(listing_id):
    """Contact the host of a specific listing"""
    listing = Listing.query.get_or_404(listing_id)
    
    # Check if user is trying to contact themselves
    if listing.user_id == current_user.id:
        flash('You cannot contact yourself.', 'error')
        return redirect(url_for('listings.listing_detail', listing_id=listing_id))
    
    # Check if conversation already exists
    existing_conversation = Conversation.query.filter(
        ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == listing.user_id)) |
        ((Conversation.user1_id == listing.user_id) & (Conversation.user2_id == current_user.id))
    ).first()
    
    if existing_conversation:
        return redirect(url_for('messages.conversation', conversation_id=existing_conversation.id))
    
    form = MessageForm()
    
    if form.validate_on_submit():
        # Create new conversation
        new_conversation = Conversation(
            user1_id=current_user.id,
            user2_id=listing.user_id
        )
        
        try:
            db.session.add(new_conversation)
            db.session.flush()  # Get the conversation ID
            
            # Create first message
            new_message = Message(
                conversation_id=new_conversation.id,
                sender_id=current_user.id,
                recipient_id=listing.user_id,
                content=form.content.data
            )
            
            db.session.add(new_message)
            db.session.commit()
            
            flash('Message sent to host successfully!', 'success')
            return redirect(url_for('messages.conversation', conversation_id=new_conversation.id))
        except Exception as e:
            db.session.rollback()
            flash('Error sending message. Please try again.', 'error')
    
    return render_template('messages/contact_host.html', form=form, listing=listing)

@messages_bp.route('/delete-conversation/<int:conversation_id>', methods=['POST'])
@login_required
def delete_conversation(conversation_id):
    """Delete a conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Ensure user is part of this conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('messages.messages'))
    
    try:
        # Delete all messages in the conversation
        Message.query.filter_by(conversation_id=conversation_id).delete()
        
        # Delete the conversation
        db.session.delete(conversation)
        db.session.commit()
        
        flash('Conversation deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting conversation. Please try again.', 'error')
    
    return redirect(url_for('messages.messages')) 