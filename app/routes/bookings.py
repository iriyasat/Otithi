from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Listing, Booking, ListingImage
from datetime import datetime, date

bookings_bp = Blueprint('bookings', __name__)

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
            'bedrooms': listing.bedrooms,
            'bathrooms': listing.bathrooms,
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
    """View user's bookings"""
    try:
        bookings = Booking.get_by_user(current_user.id)
        
        # Enrich bookings with listing information
        enriched_bookings = []
        for booking in bookings:
            listing = Listing.get(booking.listing_id)
            host = User.get(listing.host_id) if listing else None
            confirmed_by_user = User.get(booking.confirmed_by) if booking.confirmed_by else None
            
            booking_data = {
                'booking_id': booking.booking_id,
                'user_id': booking.user_id,
                'listing_id': booking.listing_id,
                'check_in': booking.check_in,
                'check_out': booking.check_out,
                'total_price': booking.total_price,
                'status': booking.status,
                'created_at': booking.created_at,
                'confirmed_by': booking.confirmed_by,
                'confirmed_at': booking.confirmed_at,
                'confirmed_by_name': confirmed_by_user.full_name if confirmed_by_user else None,
                'listing': {
                    'id': listing.id if listing else None,
                    'title': listing.title if listing else 'Unknown Listing',
                    'location': listing.location if listing else '',
                    'image': 'demo_listing_1.jpg',
                    'host_name': host.full_name if host else 'Unknown Host'
                } if listing else None
            }
            enriched_bookings.append(booking_data)
        
        # Sort by creation date
        enriched_bookings.sort(key=lambda x: x['created_at'], reverse=True)
        
        return render_template('guest/my_bookings.html', bookings=enriched_bookings, user=current_user)
    
    except Exception as e:
        flash('Error loading bookings.', 'error')
        return render_template('guest/my_bookings.html', bookings=[], user=current_user)

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
