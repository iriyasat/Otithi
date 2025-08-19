from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Listing, Booking, Review, ListingImage

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with featured listings and recent reviews"""
    try:
        # Get listings from database
        listings = Listing.get_all()
        
        # Convert to format expected by template (limit to 5 for homepage)
        listings_data = []
        for listing in listings[:5]:
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
                'bathrooms': listing.bathrooms
            })
        
        # Get recent reviews for the homepage
        all_reviews = Review.get_all()
        recent_reviews = sorted(all_reviews, key=lambda x: x.created_date, reverse=True)[:6]
        
        # Convert reviews to format expected by template
        reviews_data = []
        for review in recent_reviews:
            guest = User.get(review.user_id)
            listing = Listing.get(review.listing_id)
            
            reviews_data.append({
                'guest_name': guest.name if guest else 'Anonymous Guest',
                'rating': review.rating,
                'comment': review.comment,
                'created_at': review.created_date,
                'listing_title': listing.title if listing else 'Unknown Listing'
            })
        
        # Calculate hosting statistics
        all_bookings = Booking.get_all()
        all_listings = Listing.get_all()
        
        ratings = [l.rating for l in all_listings if hasattr(l, 'rating') and l.rating > 0]
        avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0.0
        
        unique_hosts = set()
        for listing in all_listings:
            if hasattr(listing, 'host_id') and listing.host_id:
                unique_hosts.add(listing.host_id)
        
        hosting_stats = {
            'total_listings': len(all_listings),
            'total_bookings': len(all_bookings),
            'avg_rating': avg_rating,
            'total_hosts': len(unique_hosts)
        }
        
        return render_template('index.html', 
                             listings=listings_data, 
                             reviews=reviews_data, 
                             hosting_stats=hosting_stats)
    
    except Exception as e:
        flash('Error loading homepage data.', 'error')
        return render_template('index.html', listings=[], reviews=[], hosting_stats={})

@main_bp.route('/explore')
def explore():
    """Explore all listings with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 12
        
        all_listings = Listing.get_all()
        total_listings = len(all_listings)
        total_pages = (total_listings + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        page_listings = all_listings[start_idx:end_idx]
        
        # Convert to template format
        listings_data = []
        for listing in page_listings:
            listing_images = ListingImage.get_by_listing(listing.id)
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
                'image': listing_images[0].image_filename if listing_images else 'demo_listing_1.jpg',
                'type': listing.property_type.title(),
                'guests': listing.guests,
                'bedrooms': listing.bedrooms,
                'bathrooms': listing.bathrooms,
                'description': listing.description
            })
        
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
    
    except Exception as e:
        flash('Error loading listings.', 'error')
        return render_template('explore.html', listings=[], pagination={})

@main_bp.route('/search')
def search():
    """Search listings with filters"""
    try:
        query = request.args.get('query', '')
        location = request.args.get('location', '')
        checkin = request.args.get('checkin', '')
        checkout = request.args.get('checkout', '')
        guests = request.args.get('guests', '')
        
        listings = Listing.get_all()
        
        # Apply filters
        if location:
            listings = [l for l in listings if location.lower() in l.location.lower()]
        
        if checkin and checkout:
            try:
                from datetime import datetime
                checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()
                checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()
                listings = [l for l in listings if l.is_available(checkin_date, checkout_date)]
            except ValueError:
                pass
        
        if guests:
            try:
                guest_count = int(guests)
                listings = [l for l in listings if l.guests >= guest_count]
            except ValueError:
                pass
        
        # Convert to template format
        listings_data = []
        for listing in listings:
            listing_images = ListingImage.get_by_listing(listing.id)
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
                'price_per_night': listing.price
            })
        
        return render_template('host/search.html', 
                             listings=listings_data,
                             query=query, 
                             location=location,
                             checkin=checkin,
                             checkout=checkout,
                             guests=guests)
    
    except Exception as e:
        flash('Error performing search.', 'error')
        return render_template('host/search.html', listings=[])

@main_bp.route('/test-password/<password>')
def test_password(password):
    """Test password against admin hash"""
    from werkzeug.security import check_password_hash
    
    # Admin hash from database
    admin_hash = 'pbkdf2:sha256:600000$BMlfFUDFo6o5PCbL$83629fe92704f02e2fedbd014ee8ec31da52f2e9f15d14ce79f470ee2c4dcf38'
    
    # Test password
    result = check_password_hash(admin_hash, password)
    
    return f"""
    <h2>Password Test</h2>
    <p>Testing password: <strong>{password}</strong></p>
    <p>Result: <strong>{'VALID' if result else 'INVALID'}</strong></p>
    
    <h3>Common passwords to try:</h3>
    <ul>
        <li><a href="/test-password/admin">admin</a></li>
        <li><a href="/test-password/password">password</a></li>
        <li><a href="/test-password/123456">123456</a></li>
        <li><a href="/test-password/admin123">admin123</a></li>
        <li><a href="/test-password/otithi">otithi</a></li>
        <li><a href="/test-password/admin@otithi.com">admin@otithi.com</a></li>
    </ul>
    
    <p><a href="/">Back to Home</a></p>
    """

@main_bp.route('/debug-users')
def debug_users():
    """Debug route to check users in database"""
    from app.models import User
    from app.database import db
    
    # Get all users
    query = "SELECT user_id, name, email, user_type, verified FROM users"
    result = db.execute_query(query)
    
    users_info = []
    for user_data in result:
        users_info.append({
            'id': user_data['user_id'],
            'name': user_data['name'],
            'email': user_data['email'],
            'type': user_data['user_type'],
            'verified': user_data['verified']
        })
    
    # Try to get admin user specifically
    admin_user = User.get_by_email('admin@otithi.com')
    admin_info = None
    if admin_user:
        admin_info = {
            'found': True,
            'name': admin_user.full_name,
            'type': admin_user.user_type,
            'has_password_hash': bool(admin_user.password_hash),
            'password_hash_length': len(admin_user.password_hash) if admin_user.password_hash else 0
        }
    else:
        admin_info = {'found': False}
    
    return f"""
    <h2>Database Debug Info</h2>
    <h3>All Users:</h3>
    <pre>{users_info}</pre>
    
    <h3>Admin User Check:</h3>
    <pre>{admin_info}</pre>
    
    <p><a href="/">Back to Home</a></p>
    """

@main_bp.route('/status')
def status():
    """Application status page"""
    return render_template('status.html')

@main_bp.route('/dashboard')
@login_required  
def dashboard():
    """User dashboard"""
    try:
        if current_user.user_type == 'admin':
            return redirect(url_for('admin.dashboard'))

        # Get user's bookings and listings
        bookings = Booking.get_by_user(current_user.id)
        
        if current_user.user_type == 'host':
            listings = Listing.get_by_host(current_user.id)
            host_bookings = Booking.get_by_host(current_user.id)
            return render_template('host/host.html', 
                                 user=current_user,
                                 listings=listings, 
                                 bookings=bookings,
                                 host_bookings=host_bookings)
        else:
            return render_template('guest/guest.html', 
                                 user=current_user,
                                 bookings=bookings)
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        return render_template('guest/guest.html', 
                             user=current_user,
                             bookings=[])

@main_bp.route('/my-bookings')
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

# Remove the redirect routes - auth blueprint handles /login and /register directly
# Note: Removed duplicate logout route to prevent conflicts - auth.logout handles this

@main_bp.route('/book/<int:listing_id>')
@login_required
def book_listing(listing_id):
    """Booking page - redirect to bookings blueprint"""
    return redirect(url_for('bookings.book_listing', listing_id=listing_id))
