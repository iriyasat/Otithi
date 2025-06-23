from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from ..models import User, Listing, Booking, Review, Message, Conversation, ListingStatus, BookingStatus, UserRole
from .. import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin privileges"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with comprehensive statistics"""
    # Get total counts
    total_users = User.query.count()
    total_hosts = User.query.filter_by(role='host').count()
    total_guests = User.query.filter_by(role='guest').count()
    total_listings = Listing.query.count()
    total_bookings = Booking.query.count()
    total_reviews = Review.query.count()
    
    # Get pending counts
    pending_listings = Listing.query.filter_by(status=ListingStatus.PENDING).count()
    pending_bookings = Booking.query.filter_by(status=BookingStatus.PENDING).count()
    
    # Get recent activity (enhanced with more details)
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_listings = Listing.query.order_by(Listing.created_at.desc()).limit(5).all()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    
    # Get monthly statistics
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_users = User.query.filter(User.created_at >= current_month).count()
    monthly_listings = Listing.query.filter(Listing.created_at >= current_month).count()
    monthly_bookings = Booking.query.filter(Booking.created_at >= current_month).count()
    
    # Calculate total earnings
    total_earnings = db.session.query(func.sum(Booking.total_price)).filter(
        Booking.status == BookingStatus.CONFIRMED
    ).scalar() or 0
    
    # Get top performing listings (enhanced query)
    top_listings = db.session.query(
        Listing, 
        func.count(Booking.id).label('booking_count'),
        func.avg(Review.rating).label('avg_rating'),
        func.sum(Booking.total_price).label('total_earnings')
    ).outerjoin(Booking).outerjoin(Review).group_by(Listing.id)\
     .order_by(desc('booking_count')).limit(5).all()
    
    # New: Get weekly trends for the last 4 weeks
    weekly_stats = []
    for i in range(4):
        week_start = datetime.now() - timedelta(weeks=i+1)
        week_end = datetime.now() - timedelta(weeks=i)
        
        week_users = User.query.filter(
            User.created_at >= week_start,
            User.created_at < week_end
        ).count()
        
        week_listings = Listing.query.filter(
            Listing.created_at >= week_start,
            Listing.created_at < week_end
        ).count()
        
        week_bookings = Booking.query.filter(
            Booking.created_at >= week_start,
            Booking.created_at < week_end
        ).count()
        
        weekly_stats.append({
            'week': f"Week {4-i}",
            'users': week_users,
            'listings': week_listings,
            'bookings': week_bookings
        })
    
    # New: Get popular locations
    popular_locations = db.session.query(
        Listing.location,
        func.count(Listing.id).label('listing_count'),
        func.avg(Listing.price_per_night).label('avg_price')
    ).group_by(Listing.location)\
     .order_by(desc('listing_count')).limit(5).all()
    
    # New: Get recent reviews for admin review
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(5).all()
    
    # Debug logging
    print("=== ADMIN DASHBOARD DATA ===")
    print(f"Total Users: {total_users}")
    print(f"Total Hosts: {total_hosts}")
    print(f"Total Guests: {total_guests}")
    print(f"Total Listings: {total_listings}")
    print(f"Total Bookings: {total_bookings}")
    print(f"Total Reviews: {total_reviews}")
    print(f"Pending Listings: {pending_listings}")
    print(f"Pending Bookings: {pending_bookings}")
    print(f"Monthly Users: {monthly_users}")
    print(f"Monthly Listings: {monthly_listings}")
    print(f"Monthly Bookings: {monthly_bookings}")
    print(f"Total Earnings: {total_earnings}")
    print("===========================")
    
    return render_template('admin/admin_dashboard.html',
                         total_users=total_users,
                         total_hosts=total_hosts,
                         total_guests=total_guests,
                         total_listings=total_listings,
                         total_bookings=total_bookings,
                         total_reviews=total_reviews,
                         pending_listings=pending_listings,
                         pending_bookings=pending_bookings,
                         monthly_users=monthly_users,
                         monthly_listings=monthly_listings,
                         monthly_bookings=monthly_bookings,
                         total_earnings=total_earnings,
                         recent_users=recent_users,
                         recent_listings=recent_listings,
                         recent_bookings=recent_bookings,
                         top_listings=top_listings,
                         weekly_stats=weekly_stats,
                         popular_locations=popular_locations,
                         recent_reviews=recent_reviews)

@admin_bp.route('/manage-users')
@login_required
@admin_required
def manage_users():
    """Manage users with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    role_filter = request.args.get('role', '')
    search = request.args.get('search', '')
    
    query = User.query
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search))
        )
    
    pagination = query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/manage_users.html', 
                         pagination=pagination,
                         role_filter=role_filter,
                         search=search)

@admin_bp.route('/manage-listings')
@login_required
@admin_required
def manage_listings():
    """Manage listings with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search = request.args.get('search', '')
    
    query = Listing.query
    
    if status_filter:
        query = query.filter_by(status=ListingStatus(status_filter))
    
    if search:
        query = query.filter(
            (Listing.title.contains(search)) |
            (Listing.location.contains(search))
        )
    
    pagination = query.order_by(Listing.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/manage_listings.html', 
                         pagination=pagination,
                         status_filter=status_filter,
                         search=search)

@admin_bp.route('/approve-listing/<int:listing_id>', methods=['POST'])
@login_required
@admin_required
def approve_listing(listing_id):
    """Approve a listing"""
    listing = Listing.query.get_or_404(listing_id)
    
    try:
        listing.status = ListingStatus.APPROVED
        db.session.commit()
        flash(f'Listing "{listing.title}" has been approved.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error approving listing. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_listings'))

