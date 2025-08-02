from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import User, Listing, Booking, Review
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Main admin routes
@admin_bp.route('/')
@login_required
@admin_required
def admin():
    """Main admin route - redirects to dashboard"""
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    all_users = User.get_all()
    all_listings = Listing.get_all()
    all_bookings = Booking.get_all()
    
    return render_template('admin/admin.html', 
                         user=current_user, 
                         users=all_users,
                         bookings=all_bookings, 
                         listings=all_listings)

# User management routes
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Admin panel - manage users"""
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle-verification', methods=['POST'])
@login_required
@admin_required
def toggle_verification(user_id):
    """Admin panel - toggle user verification status"""
    user = User.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    new_status = not user.verified
    if user.update_verification_status(new_status):
        status_text = 'Verified' if new_status else 'Unverified'
        badge_class = 'success' if new_status else 'warning'
        btn_class = 'warning' if new_status else 'success'
        btn_icon = 'times-circle' if new_status else 'check-circle'
        btn_title = 'Unverify User' if new_status else 'Verify User'
        
        return jsonify({
            'success': True, 
            'message': f'User verification status updated to {status_text}',
            'verified': new_status,
            'badge_class': badge_class,
            'status_text': status_text,
            'btn_class': btn_class,
            'btn_icon': btn_icon,
            'btn_title': btn_title
        })
    else:
        return jsonify({'success': False, 'message': 'Failed to update verification status'})

@admin_bp.route('/users/<int:user_id>/edit-confirm')
@login_required
@admin_required
def edit_user_confirm(user_id):
    """Admin panel - edit user confirmation page"""
    user = User.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_user_confirm.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete-confirm')
@login_required
@admin_required
def delete_user_confirm(user_id):
    """Admin panel - delete user confirmation page"""
    user = User.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/delete_user_confirm.html', user=user)

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Admin panel - edit user"""
    user = User.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('admin.users'))
    
    if request.method == 'POST':
        full_name = request.form['full_name']
        phone = request.form['phone']
        user_type = request.form['user_type']
        bio = request.form.get('bio', '')
        verified = request.form.get('verified') == '1'
        
        # Update user details
        user.update_profile(full_name=full_name, phone=phone, bio=bio)
        user.update_user_type(user_type)
        user.update_verification_status(verified)
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Admin panel - delete user"""
    print(f"DEBUG: delete_user called with user_id: {user_id}")
    user = User.get(user_id)
    if not user:
        print(f"DEBUG: User {user_id} not found")
        flash('User not found.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    if user.id == current_user.id:
        print(f"DEBUG: Cannot delete own account")
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.dashboard'))
    
    print(f"DEBUG: Attempting to delete user {user.name} (ID: {user.id})")
    if user.delete():
        print(f"DEBUG: User deleted successfully")
        flash('User deleted successfully!', 'success')
    else:
        print(f"DEBUG: Error deleting user")
        flash('Error deleting user.', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    """Admin panel - change user role"""
    user = User.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    try:
        data = request.get_json()
        new_role = data.get('role') if data else None
    except:
        new_role = None
        
    if new_role not in ['guest', 'host', 'admin']:
        return jsonify({'success': False, 'message': 'Invalid role'})
    
    if user.update_user_type(new_role):
        return jsonify({'success': True, 'message': 'Role updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to update role'})

# Listing management routes
@admin_bp.route('/listings')
@login_required
@admin_required
def listings():
    """Admin panel - manage listings"""
    listings = Listing.get_all()
    return render_template('admin/listings.html', listings=listings)

@admin_bp.route('/listings/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_listing(listing_id):
    """Admin panel - edit listing"""
    listing = Listing.get(listing_id)
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('admin.listings'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        property_type = request.form['property_type']
        guests = int(request.form['guests'])
        amenities = request.form.getlist('amenities')
        
        # Update listing
        listing.update(
            title=title,
            description=description,
            price=price,
            property_type=property_type,
            guests=guests,
            amenities=amenities
        )
        
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('admin.listings'))
    
    return render_template('admin/edit_listing.html', listing=listing)

@admin_bp.route('/listings/<int:listing_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_listing(listing_id):
    """Admin panel - delete listing"""
    listing = Listing.get(listing_id)
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('admin.listings'))
    
    if listing.delete():
        flash('Listing deleted successfully!', 'success')
    else:
        flash('Error deleting listing.', 'error')
    
    return redirect(url_for('admin.listings'))

@admin_bp.route('/listings/<int:listing_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_listing(listing_id):
    """Admin panel - approve listing"""
    listing = Listing.get(listing_id)
    if not listing:
        return jsonify({'success': False, 'message': 'Listing not found'})
    
    if listing.approve():
        return jsonify({'success': True, 'message': 'Listing approved successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to approve listing'})

# Booking management routes
@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings():
    """Admin panel - manage bookings"""
    bookings = Booking.get_all()
    return render_template('admin/bookings.html', bookings=bookings)

@admin_bp.route('/bookings/<int:booking_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_booking_status(booking_id):
    """Admin panel - update booking status"""
    booking = Booking.get(booking_id)
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('admin.bookings'))
    
    # Get status from form data
    new_status = request.form.get('status')
        
    if new_status not in ['pending', 'confirmed', 'cancelled']:
        flash('Invalid status.', 'error')
        return redirect(url_for('admin.bookings'))
    
    if booking.update_status(new_status):
        flash(f'Booking status updated to {new_status.title()}.', 'success')
    else:
        flash('Failed to update booking status.', 'error')
    
    return redirect(url_for('admin.bookings'))

# Admin profile management
@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    """Admin profile management"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            full_name = request.form['full_name']
            phone = request.form['phone']
            
            if current_user.update_profile(full_name=full_name, phone=phone):
                flash('Profile updated successfully!', 'success')
            else:
                flash('Error updating profile.', 'error')
                
        elif action == 'change_password':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect.', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'error')
            elif len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'error')
            else:
                if current_user.update_password(new_password):
                    flash('Password changed successfully!', 'success')
                else:
                    flash('Error changing password.', 'error')
        
        return redirect(url_for('admin.profile'))
    
    # Get statistics for the profile page
    users = User.get_all()
    bookings = Booking.get_all()
    
    stats = {
        'total_users': len(users) if users else 0,
        'total_bookings': len(bookings) if bookings else 0,
    }
    
    return render_template('admin/profile.html', user=current_user, stats=stats)

# Statistics and reporting
@admin_bp.route('/stats')
@login_required
@admin_required
def stats():
    """Admin panel - statistics"""
    users = User.get_all()
    listings = Listing.get_all()
    bookings = Booking.get_all()
    
    stats = {
        'total_users': len(users),
        'total_hosts': len([u for u in users if u.user_type == 'host']),
        'total_guests': len([u for u in users if u.user_type == 'guest']),
        'total_listings': len(listings),
        'total_bookings': len(bookings),
        'confirmed_bookings': len([b for b in bookings if b.status == 'confirmed']),
        'pending_bookings': len([b for b in bookings if b.status == 'pending']),
        'total_revenue': sum(b.total_price for b in bookings if b.status == 'confirmed'),
        'recent_users': sorted(users, key=lambda x: x.joined_date, reverse=True)[:10],
        'recent_listings': sorted(listings, key=lambda x: x.created_date, reverse=True)[:10],
        'recent_bookings': sorted(bookings, key=lambda x: x.created_date, reverse=True)[:10]
    }
    
    return render_template('admin/stats.html', stats=stats)
