"""
Admin routes for admin dashboard and management functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from ..models import User, Listing, Booking, Message, ListingStatus, BookingStatus
from .. import db
from ..helpers import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with overview statistics"""
    # User statistics
    total_users = User.query.count()
    total_hosts = User.query.filter_by(role='host').count()
    total_guests = User.query.filter_by(role='guest').count()
    verified_hosts = User.query.filter_by(role='host', is_verified=True).count()
    
    # Listing statistics
    total_listings = Listing.query.count()
    approved_listings = Listing.query.filter_by(status=ListingStatus.APPROVED).count()
    pending_listings = Listing.query.filter_by(status=ListingStatus.PENDING_APPROVAL).count()
    rejected_listings = Listing.query.filter_by(status=ListingStatus.REJECTED).count()
    
    # Booking statistics
    total_bookings = Booking.query.count()
    confirmed_bookings = Booking.query.filter_by(status=BookingStatus.CONFIRMED).count()
    pending_bookings = Booking.query.filter_by(status=BookingStatus.PENDING).count()
    
    # Recent activity
    recent_listings = Listing.query.order_by(desc(Listing.created_at)).limit(5).all()
    recent_bookings = Booking.query.order_by(desc(Booking.created_at)).limit(5).all()
    recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
    
    # Monthly statistics (last 6 months)
    months = []
    listing_counts = []
    booking_counts = []
    
    for i in range(6):
        month = datetime.now() - timedelta(days=30*i)
        month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        months.append(month_start.strftime('%b %Y'))
        listing_counts.append(
            Listing.query.filter(
                Listing.created_at >= month_start,
                Listing.created_at <= month_end
            ).count()
        )
        booking_counts.append(
            Booking.query.filter(
                Booking.created_at >= month_start,
                Booking.created_at <= month_end
            ).count()
        )
    
    months.reverse()
    listing_counts.reverse()
    booking_counts.reverse()
    
    return render_template('admin/admin_dashboard.html',
                         total_users=total_users,
                         total_hosts=total_hosts,
                         total_guests=total_guests,
                         verified_hosts=verified_hosts,
                         total_listings=total_listings,
                         approved_listings=approved_listings,
                         pending_listings=pending_listings,
                         rejected_listings=rejected_listings,
                         total_bookings=total_bookings,
                         confirmed_bookings=confirmed_bookings,
                         pending_bookings=pending_bookings,
                         recent_listings=recent_listings,
                         recent_bookings=recent_bookings,
                         recent_users=recent_users,
                         months=months,
                         listing_counts=listing_counts,
                         booking_counts=booking_counts)

@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    verified_filter = request.args.get('verified', '')
    
    query = User.query
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if verified_filter == 'true':
        query = query.filter_by(is_verified=True)
    elif verified_filter == 'false':
        query = query.filter_by(is_verified=False)
    
    pagination = query.order_by(desc(User.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/manage_users.html',
                         pagination=pagination,
                         role_filter=role_filter,
                         verified_filter=verified_filter)

@admin_bp.route('/listings')
@login_required
@admin_required
def manage_listings():
    """Manage listings"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Listing.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    pagination = query.order_by(desc(Listing.created_at)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/manage_listings.html',
                         pagination=pagination,
                         status_filter=status_filter)

@admin_bp.route('/approve-listing/<int:id>')
@login_required
@admin_required
def approve_listing(id):
    """Approve a listing"""
    listing = Listing.query.get_or_404(id)
    listing.status = ListingStatus.APPROVED
    db.session.commit()
    flash('Listing approved successfully!', 'success')
    return redirect(url_for('admin.manage_listings'))

@admin_bp.route('/reject-listing/<int:id>')
@login_required
@admin_required
def reject_listing(id):
    """Reject a listing"""
    listing = Listing.query.get_or_404(id)
    listing.status = ListingStatus.REJECTED
    db.session.commit()
    flash('Listing rejected.', 'info')
    return redirect(url_for('admin.manage_listings'))

@admin_bp.route('/verify-host/<int:id>')
@login_required
@admin_required
def verify_host(id):
    """Verify a host"""
    user = User.query.get_or_404(id)
    if user.role != 'host':
        flash('User is not a host.', 'warning')
        return redirect(url_for('admin.manage_users'))
    
    user.is_verified = True
    db.session.commit()
    flash('Host verified successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/unverify-host/<int:id>')
@login_required
@admin_required
def unverify_host(id):
    """Unverify a host"""
    user = User.query.get_or_404(id)
    if user.role != 'host':
        flash('User is not a host.', 'warning')
        return redirect(url_for('admin.manage_users'))
    
    user.is_verified = False
    db.session.commit()
    flash('Host verification removed.', 'info')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/delete-user/<int:id>')
@login_required
@admin_required
def delete_user(id):
    """Delete a user"""
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    # Delete user's listings and bookings
    Listing.query.filter_by(user_id=user.id).delete()
    Booking.query.filter_by(guest_id=user.id).delete()
    Booking.query.filter(Listing.user_id == user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/delete-listing/<int:id>')
@login_required
@admin_required
def delete_listing(id):
    """Delete a listing"""
    listing = Listing.query.get_or_404(id)
    
    # Delete associated bookings
    Booking.query.filter_by(listing_id=listing.id).delete()
    
    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted successfully!', 'success')
    return redirect(url_for('admin.manage_listings'))

@admin_bp.route('/cache-stats')
@login_required
@admin_required
def cache_stats():
    """View cache statistics"""
    return render_template('admin/cache_stats.html')

@admin_bp.route('/clear-cache', methods=['POST'])
@login_required
@admin_required
def clear_cache():
    """Clear application cache"""
    # This is a placeholder for cache clearing functionality
    # In a real application, you would clear your cache here
    flash('Cache cleared successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/nid-verifications')
@login_required
@admin_required
def nid_verifications():
    """List hosts with uploaded NIDs pending approval"""
    hosts = User.query.filter(User.role == 'host', User.nid_filename != None).order_by(desc(User.created_at)).all()
    return render_template('admin/nid_verifications.html', hosts=hosts)

@admin_bp.route('/approve-nid/<int:user_id>')
@login_required
@admin_required
def approve_nid(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'host' or not user.nid_filename:
        flash('Invalid host or no NID uploaded.', 'danger')
        return redirect(url_for('admin.nid_verifications'))
    user.is_verified = True
    db.session.commit()
    flash('Host NID approved and host verified!', 'success')
    return redirect(url_for('admin.nid_verifications'))

@admin_bp.route('/reject-nid/<int:user_id>')
@login_required
@admin_required
def reject_nid(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'host' or not user.nid_filename:
        flash('Invalid host or no NID uploaded.', 'danger')
        return redirect(url_for('admin.nid_verifications'))
    user.nid_filename = None
    user.is_verified = False
    db.session.commit()
    flash('Host NID rejected and removed.', 'info')
    return redirect(url_for('admin.nid_verifications')) 