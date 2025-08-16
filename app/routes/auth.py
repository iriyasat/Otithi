from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf.csrf import validate_csrf
from app.models import User
from app.forms import LoginForm, RegistrationForm
from app.email_verification import EmailVerification, email_service
import os
import re
import time

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Secure user login with CSRF protection"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        remember_me = form.remember_me.data
        
        try:
            user = User.get_by_email(email)
            current_app.logger.info(f"Login attempt for email: {email}")
            
            if user and user.check_password(password):
                # Check if user's email is verified
                if not user.verified:
                    # Store user id in session for verification
                    session['verification_user_id'] = user.id
                    session['verification_email'] = user.email
                    flash('Please verify your email address before logging in.', 'warning')
                    return redirect(url_for('auth.verify_email_page'))
                
                login_user(user, remember=remember_me)
                flash(f'Welcome back, {user.full_name}!', 'success')
                current_app.logger.info(f"Login successful for: {user.full_name}")
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('main.dashboard'))
            else:
                current_app.logger.info("Invalid login credentials")
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Secure user registration with CSRF protection"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Handle profile photo upload
            profile_photo_filename = None
            if form.profile_photo.data:
                profile_photo = form.profile_photo.data
                if profile_photo and profile_photo.filename:
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                    if '.' in profile_photo.filename and \
                       profile_photo.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                        
                        # Validate file size (5MB max)
                        profile_photo.seek(0, 2)  # Seek to end
                        file_size = profile_photo.tell()
                        profile_photo.seek(0)  # Reset to beginning
                        
                        if file_size > 5 * 1024 * 1024:  # 5MB limit
                            flash('File size too large. Please upload an image smaller than 5MB.', 'error')
                            return render_template('auth/register.html', form=form)
                        
                        # Create filename
                        file_extension = profile_photo.filename.rsplit('.', 1)[1].lower()
                        clean_name = ''.join(c for c in form.full_name.data if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        clean_name = clean_name.replace(' ', '_').lower()
                        timestamp = int(time.time())
                        profile_photo_filename = f"{clean_name}_{timestamp}_profile.{file_extension}"
                        
                        # Save file
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        temp_file_path = os.path.join(upload_folder, profile_photo_filename)
                        profile_photo.save(temp_file_path)
                    else:
                        flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
                        return render_template('auth/register.html', form=form)
            
            # Create new user
            user = User.create(
                name=form.full_name.data,
                email=form.email.data.strip().lower(),
                password=form.password.data,
                phone=form.phone.data,
                bio=form.bio.data,
                user_type=form.user_type.data
            )
            
            if user:
                # Update profile photo after user creation
                if profile_photo_filename:
                    try:
                        file_extension = profile_photo_filename.rsplit('.', 1)[1].lower()
                        clean_name = ''.join(c for c in form.full_name.data if c.isalnum() or c in (' ', '-', '_')).rstrip()
                        clean_name = clean_name.replace(' ', '_').lower()
                        final_filename = f"{clean_name}_{user.id}_profile.{file_extension}"
                        
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                        old_path = os.path.join(upload_folder, profile_photo_filename)
                        new_path = os.path.join(upload_folder, final_filename)
                        
                        if os.path.exists(old_path):
                            os.rename(old_path, new_path)
                            user.update_profile(profile_photo=final_filename)
                    except Exception:
                        pass
                
                # Send verification email
                try:
                    verification = EmailVerification.create_verification_code(user.id, user.email)
                    if verification:
                        email_sent = email_service.send_verification_email(
                            user.email, 
                            user.full_name, 
                            verification['code']
                        )
                        if email_sent:
                            # Store user info in session for verification
                            session['verification_user_id'] = user.id
                            session['verification_email'] = user.email
                            flash(f'Account created! Please check your email ({user.email}) for a verification code.', 'success')
                            return redirect(url_for('auth.verify_email_page'))
                        else:
                            flash('Account created but failed to send verification email. Please contact support.', 'warning')
                            return redirect(url_for('auth.login'))
                    else:
                        flash('Account created but failed to generate verification code. Please contact support.', 'warning')
                        return redirect(url_for('auth.login'))
                except Exception as e:
                    current_app.logger.error(f"Verification email error: {e}")
                    flash('Account created but failed to send verification email. Please contact support.', 'warning')
                    return redirect(url_for('auth.login'))
            else:
                # Clean up uploaded file if user creation failed
                if profile_photo_filename:
                    try:
                        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                        temp_file_path = os.path.join(upload_folder, profile_photo_filename)
                        if os.path.exists(temp_file_path):
                            os.remove(temp_file_path)
                    except:
                        pass
                flash('Registration failed. Please try again.', 'error')
        
        except Exception as e:
            current_app.logger.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    """Simple and reliable user logout"""
    try:
        if current_user.is_authenticated:
            user_name = current_user.full_name
            logout_user()
            flash(f'You have been logged out successfully. Goodbye, {user_name}!', 'success')
        else:
            flash('You are not currently logged in.', 'info')
    except Exception as e:
        current_app.logger.error(f"Logout error: {e}")
        flash('Logout completed.', 'info')
    
    # Clear session data
    session.clear()
    
    return redirect(url_for('main.index'))

@auth_bp.route('/logout-complete')
def logout_complete():
    """Logout completion page to break redirect loops"""
    return render_template('auth/logout_complete.html')

@auth_bp.route('/switch-user-type/<user_type>')
@login_required
def switch_user_type(user_type):
    """Switch user type between guest and host"""
    from flask_login import login_required
    
    # Only allow switching between guest and host
    if user_type not in ['guest', 'host']:
        flash('Invalid user type.', 'error')
        return redirect(url_for('profile.profile'))
    
    # Prevent admin users from switching
    if current_user.user_type == 'admin':
        flash('Admin users cannot switch user types.', 'error')
        return redirect(url_for('profile.profile'))
    
    try:
        from app.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET user_type = %s WHERE id = %s", 
                      (user_type, current_user.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Update current_user object
        current_user.user_type = user_type
        
        flash(f'Successfully switched to {user_type} account!', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error switching user type: {e}")
        flash('Failed to switch user type. Please try again.', 'error')
    
    return redirect(url_for('profile.profile'))

@auth_bp.route('/verify-email')
def verify_email_page():
    """Display email verification page"""
    user_id = session.get('verification_user_id')
    user_email = session.get('verification_email')
    
    if not user_id or not user_email:
        flash('No verification in progress. Please register or log in.', 'warning')
        return redirect(url_for('auth.register'))
    
    return render_template('auth/verify_email.html', user_email=user_email)

@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    """Handle email verification code submission"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data received'})
        
        code = data.get('code', '').strip()
        if not code or len(code) != 6:
            return jsonify({'success': False, 'error': 'Please enter a valid 6-digit code'})
        
        user_id = session.get('verification_user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'No verification in progress'})
        
        # Verify the code
        result = EmailVerification.verify_code(user_id, code)
        
        if result['success']:
            # Clear verification session data
            session.pop('verification_user_id', None)
            session.pop('verification_email', None)
            
            # Log in the user
            user = User.get(user_id)
            if user:
                login_user(user)
                # Send success email
                try:
                    email_service.send_verification_success_email(user.email, user.full_name)
                except Exception as e:
                    current_app.logger.error(f"Failed to send success email: {e}")
                
                return jsonify({
                    'success': True, 
                    'message': 'Email verified successfully!',
                    'redirect': url_for('main.dashboard')
                })
            else:
                return jsonify({'success': False, 'error': 'User not found'})
        else:
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        current_app.logger.error(f"Email verification error: {e}")
        return jsonify({'success': False, 'error': 'Verification failed. Please try again.'})

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification code"""
    try:
        user_id = session.get('verification_user_id')
        user_email = session.get('verification_email')
        
        if not user_id or not user_email:
            return jsonify({'success': False, 'error': 'No verification in progress'})
        
        # Check rate limiting
        if not EmailVerification.can_resend_code(user_id):
            return jsonify({'success': False, 'error': 'Please wait before requesting a new code'})
        
        # Get user
        user = User.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'})
        
        # Create new verification code
        verification = EmailVerification.create_verification_code(user_id, user_email)
        if not verification:
            return jsonify({'success': False, 'error': 'Failed to generate verification code'})
        
        # Send email
        email_sent = email_service.send_verification_email(
            user_email, 
            user.full_name, 
            verification['code']
        )
        
        if email_sent:
            return jsonify({'success': True, 'message': 'New verification code sent!'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send email'})
            
    except Exception as e:
        current_app.logger.error(f"Resend verification error: {e}")
        return jsonify({'success': False, 'error': 'Failed to resend code'})

@auth_bp.route('/send-verification-button')
@login_required
def send_verification_button():
    """Send verification email for already logged in unverified users"""
    if current_user.verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('profile.profile'))
    
    try:
        # Check rate limiting
        if not EmailVerification.can_resend_code(current_user.id):
            flash('Please wait before requesting a new verification code.', 'warning')
            return redirect(url_for('profile.profile'))
        
        # Create verification code
        verification = EmailVerification.create_verification_code(current_user.id, current_user.email)
        if not verification:
            flash('Failed to generate verification code. Please try again.', 'error')
            return redirect(url_for('profile.profile'))
        
        # Send email
        email_sent = email_service.send_verification_email(
            current_user.email, 
            current_user.full_name, 
            verification['code']
        )
        
        if email_sent:
            # Store verification info in session
            session['verification_user_id'] = current_user.id
            session['verification_email'] = current_user.email
            logout_user()  # Log out user to complete verification
            flash('Verification email sent! Please check your email and verify to continue.', 'success')
            return redirect(url_for('auth.verify_email_page'))
        else:
            flash('Failed to send verification email. Please try again.', 'error')
            return redirect(url_for('profile.profile'))
            
    except Exception as e:
        current_app.logger.error(f"Send verification button error: {e}")
        flash('Failed to send verification email. Please try again.', 'error')
        return redirect(url_for('profile.profile'))
