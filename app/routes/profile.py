from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app.models import User, Booking, Listing, Review, Favorite
from app.database import get_db_connection
from app.email_verification import email_service, EmailVerification
import os
import uuid

profile_bp = Blueprint('profile', __name__)

UPLOAD_FOLDER = 'app/static/uploads/profiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Unified profile page for all user types with CRUD operations"""
    
    if request.method == 'POST':
        action = request.form.get('action') or request.json.get('action') if request.is_json else None
        
        if action == 'update_profile':
            return handle_profile_update()
        elif action == 'change_password':
            return handle_password_change()
        elif action == 'toggle_notifications':
            return handle_notification_toggle()
    
    # GET request - display profile
    stats = get_user_stats()
    context = {
        'stats': stats,
        'edit_mode': False
    }
    
    # Add admin-specific data
    if current_user.user_type == 'admin':
        context.update(get_admin_stats())
    
    return render_template('profile.html', **context)

def get_user_stats():
    """Get user-specific statistics"""
    stats = {
        'total_bookings': 0,
        'average_rating': 0.0,
        'favorites': 0,
        'reviews_given': 0,
        'total_listings': 0,
        'total_earnings': 0
    }
    
    try:
        # Get user bookings
        if current_user.user_type == 'guest':
            bookings = Booking.get_by_guest(current_user.id)
            stats['total_bookings'] = len(bookings) if bookings else 0
            
            # Get favorites
            favorites = Favorite.get_by_user(current_user.id)
            stats['favorites'] = len(favorites) if favorites else 0
            
        elif current_user.user_type == 'host':
            # Host bookings
            host_bookings = Booking.get_by_host(current_user.id)
            stats['total_bookings'] = len(host_bookings) if host_bookings else 0
            
            # Host listings
            listings = Listing.get_by_host(current_user.id)
            stats['total_listings'] = len(listings) if listings else 0
            
            # Calculate earnings and ratings
            if host_bookings:
                total_earnings = sum(booking.total_amount for booking in host_bookings if booking.status == 'completed')
                stats['total_earnings'] = total_earnings
                
                # Average rating calculation
                total_rating = 0
                rating_count = 0
                for booking in host_bookings:
                    if hasattr(booking, 'rating') and booking.rating:
                        total_rating += booking.rating
                        rating_count += 1
                if rating_count > 0:
                    stats['average_rating'] = round(total_rating / rating_count, 1)
        
        # Reviews given by user
        reviews = Review.get_by_user(current_user.id)
        stats['reviews_given'] = len(reviews) if reviews else 0
        
    except Exception as e:
        print(f"Error getting user stats: {e}")
    
    return stats

