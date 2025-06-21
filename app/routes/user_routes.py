from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, date
from ..models import User, Listing, Booking, Review, BookingStatus
from ..forms import BookingForm, ReviewForm
from .. import db

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Get user's bookings
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).limit(5).all()
    
    # Get user's reviews
    user_reviews = Review.query.filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).limit(5).all()
    
    return render_template('user/profile.html', 
                         user=current_user,
                         recent_bookings=user_bookings,
                         recent_reviews=user_reviews)

@user_bp.route('/my-bookings')
@login_required
def my_bookings():
    """User's bookings with pagination"""
    page = request.args.get('page', 1, type=int)
    pagination = Booking.query.filter_by(user_id=current_user.id)\
        .order_by(Booking.created_at.desc())\
        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('user/my_bookings.html', pagination=pagination)

@user_bp.route('/book-listing/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def book_listing(listing_id):
    """Book a listing"""
    listing = Listing.query.get_or_404(listing_id)
    
    # Check if listing is approved
    if listing.status.value != 'APPROVED':
        flash('This listing is not available for booking.', 'error')
        return redirect(url_for('listings.listing_detail', id=listing_id))
    
    # Check if user is trying to book their own listing
    if listing.user_id == current_user.id:
        flash('You cannot book your own listing.', 'error')
        return redirect(url_for('listings.listing_detail', id=listing_id))
    
    form = BookingForm()
    
    if form.validate_on_submit():
        # Parse dates
        try:
            check_in_date = datetime.strptime(form.check_in_date.data, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(form.check_out_date.data, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format.', 'error')
            return render_template('user/book_listing.html', form=form, listing=listing, today=date.today().isoformat())
        
        # Validate dates
        today = date.today()
        if check_in_date < today:
            flash('Check-in date cannot be in the past.', 'error')
            return render_template('user/book_listing.html', form=form, listing=listing, today=today.isoformat())
        
        if check_out_date <= check_in_date:
            flash('Check-out date must be after check-in date.', 'error')
            return render_template('user/book_listing.html', form=form, listing=listing, today=today.isoformat())
        
        # Validate guest count
        if form.guest_count.data > listing.guest_capacity:
            flash(f'Maximum {listing.guest_capacity} guests allowed for this property.', 'error')
            return render_template('user/book_listing.html', form=form, listing=listing, today=today.isoformat())
        
        # Check for existing bookings in the same date range
        existing_booking = Booking.query.filter(
            Booking.listing_id == listing_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            Booking.check_in_date < check_out_date,
            Booking.check_out_date > check_in_date
        ).first()
        
        if existing_booking:
            flash('This property is not available for the selected dates.', 'error')
            return render_template('user/book_listing.html', form=form, listing=listing, today=today.isoformat())
        
        # Calculate total price
        nights = (check_out_date - check_in_date).days
        total_price = nights * listing.price_per_night
        
        # Create booking
        new_booking = Booking(
            user_id=current_user.id,
            listing_id=listing_id,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            guest_count=form.guest_count.data,
            total_price=total_price,
            special_requests=form.special_requests.data,
            status=BookingStatus.PENDING
        )
        
        try:
            db.session.add(new_booking)
            db.session.commit()
            flash('Booking request sent successfully! The host will review and confirm your booking.', 'success')
            return redirect(url_for('user.my_bookings'))
        except Exception as e:
            db.session.rollback()
            flash('Error creating booking. Please try again.', 'error')
    
    return render_template('user/book_listing.html', form=form, listing=listing, today=date.today().isoformat())

@user_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Ensure user owns this booking
    if booking.user_id != current_user.id:
        flash('Access denied. You can only cancel your own bookings.', 'error')
        return redirect(url_for('user.my_bookings'))
    
    # Check if booking can be cancelled
    if booking.status.value not in ['PENDING', 'CONFIRMED']:
        flash('This booking cannot be cancelled.', 'error')
        return redirect(url_for('user.my_bookings'))
    
    try:
        booking.status = BookingStatus.CANCELLED
        db.session.commit()
        flash('Booking cancelled successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error cancelling booking. Please try again.', 'error')
    
    return redirect(url_for('user.my_bookings'))

@user_bp.route('/add-review/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def add_review(listing_id):
    """Add a review for a listing"""
    listing = Listing.query.get_or_404(listing_id)
    
    # Check if user has stayed at this listing
    booking = Booking.query.filter_by(
        user_id=current_user.id,
        listing_id=listing_id,
        status=BookingStatus.COMPLETED
    ).first()
    
    if not booking:
        flash('You can only review listings where you have completed a stay.', 'error')
        return redirect(url_for('listings.listing_detail', id=listing_id))
    
    # Check if user already reviewed this listing
    existing_review = Review.query.filter_by(
        user_id=current_user.id,
        listing_id=listing_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this listing.', 'error')
        return redirect(url_for('listings.listing_detail', id=listing_id))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        new_review = Review(
            user_id=current_user.id,
            listing_id=listing_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        
        try:
            db.session.add(new_review)
            db.session.commit()
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('listings.listing_detail', id=listing_id))
        except Exception as e:
            db.session.rollback()
            flash('Error submitting review. Please try again.', 'error')
    
    return render_template('user/add_review.html', form=form, listing=listing)

@user_bp.route('/edit-review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    """Edit a review"""
    review = Review.query.get_or_404(review_id)
    
    # Ensure user owns this review
    if review.user_id != current_user.id:
        flash('Access denied. You can only edit your own reviews.', 'error')
        return redirect(url_for('listings.listing_detail', id=review.listing_id))
    
    form = ReviewForm(obj=review)
    
    if form.validate_on_submit():
        review.rating = form.rating.data
        review.comment = form.comment.data
        
        try:
            db.session.commit()
            flash('Review updated successfully!', 'success')
            return redirect(url_for('listings.listing_detail', id=review.listing_id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating review. Please try again.', 'error')
    
    return render_template('user/edit_review.html', form=form, review=review)

@user_bp.route('/delete-review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """Delete a review"""
    review = Review.query.get_or_404(review_id)
    
    # Ensure user owns this review
    if review.user_id != current_user.id:
        flash('Access denied. You can only delete your own reviews.', 'error')
        return redirect(url_for('listings.listing_detail', id=review.listing_id))
    
    listing_id = review.listing_id
    
    try:
        db.session.delete(review)
        db.session.commit()
        flash('Review deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting review. Please try again.', 'error')
    
    return redirect(url_for('listings.listing_detail', id=listing_id))

@user_bp.route('/send-message/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    """Send a message to another user"""
    recipient = User.query.get_or_404(recipient_id)
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            # Handle message sending logic here
            flash('Message sent successfully!', 'success')
            return redirect(url_for('messages.conversation', user_id=recipient_id))
    
    return render_template('messages/send_message.html', recipient=recipient) 