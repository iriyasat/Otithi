"""
Email Verification System for Otithi
Handles email verification codes, sending emails, and verification process
"""

import random
import string
from datetime import datetime, timedelta
from flask import current_app, url_for, render_template
from flask_mail import Mail, Message
from app.database import db

class EmailVerification:
    """Handle email verification operations"""
    
    @staticmethod
    def generate_verification_code():
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def create_verification_code(user_id, email):
        """Create a new verification code for a user"""
        # Expire any existing codes for this user
        EmailVerification.expire_existing_codes(user_id)
        
        # Generate new code
        code = EmailVerification.generate_verification_code()
        expires_at = datetime.now() + timedelta(minutes=15)  # 15 minutes expiry
        
        # Store in database
        query = """
            INSERT INTO email_verifications (user_id, verification_code, email, expires_at)
            VALUES (%s, %s, %s, %s)
        """
        verification_id = db.execute_insert(query, (user_id, code, email, expires_at))
        
        if verification_id:
            return {
                'verification_id': verification_id,
                'code': code,
                'expires_at': expires_at
            }
        return None
    
    @staticmethod
    def expire_existing_codes(user_id):
        """Mark all existing codes for a user as used"""
        query = """
            UPDATE email_verifications 
            SET is_used = 1, used_at = %s 
            WHERE user_id = %s AND is_used = 0
        """
        db.execute_query(query, (datetime.now(), user_id))
    
    @staticmethod
    def verify_code(user_id, code):
        """Verify a code for a user"""
        query = """
            SELECT verification_id, expires_at 
            FROM email_verifications 
            WHERE user_id = %s AND verification_code = %s AND is_used = 0
            ORDER BY created_at DESC
            LIMIT 1
        """
        result = db.execute_query(query, (user_id, code))
        
        if not result:
            return {'success': False, 'error': 'Invalid verification code'}
        
        verification = result[0]
        
        # Check if code has expired
        if datetime.now() > verification['expires_at']:
            return {'success': False, 'error': 'Verification code has expired'}
        
        # Mark code as used
        update_query = """
            UPDATE email_verifications 
            SET is_used = 1, used_at = %s 
            WHERE verification_id = %s
        """
        db.execute_query(update_query, (datetime.now(), verification['verification_id']))
        
        # Mark user as verified
        user_query = """
            UPDATE user_details 
            SET verified = 1, updated_at = %s 
            WHERE user_id = %s
        """
        db.execute_query(user_query, (datetime.now(), user_id))
        
        return {'success': True, 'message': 'Email verified successfully'}
    
    @staticmethod
    def get_last_verification_time(user_id):
        """Get the last time a verification code was sent"""
        query = """
            SELECT created_at 
            FROM email_verifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        result = db.execute_query(query, (user_id,))
        return result[0]['created_at'] if result else None
    
    @staticmethod
    def can_resend_code(user_id, cooldown_minutes=2):
        """Check if user can request a new code (rate limiting)"""
        last_time = EmailVerification.get_last_verification_time(user_id)
        if not last_time:
            return True
        
        time_diff = datetime.now() - last_time
        return time_diff.total_seconds() >= (cooldown_minutes * 60)
    
    @staticmethod
    def cleanup_expired_codes():
        """Clean up expired verification codes (should be run periodically)"""
        query = """
            DELETE FROM email_verifications 
            WHERE expires_at < %s AND is_used = 0
        """
        db.execute_query(query, (datetime.now(),))

class EmailService:
    """Handle email sending operations"""
    
    def __init__(self, app=None):
        self.mail = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Flask-Mail with app"""
        self.mail = Mail(app)
    
    def send_verification_email(self, user_email, user_name, verification_code):
        """Send verification email to user"""
        if not self.mail:
            current_app.logger.error("Mail service not initialized")
            return False
        
        try:
            subject = "Verify Your Otithi Account"
            
            # Create email content
            html_body = render_template('emails/verification_email.html', 
                                      user_name=user_name, 
                                      verification_code=verification_code)
            
            text_body = f"""
            Hello {user_name},
            
            Welcome to Otithi! Please verify your email address by entering this code:
            
            Verification Code: {verification_code}
            
            This code will expire in 15 minutes.
            
            If you didn't create an account with Otithi, please ignore this email.
            
            Best regards,
            The Otithi Team
            """
            
            # Create and send message
            msg = Message(
                subject=subject,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@otithi.com'),
                recipients=[user_email],
                body=text_body,
                html=html_body
            )
            
            self.mail.send(msg)
            current_app.logger.info(f"Verification email sent to {user_email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send verification email: {str(e)}")
            return False
    
    def send_verification_success_email(self, user_email, user_name):
        """Send confirmation email after successful verification"""
        if not self.mail:
            return False
        
        try:
            subject = "Email Verified - Welcome to Otithi!"
            
            html_body = render_template('emails/verification_success.html', 
                                      user_name=user_name)
            
            text_body = f"""
            Hello {user_name},
            
            Great news! Your email address has been successfully verified.
            
            You can now enjoy all the features of Otithi:
            - Browse and book unique accommodations
            - List your own property as a host
            - Message hosts and guests
            - Leave and read reviews
            
            Start exploring: {url_for('main.index', _external=True)}
            
            Welcome to the Otithi community!
            
            Best regards,
            The Otithi Team
            """
            
            msg = Message(
                subject=subject,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@otithi.com'),
                recipients=[user_email],
                body=text_body,
                html=html_body
            )
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send verification success email: {str(e)}")
            return False

# Global email service instance
email_service = EmailService()
