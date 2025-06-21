"""
Email utility functions for sending notifications and emails.
"""

from flask import current_app, render_template
from flask_mail import Message
from threading import Thread

def send_email(subject: str, recipients: list, template: str, **kwargs):
    """Send an email using a template."""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@otithi.com')
        )
        
        msg.html = render_template(f'emails/{template}.html', **kwargs)
        msg.body = render_template(f'emails/{template}.txt', **kwargs)
        
        # Send email asynchronously
        Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {e}")
        return False

def send_async_email(app, msg):
    """Send email asynchronously."""
    with app.app_context():
        try:
            from app import mail
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Error in async email sending: {e}")

def send_booking_notification(booking, user_type='guest'):
    """Send booking notification email."""
    if user_type == 'guest':
        subject = f"Booking Confirmation - {booking.listing.title}"
        recipients = [booking.guest.email]
        template = 'booking_confirmation_guest'
    else:
        subject = f"New Booking Request - {booking.listing.title}"
        recipients = [booking.listing.user.email]
        template = 'booking_request_host'
    
    return send_email(subject, recipients, template, booking=booking)

def send_listing_approval_email(listing, approved=True):
    """Send listing approval/rejection email."""
    if approved:
        subject = f"Listing Approved - {listing.title}"
        template = 'listing_approved'
    else:
        subject = f"Listing Update - {listing.title}"
        template = 'listing_rejected'
    
    recipients = [listing.user.email]
    return send_email(subject, recipients, template, listing=listing) 