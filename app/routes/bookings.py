from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import User, Listing, Booking, ListingImage
from datetime import datetime, date

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/debug-user')
@login_required
def debug_user():
    """Debug route to check current user and their bookings"""
    user_bookings = Booking.get_by_user(current_user.id)
    return jsonify({
        'user_id': current_user.id,
        'user_name': current_user.name,
        'user_email': current_user.email,
        'user_type': current_user.user_type,
        'bookings_count': len(user_bookings),
        'bookings': [{'id': b.id, 'status': b.status, 'listing_id': b.listing_id} for b in user_bookings]
    })

@bookings_bp.route('/book/<int:listing_id>')
@login_required
def book_listing(listing_id):
    """Display booking form for a listing"""
    try:
        listing = Listing.get(listing_id)
        
        if not listing:
            flash('Listing not found.', 'error')
            return redirect(url_for('main.index'))
        
        if listing.host_id == current_user.id:
            flash('You cannot book your own listing.', 'error')
            return redirect(url_for('listings.listing_detail', listing_id=listing_id))
        
        # Get host and images
        host = User.get(listing.host_id)
        unavailable_dates = listing.get_unavailable_dates()
        listing_images = ListingImage.get_by_listing(listing_id)
        
        # Prepare listing data
        listing_data = {
            'id': listing.id,
            'title': listing.title,
            'location': listing.location,
            'price': listing.price,
            'price_per_night': listing.price,
            'rating': listing.rating,
            'reviews': listing.reviews_count,
            'images': [img.image_filename for img in listing_images] if listing_images else ['demo_listing_1.jpg'],
            'image': listing_images[0].image_filename if listing_images else 'demo_listing_1.jpg',
            'type': listing.property_type.title(),
            'guests': listing.guests,
            'room_type': listing.room_type,
            'description': listing.description,
            'amenities': listing.amenities,
            'host': {
                'name': host.full_name if host else 'Unknown Host',
                'avatar': 'user-gear.png'
            },
            'unavailable_dates': unavailable_dates
        }
        
        return render_template('guest/booking.html', listing=listing_data)
    
    except Exception as e:
        flash('Error loading booking page.', 'error')
        return redirect(url_for('main.index'))

