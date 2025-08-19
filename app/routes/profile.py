from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import os
import time
from app.models import User

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
@login_required
def profile():
    """User profile page for all user types"""
    return render_template('profile/profile.html', user=current_user)

@profile_bp.route("/profile/edit", methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        try:
            # Get form data
            full_name = request.form.get('full_name', '').strip()
            phone = request.form.get('phone', '').strip()
            bio = request.form.get('bio', '').strip()
            
            # Handle profile photo upload
            profile_photo = None
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file and file.filename and file.filename != '':
                    filename = secure_filename(file.filename)
                    # Create unique filename
                    name, ext = os.path.splitext(filename)
                    filename = f"{current_user.id}_{name}_{int(time.time())}{ext}"
                    
                    # Save file
                    upload_path = os.path.join('app', 'static', 'uploads', filename)
                    file.save(upload_path)
                    profile_photo = filename
            
            # Update user profile
            success = current_user.update_profile(
                full_name=full_name if full_name else None,
                phone=phone if phone else None,
                bio=bio if bio else None,
                profile_photo=profile_photo if profile_photo else None
            )
            
            if success:
                flash('Profile updated successfully!', 'success')
            else:
                flash('Error updating profile. Please try again.', 'error')
                
        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
        
        return redirect(url_for('profile.edit_profile'))
    
    return render_template('profile/edit.html', user=current_user)

@profile_bp.route("/profile/settings", methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    return render_template('profile/settings.html', user=current_user)

@profile_bp.route("/profile/change-password", methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validate current password
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('profile.change_password'))
            
            # Validate new password
            if len(new_password) < 8:
                flash('New password must be at least 8 characters long.', 'error')
                return redirect(url_for('profile.change_password'))
            
            if new_password != confirm_password:
                flash('New passwords do not match.', 'error')
                return redirect(url_for('profile.change_password'))
            
            # Update password
            success = current_user.update_password(new_password)
            
            if success:
                flash('Password updated successfully! You have been logged out of other devices.', 'success')
                return redirect(url_for('profile.profile'))
            else:
                flash('Error updating password. Please try again.', 'error')
                
        except Exception as e:
            flash(f'Error updating password: {str(e)}', 'error')
        
        return redirect(url_for('profile.change_password'))
    
    return render_template('profile/change_password.html', user=current_user)

@profile_bp.route("/profile/update-notification-settings", methods=['POST'])
@login_required
def update_notification_settings():
    """Update user notification preferences"""
    try:
        # Get notification preferences from form
        email_bookings = 'email_bookings' in request.form
        email_messages = 'email_messages' in request.form
        email_listings = 'email_listings' in request.form
        email_marketing = 'email_marketing' in request.form
        push_notifications = 'push_notifications' in request.form
        
        # Here you would update the notification preferences in the database
        # For now, just flash a success message
        flash('Notification settings updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating notification settings: {str(e)}', 'error')
    
    return redirect(url_for('profile.settings'))

@profile_bp.route("/profile/update-privacy-settings", methods=['POST'])
@login_required
def update_privacy_settings():
    """Update user privacy preferences"""
    try:
        # Get privacy preferences from form
        public_profile = 'public_profile' in request.form
        show_contact = 'show_contact' in request.form
        show_listings_count = 'show_listings_count' in request.form
        analytics = 'analytics' in request.form
        
        # Here you would update the privacy preferences in the database
        # For now, just flash a success message
        flash('Privacy settings updated successfully!', 'success')
        
    except Exception as e:
        flash(f'Error updating privacy settings: {str(e)}', 'error')
    
    return redirect(url_for('profile.settings'))

@profile_bp.route("/my_listings")
@login_required
def my_listings():
    """User's property listings (for hosts)"""
    if current_user.user_type == 'host':
        # Get user's listings from database
        from app.models import Listing, Booking, Review
        
        try:
            user_listings = Listing.get_by_host(current_user.id)
            
            # Calculate statistics
            total_views = 0
            pending_listings = 0
            for listing in user_listings if user_listings else []:
                if hasattr(listing, 'views'):
                    total_views += listing.views or 0
                if hasattr(listing, 'status') and listing.status == 'pending':
                    pending_listings += 1
            
            return render_template('host/my_listings.html', 
                                   user=current_user,
                                   listings=user_listings or [],
                                   total_views=total_views,
                                   pending_listings=pending_listings)
        except Exception as e:
            print(f"Error loading listings: {e}")
            return render_template('host/my_listings.html', 
                                   user=current_user,
                                   listings=[],
                                   total_views=0,
                                   pending_listings=0)
    else:
        return redirect(url_for('profile.profile'))

@profile_bp.route("/api/profile/data", methods=['GET'])
@login_required
def api_profile_data():
    """API endpoint for real-time profile data updates"""
    try:
        # Calculate completion score
        completion_score = (
            (25 if current_user.name else 0) +
            (25 if current_user.email else 0) +
            (20 if current_user.phone else 0) +
            (15 if current_user.bio else 0) +
            (15 if current_user.profile_photo else 0)
        )
        
        # Get statistics based on user type
        statistics = {
            'favorites': len(current_user.favorites) if current_user.favorites else 0,
            'reviews': 0  # Placeholder for review count
        }
        
        if current_user.user_type == 'host':
            statistics.update({
                'properties': len(current_user.listings) if current_user.listings else 0,
                'host_bookings': len(current_user.host_bookings) if current_user.host_bookings else 0
            })
        else:
            statistics.update({
                'bookings': len(current_user.guest_bookings) if current_user.guest_bookings else 0
            })
        
        # Add verification status
        statistics['verification'] = 'Yes' if current_user.verified else 'No'
        
        return jsonify({
            'success': True,
            'statistics': statistics,
            'completion_score': completion_score,
            'verification_status': current_user.verified,
            'last_updated': time.time()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route("/api/profile/verify-password", methods=['POST'])
@login_required
def api_verify_password():
    """API endpoint for real-time password verification"""
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        
        if not current_password:
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Password is required'
            }), 400
        
        # Verify current password
        is_valid = check_password_hash(current_user.password_hash, current_password)
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'message': 'Password verified' if is_valid else 'Invalid password'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'valid': False,
            'error': str(e)
        }), 500
