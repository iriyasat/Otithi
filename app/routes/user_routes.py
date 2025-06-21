"""
User routes for profile, bookings, and booking functionality.
"""

from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import desc
from ..models import User, Booking, BookingStatus, Listing, ListingStatus, Review
from ..forms import BookingForm, UserProfileForm
from .. import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    booking_count = Booking.query.filter_by(guest_id=current_user.id).count()
    listing_count = 0
    if current_user.role in ['host', 'admin']:
        listing_count = Listing.query.filter_by(user_id=current_user.id).count()
    
    return render_template('user/profile.html', 
                         booking_count=booking_count,
                         listing_count=listing_count)

@user_bp.route('/book-listing/<int:id>', methods=['GET', 'POST'])
@login_required
def book_listing(id):
    """Book a listing"""
    listing = Listing.query.get_or_404(id)
    
    if listing.status != ListingStatus.APPROVED:
        flash('This listing is not available for booking.', 'warning')
        return redirect(url_for('listings.listing_detail', id=id))
    
    if listing.user_id == current_user.id:
        flash('You cannot book your own listing.', 'warning')
        return redirect(url_for('listings.listing_detail', id=id))
    
    form = BookingForm()
    if form.validate_on_submit():
        # Simple validation
        if form.check_in_date.data < date.today():
            flash('Check-in date cannot be in the past.', 'danger')
            return render_template('user/book_listing.html', form=form, listing=listing)
        
        if form.check_out_date.data <= form.check_in_date.data:
            flash('Check-out date must be after check-in date.', 'danger')
            return render_template('user/book_listing.html', form=form, listing=listing)
        
        # Calculate total price (simple calculation)
        nights = (form.check_out_date.data - form.check_in_date.data).days
        total_price = float(listing.price_per_night) * nights
        
        booking = Booking(
            listing_id=listing.id,
            guest_id=current_user.id,
            check_in_date=form.check_in_date.data,
            check_out_date=form.check_out_date.data,
            guest_count=form.guest_count.data,
            total_price=total_price,
            special_requests=form.special_requests.data,
            status=BookingStatus.PENDING
        )
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Booking request submitted successfully! The host will review your request.', 'success')
        return redirect(url_for('user.my_bookings'))
    
    return render_template('user/book_listing.html', form=form, listing=listing)

@user_bp.route('/my-bookings')
@login_required
def my_bookings():
    """View user's bookings"""
    page = request.args.get('page', 1, type=int)
    bookings_query = Booking.query.filter_by(guest_id=current_user.id)
    pagination = bookings_query.order_by(desc(Booking.created_at)).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('user/my_bookings.html', pagination=pagination)

@user_bp.route('/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    """Update user profile"""
    form = UserProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # Check if username is already taken by another user
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Username already exists. Please choose a different one.', 'danger')
            return render_template('user/profile.html', form=form)
        
        # Check if email is already taken by another user
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user and existing_user.id != current_user.id:
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template('user/profile.html', form=form)
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        
        # Handle profile image upload
        if form.profile_image.data:
            from ..helpers import save_image, delete_image
            # Delete old image if exists
            if current_user.profile_picture:
                delete_image(current_user.profile_picture, 'profiles')
            
            image_filename = save_image(form.profile_image.data, 'profiles')
            current_user.profile_picture = image_filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('user/profile.html', form=form)

@user_bp.route('/cancel-booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.guest_id != current_user.id:
        flash('Access denied. You can only cancel your own bookings.', 'danger')
        return redirect(url_for('user.my_bookings'))
    
    if booking.status != BookingStatus.PENDING:
        flash('This booking cannot be cancelled.', 'warning')
        return redirect(url_for('user.my_bookings'))
    
    booking.status = BookingStatus.CANCELLED
    db.session.commit()
    
    flash('Booking cancelled successfully!', 'success')
    return redirect(url_for('user.my_bookings'))

@user_bp.route('/add-review/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def add_review(booking_id):
    """Add a review for a booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.guest_id != current_user.id:
        flash('Access denied. You can only review your own bookings.', 'danger')
        return redirect(url_for('user.my_bookings'))
    
    if booking.status != BookingStatus.CONFIRMED:
        flash('You can only review confirmed bookings.', 'warning')
        return redirect(url_for('user.my_bookings'))
    
    # Check if review already exists
    existing_review = Review.query.filter_by(
        booking_id=booking_id,
        reviewer_id=current_user.id,
        reviewed_by_host=False
    ).first()
    
    if existing_review:
        flash('You have already reviewed this booking.', 'warning')
        return redirect(url_for('user.my_bookings'))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()
        
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a valid rating (1-5).', 'danger')
            return redirect(url_for('user.add_review', booking_id=booking_id))
        
        if not comment:
            flash('Please provide a comment.', 'danger')
            return redirect(url_for('user.add_review', booking_id=booking_id))
        
        review = Review(
            listing_id=booking.listing_id,
            booking_id=booking_id,
            reviewer_id=current_user.id,
            rating=rating,
            comment=comment,
            reviewed_by_host=False
        )
        
        db.session.add(review)
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('user.my_bookings'))
    
    return render_template('user/add_review.html', booking=booking) 