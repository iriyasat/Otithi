from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Listing, Booking, Review
from datetime import datetime, date

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
        listings_data.append({
            'id': listing.id,
            'title': listing.title,
            'location': listing.location,
            'price': listing.price,
            'rating': listing.rating,
            'reviews': listing.reviews_count,
            'image': 'demo_listing_1.jpg',  # Default image
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
        listings_data.append({
            'id': listing.id,
            'title': listing.title,
            'location': listing.location,
            'city': listing.city,
            'country': listing.country,
            'price': listing.price,
            'rating': listing.rating,
            'reviews': listing.reviews_count,
            'image': 'demo_listing_1.jpg',  # Default image
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
        listings_data.append({
            'id': listing.id,
            'title': listing.title,
            'location': listing.location,
            'price': listing.price,
            'rating': listing.rating,
            'reviews': listing.reviews_count,
            'image': 'demo_listing_1.jpg',
            'type': listing.property_type.title(),
            'guests': listing.guests,
            'bedrooms': listing.bedrooms,
            'bathrooms': listing.bathrooms
        })
    
    return render_template('host/search.html', 
                         listings=listings_data,
                         query=query, 
                         location=location,
                         checkin=checkin,
                         checkout=checkout,
                         guests=guests)

# Listing Routes

@bp.route('/listings/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.get(listing_id)
    
    if not listing:
        flash('Listing not found.', 'error')
        return redirect(url_for('main.index'))
    
    # Get host information
    host = User.get(listing.host_id)
    
    # Get reviews
    reviews = Review.get_by_listing(listing_id)
    
    # Get unavailable dates for calendar
    unavailable_dates = listing.get_unavailable_dates()
    
    # Prepare listing data for template
    listing_data = {
        'id': listing.id,
        'title': listing.title,
        'location': listing.location,
        'address': listing.address,
        'city': listing.city,
        'country': listing.country,
        'price': listing.price,
        'rating': listing.rating,
        'reviews': listing.reviews_count,
        'image': 'demo_listing_1.jpg',
        'type': listing.property_type.title(),
        'guests': listing.guests,
        'bedrooms': listing.bedrooms,
        'bathrooms': listing.bathrooms,
        'description': listing.description,
        'amenities': listing.amenities,
        'host': {
            'id': host.id if host else None,
            'name': host.full_name if host else 'Unknown Host',
            'avatar': 'user-gear.png',
            'joined': host.joined_date.year if host else '2023',
            'verified': host.verified if host else False,
            'bio': host.bio if host else ''
        },
        'unavailable_dates': unavailable_dates
    }
    
    return render_template('host/listing_detail.html', listing=listing_data, reviews=reviews)

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
        property_type = request.form.get('property_type', 'apartment')
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        country = request.form.get('country', 'Bangladesh').strip()
        price = request.form.get('price')
        guests = request.form.get('guests')
        bedrooms = request.form.get('bedrooms')
        bathrooms = request.form.get('bathrooms')
        amenities = request.form.getlist('amenities')
        
        # Validation
        errors = []
        
        if not title:
            errors.append('Title is required.')
        
        if not description:
            errors.append('Description is required.')
        
        if not address:
            errors.append('Address is required.')
        
        if not city:
            errors.append('City is required.')
        
        try:
            price = float(price)
            if price <= 0:
                errors.append('Price must be greater than 0.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid price.')
        
        try:
            guests = int(guests)
            if guests <= 0:
                errors.append('Guest count must be at least 1.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid guest count.')
        
        try:
            bedrooms = int(bedrooms)
            if bedrooms <= 0:
                errors.append('Bedroom count must be at least 1.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid bedroom count.')
        
        try:
            bathrooms = int(bathrooms)
            if bathrooms <= 0:
                errors.append('Bathroom count must be at least 1.')
        except (ValueError, TypeError):
            errors.append('Please enter a valid bathroom count.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('host/create_listing.html')
        
        # Create location string
        location = f"{city}, {country}"
        
        # Create listing
        listing = Listing.create(
            title=title,
            description=description,
            location=location,
            price=price,
            host_id=current_user.id,
            property_type=property_type,
            guests=guests,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            amenities=amenities,
            address=address,
            city=city,
            country=country
        )
        
        if listing:
            flash(f'Listing "{title}" created successfully!', 'success')
            return redirect(url_for('main.listing_detail', listing_id=listing.id))
        else:
            flash('Failed to create listing. Please try again.', 'error')
    
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
    
    # Prepare listing data
    listing_data = {
        'id': listing.id,
        'title': listing.title,
        'location': listing.location,
        'price': listing.price,
        'rating': listing.rating,
        'reviews': listing.reviews_count,
        'image': 'demo_listing_1.jpg',
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
    
    # Enrich bookings with listing information
    enriched_bookings = []
    for booking in bookings:
        listing = Listing.get(booking.listing_id)
        host = User.get(listing.host_id) if listing else None
        
        booking_data = {
            'id': booking.id,
            'check_in': booking.check_in,
            'check_out': booking.check_out,
            'guests': booking.guests,
            'total_price': booking.total_price,
            'status': booking.status,
            'created_date': booking.created_date,
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
    enriched_bookings.sort(key=lambda x: x['created_date'], reverse=True)
    
    return render_template('guest/booking.html', bookings=enriched_bookings, user=user)

# API Routes

@bp.route('/api/calculate_price/<int:listing_id>')
def calculate_price(listing_id):
    listing = Listing.get(listing_id)
    
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    guests = request.args.get('guests', 1)
    
    try:
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()
        guest_count = int(guests)
        
        if checkout_date <= checkin_date:
            return jsonify({'error': 'Invalid dates'}), 400
        
        price_breakdown = listing.calculate_total_price(checkin_date, checkout_date, guest_count)
        
        return jsonify({
            'nights': price_breakdown['nights'],
            'base_price': price_breakdown['base_price'],
            'cleaning_fee': price_breakdown['cleaning_fee'],
            'service_fee': price_breakdown['service_fee'],
            'total': price_breakdown['total']
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

@bp.route('/api/check_availability/<int:listing_id>')
def check_availability(listing_id):
    listing = Listing.get(listing_id)
    
    if not listing:
        return jsonify({'error': 'Listing not found'}), 404
    
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    
    try:
        checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()
        
        available = listing.is_available(checkin_date, checkout_date)
        
        return jsonify({
            'available': available,
            'unavailable_dates': listing.get_unavailable_dates()
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

# Authentication Routes

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
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name}!', 'success')
            
            # Redirect to next page or appropriate dashboard based on user type
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirect based on user type
            if user.user_type in ['admin', 'host']:
                return redirect(url_for('main.dashboard'))  # Admin and hosts go to their dashboards
            else:
                return redirect(url_for('main.index'))      # Guests go to search/browse
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        user_type = request.form.get('user_type', 'guest')
        terms_agreement = request.form.get('terms_agreement')
        
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
            login_user(user)
            flash(f'Welcome to Otithi, {user.full_name}! Your account has been created successfully.', 'success')
            return redirect(url_for('main.dashboard'))
        else:
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

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.bio = request.form.get('bio', current_user.bio)
        current_user.save()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    
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
    
    # Use shared template for all user types
    return render_template('profile.html', 
                         edit_mode=True, 
                         stats=stats, 
                         recent_activities=recent_activities)

@bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Handle profile photo upload
        profile_photo = request.files.get('profile_photo')
        if profile_photo and profile_photo.filename:
            # Save the uploaded file (implement file upload logic)
            # For now, we'll skip the actual file upload
            pass
        
        # Update user data
        if current_user.update_profile(full_name=full_name, phone=phone):
            # Update bio separately if needed
            current_user.bio = bio
            current_user.save()
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

# API Routes for AJAX requests

@bp.route('/api/check-email')
def check_email():
    email = request.args.get('email', '').strip()
    if email:
        user = User.get_by_email(email)
        return jsonify({'available': user is None})
    return jsonify({'available': False})

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
        
        # Update user details
        user.update_profile(full_name=full_name, phone=phone)
        user.update_user_type(user_type)
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('main.admin_users'))
    
    return render_template('admin/edit_user.html', user=user)

@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    """Admin panel - delete user"""
    user = User.get(user_id)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('main.admin_users'))
    
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('main.admin_users'))
    
    if user.delete():
        flash('User deleted successfully!', 'success')
    else:
        flash('Error deleting user.', 'error')
    
    return redirect(url_for('main.admin_users'))

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
