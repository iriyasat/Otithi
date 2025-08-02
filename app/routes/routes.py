from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Listing, Booking, Review
from app.location_models import Location, ListingImage
from datetime import datetime, date
import os
import uuid
from werkzeug.utils import secure_filename

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # Get listings from database
    listings = Listing.get_all()
    
    # Use all listings (these appear to be real listings with real data)
    real_listings = listings
    
    # Convert to format expected by template (limit to 5 for homepage)
    listings_data = []
    for listing in real_listings[:5]:  # Only show first 5 listings on homepage
        # Get listing images
        listing_images = ListingImage.get_by_listing(listing.id)
        
        # Calculate real-time rating and review count
        listing_reviews = Review.get_by_listing(listing.id)
        avg_rating = 0.0
        review_count = len(listing_reviews)
        if listing_reviews:
            total_rating = sum(review.rating for review in listing_reviews)
            avg_rating = round(total_rating / review_count, 1)
        
        listings_data.append({
            'id': listing.id,
            'title': listing.title,
            'location': listing.location,
            'price': listing.price,
            'rating': avg_rating,
            'reviews': review_count,
            'image': listing_images[0].image_filename if listing_images else 'demo_listing_1.jpg',  # Use real image or fallback
            'type': listing.property_type.title(),
            'guests': listing.guests,
            'bedrooms': listing.bedrooms,
            'bathrooms': listing.bathrooms
        })
    
    # Get recent reviews for the homepage
    all_reviews = Review.get_all()
    # Filter out any dummy reviews and get the most recent ones
    real_reviews = [review for review in all_reviews 
                   if hasattr(review, 'comment') and review.comment and 
                   not any(dummy_word in review.comment.lower() 
                          for dummy_word in ['test', 'demo', 'sample'])]
    
    # Get latest 6 reviews for display
    recent_reviews = sorted(real_reviews, key=lambda x: x.created_date, reverse=True)[:6]
    
    # Convert reviews to format expected by template
    reviews_data = []
    for review in recent_reviews:
        # Get guest name and listing title
        guest = User.get(review.user_id)
        listing = Listing.get(review.listing_id)
        
        reviews_data.append({
            'guest_name': guest.name if guest else 'Anonymous Guest',
            'rating': review.rating,
            'comment': review.comment,
            'created_at': review.created_date,
            'listing_title': listing.title if listing else 'Unknown Listing'
        })
    
    # Calculate hosting statistics from real data
    all_bookings = Booking.get_all() if hasattr(Booking, 'get_all') else []
    all_listings = Listing.get_all()
    
    # Use all listings for stats (these appear to be real listings, not dummy data)
    real_listings = all_listings
    
    # Calculate average rating from all listings
    ratings = [l.rating for l in real_listings if hasattr(l, 'rating') and l.rating > 0]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0
    
    # Get unique hosts from all listings
    unique_hosts = set()
    for listing in real_listings:
        if hasattr(listing, 'host_id') and listing.host_id:
            unique_hosts.add(listing.host_id)
    
    hosting_stats = {
        'total_listings': len(real_listings),
        'total_bookings': len(all_bookings),
        'avg_rating': avg_rating,
        'total_hosts': len(unique_hosts)
    }
    
    return render_template('index.html', 
                         listings=listings_data, 
                         reviews=reviews_data, 
                         hosting_stats=hosting_stats)

@bp.route('/explore')
def explore():
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Show 12 listings per page
    
    # Get all listings for explore page
    all_listings = Listing.get_all()
    
    # Calculate pagination
    total_listings = len(all_listings)
    total_pages = (total_listings + per_page - 1) // per_page  # Ceiling division
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    # Get listings for current page
    page_listings = all_listings[start_idx:end_idx]
    
    # Convert to format expected by template
    listings_data = []
    for listing in page_listings:
        # Get listing images
        listing_images = ListingImage.get_by_listing(listing.id)
        
        # Calculate real-time rating and review count
        listing_reviews = Review.get_by_listing(listing.id)
        avg_rating = 0.0
        review_count = len(listing_reviews)
        if listing_reviews:
            total_rating = sum(review.rating for review in listing_reviews)
            avg_rating = round(total_rating / review_count, 1)
        
        listings_data.append({
            'id': listing.id,
            'title': listing.title,
            'location': listing.location,
            'city': listing.city,
            'country': listing.country,
            'price': listing.price,
            'rating': avg_rating,
            'reviews': review_count,
            'image': listing_images[0].image_filename if listing_images else 'demo_listing_1.jpg',  # Use real image or fallback
            'type': listing.property_type.title(),
            'guests': listing.guests,
            'bedrooms': listing.bedrooms,
            'bathrooms': listing.bathrooms,
            'description': listing.description
        })
    
    # Pagination info
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_listings,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < total_pages else None,
        'pages': list(range(1, total_pages + 1))
    }
    
    return render_template('explore.html', listings=listings_data, pagination=pagination)