@bookings_bp.route('/book/<int:listing_id>/confirm', methods=['POST'])
@login_required
def confirm_booking(listing_id):
    """Confirm a booking"""
    try:
        listing = Listing.get(listing_id)
        
        if not listing:
            flash('Listing not found.', 'error')
            return redirect(url_for('main.index'))
        
        if listing.host_id == current_user.id:
            flash('You cannot book your own listing.', 'error')
            return redirect(url_for('listings.listing_detail', listing_id=listing_id))
        
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        guests = request.form.get('guests')
        
        # Validation
        errors = []
        
        try:
            checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()
            checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()
            
            if checkin_date < date.today():
                errors.append('Check-in date cannot be in the past.')
            
            if checkout_date <= checkin_date:
                errors.append('Check-out date must be after check-in date.')
            
            if not listing.is_available(checkin_date, checkout_date):
                errors.append('These dates are not available.')
            
        except ValueError:
            errors.append('Please enter valid dates.')
        
        try:
            guest_count = int(guests)
            if guest_count <= 0:
                errors.append('Guest count must be at least 1.')
            if guest_count > listing.guests:
                errors.append(f'This listing can accommodate maximum {listing.guests} guests.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid guest count.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('bookings.book_listing', listing_id=listing_id))
        
        # Create booking
        booking = Booking.create(
            listing_id=listing_id,
            user_id=current_user.id,
            check_in=checkin_date,
            check_out=checkout_date,
            guests=guest_count
        )
        
        if booking:
            flash('Booking request submitted successfully! Waiting for host approval.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Failed to create booking. Please try again.', 'error')
            return redirect(url_for('bookings.book_listing', listing_id=listing_id))
    
    except Exception as e:
        flash('Error processing booking.', 'error')
        return redirect(url_for('bookings.book_listing', listing_id=listing_id))

@bookings_bp.route('/my-bookings')
@login_required
def my_bookings():
    """View user's bookings with real-time updates"""
    try:
        # Debug: Print current user info and authentication status
        print(f"DEBUG: Current user ID: {current_user.id}, Name: {current_user.name}, Email: {current_user.email}")
        print(f"DEBUG: User authenticated: {current_user.is_authenticated}")
        print(f"DEBUG: User type: {getattr(current_user, 'user_type', 'unknown')}")
        print(f"DEBUG: Session data: {dict(request.cookies)}")
        
        # Update expired booking statuses first
        try:
            Booking.update_expired_statuses()
        except Exception as e:
            print(f"DEBUG: Error updating expired statuses: {e}")
            # Continue without updating expired statuses
        
        # Get all user bookings
        try:
            bookings = Booking.get_by_user(current_user.id)
            print(f"DEBUG: Found {len(bookings)} bookings for user {current_user.id}")
        except Exception as e:
            print(f"DEBUG: Error getting user bookings: {e}")
            bookings = []
        
        # Get upcoming check-ins and recently completed stays
        try:
            upcoming_checkins = Booking.get_upcoming_checkins(current_user.id, days_ahead=7)
        except Exception as e:
            print(f"DEBUG: Error getting upcoming checkins: {e}")
            upcoming_checkins = []
            
        try:
            recently_completed = Booking.get_recently_completed(current_user.id, days_back=30)
        except Exception as e:
            print(f"DEBUG: Error getting recently completed: {e}")
            recently_completed = []
        
        # Enrich bookings with listing information and real-time data
        enriched_bookings = []
        total_spent = 0
        
        for booking in bookings:
            try:
                listing = Listing.get(booking.listing_id)
                host = User.get(listing.host_id) if listing else None
                confirmed_by_user = User.get(booking.confirmed_by) if booking.confirmed_by else None
            except Exception as e:
                print(f"DEBUG: Error getting listing/user data for booking {booking.id}: {e}")
                listing = None
                host = None
                confirmed_by_user = None
            
            # Skip this booking if we can't get basic data
            if not listing:
                print(f"DEBUG: Skipping booking {booking.id} - no listing data")
                continue
            
            # Check if user has already reviewed this booking
            has_reviewed = False
            try:
                if hasattr(booking, 'can_review') and booking.can_review:
                    from app.models import Review
                    has_reviewed = Review.has_user_reviewed_booking(current_user.id, booking.id)
            except Exception as e:
                print(f"DEBUG: Error checking review status for booking {booking.id}: {e}")
                has_reviewed = False
            
            # Calculate total spent for confirmed/completed bookings
            try:
                if booking.status in ['confirmed', 'completed']:
                    total_spent += float(booking.total_price or 0)
            except Exception as e:
                print(f"DEBUG: Error calculating total spent for booking {booking.id}: {e}")
                # Continue with the booking even if price calculation fails
            
            try:
                booking_data = {
                    'id': booking.id,
                    'booking_id': booking.booking_id,
                    'user_id': booking.user_id,
                    'listing_id': booking.listing_id,
                    'check_in': booking.check_in,
                    'check_out': booking.check_out,
                    'guests': booking.guests,
                    'total_price': booking.total_price,
                    'total_amount': booking.total_price,  # Alias for template
                    'status': booking.status,
                    'created_at': booking.created_at,
                    'confirmed_by': booking.confirmed_by,
                    'confirmed_at': booking.confirmed_at,
                    'confirmed_by_name': confirmed_by_user.full_name if confirmed_by_user else None,
                    
                    # Real-time properties - with safe property access
                    'is_checkin_today': getattr(booking, 'is_checkin_today', False),
                    'is_checkout_today': getattr(booking, 'is_checkout_today', False),
                    'days_until_checkin': getattr(booking, 'days_until_checkin', None),
                    'days_until_checkout': getattr(booking, 'days_until_checkout', None),
                    'stay_duration': getattr(booking, 'stay_duration', None),
                    'can_review': getattr(booking, 'can_review', False),
                    'has_reviewed': has_reviewed,
                    
                    'listing': {
                        'id': getattr(listing, 'id', None) if listing else None,
                        'title': getattr(listing, 'title', 'Unknown Listing') if listing else 'Unknown Listing',
                        'location': getattr(listing, 'location', '') if listing else '',
                        'image': 'demo_listing_1.jpg',
                        'host_name': getattr(host, 'full_name', 'Unknown Host') if host else 'Unknown Host'
                    } if listing else None
                }
                enriched_bookings.append(booking_data)
            except Exception as e:
                print(f"DEBUG: Error creating booking data for booking {booking.id}: {e}")
                # Continue with next booking
                continue
        
        # Sort by creation date
        try:
            enriched_bookings.sort(key=lambda x: x.get('created_at', datetime.now()), reverse=True)
        except Exception as e:
            print(f"DEBUG: Error sorting bookings: {e}")
            # Continue without sorting
        
        # Debug: Print final data being passed to template
        print(f"DEBUG: Passing to template - Bookings: {len(enriched_bookings)}, Total spent: {total_spent}")
        print(f"DEBUG: Upcoming checkins: {len(upcoming_checkins)}, Recently completed: {len(recently_completed)}")
        print(f"DEBUG: About to render template with {len(enriched_bookings)} bookings")
        
        # Check if we're actually going to render the template
        if len(enriched_bookings) == 0:
            print("DEBUG: WARNING - No enriched bookings to pass to template!")
        
        return render_template('guest/my_bookings.html', 
                             bookings=enriched_bookings, 
                             user=current_user,
                             total_spent=total_spent,
                             upcoming_checkins=upcoming_checkins,
                             recently_completed=recently_completed)
    
    except Exception as e:
        print(f"DEBUG: EXCEPTION OCCURRED: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        flash('Error loading bookings.', 'error')
        return render_template('guest/my_bookings.html', 
                             bookings=[], 
                             user=current_user,
                             total_spent=0,
                             upcoming_checkins=[],
                             recently_completed=[])

@bookings_bp.route('/host-bookings')
@login_required
def host_bookings():
    """View bookings for host's listings"""
    try:
        if current_user.user_type != 'host':
            flash('Access denied. Host privileges required.', 'error')
            return redirect(url_for('main.dashboard'))
            
        # Get all bookings for this host's listings
        host_bookings = Booking.get_by_host(current_user.id)
        
        enriched_bookings = []
        for booking in host_bookings:
            guest = User.get(booking.guest_id) if booking.guest_id else None
            listing = Listing.get(booking.listing_id) if booking.listing_id else None
            
            booking_data = {
                'id': booking.id,
                'guest_name': guest.full_name if guest else 'Unknown Guest',
                'guest_email': guest.email if guest else '',
                'listing_title': listing.title if listing else 'Unknown Listing',
                'listing_location': listing.location if listing else '',
                'check_in': booking.check_in,
                'check_out': booking.check_out,
                'guests': booking.guests,
                'total_price': booking.total_price,
                'status': booking.status,
                'created_at': booking.created_at,
                'special_requests': booking.special_requests,
                'listing': {
                    'id': listing.id if listing else None,
                    'title': listing.title if listing else 'Unknown Listing',
                    'image': 'demo_listing_1.jpg'
                } if listing else None
            }
            enriched_bookings.append(booking_data)
        
        # Sort by creation date
        enriched_bookings.sort(key=lambda x: x['created_at'], reverse=True)
        
        return render_template('host/host_bookings.html', bookings=enriched_bookings, user=current_user)
    
    except Exception as e:
        flash('Error loading host bookings.', 'error')
        return render_template('host/host_bookings.html', bookings=[], user=current_user)

@bookings_bp.route('/review-form/<int:booking_id>')
@login_required
def review_form(booking_id):
    """Show review form for a completed stay"""
    try:
        # Get the booking
        booking = Booking.get(booking_id)
        if not booking:
            flash('Booking not found.', 'error')
            return redirect(url_for('bookings.my_bookings'))
        
        # Verify the booking belongs to the current user
        if booking.user_id != current_user.id:
            flash('Access denied.', 'error')
            return redirect(url_for('bookings.my_bookings'))
        
        # Check if user can review this booking
        if not booking.can_review:
            flash('This booking cannot be reviewed yet.', 'error')
            return redirect(url_for('bookings.my_bookings'))
        
        # Check if user has already reviewed this booking
        from app.models import Review
        if Review.has_user_reviewed_booking(current_user.id, int(booking_id)):
            flash('You have already reviewed this stay.', 'info')
            return redirect(url_for('bookings.my_bookings'))
        
        # Get listing information
        from app.models import Listing
        listing = Listing.get(booking.listing_id)
        
        # Enrich booking with listing data
        booking.listing = listing
        
        return render_template('guest/review_form.html', booking=booking, user=current_user)
        
    except Exception as e:
        flash('Error loading review form.', 'error')
        return redirect(url_for('bookings.my_bookings'))

@bookings_bp.route('/submit-review', methods=['POST'])
@login_required
def submit_review():
    """Submit a review for a completed stay"""
    try:
        booking_id = request.form.get('booking_id')
        rating = request.form.get('rating')
        comment = request.form.get('comment')
        
        if not all([booking_id, rating, comment]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        # Get the booking
        booking = Booking.get(int(booking_id))
        if not booking:
            return jsonify({'success': False, 'message': 'Booking not found'})
        
        # Verify the booking belongs to the current user
        if booking.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Access denied'})
        
        # Check if user can review this booking
        if not booking.can_review:
            return jsonify({'success': False, 'message': 'This booking cannot be reviewed yet'})
        
        # Check if user has already reviewed this booking
        from app.models import Review
        if Review.has_user_reviewed_booking(current_user.id, int(booking_id)):
            return jsonify({'success': False, 'message': 'You have already reviewed this stay'})
        
        # Create the review
        review = Review.create(
            listing_id=booking.listing_id,
            user_id=current_user.id,
            rating=float(rating),
            comment=comment,
            booking_id=int(booking_id)
        )
        
        if review:
            return jsonify({'success': True, 'message': 'Review submitted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to submit review'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred while submitting review'})

@bookings_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    """Cancel a booking"""
    try:
        booking = Booking.get(booking_id)
        if not booking:
            return jsonify({'success': False, 'message': 'Booking not found'})
        
        # Verify the booking belongs to the current user
        if booking.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Access denied'})
        
        # Only allow cancellation of pending or confirmed bookings
        if booking.status not in ['pending', 'confirmed']:
            return jsonify({'success': False, 'message': 'This booking cannot be cancelled'})
        
        # Cancel the booking
        if booking.cancel():
            return jsonify({'success': True, 'message': 'Booking cancelled successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to cancel booking'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred while cancelling booking'})
