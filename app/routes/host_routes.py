"""
Host routes for listing management and host dashboard functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import desc
import os
from datetime import datetime
from ..models import Listing, Booking, ListingStatus, BookingStatus, User
from ..forms import ListingForm
from .. import db
from ..helpers import save_image, delete_image

host_bp = Blueprint('host', __name__)

@host_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """Host dashboard with listings, bookings, and NID upload/status"""
    if current_user.role not in ['host', 'admin']:
        flash('Access denied. Host privileges required.', 'danger')
        return redirect(url_for('public.index'))

    # NID upload logic (POST)
    if request.method == 'POST' and 'nid_file' in request.files:
        file = request.files['nid_file']
        if file.filename == '':
            flash('No file selected.', 'danger')
        elif file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'pdf'}):
            filename = secure_filename(f"nid_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
            nid_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'nid_host_uploads')
            os.makedirs(nid_folder, exist_ok=True)
            filepath = os.path.join(nid_folder, filename)
            file.save(filepath)
            current_user.nid_filename = filename
            db.session.commit()
            flash('NID uploaded successfully! It will be reviewed by admin for verification.', 'success')
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, or PDF files only.', 'danger')

    # Get host's listings
    listings = Listing.query.filter_by(user_id=current_user.id).order_by(desc(Listing.created_at)).all()
    # Get bookings for host's listings
    listing_ids = [listing.id for listing in listings]
    bookings = []
    if listing_ids:
        bookings = Booking.query.filter(Booking.listing_id.in_(listing_ids)).order_by(desc(Booking.created_at)).limit(10).all()
    # Calculate statistics
    total_listings = len(listings)
    approved_listings = len([l for l in listings if l.status == ListingStatus.APPROVED])
    pending_listings = len([l for l in listings if l.status == ListingStatus.PENDING_APPROVAL])
    total_bookings = len(bookings)
    return render_template('host/host_dashboard.html',
                         listings=listings,
                         bookings=bookings,
                         total_listings=total_listings,
                         approved_listings=approved_listings,
                         pending_listings=pending_listings,
                         total_bookings=total_bookings)

@host_bp.route('/add-listing', methods=['GET', 'POST'])
@login_required
def add_listing():
    """Add a new listing"""
    if current_user.role not in ['host', 'admin']:
        flash('Access denied. Host privileges required.', 'danger')
        return redirect(url_for('public.index'))
    
    form = ListingForm()
    if form.validate_on_submit():
        listing = Listing(
            title=form.title.data,
            description=form.description.data,
            location=form.location.data,
            price_per_night=form.price_per_night.data,
            guest_capacity=form.guest_capacity.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            house_rules=form.house_rules.data,
            user_id=current_user.id,
            status=ListingStatus.PENDING_APPROVAL
        )
        
        # Handle image upload
        if form.image.data:
            image_filename = save_image(form.image.data, 'listings')
            listing.image_filename = image_filename
        
        db.session.add(listing)
        db.session.commit()
        
        flash('Listing added successfully! It will be reviewed by admin before approval.', 'success')
        return redirect(url_for('host.dashboard'))
    
    return render_template('listings/add_listing.html', form=form)

@host_bp.route('/edit-listing/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_listing(id):
    """Edit an existing listing"""
    listing = Listing.query.get_or_404(id)
    
    if listing.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied. You can only edit your own listings.', 'danger')
        return redirect(url_for('host.dashboard'))
    
    form = ListingForm(obj=listing)
    if form.validate_on_submit():
        listing.title = form.title.data
        listing.description = form.description.data
        listing.location = form.location.data
        listing.price_per_night = form.price_per_night.data
        listing.guest_capacity = form.guest_capacity.data
        listing.bedrooms = form.bedrooms.data
        listing.bathrooms = form.bathrooms.data
        listing.house_rules = form.house_rules.data
        
        # Handle image upload
        if form.image.data:
            # Delete old image if exists
            if listing.image_filename:
                delete_image(listing.image_filename, 'listings')
            
            image_filename = save_image(form.image.data, 'listings')
            listing.image_filename = image_filename
        
        # Reset status to pending if admin is editing
        if current_user.role == 'admin':
            listing.status = ListingStatus.PENDING_APPROVAL
        
        db.session.commit()
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('host.dashboard'))
    
    return render_template('listings/edit_listing.html', form=form, listing=listing)

@host_bp.route('/my-listings')
@login_required
def my_listings():
    """View host's listings"""
    if current_user.role not in ['host', 'admin']:
        flash('Access denied. Host privileges required.', 'danger')
        return redirect(url_for('public.index'))
    
    page = request.args.get('page', 1, type=int)
    listings_query = Listing.query.filter_by(user_id=current_user.id)
    pagination = listings_query.order_by(desc(Listing.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('host/my_listings.html', pagination=pagination)

@host_bp.route('/bookings')
@login_required
def bookings():
    """View bookings for host's listings"""
    if current_user.role not in ['host', 'admin']:
        flash('Access denied. Host privileges required.', 'danger')
        return redirect(url_for('public.index'))
    
    # Get host's listing IDs
    listing_ids = [listing.id for listing in Listing.query.filter_by(user_id=current_user.id).all()]
    
    if not listing_ids:
        return render_template('host/host_bookings.html', pagination=None)
    
    page = request.args.get('page', 1, type=int)
    bookings_query = Booking.query.filter(Booking.listing_id.in_(listing_ids))
    pagination = bookings_query.order_by(desc(Booking.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('host/host_bookings.html', pagination=pagination)

@host_bp.route('/approve-booking/<int:booking_id>')
@login_required
def approve_booking(booking_id):
    """Approve a booking request"""
    booking = Booking.query.get_or_404(booking_id)
    listing = Listing.query.get_or_404(booking.listing_id)
    
    if listing.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('host.bookings'))
    
    booking.status = BookingStatus.CONFIRMED
    db.session.commit()
    flash('Booking approved successfully!', 'success')
    return redirect(url_for('host.bookings'))

@host_bp.route('/reject-booking/<int:booking_id>')
@login_required
def reject_booking(booking_id):
    """Reject a booking request"""
    booking = Booking.query.get_or_404(booking_id)
    listing = Listing.query.get_or_404(booking.listing_id)
    
    if listing.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('host.bookings'))
    
    booking.status = BookingStatus.CANCELLED
    db.session.commit()
    flash('Booking rejected.', 'info')
    return redirect(url_for('host.bookings'))

@host_bp.route('/upload-nid', methods=['GET', 'POST'])
@login_required
def upload_nid():
    """Upload NID for host verification"""
    if current_user.role not in ['host', 'admin']:
        flash('Access denied. Host privileges required.', 'danger')
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        if 'nid_file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        file = request.files['nid_file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'pdf'}):
            filename = secure_filename(f"nid_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'nid_host_uploads', filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            file.save(filepath)
            
            # Update user's NID filename
            current_user.nid_filename = filename
            db.session.commit()
            
            flash('NID uploaded successfully! It will be reviewed by admin for verification.', 'success')
            return redirect(url_for('host.dashboard'))
        else:
            flash('Invalid file type. Please upload PNG, JPG, JPEG, or PDF files only.', 'danger')
    
    return render_template('host/host_upload_nid.html')

@host_bp.route('/delete-listing/<int:id>', methods=['POST'])
@login_required
def delete_listing(id):
    """Delete a listing"""
    listing = Listing.query.get_or_404(id)
    
    if listing.user_id != current_user.id and current_user.role != 'admin':
        flash('Access denied. You can only delete your own listings.', 'danger')
        return redirect(url_for('host.dashboard'))
    
    # Delete associated bookings
    Booking.query.filter_by(listing_id=listing.id).delete()
    
    # Delete listing image if exists
    if listing.image_filename:
        delete_image(listing.image_filename, 'listings')
    
    db.session.delete(listing)
    db.session.commit()
    
    flash('Listing deleted successfully!', 'success')
    return redirect(url_for('host.dashboard'))

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions 