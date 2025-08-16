from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from flask_login import login_user, logout_user, current_user
from flask_wtf.csrf import validate_csrf
from app.models import User
from app.forms import LoginForm, RegistrationForm
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
                full_name=form.full_name.data,
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
