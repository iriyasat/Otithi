from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from ..models import User, Listing, Booking, Review, ListingStatus
from ..forms import ListingForm
from .. import db

host_bp = Blueprint('host', __name__, url_prefix='/host')

def allowed_file(filename):
    """Check if uploaded file is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@host_bp.route('/dashboard')
@login_required
def dashboard():
    """Host dashboard with comprehensive statistics"""
    if current_user.role != 'host':
        flash('Access denied. Host privileges required.', 'error')
        return redirect(url_for('public.index'))
    
    # Get host's listings
    listings = Listing.query.filter_by(user_id=current_user.id).all()
    
    # Get bookings for host's listings
    host_bookings = Booking.query.join(Listing).filter(Listing.user_id == current_user.id).all()
    
    # Calculate statistics
    total_bookings = len(host_bookings)
    
    # Calculate average rating from reviews of host's listings
    reviews = Review.query.join(Listing).filter(Listing.user_id == current_user.id).all()
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    # Calculate total earnings
    total_earnings = sum(booking.total_price for booking in host_bookings if booking.status.value == 'CONFIRMED')
    
    # Get recent bookings
    recent_bookings = Booking.query.join(Listing).filter(Listing.user_id == current_user.id)\
        .order_by(Booking.created_at.desc()).limit(5).all()
    
    return render_template('host/host_dashboard.html', 
                         listings=listings,
                         total_bookings=total_bookings,
                         avg_rating=round(avg_rating, 1),
                         total_earnings=total_earnings,
                         recent_bookings=recent_bookings)

@host_bp.route('/my-listings')
@login_required
def my_listings():
    """Host's listings management with pagination"""
    if current_user.role != 'host':
        flash('Access denied. Host privileges required.', 'error')
        return redirect(url_for('public.index'))
    
    page = request.args.get('page', 1, type=int)
    pagination = Listing.query.filter_by(user_id=current_user.id)\
        .order_by(Listing.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('host/my_listings.html', pagination=pagination)

@host_bp.route('/add-listing', methods=['GET', 'POST'])
@login_required
def add_listing():
    """Add a new listing"""
    if current_user.role != 'host':
        flash('Access denied. Host privileges required.', 'error')
        return redirect(url_for('public.index'))
    
    form = ListingForm()
    if form.validate_on_submit():
        # Handle file upload
        image_filename = None
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                
                # Save file
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
                file.save(file_path)
        
        # Create new listing
        new_listing = Listing(
            title=form.title.data,
            location=form.location.data,
            description=form.description.data,
            price_per_night=form.price_per_night.data,
            guest_capacity=form.guest_capacity.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            house_rules=form.house_rules.data,
            image_filename=image_filename,
            status=ListingStatus.PENDING,
            user_id=current_user.id
        )
        
        try:
            db.session.add(new_listing)
            db.session.commit()
            flash('Listing created successfully! It will be reviewed by our team.', 'success')
            return redirect(url_for('host.my_listings'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating listing. Please try again.', 'error')
    
    return render_template('listings/add_listing.html', form=form)

@host_bp.route('/edit-listing/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_listing(id):
    """Edit a listing"""
    if current_user.role != 'host':
        flash('Access denied. Host privileges required.', 'error')
        return redirect(url_for('public.index'))
    
    listing = Listing.query.get_or_404(id)
    
    # Ensure user owns this listing
    if listing.user_id != current_user.id:
        flash('Access denied. You can only edit your own listings.', 'error')
        return redirect(url_for('host.my_listings'))
    
    form = ListingForm(obj=listing)
    
    if form.validate_on_submit():
        # Handle file upload
        if form.image.data:
            file = form.image.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                image_filename = f"{timestamp}_{filename}"
                
                # Save new file
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
                file.save(file_path)
                
                # Delete old file if exists
                if listing.image_filename:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], listing.image_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                listing.image_filename = image_filename
        
        # Update listing
        listing.title = form.title.data
        listing.location = form.location.data
        listing.description = form.description.data
        listing.price_per_night = form.price_per_night.data
        listing.guest_capacity = form.guest_capacity.data
        listing.bedrooms = form.bedrooms.data
        listing.bathrooms = form.bathrooms.data
        listing.house_rules = form.house_rules.data
        listing.status = ListingStatus.PENDING  # Reset to pending for review
        
        try:
            db.session.commit()
            flash('Listing updated successfully! It will be reviewed again.', 'success')
            return redirect(url_for('host.my_listings'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating listing. Please try again.', 'error')
    
    return render_template('listings/edit_listing.html', form=form, listing=listing)

@host_bp.route('/delete-listing/<int:id>', methods=['POST'])
@login_required
def delete_listing(id):
    """Delete a listing"""
    if current_user.role != 'host':
        flash('Access denied. Host privileges required.', 'error')
        return redirect(url_for('public.index'))
    
    listing = Listing.query.get_or_404(id)
    
    # Ensure user owns this listing
    if listing.user_id != current_user.id:
        flash('Access denied. You can only delete your own listings.', 'error')
        return redirect(url_for('host.my_listings'))
    
    try:
        # Delete image file if exists
        if listing.image_filename:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], listing.image_filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(listing)
        db.session.commit()
        flash('Listing deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting listing. Please try again.', 'error')
    
    return redirect(url_for('host.my_listings'))

@host_bp.route('/bookings')
@login_required
def bookings():
    """Host's bookings management with pagination"""
    if current_user.role != 'host':
        flash('Access denied. Host privileges required.', 'error')
        return redirect(url_for('public.index'))
    
    page = request.args.get('page', 1, type=int)
    # Get bookings for host's listings with pagination
    pagination = Booking.query.join(Listing).filter(Listing.user_id == current_user.id)\
        .order_by(Booking.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('host/host_bookings.html', pagination=pagination)

@host_bp.route('/upload-nid', methods=['GET', 'POST'])
@login_required
def upload_nid():
    """Upload NID for host verification"""
    if current_user.role != 'host':
        flash('Access denied. Host privileges required.', 'error')
        return redirect(url_for('public.index'))
    
    # Handle NID upload logic here
    return render_template('host/host_upload_nid.html')

@host_bp.route('/become-host')
@login_required
def become_host():
    """Convert guest to host"""
    if current_user.role == 'host':
        flash('You are already a host!', 'info')
        return redirect(url_for('host.dashboard'))
    
    current_user.role = 'host'
    db.session.commit()
    flash('Congratulations! You are now a host. You can start adding listings.', 'success')
    return redirect(url_for('host.dashboard')) 