@bp.route('/search')
def search():
    query = request.args.get('query', '')
    location = request.args.get('location', '')
    checkin = request.args.get('checkin', '')
    checkout = request.args.get('checkout', '')
    guests = request.args.get('guests', '')
    
    # Get all listings and filter based on search criteria
    listings = Listing.get_all()
    
    # Filter by location if provided
    if location:
        listings = [l for l in listings if location.lower() in l.location.lower() or location.lower() in l.city.lower()]
    
    # Filter by availability if dates provided
    if checkin and checkout:
        try:
            checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()
            checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()
            listings = [l for l in listings if l.is_available(checkin_date, checkout_date)]
        except ValueError:
            pass
    
    # Filter by guest count if provided
    if guests:
        try:
            guest_count = int(guests)
            listings = [l for l in listings if l.guests >= guest_count]
        except ValueError:
            pass
    
    # Convert to template format
    listings_data = []
    for listing in listings:
        # Get listing images
        listing_images = ListingImage.get_by_listing(listing.id)
        
        # Calculate real-time rating and review count
        listing_reviews = Review.get_by_listing(listing.id)
        avg_rating = 0.0
        review_count = len(listing_reviews)
        if listing_reviews:
            total_rating = sum(review.rating for review in listing_reviews)
            avg_rating = round(total_rating / review_count, 1)
        
        listings_data.append({
            'id': listing.id,
            'title': listing.title,
            'location': listing.location,
            'price': listing.price,
            'rating': avg_rating,
            'reviews': review_count,
            'image': listing_images[0].image_filename if listing_images else 'demo_listing_1.jpg',
            'type': listing.property_type.title(),
            'guests': listing.guests,
            'bedrooms': listing.bedrooms,
            'bathrooms': listing.bathrooms,
            'price_per_night': listing.price  # Add for template compatibility
        })
    
    return render_template('host/search.html', 
                         listings=listings_data,
                         query=query, 
                         location=location,
                         checkin=checkin,
                         checkout=checkout,
                         guests=guests)

# Listing Routes

# Redirect singular /listing/ to plural /listings/ for better UX
@bp.route('/listing/<int:listing_id>')
def listing_redirect(listing_id):
    """Redirect singular /listing/ to plural /listings/ for consistency"""
    return redirect(url_for('main.listing_detail', listing_id=listing_id), code=301)