@admin_bp.route('/reject-listing/<int:listing_id>', methods=['POST'])
@login_required
@admin_required
def reject_listing(listing_id):
    """Reject a listing"""
    listing = Listing.query.get_or_404(listing_id)
    
    try:
        listing.status = ListingStatus.REJECTED
        db.session.commit()
        flash(f'Listing "{listing.title}" has been rejected.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error rejecting listing. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_listings'))

@admin_bp.route('/delete-listing/<int:listing_id>', methods=['POST'])
@login_required
@admin_required
def delete_listing(listing_id):
    """Delete a listing"""
    listing = Listing.query.get_or_404(listing_id)
    
    try:
        # Delete associated bookings and reviews
        Booking.query.filter_by(listing_id=listing_id).delete()
        Review.query.filter_by(listing_id=listing_id).delete()
        
        # Delete the listing
        db.session.delete(listing)
        db.session.commit()
        flash(f'Listing "{listing.title}" has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting listing. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_listings'))

@admin_bp.route('/manage-bookings')
@login_required
@admin_required
def manage_bookings():
    """Manage bookings with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Booking.query
    
    if status_filter:
        query = query.filter_by(status=BookingStatus(status_filter))
    
    pagination = query.order_by(Booking.created_at.desc())\
        .paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/manage_bookings.html', 
                         pagination=pagination,
                         status_filter=status_filter)

@admin_bp.route('/update-booking-status/<int:booking_id>', methods=['POST'])
@login_required
@admin_required
def update_booking_status(booking_id):
    """Update booking status"""
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get('status')
    
    if new_status in ['PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED']:
        try:
            booking.status = BookingStatus(new_status)
            db.session.commit()
            flash(f'Booking status updated to {new_status}.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating booking status. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_bookings'))

@admin_bp.route('/user-details/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    """View detailed user information"""
    user = User.query.get_or_404(user_id)
    
    # Get user's listings
    user_listings = Listing.query.filter_by(user_id=user_id).all()
    
    # Get user's bookings
    user_bookings = Booking.query.filter_by(user_id=user_id).all()
    
    # Get user's reviews
    user_reviews = Review.query.filter_by(user_id=user_id).all()
    
    return render_template('admin/user_details.html',
                         user=user,
                         listings=user_listings,
                         bookings=user_bookings,
                         reviews=user_reviews)

@admin_bp.route('/update-user-role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user_role(user_id):
    """Update user role"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role in ['guest', 'host', 'admin']:
        try:
            user.role = new_role
            db.session.commit()
            flash(f'User role updated to {new_role}.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error updating user role. Please try again.', 'error')
    
    return redirect(url_for('admin.user_details', user_id=user_id))

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('admin.manage_users'))
    
    try:
        # Delete user's listings, bookings, reviews, and messages
        Listing.query.filter_by(user_id=user_id).delete()
        Booking.query.filter_by(user_id=user_id).delete()
        Review.query.filter_by(user_id=user_id).delete()
        Message.query.filter(
            (Message.sender_id == user_id) | (Message.recipient_id == user_id)
        ).delete()
        Conversation.query.filter(
            (Conversation.user1_id == user_id) | (Conversation.user2_id == user_id)
        ).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{user.username}" has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user. Please try again.', 'error')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/system-stats')
@login_required
@admin_required
def system_stats():
    """Detailed system statistics"""
    # Get daily statistics for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    daily_stats = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('new_users'),
        func.count(Listing.id).label('new_listings'),
        func.count(Booking.id).label('new_bookings')
    ).outerjoin(Listing, func.date(User.created_at) == func.date(Listing.created_at))\
     .outerjoin(Booking, func.date(User.created_at) == func.date(Booking.created_at))\
     .filter(User.created_at >= start_date)\
     .group_by(func.date(User.created_at))\
     .order_by(func.date(User.created_at)).all()
    
    # Get top locations
    top_locations = db.session.query(
        Listing.location,
        func.count(Listing.id).label('listing_count')
    ).group_by(Listing.location)\
     .order_by(desc('listing_count'))\
     .limit(10).all()
    
    # Get average ratings by location
    location_ratings = db.session.query(
        Listing.location,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('review_count')
    ).join(Review)\
     .group_by(Listing.location)\
     .having(func.count(Review.id) >= 3)\
     .order_by(desc('avg_rating'))\
     .limit(10).all()
    
    return render_template('admin/system_stats.html',
                         daily_stats=daily_stats,
                         top_locations=top_locations,
                         location_ratings=location_ratings)

@admin_bp.route('/verify-host/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def verify_host(user_id):
    """Verify a host (set is_verified=True)"""
    user = User.query.get_or_404(user_id)
    if user.role != 'host':
        flash('User is not a host.', 'error')
        return redirect(url_for('admin.manage_users'))
    try:
        user.is_verified = True
        db.session.commit()
        flash(f'Host {user.username} has been verified.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error verifying host. Please try again.', 'error')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/unverify-host/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def unverify_host(user_id):
    """Unverify a host (set is_verified=False)"""
    user = User.query.get_or_404(user_id)
    if user.role != 'host':
        flash('User is not a host.', 'error')
        return redirect(url_for('admin.manage_users'))
    try:
        user.is_verified = False
        db.session.commit()
        flash(f'Host {user.username} has been unverified.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error unverifying host. Please try again.', 'error')
    return redirect(url_for('admin.manage_users')) 