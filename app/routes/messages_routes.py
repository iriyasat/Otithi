"""
Messages routes for user messaging functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import desc, or_, and_
from ..models import Message, User
from ..forms import MessageForm
from .. import db

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages')
@login_required
def messages():
    """View user's messages"""
    page = request.args.get('page', 1, type=int)
    messages_query = Message.query.filter(
        or_(
            Message.sender_id == current_user.id,
            Message.recipient_id == current_user.id
        )
    )
    pagination = messages_query.order_by(desc(Message.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('messages/messages.html', pagination=pagination)

@messages_bp.route('/send-message/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    """Send a message to another user"""
    recipient = User.query.get_or_404(recipient_id)
    
    if recipient.id == current_user.id:
        flash('You cannot send a message to yourself.', 'warning')
        return redirect(url_for('messages.messages'))
    
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            content=form.content.data
        )
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('messages.messages'))
    
    return render_template('messages/send_message.html', form=form, recipient=recipient)

@messages_bp.route('/conversation/<int:user_id>')
@login_required
def conversation(user_id):
    """View conversation with a specific user"""
    other_user = User.query.get_or_404(user_id)
    
    if other_user.id == current_user.id:
        flash('You cannot view a conversation with yourself.', 'warning')
        return redirect(url_for('messages.messages'))
    
    # Get messages between current user and other user
    messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.recipient_id == other_user.id),
            and_(Message.sender_id == other_user.id, Message.recipient_id == current_user.id)
        )
    ).order_by(Message.created_at.asc()).all()
    
    return render_template('messages/conversation.html', 
                         messages=messages, 
                         other_user=other_user)

@messages_bp.route('/delete-message/<int:message_id>')
@login_required
def delete_message(message_id):
    """Delete a message"""
    message = Message.query.get_or_404(message_id)
    
    if message.sender_id != current_user.id:
        flash('You can only delete your own messages.', 'danger')
        return redirect(url_for('messages.messages'))
    
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully!', 'success')
    return redirect(url_for('messages.messages')) 