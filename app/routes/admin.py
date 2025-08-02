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

@admin_bp.route('/')
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
    """Toggle user verification status"""
    user = User.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    new_status = not user.verified
    if user.update_verification_status(new_status):
        return jsonify({
            'success': True, 
            'message': f'User verification status updated',
            'verified': new_status
        })
    else:
        return jsonify({'success': False, 'message': 'Failed to update verification status'})
