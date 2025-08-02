from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from app.models import User
import os

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
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/login.html')
        
        try:
            user = User.get_by_email(email)
            
            if user and user.check_password(password):
                login_user(user, remember=remember_me)
                
                # Log successful login
                flash(f'Welcome back, {user.full_name}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    if user.user_type == 'admin':
                        return redirect(url_for('admin.dashboard'))
                    else:
                        return redirect(url_for('main.dashboard'))
            else:
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            flash('Login failed. Please try again.', 'error')
            print(f"Login error: {e}")  # For debugging
    
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
                login_user(user)
                flash(f'Welcome to Otithi, {user.full_name}! Your account has been created successfully.', 'success')
                return redirect(url_for('main.dashboard'))
            else:
                flash('Registration failed. Please try again.', 'error')
                
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
            print(f"Registration error: {e}")  # For debugging
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
            
            if errors:
                for error in errors:
                    flash(error, 'error')
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
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))