@bp.route('/listings/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.get(listing_id)
    
    if not listing:
        # Get available listings for helpful error message
        available_listings = Listing.get_all()
        error_html = f"""
        <div style="max-width: 600px; margin: 50px auto; padding: 20px; font-family: system-ui; text-align: center;">
            <h1 style="color: #dc3545; margin-bottom: 20px;">Listing Not Found</h1>
            <p style="font-size: 18px; color: #6c757d; margin-bottom: 30px;">
                Sorry, we couldn't find a listing with ID {listing_id}.
            </p>
            
            {f'''
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                <h3 style="color: #006a4e; margin-bottom: 15px;">Available Listings:</h3>
                <div style="display: grid; gap: 10px;">
                    {"".join([f'''
                    <div style="background: white; border: 1px solid #dee2e6; border-radius: 6px; padding: 15px;">
                        <h4 style="margin: 0 0 5px 0;">
                            <a href="/listings/{available_listing.id}" style="color: #006a4e; text-decoration: none;">
                                {available_listing.title}
                            </a>
                        </h4>
                        <p style="margin: 0; color: #6c757d; font-size: 14px;">
                            {available_listing.location} • ৳{available_listing.price}/night
                        </p>
                    </div>
                    ''' for available_listing in available_listings[:5]])}
                </div>
            </div>
            ''' if available_listings else '<p style="color: #6c757d;">No listings are currently available.</p>'}
            
            <div style="margin-top: 30px;">
                <a href="/" style="background: #006a4e; color: white, padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 500;">
                    ← Back to Home
                </a>
            </div>
        </div>
        """
        return error_html, 404
    
    # Get host information
    host = User.get(listing.host_id)
    
    # Get reviews
    reviews = Review.get_by_listing(listing_id)
    
    # Get unavailable dates for calendar
    unavailable_dates = listing.get_unavailable_dates()
    
    # Get listing images
    listing_images = ListingImage.get_by_listing(listing_id)
    
    # Calculate real rating and review count
    avg_rating = 0.0
    review_count = len(reviews)
    if reviews:
        total_rating = sum(review.rating for review in reviews)
        avg_rating = total_rating / review_count
    
    # Prepare listing data for template
    listing_data = {
        'id': listing.id,
        'listing_id': listing.id,  # Add this for template compatibility
        'title': listing.title,
        'location': listing.location,
        'address': listing.address,
        'city': listing.city,
        'country': listing.country,
        'price': listing.price,
        'price_per_night': listing.price,  # Add this for template compatibility
        'rating': avg_rating,
        'reviews': review_count,
        'images': [img.image_filename for img in listing_images] if listing_images else ['demo_listing_1.jpg'],
        'image': listing_images[0].image_filename if listing_images else 'demo_listing_1.jpg',  # First image for backward compatibility
        'type': listing.property_type.title(),
        'room_type': listing.property_type,  # Add this for template compatibility
        'guests': listing.guests,
        'max_guests': listing.guests,  # Add this for template compatibility
        'bedrooms': listing.bedrooms,
        'bathrooms': listing.bathrooms,
        'description': listing.description,
        'amenities': ','.join(listing.amenities) if listing.amenities else '',  # Convert list to string
        'latitude': listing.latitude,  # Add coordinates for potential map display
        'longitude': listing.longitude,
        'host': {
            'id': host.id if host else None,
            'name': host.full_name if host else 'Unknown Host',
            'avatar': host.profile_photo if host and host.profile_photo else 'user-gear.png',
            'joined': host.joined_date.year if host else '2023',
            'verified': host.verified if host else False,
            'bio': host.bio if host else ''
        },
        'unavailable_dates': unavailable_dates
    }
    
    return render_template('host/listing_detail.html', listing=listing_data, reviews=reviews)

@bp.route('/listings/<int:listing_id>/review', methods=['POST'])
@login_required
def add_review(listing_id):
    """Add a review for a listing"""
    # Check if listing exists
    listing = Listing.get(listing_id)
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Check if user is not the host
    if listing.host_id == current_user.id:
        flash('You cannot review your own listing.', 'error')
        return redirect(url_for('main.listing_detail', listing_id=listing_id))
    
    # Get form data
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    
    # Validate input
    if not rating or not comment:
        flash('Please provide both a rating and comment.', 'error')
        return redirect(url_for('main.listing_detail', listing_id=listing_id))
    
    try:
        rating = float(rating)
        if rating < 1 or rating > 5:
            flash('Rating must be between 1 and 5.', 'error')
            return redirect(url_for('main.listing_detail', listing_id=listing_id))
    except ValueError:
        flash('Invalid rating value.', 'error')
        return redirect(url_for('main.listing_detail', listing_id=listing_id))
    
    # Check if user has already reviewed this listing
    existing_reviews = Review.get_by_listing(listing_id)
    for review in existing_reviews:
        if review.user_id == current_user.id:
            flash('You have already reviewed this listing.', 'error')
            return redirect(url_for('main.listing_detail', listing_id=listing_id))
    
    # Create the review
    review = Review.create(listing_id, current_user.id, rating, comment)
    if review:
        flash('Your review has been added successfully!', 'success')
    else:
        flash('Failed to add review. Please try again.', 'error')
    
    return redirect(url_for('main.listing_detail', listing_id=listing_id))

@bp.route('/create_listing', methods=['GET', 'POST'])
@login_required
def create_listing():
    # Only hosts can create listings
    if current_user.user_type != 'host':
        flash('Only hosts can create listings.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        room_type = request.form.get('room_type', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        country = request.form.get('country', 'Bangladesh').strip()
        price_per_night = request.form.get('price_per_night')
        max_guests = request.form.get('max_guests')
        amenities = request.form.get('amenities', '').strip()
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        bedrooms = request.form.get('bedrooms')
        bathrooms = request.form.get('bathrooms')
        
        # Validation
        errors = []
        
        if not title:
            errors.append('Title is required.')
        
        if not description:
            errors.append('Description is required.')
        
        if not room_type:
            errors.append('Property type is required.')
            
        if room_type not in ['entire_place', 'private_room', 'shared_room']:
            errors.append('Invalid property type selected.')
        
        if not address:
            errors.append('Address is required.')
        
        if not city:
            errors.append('City is required.')
        
        if not latitude or not longitude:
            errors.append('Please select a location on the map.')
        
        try:
            price_per_night = float(price_per_night)
            if price_per_night <= 0:
                errors.append('Price per night must be greater than 0.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid price per night.')
        
        try:
            max_guests = int(max_guests)
            if max_guests <= 0:
                errors.append('Maximum guests must be at least 1.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid maximum guest count.')
            
        # Handle bedrooms and bathrooms based on room type
        if room_type == 'entire_place':
            # For entire place, get values from form and validate
            try:
                bedrooms = int(bedrooms)
                if bedrooms <= 0:
                    errors.append('Bedrooms must be at least 1.')
            except (ValueError, TypeError):
                errors.append('Please enter a valid number of bedrooms.')
                
            try:
                bathrooms = float(bathrooms)  # Allow 0.5, 1.5, etc.
                if bathrooms <= 0:
                    errors.append('Bathrooms must be at least 1.')
            except (ValueError, TypeError):
                errors.append('Please enter a valid number of bathrooms.')
        else:
            # For private room and shared room, always use 1
            bedrooms = 1
            bathrooms = 1
            
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            # Basic coordinate validation for Bangladesh region
            if not (20.5 <= latitude <= 26.5 and 88.0 <= longitude <= 93.0):
                # Log warning but don't block listing creation for international properties
                pass
        except (ValueError, TypeError):
            errors.append('Invalid coordinates. Please select a valid location on the map.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('host/create_listing.html')
        
        # Create location string
        location = f"{city}, {country}"
        
        # Handle file uploads first
        uploaded_files = []
        if 'listing_images' in request.files:
            files = request.files.getlist('listing_images')
            for i, file in enumerate(files):
                if file and file.filename:
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
                    
                    if file_ext not in allowed_extensions:
                        errors.append(f'Invalid file type for image {i+1}. Allowed types: PNG, JPG, JPEG, GIF, WEBP')
                        continue
                    
                    # Check file size (5MB limit)
                    file.seek(0, 2)  # Seek to end
                    file_size = file.tell()
                    file.seek(0)  # Reset to beginning
                    
                    if file_size > 5 * 1024 * 1024:  # 5MB
                        errors.append(f'Image {i+1} is too large. Maximum size is 5MB.')
                        continue
                    
                    uploaded_files.append((file, i + 1))
        
        if not uploaded_files:
            errors.append('At least one listing image is required.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('host/create_listing.html')
        
        # Create or find location
        try:
            location_obj = Location.find_or_create(
                address=address,
                city=city,
                country=country,
                latitude=latitude,
                longitude=longitude
            )
            
            if not location_obj:
                flash('Failed to create location. Please try again.', 'error')
                return render_template('host/create_listing.html')
        except Exception as e:
            flash('An error occurred while creating location. Please try again.', 'error')
            return render_template('host/create_listing.html')
        
        # Create listing - we'll need to update the Listing.create method to handle the new fields
        try:
            listing = Listing.create(
                title=title,
                description=description,
                location=location,
                price=price_per_night,
                host_id=current_user.id,
                property_type=room_type,
                guests=max_guests,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                amenities=amenities.split(',') if amenities else [],
                location_id=location_obj.location_id
            )
            
            if listing:
                # Save uploaded images
                saved_images = []
                upload_dir = os.path.join('app', 'static', 'uploads', 'listings')
                os.makedirs(upload_dir, exist_ok=True)
                
                for file, order in uploaded_files:
                    try:
                        # Generate unique filename
                        file_ext = file.filename.rsplit('.', 1)[1].lower()
                        unique_filename = f"listing_{listing.id}_{uuid.uuid4().hex[:8]}.{file_ext}"
                        
                        # Save file
                        file_path = os.path.join(upload_dir, unique_filename)
                        file.save(file_path)
                        
                        # Create database record
                        image_record = ListingImage.create(
                            listing_id=listing.id,
                            image_filename=unique_filename,
                            image_order=order
                        )
                        
                        if image_record:
                            saved_images.append(unique_filename)
                        else:
                            # If DB record creation fails, remove the file
                            try:
                                os.remove(file_path)
                            except:
                                pass
                    except Exception as e:
                        # Skip this image if there's an error
                        continue
                
                if saved_images:
                    flash(f'Listing "{title}" created successfully with {len(saved_images)} images!', 'success')
                else:
                    flash(f'Listing "{title}" created but no images were saved. You can add images later.', 'warning')
                
                return redirect(url_for('main.listing_detail', listing_id=listing.id))
            else:
                flash('Failed to create listing. Please try again.', 'error')
        except Exception as e:
            flash('An error occurred while creating the listing. Please try again.', 'error')
    
    return render_template('host/create_listing.html')

# Booking Routes

@bp.route('/book/<int:listing_id>')
@login_required
def book_listing(listing_id):
    listing = Listing.get(listing_id)
    
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Hosts cannot book their own listings
    if listing.host_id == current_user.id:
        flash('You cannot book your own listing.', 'error')
        return redirect(url_for('main.listing_detail', listing_id=listing_id))
    
    # Get host information
    host = User.get(listing.host_id)
    
    # Get unavailable dates
    unavailable_dates = listing.get_unavailable_dates()
    
    # Get listing images
    listing_images = ListingImage.get_by_listing(listing_id)
    
    # Prepare listing data
    listing_data = {
        'id': listing.id,
        'title': listing.title,
        'location': listing.location,
        'price': listing.price,
        'price_per_night': listing.price,  # Add for template compatibility
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

@bp.route('/book/<int:listing_id>/confirm', methods=['POST'])
@login_required
def confirm_booking(listing_id):
    listing = Listing.get(listing_id)
    
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Hosts cannot book their own listings
    if listing.host_id == current_user.id:
        flash('You cannot book your own listing.', 'error')
        return redirect(url_for('main.listing_detail', listing_id=listing_id))
    
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
        return redirect(url_for('main.book_listing', listing_id=listing_id))
    
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
        return redirect(url_for('main.book_listing', listing_id=listing_id))

# Booking Management Routes

@bp.route('/my-bookings')
@login_required
def my_bookings():
    """View user's bookings"""
    user = current_user
    
    # Get user's bookings
    bookings = Booking.get_by_user(user.id)
    
    # Enrich bookings with listing information and confirmed_by user info
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
    
    # Sort by creation date (newest first)
    enriched_bookings.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('guest/my_bookings.html', bookings=enriched_bookings, user=user)

@bp.route('/favorites')
@login_required
def favorites():
    """View user's favorite listings"""
    # Placeholder for favorites functionality
    return render_template('guest/favorites.html', favorites=[], user=current_user)

# Profile Routes

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))
        
        if not email or not password:
            flash('Please provide both email and password.', 'error')
            return render_template('auth/login.html')
        
        try:
            user = User.get_by_email(email)
            
            if user and user.check_password(password):
                login_user(user, remember=remember)
                flash(f'Welcome back, {user.full_name}!', 'success')
                
                # Redirect to next page or appropriate dashboard based on user type
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                
                # Fix the redirect logic - redirect to dashboard for admin
                if user.user_type == 'admin':
                    return redirect(url_for('main.dashboard'))
                elif user.user_type == 'host':
                    return redirect(url_for('main.dashboard'))
                else:  # guest
                    return redirect(url_for('main.dashboard'))  # Changed from index to dashboard
            else:
                flash('Invalid email or password.', 'error')
                
        except Exception as e:
            print(f"Login error: {e}")  # Debug print
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        import os
        from werkzeug.utils import secure_filename
        from flask import current_app
        
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        user_type = request.form.get('user_type', 'guest')
        terms_agreement = request.form.get('terms_agreement')
        
        # Handle profile photo upload
        profile_photo = request.files.get('profile_photo')
        profile_photo_filename = None
        
        if profile_photo and profile_photo.filename:
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in profile_photo.filename and \
               profile_photo.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                
                # Validate file size (5MB max)
                profile_photo.seek(0, 2)  # Seek to end
                file_size = profile_photo.tell()
                profile_photo.seek(0)  # Reset to beginning
                
                if file_size > 5 * 1024 * 1024:  # 5MB limit
                    flash('File size too large. Please upload an image smaller than 5MB.', 'error')
                    return render_template('auth/register.html')
                
                # Create filename with user name for organization
                file_extension = profile_photo.filename.rsplit('.', 1)[1].lower()
                # Clean the user name for filename (remove spaces, special chars)
                clean_name = ''.join(c for c in full_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_name = clean_name.replace(' ', '_')  # Replace spaces with underscores
                clean_name = clean_name.lower()  # Convert to lowercase for consistency
                
                # Create temporary filename (we'll update with user ID after user creation)
                import time
                timestamp = int(time.time())
                profile_photo_filename = f"{clean_name}_{timestamp}_profile.{file_extension}"
                
                # Create uploads directory if it doesn't exist
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Save the file temporarily
                temp_file_path = os.path.join(upload_folder, profile_photo_filename)
                profile_photo.save(temp_file_path)
            else:
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
                return render_template('auth/register.html')
        
        # Validation
        errors = []
        
        if not full_name:
            errors.append('Full name is required.')
        
        if not email:
            errors.append('Email is required.')
        elif User.get_by_email(email):
            errors.append('Email already registered.')
        
        if not password:
            errors.append('Password is required.')
        elif len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        if user_type not in ['guest', 'host']:
            errors.append('Please select a valid account type.')
        
        if not terms_agreement:
            errors.append('You must agree to the Terms of Service and Privacy Policy.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        user = User.create(
            full_name=full_name,
            email=email,
            password=password,
            phone=phone,
            bio=bio,
            user_type=user_type
        )
        
        if user:
            # Handle profile photo renaming and updating after user creation
            if profile_photo_filename:
                try:
                    # Create proper filename with user ID
                    file_extension = profile_photo_filename.rsplit('.', 1)[1].lower()
                    clean_name = ''.join(c for c in full_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    clean_name = clean_name.replace(' ', '_').lower()
                    final_filename = f"{clean_name}_{user.id}_profile.{file_extension}"
                    
                    # Rename the temporary file to final filename
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                    old_path = os.path.join(upload_folder, profile_photo_filename)
                    new_path = os.path.join(upload_folder, final_filename)
                    
                    if os.path.exists(old_path):
                        os.rename(old_path, new_path)
                        
                        # Update user's profile photo in database
                        user.update_profile(profile_photo=final_filename)
                        
                except Exception as e:
                    # If file operations fail, continue with registration
                    pass
            
            login_user(user)
            flash(f'Welcome to Otithi, {user.full_name}! Your account has been created successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            # If user creation failed, clean up uploaded file
            if profile_photo_filename:
                try:
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                    temp_file_path = os.path.join(upload_folder, profile_photo_filename)
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                except:
                    pass
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    
    # Get user's bookings
    bookings = Booking.get_by_user(user.id)
    
    # Get user's listings (if host)
    listings = []
    host_bookings = []
    if user.user_type == 'host':
        listings = Listing.get_by_host(user.id)
        host_bookings = Booking.get_by_host(user.id)
    
    # Render appropriate dashboard based on user type
    if user.user_type == 'admin':
        # Get all data for admin dashboard
        all_users = User.get_all()
        all_listings = Listing.get_all()
        all_bookings = Booking.get_all()
        
        return render_template('admin/admin.html', 
                             user=user, 
                             users=all_users,
                             bookings=all_bookings, 
                             listings=all_listings,
                             host_bookings=host_bookings)
    elif user.user_type == 'host':
        return render_template('host/host.html', 
                             user=user, 
                             bookings=bookings, 
                             listings=listings,
                             host_bookings=host_bookings)
    else:  # guest
        return render_template('guest/guest.html', 
                             user=user, 
                             bookings=bookings, 
                             listings=listings,
                             host_bookings=host_bookings)

@bp.route('/profile')
@login_required
def profile():
    """User profile page - shared template for all user types"""
    # Calculate user statistics
    stats = {
        'total_bookings': 0,
        'average_rating': 0.0,
        'favorites': 0,
        'reviews_given': 0
    }
    
    # Get user bookings
    bookings = Booking.get_by_user(current_user.id)
    stats['total_bookings'] = len(bookings) if bookings else 0
    
    # Get user reviews given
    reviews = Review.get_by_user(current_user.id)
    stats['reviews_given'] = len(reviews) if reviews else 0
    
    # Calculate average rating received (for hosts)
    if current_user.user_type == 'host':
        host_listings = Listing.get_by_host(current_user.id)
        if host_listings:
            total_rating = 0
            total_reviews = 0
            for listing in host_listings:
                if listing.rating > 0:
                    total_rating += listing.rating * listing.reviews_count
                    total_reviews += listing.reviews_count
            if total_reviews > 0:
                stats['average_rating'] = total_rating / total_reviews
    
    # Get recent activity (placeholder for now)
    recent_activities = []
    
    return render_template('profile.html', 
                         edit_mode=False, 
                         stats=stats, 
                         recent_activities=recent_activities)

@bp.route('/profile/edit', methods=['GET'])
@login_required
def edit_profile():
    # Calculate user statistics
    stats = {
        'total_bookings': 0,
        'average_rating': 0.0,
        'favorites': 0,
        'reviews_given': 0
    }
    
    # Get user bookings
    bookings = Booking.get_by_user(current_user.id)
    stats['total_bookings'] = len(bookings) if bookings else 0
    
    # Get user reviews given
    reviews = Review.get_by_user(current_user.id)
    stats['reviews_given'] = len(reviews) if reviews else 0
    
    # Calculate average rating received (for hosts)
    if current_user.user_type == 'host':
        host_listings = Listing.get_by_host(current_user.id)
        if host_listings:
            total_rating = 0
            total_reviews = 0
            for listing in host_listings:
                if listing.rating > 0:
                    total_rating += listing.rating * listing.reviews_count
                    total_reviews += listing.reviews_count
            if total_reviews > 0:
                stats['average_rating'] = total_rating / total_reviews
    
    # Get recent activity
    recent_activities = []
    
    # Add recent bookings
    if bookings:
        for booking in bookings[:5]:  # Last 5 bookings
            listing = Listing.get(booking.listing_id)
            recent_activities.append({
                'type': 'booking',
                'action': f"Booked {listing.title if listing else 'a listing'}",
                'date': booking.created_date,
                'status': booking.status,
                'icon': 'fas fa-calendar-check',
                'color': 'success' if booking.status == 'confirmed' else 'warning' if booking.status == 'pending' else 'danger'
            })
    
    # Add recent reviews given
    if reviews:
        for review in reviews[:3]:  # Last 3 reviews
            listing = Listing.get(review.listing_id)
            recent_activities.append({
                'type': 'review',
                'action': f"Reviewed {listing.title if listing else 'a listing'}",
                'date': review.created_date,
                'rating': review.rating,
                'icon': 'fas fa-star',
                'color': 'info'
            })
    
    # Add host activities (if user is a host)
    if current_user.user_type == 'host':
        host_listings = Listing.get_by_host(current_user.id)
        if host_listings:
            for listing in host_listings[:3]:  # Last 3 listings
                recent_activities.append({
                    'type': 'listing',
                    'action': f"Created listing: {listing.title}",
                    'date': listing.created_date if hasattr(listing, 'created_date') and listing.created_date else None,
                    'icon': 'fas fa-home',
                    'color': 'primary'
                })
        
        # Add recent bookings received (for hosts)
        host_bookings = Booking.get_by_host(current_user.id)
        if host_bookings:
            for booking in host_bookings[:3]:  # Last 3 bookings received
                guest = User.get(booking.user_id)
                listing = Listing.get(booking.listing_id)
                recent_activities.append({
                    'type': 'host_booking',
                    'action': f"Received booking from {guest.name if guest else 'a guest'} for {listing.title if listing else 'your listing'}",
                    'date': booking.created_date,
                    'status': booking.status,
                    'icon': 'fas fa-user-check',
                    'color': 'success' if booking.status == 'confirmed' else 'warning' if booking.status == 'pending' else 'danger'
                })
    
    # Sort all activities by date (most recent first)
    recent_activities = sorted(
        [activity for activity in recent_activities if activity.get('date')],
        key=lambda x: x['date'],
        reverse=True
    )[:10]  # Keep only the 10 most recent activities
    
    # Use shared template for all user types
    return render_template('profile.html', 
                         edit_mode=True, 
                         stats=stats, 
                         recent_activities=recent_activities)

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    import os
    from werkzeug.utils import secure_filename
    from flask import current_app
    
    try:
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Handle profile photo upload
        profile_photo = request.files.get('profile_photo')
        profile_photo_filename = None
        
        if profile_photo and profile_photo.filename:
            # Validate file type
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
            if '.' in profile_photo.filename and \
               profile_photo.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                
                # Create filename with user name for organization
                file_extension = profile_photo.filename.rsplit('.', 1)[1].lower()
                # Clean the user name for filename (remove spaces, special chars)
                clean_name = ''.join(c for c in current_user.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_name = clean_name.replace(' ', '_')  # Replace spaces with underscores
                clean_name = clean_name.lower()  # Convert to lowercase for consistency
                
                # Add user ID to prevent conflicts if multiple users have same name
                profile_photo_filename = f"{clean_name}_{current_user.id}_profile.{file_extension}"
                
                # Create uploads directory if it doesn't exist
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                # Save the file
                file_path = os.path.join(upload_folder, profile_photo_filename)
                profile_photo.save(file_path)
                
                # Remove old profile photo if it exists
                if current_user.profile_photo and current_user.profile_photo != profile_photo_filename:
                    old_file_path = os.path.join(upload_folder, current_user.profile_photo)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
            else:
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files only.', 'error')
                return redirect(url_for('main.edit_profile'))
        
        # Update user data
        if current_user.update_profile(full_name=full_name, phone=phone, profile_photo=profile_photo_filename, bio=bio):
            flash('Profile updated successfully!', 'success')
        else:
            flash('Error updating profile. Please try again.', 'error')
            
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'error')
    
    return redirect(url_for('main.profile'))

@bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validate current password
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('main.profile'))
        
        # Validate new password
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'error')
            return redirect(url_for('main.profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('main.profile'))
        
        # Update password
        if current_user.update_password(new_password):
            flash('Password changed successfully!', 'success')
        else:
            flash('Error changing password. Please try again.', 'error')
            
    except Exception as e:
        flash(f'Error changing password: {str(e)}', 'error')
    
    return redirect(url_for('main.profile'))

@bp.route('/profile/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    try:
        delete_confirmation = request.form.get('delete_confirmation', '')
        password = request.form.get('delete_password', '')
        
        # Validate confirmation
        if delete_confirmation != 'DELETE':
            flash('Account deletion confirmation failed. Please type DELETE exactly.', 'error')
            return redirect(url_for('main.profile'))
        
        # Validate password
        if not current_user.check_password(password):
            flash('Password is incorrect.', 'error')
            return redirect(url_for('main.profile'))
        
        # Store user ID for deletion
        user_id = current_user.id
        
        # Log out user
        logout_user()
        
        # Delete user account
        user = User.get(user_id)
        if user and user.delete():
            flash('Your account has been deleted successfully.', 'success')
        else:
            flash('Error deleting account. Please contact support.', 'error')
            
    except Exception as e:
        flash(f'Error deleting account: {str(e)}', 'error')
    
    return redirect(url_for('main.index'))

# My Listings Route for Hosts

@bp.route('/my-listings')
@login_required
def my_listings():
    """Display user's listings (for hosts) or redirect guests"""
    if current_user.user_type not in ['host', 'admin']:
        flash('Access denied. Only hosts can view listings.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get user's listings
    user_listings = Listing.get_by_host(current_user.id)
    
    # Get bookings for these listings
    host_bookings = Booking.get_by_host(current_user.id)
    
    return render_template('host/my_listings.html', 
                         listings=user_listings,
                         bookings=host_bookings,
                         user=current_user)

# API Routes for AJAX requests

@bp.route('/api/check-email')
def check_email():
    email = request.args.get('email', '').strip()
    if email:
        user = User.get_by_email(email)
        return jsonify({'available': user is None})
    return jsonify({'available': False})

@bp.route('/api/user/reviews')
@login_required
def get_user_reviews():
    """API endpoint to get all reviews posted by the current user"""
    try:
        # Get all reviews by the current user
        user_reviews = Review.get_by_user(current_user.id)
        
        # Convert reviews to JSON format with listing information
        reviews_data = []
        for review in user_reviews:
            # Get the listing for this review
            listing = Listing.get_by_id(review.listing_id)
            
            review_data = {
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'created_date': review.created_date.strftime('%B %d, %Y') if review.created_date else '',
                'listing_title': listing.title if listing else 'Listing not found',
                'listing_location': listing.location if listing else '',
                'listing_id': review.listing_id
            }
            reviews_data.append(review_data)
        
        # Sort by date (newest first)
        reviews_data.sort(key=lambda x: x['created_date'], reverse=True)
        
        return jsonify({
            'success': True,
            'reviews': reviews_data,
            'total_count': len(reviews_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching reviews: {str(e)}'
        }), 500

# Legacy routes (for compatibility)
@bp.route('/host')
def become_host():
    return redirect(url_for('main.register') + '?type=host')

@bp.route('/become-host')
def become_host_alt():
    return redirect(url_for('main.register') + '?type=host')

# =============================================================================
# ADMIN ROUTES
# =============================================================================

@bp.route('/admin')
@login_required
def admin():
    """Main admin route - redirects to dashboard"""
    if current_user.user_type != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.index'))
    return redirect(url_for('main.dashboard'))

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Admin panel - manage users"""
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@bp.route('/admin/users/<int:user_id>/toggle-verification', methods=['POST'])
@login_required
@admin_required
def admin_toggle_verification(user_id):
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

@bp.route('/admin/users/<int:user_id>/edit-confirm')
@login_required
@admin_required
def admin_edit_user_confirm(user_id):
    """Admin panel - edit user confirmation page"""
    user = User.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('admin/edit_user_confirm.html', user=user)

@bp.route('/admin/users/<int:user_id>/delete-confirm')
@login_required
@admin_required
def admin_delete_user_confirm(user_id):
    """Admin panel - delete user confirmation page"""
    user = User.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('main.dashboard'))
        
    return render_template('admin/delete_user_confirm.html', user=user)

@bp.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    """Admin panel - edit user"""
    user = User.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main.admin_users'))
    
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
        return redirect(url_for('main.dashboard'))
    
    return render_template('admin/edit_user.html', user=user)

@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Admin panel - delete user"""
    user = User.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if user.delete():
        flash('User deleted successfully!', 'success')
    else:
        flash('Error deleting user.', 'error')
    
    return redirect(url_for('main.dashboard'))

@bp.route('/admin/users/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def admin_change_user_role(user_id):
    """Admin panel - change user role"""
    user = User.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    new_role = request.json.get('role')
    if new_role not in ['guest', 'host', 'admin']:
        return jsonify({'success': False, 'message': 'Invalid role'})
    
    if user.update_user_type(new_role):
        return jsonify({'success': True, 'message': 'Role updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to update role'})

@bp.route('/admin/listings')
@login_required
@admin_required
def admin_listings():
    """Admin panel - manage listings"""
    listings = Listing.get_all()
    return render_template('admin/listings.html', listings=listings)

@bp.route('/admin/listings/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit_listing(listing_id):
    """Admin panel - edit listing"""
    listing = Listing.get(listing_id)
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('main.admin_listings'))
    
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
        return redirect(url_for('main.admin_listings'))
    
    return render_template('admin/edit_listing.html', listing=listing)

@bp.route('/admin/listings/<int:listing_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_listing(listing_id):
    """Admin panel - delete listing"""
    listing = Listing.get(listing_id)
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('main.admin_listings'))
    
    if listing.delete():
        flash('Listing deleted successfully!', 'success')
    else:
        flash('Error deleting listing.', 'error')
    
    return redirect(url_for('main.admin_listings'))

@bp.route('/admin/listings/<int:listing_id>/approve', methods=['POST'])
@login_required
@admin_required
def admin_approve_listing(listing_id):
    """Admin panel - approve listing"""
    listing = Listing.get(listing_id)
    if not listing:
        return jsonify({'success': False, 'message': 'Listing not found'})
    
    if listing.approve():
        return jsonify({'success': True, 'message': 'Listing approved successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to approve listing'})

@bp.route('/admin/bookings')
@login_required
@admin_required
def admin_bookings():
    """Admin panel - manage bookings"""
    bookings = Booking.get_all()
    return render_template('admin/bookings.html', bookings=bookings)

@bp.route('/admin/bookings/<int:booking_id>/update-status', methods=['POST'])
@login_required
@admin_required
def admin_update_booking_status(booking_id):
    """Admin panel - update booking status"""
    booking = Booking.get(booking_id)
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'})
    
    new_status = request.json.get('status')
    if new_status not in ['pending', 'confirmed', 'cancelled']:
        return jsonify({'success': False, 'message': 'Invalid status'})
    
    if booking.update_status(new_status):
        return jsonify({'success': True, 'message': 'Status updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to update status'})

@bp.route('/admin/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_profile():
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
        
        return redirect(url_for('main.admin_profile'))
    
    return render_template('admin/profile.html', user=current_user)

@bp.route('/admin/stats')
@login_required
@admin_required
def admin_stats():
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
# =============================================================================
# END OF PRODUCTION ROUTES
# =============================================================================