def get_admin_stats():
    """Get admin-specific statistics"""
    stats = {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_type != 'admin'")
        stats['total_users'] = cursor.fetchone()[0]
        
        # Total listings
        cursor.execute("SELECT COUNT(*) FROM listings WHERE status = 'active'")
        stats['total_listings'] = cursor.fetchone()[0]
        
        # Total bookings
        cursor.execute("SELECT COUNT(*) FROM bookings")
        stats['total_bookings'] = cursor.fetchone()[0]
        
        # Total revenue
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM bookings WHERE status = 'completed'")
        stats['total_revenue'] = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error getting admin stats: {e}")
        stats = {'total_users': 0, 'total_listings': 0, 'total_bookings': 0, 'total_revenue': 0}
    
    return stats

def handle_profile_update():
    """Handle profile update"""
    try:
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Validate required fields
        if not first_name or not last_name or not email:
            return jsonify({'success': False, 'message': 'First name, last name, and email are required'})
        
        # Handle profile picture upload
        profile_picture_path = current_user.profile_picture_path
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                # Create upload directory if it doesn't exist
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Generate unique filename
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                unique_filename = f"{current_user.first_name}_{current_user.last_name}_{current_user.id}_profile{ext}"
                
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                profile_picture_path = f"profiles/{unique_filename}"
        
        # Update user in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET first_name = %s, last_name = %s, email = %s, phone = %s, 
                bio = %s, profile_picture_path = %s
            WHERE id = %s
        """, (first_name, last_name, email, phone, bio, profile_picture_path, current_user.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Update current_user object
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.email = email
        current_user.phone = phone
        current_user.bio = bio
        current_user.profile_picture_path = profile_picture_path
        
        return jsonify({'success': True, 'message': 'Profile updated successfully!'})
        
    except Exception as e:
        print(f"Error updating profile: {e}")
        return jsonify({'success': False, 'message': 'Failed to update profile'})

def handle_password_change():
    """Handle password change"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords
        if not current_password or not new_password or not confirm_password:
            return jsonify({'success': False, 'message': 'All password fields are required'})
        
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'New passwords do not match'})
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'})
        
        # Verify current password
        if not check_password_hash(current_user.password_hash, current_password):
            return jsonify({'success': False, 'message': 'Current password is incorrect'})
        
        # Update password
        new_password_hash = generate_password_hash(new_password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", 
                      (new_password_hash, current_user.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Password changed successfully!'})
        
    except Exception as e:
        print(f"Error changing password: {e}")
        return jsonify({'success': False, 'message': 'Failed to change password'})

def handle_notification_toggle():
    """Handle email notification toggle"""
    try:
        enabled = request.json.get('enabled', False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET email_notifications = %s WHERE id = %s", 
                      (enabled, current_user.id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        current_user.email_notifications = enabled
        
        return jsonify({'success': True, 'message': f'Email notifications {"enabled" if enabled else "disabled"}'})
        
    except Exception as e:
        print(f"Error toggling notifications: {e}")
        return jsonify({'success': False, 'message': 'Failed to update notification settings'})


@profile_bp.route('/profile/edit', methods=['GET'])
@login_required
def edit_profile():
    """Edit profile page - redirects to main profile with edit mode"""
    return redirect(url_for('profile.profile'))

@profile_bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    try:
        password = request.form.get('password')
        
        if not password:
            return jsonify({'success': False, 'message': 'Password is required to delete account'})
        
        # Verify password
        if not check_password_hash(current_user.password_hash, password):
            return jsonify({'success': False, 'message': 'Incorrect password'})
        
        # Prevent admin deletion
        if current_user.user_type == 'admin':
            return jsonify({'success': False, 'message': 'Admin accounts cannot be deleted'})
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete user (this should cascade to related records)
        cursor.execute("DELETE FROM users WHERE id = %s", (current_user.id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Logout user
        from flask_login import logout_user
        logout_user()
        
        return jsonify({'success': True, 'message': 'Account deleted successfully', 'redirect': url_for('main.index')})
        
    except Exception as e:
        print(f"Error deleting account: {e}")
        return jsonify({'success': False, 'message': 'Failed to delete account'})

@profile_bp.route('/my-listings')
@login_required
def my_listings():
    """Display user's listings (for hosts)"""
    if current_user.user_type not in ['host', 'admin']:
        flash('Access denied. Only hosts can view listings.', 'error')
        return redirect(url_for('main.dashboard'))
    
    user_listings = Listing.get_by_host(current_user.id)
    host_bookings = Booking.get_by_host(current_user.id)
    
    return render_template('host/my_listings.html', 
                         listings=user_listings,
                         bookings=host_bookings,
                         user=current_user)

@profile_bp.route('/send-verification', methods=['POST'])
@login_required
def send_verification_button():
    """Send email verification from profile page"""
    try:
        # Check if user is already verified
        if current_user.is_verified:
            return jsonify({'success': False, 'message': 'Email is already verified'})
        
        # Check rate limiting (prevent spam)
        last_verification = EmailVerification.get_last_verification_time(current_user.id)
        if last_verification:
            from datetime import datetime, timedelta
            if datetime.now() - last_verification < timedelta(minutes=1):
                return jsonify({'success': False, 'message': 'Please wait before requesting another verification email'})
        
        # Create verification code
        verification_data = EmailVerification.create_verification_code(current_user.id, current_user.email)
        
        if not verification_data:
            return jsonify({'success': False, 'message': 'Failed to create verification code'})
        
        # Send email
        user_name = f"{current_user.first_name} {current_user.last_name}".strip()
        email_sent = email_service.send_verification_email(
            current_user.email, 
            user_name, 
            verification_data['code']
        )
        
        if email_sent:
            return jsonify({'success': True, 'message': 'Verification email sent successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send verification email'})
    
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while sending verification email'})
