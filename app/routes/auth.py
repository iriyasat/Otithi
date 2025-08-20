from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
from app.forms import LoginForm, RegistrationForm

# Create the authentication blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
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
        full_name = form.full_name.data.strip()
        email = form.email.data.strip().lower()
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
                flash('Registration successful! You can now log in with your credentials.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Registration failed. Please try again.', 'danger')
        
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

# Password reset functionality (if needed)
# @auth_bp.route('/reset_password')
