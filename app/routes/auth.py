from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, current_user
from app.models import User
import os
import re
import time

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        # Debug: Log received form data
        current_app.logger.info(f"Raw form data: {dict(request.form)}")
        current_app.logger.info(f"Email received: '{email}' (length: {len(email)})")
        current_app.logger.info(f"Password received: '{password}' (length: {len(password)})")
        current_app.logger.info(f"Password bytes: {password.encode('utf-8')}")
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/login.html')
        
        try:
            user = User.get_by_email(email)
            current_app.logger.info(f"Login attempt for email: {email}")
            
            if user:
                current_app.logger.info(f"User found: {user.full_name}, type: {user.user_type}")
                current_app.logger.info(f"User password_hash exists: {bool(user.password_hash)}")
                
                password_valid = user.check_password(password)
                current_app.logger.info(f"Password validation result: {password_valid}")
                
                if password_valid:
                    login_user(user, remember=remember_me)
                    
                    # Log successful login
                    flash(f'Welcome back, {user.full_name}!', 'success')
                    current_app.logger.info(f"Login successful for: {user.full_name}")
                    
                    # Redirect to next page or dashboard
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    else:
                        if user.user_type == 'admin':
                            return redirect(url_for('main.dashboard'))
                        elif user.user_type == 'host':
                            return redirect(url_for('main.dashboard'))
                        else:  # guest
                            return redirect(url_for('main.dashboard'))
                else:
                    current_app.logger.info("Password validation failed")
                    flash('Invalid email or password.', 'error')
            else:
                current_app.logger.info(f"No user found with email: {email}")
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            flash('Login failed. Please try again.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        user_type = request.form.get('user_type', 'guest')
        terms_agreement = request.form.get('terms_agreement')
        
        # Handle profile photo upload
        profile_photo = request.files.get('profile_photo')
        profile_photo_filename = None
        
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
                    return render_template('auth/register.html')
                
                # Create filename with user name for organization
                file_extension = profile_photo.filename.rsplit('.', 1)[1].lower()
                # Clean the user name for filename (remove spaces, special chars)
                clean_name = ''.join(c for c in full_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_name = clean_name.replace(' ', '_')  # Replace spaces with underscores
                clean_name = clean_name.lower()  # Convert to lowercase for consistency
                
                # Create temporary filename (we'll update with user ID after user creation)
                import time
                timestamp = int(time.time())
                profile_photo_filename = f"{clean_name}_{timestamp}_profile.{file_extension}"
                
                # Create uploads directory if it doesn't exist
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Save the file temporarily
                temp_file_path = os.path.join(upload_folder, profile_photo_filename)
                profile_photo.save(temp_file_path)
            else:
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
                return render_template('auth/register.html')
        
        # Validation
        errors = []
        
        if not full_name or len(full_name) < 2:
            errors.append('Full name must be at least 2 characters long.')
        
        if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors.append('Please enter a valid email address.')
        
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if user_type not in ['guest', 'host']:
            user_type = 'guest'
        
        if not terms_agreement:
            errors.append('You must agree to the Terms of Service and Privacy Policy.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        try:
            # Check if user already exists
            existing_user = User.get_by_email(email)
            if existing_user:
                flash('An account with this email already exists.', 'error')
                return render_template('auth/register.html')
            
            # Create new user
            user = User.create(
                full_name=full_name,
                email=email,
                password=password,
                phone=phone,
                bio=bio,
                user_type=user_type
            )
            
            if user:
                # Handle profile photo renaming after user creation
                if profile_photo_filename:
                    try:
                        file_extension = profile_photo_filename.rsplit('.', 1)[1].lower()
                        clean_name = ''.join(c for c in full_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
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
                
                login_user(user)
                flash(f'Welcome to Otithi, {user.full_name}! Your account has been created successfully.', 'success')
                return redirect(url_for('main.dashboard'))
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
            flash('Registration failed. Please try again.', 'error')
            print(f"Registration error: {e}")
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """User logout with enhanced protection"""
    # Immediate check for user agent
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # If this is VS Code Simple Browser causing issues, just redirect immediately
    if 'VSCode' in user_agent or 'Simple Browser' in user_agent:
        current_app.logger.info(f"VSCode/Simple Browser logout redirect: {user_agent}")
        return redirect(url_for('main.index'))
    
    # Check for rapid logout attempts
    last_logout_time = session.get('last_logout_time', 0)
    current_time = time.time()
    
    # Log the request for debugging
    referer = request.headers.get('Referer', 'No referer')
    current_app.logger.info(f"Logout request from {request.remote_addr} - User-Agent: {user_agent[:50]}... - Referer: {referer}")
    
    # Prevent logout spam - only allow one logout per 5 seconds
    if current_time - last_logout_time < 5:
        current_app.logger.info("Logout rate limited - too many requests")
        return redirect(url_for('main.index'))
    
    # Update last logout time
    session['last_logout_time'] = current_time
    
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out successfully.', 'info')
        current_app.logger.info("User logged out successfully")
    else:
        current_app.logger.info("Logout attempt with no authenticated user")
    
    # Clear the session completely to prevent issues
    session.clear()
    
    return redirect(url_for('main.index'))

@auth_bp.route('/logout-complete')
def logout_complete():
    """Logout completion page to break redirect loops"""
    return render_template('auth/logout_complete.html')
