from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, EmailVerification
from app.forms import LoginForm, RegistrationForm
from app.email_utils import EmailSender

# Create the authentication blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.strip().lower() if form.email.data else ''
        password = form.password.data
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password):
            # Check if account is active
            if hasattr(user, 'is_active') and not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            
            # Handle next page redirect
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            # Redirect based on user type
            if hasattr(user, 'user_type') and user.user_type == 'admin':
                return redirect(url_for('admin.admin'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        full_name = form.full_name.data.strip() if form.full_name.data else ''
        email = form.email.data.strip().lower() if form.email.data else ''
        phone = form.phone.data.strip() if form.phone.data else None
        password = form.password.data
        user_type = form.user_type.data
        bio = form.bio.data.strip() if form.bio.data else None
        
        # Check if user already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            flash('Email address already registered. Please use a different email or try logging in.', 'danger')
            return render_template('auth/register.html', form=form)
        
        try:
            # Create new user with email verification
            result = User.create_with_verification(
                full_name=full_name,
                email=email,
                password=password,
                phone=phone,
                bio=bio,
                user_type=user_type
            )
            
            if result and len(result) == 2:
                user, verification = result
                if user and verification:
                    # Send verification email
                    email_sender = EmailSender()
                    if email_sender.send_verification_email(email, verification.verification_code, full_name):
                        # Store user info in session for verification page
                        session['pending_verification'] = {
                            'user_id': user.id,
                            'email': email,
                            'full_name': full_name
                        }
                        flash('Registration successful! Please check your email for a verification code to complete your registration.', 'success')
                        return redirect(url_for('auth.verify_email'))
                    else:
                        flash('Registration successful, but we could not send the verification email. Please contact support.', 'warning')
                        return redirect(url_for('auth.login'))
                elif user:
                    flash('Registration successful! You can now log in with your credentials.', 'success')
                    return redirect(url_for('auth.login'))
                else:
                    flash('Registration failed. Please try again.', 'danger')
            else:
                flash('Registration failed. Please try again.', 'danger')
        
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Handle email verification"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Check if user has pending verification
    pending_verification = session.get('pending_verification')
    if not pending_verification:
        flash('No pending verification found. Please register first.', 'warning')
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        verification_code = request.form.get('verification_code', '').strip()
        
        if not verification_code:
            flash('Please enter the verification code.', 'danger')
            return render_template('auth/verify_email.html', 
                                email=pending_verification['email'],
                                full_name=pending_verification['full_name'])
        
        # Verify the code
        success, message = EmailVerification.verify_code(verification_code)
        
        if success:
            # Clear session
            session.pop('pending_verification', None)
            
            # Send welcome email
            email_sender = EmailSender()
            email_sender.send_welcome_email(pending_verification['email'], pending_verification['full_name'])
            
            flash('Email verified successfully! You can now log in to your account.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(f'Verification failed: {message}', 'danger')
    
    return render_template('auth/verify_email.html', 
                         email=pending_verification['email'],
                         full_name=pending_verification['full_name'])

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email"""
    pending_verification = session.get('pending_verification')
    if not pending_verification:
        return {'success': False, 'message': 'No pending verification found'}
    
    try:
        # Get the user's verification record
        user = User.get(pending_verification['user_id'])
        if not user:
            return {'success': False, 'message': 'User not found'}
        
        # Get verification records for the user
        verifications = EmailVerification.get_by_user(pending_verification['user_id'])
        if not verifications:
            return {'success': False, 'message': 'No verification record found'}
        
        # Resend the most recent verification
        verification = verifications[0]
        if verification.resend_verification():
            # Send new verification email
            email_sender = EmailSender()
            if email_sender.send_verification_email(pending_verification['email'], verification.verification_code, pending_verification['full_name']):
                return {'success': True, 'message': 'Verification code resent successfully'}
            else:
                return {'success': False, 'message': 'Failed to send verification email'}
        else:
            return {'success': False, 'message': 'Failed to resend verification code'}
            
    except Exception as e:
        return {'success': False, 'message': 'An error occurred while resending verification'}

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

# Password reset functionality (if needed)
# @auth_bp.route('/reset_password')
