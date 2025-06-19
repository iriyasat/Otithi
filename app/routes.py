import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort, send_file, session
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Listing, User, Booking, Review, Conversation, Message, UserRole, BookingStatus, ListingStatus
from . import db
from .forms import ListingForm, RegisterForm, LoginForm, BookingForm, ReviewForm, EditUserForm, ProfileSettingsForm, MessageForm
from .decorators import role_required, admin_required, host_required, guest_required, owns_listing_or_admin, host_required_unverified
import uuid
from sqlalchemy import or_, func
from datetime import date, datetime
from PIL import Image
from flask import url_for

main = Blueprint('main', __name__)

def save_profile_picture(uploaded_file, user_id):
    """Save profile picture with user_id naming in static/images/profiles folder"""
    # Ensure target directory exists
    folder = os.path.join(current_app.root_path, 'static', 'images', 'profiles')
    os.makedirs(folder, exist_ok=True)

    # Remove any existing profile picture for this user
    for ext in ['.jpg', '.jpeg', '.png']:
        existing_file = os.path.join(folder, f"user_{user_id}{ext}")
        if os.path.exists(existing_file):
            os.remove(existing_file)

    # Define the filename (always save as .jpg for consistency)
    filename = f"user_{user_id}.jpg"
    filepath = os.path.join(folder, filename)

    # Resize and save using Pillow
    img = Image.open(uploaded_file)
    img = img.convert('RGB')  # Convert to RGB for JPEG format
    img.thumbnail((300, 300))  # Resize to 300x300 max
    img.save(filepath, format='JPEG', quality=85)

    return filename

def save_listing_image(uploaded_file, listing_id):
    """Save listing image with listing_id naming in static/images/listings folder"""
    # Ensure target directory exists
    folder = os.path.join(current_app.root_path, 'static', 'images', 'listings')
    os.makedirs(folder, exist_ok=True)

    # Remove any existing listing image for this listing
    for ext in ['.jpg', '.jpeg', '.png']:
        existing_file = os.path.join(folder, f"listing_{listing_id}{ext}")
        if os.path.exists(existing_file):
            os.remove(existing_file)

    # Define the filename (always save as .jpg for consistency)
    filename = f"listing_{listing_id}.jpg"
    filepath = os.path.join(folder, filename)

    # Resize and save using Pillow
    img = Image.open(uploaded_file)
    img = img.convert('RGB')  # Convert to RGB for JPEG format
    img.thumbnail((800, 600))  # Larger size for listing images
    img.save(filepath, format='JPEG', quality=90)

    return filename

def get_profile_image_url(filename):
    """Get the correct URL for profile images with fallback"""
    if filename:
        # Check if file exists, otherwise use default
        file_path = os.path.join(current_app.root_path, 'static', 'images', 'profiles', filename)
        if os.path.exists(file_path):
            return url_for('static', filename=f'images/profiles/{filename}')
    return url_for('static', filename='images/ui/default_avatar.png')

def get_listing_image_url(filename):
    """Get the correct URL for listing images with fallback"""
    if filename:
        # Check if file exists, otherwise use default
        file_path = os.path.join(current_app.root_path, 'static', 'images', 'listings', filename)
        if os.path.exists(file_path):
            return url_for('static', filename=f'images/listings/{filename}')
    return url_for('static', filename='images/ui/default_listing.jpg')

def save_nid_file(uploaded_file, booking_id):
    """Save NID document with booking_id naming in static/nid_uploads folder"""
    # Ensure target directory exists
    folder = os.path.join(current_app.root_path, 'static', 'nid_uploads')
    os.makedirs(folder, exist_ok=True)

    # Get file extension
    original_filename = secure_filename(uploaded_file.filename)
    file_ext = os.path.splitext(original_filename)[1].lower()
    
    # Remove any existing NID file for this booking
    for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
        existing_file = os.path.join(folder, f"nid_{booking_id}{ext}")
        if os.path.exists(existing_file):
            os.remove(existing_file)

    # Define the secure filename
    filename = f"nid_{booking_id}{file_ext}"
    filepath = os.path.join(folder, filename)

    # Save the file
    uploaded_file.save(filepath)

    return filename

def save_host_nid_file(uploaded_file, user_id):
    """Save host NID document with user_id naming in static/nid_host_uploads folder"""
    # Ensure target directory exists
    folder = os.path.join(current_app.root_path, 'static', 'nid_host_uploads')
    os.makedirs(folder, exist_ok=True)

    # Get file extension
    original_filename = secure_filename(uploaded_file.filename)
    file_ext = os.path.splitext(original_filename)[1].lower()
    
    # Remove any existing NID file for this user
    for ext in ['.jpg', '.jpeg', '.png', '.pdf']:
        existing_file = os.path.join(folder, f"host_nid_{user_id}{ext}")
        if os.path.exists(existing_file):
            os.remove(existing_file)

    # Define the secure filename
    filename = f"host_nid_{user_id}{file_ext}"
    filepath = os.path.join(folder, filename)

    # Save the file
    uploaded_file.save(filepath)

    return filename

@main.route('/')
def home():
    # Get real reviews for homepage (latest 2 reviews with good ratings)
    recent_reviews = (Review.query
                     .filter(Review.rating >= 4)  # Only show 4+ star reviews
                     .order_by(Review.created_at.desc())
                     .limit(2)
                     .all())
    
    return render_template('index.html', recent_reviews=recent_reviews)

@main.route('/about')
def about():
    # Get total user count for about page
    total_users = User.query.count()
    total_guests = User.query.filter_by(role='guest').count()
    total_hosts = User.query.filter_by(role='host').count()
    
    # Get real-time platform statistics for about page
    total_listings = Listing.query.filter_by(approved=True).count()
    
    # Calculate average rating from all reviews with fallback
    avg_rating = db.session.query(func.avg(Review.rating)).scalar()
    if avg_rating and not (isinstance(avg_rating, float) and avg_rating != avg_rating):  # Check for NaN
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = 0.0
    
    # Get total bookings completed
    total_bookings = Booking.query.filter_by(status='checked_out').count()
    
    # Count unique districts/locations covered
    unique_locations = db.session.query(func.count(func.distinct(Listing.location))).filter_by(approved=True).scalar() or 0
    
    return render_template('about.html', 
                         total_users=total_users,
                         total_guests=total_guests,
                         total_hosts=total_hosts,
                         total_listings=total_listings,
                         avg_rating=avg_rating,
                         total_bookings=total_bookings,
                         unique_locations=unique_locations)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegisterForm()
    
    if request.method == 'POST':
        # Debug: Print form data and validation status
        print(f"DEBUG: Form data received: {request.form}")
        print(f"DEBUG: Form validation status: {form.validate()}")
        print(f"DEBUG: Form errors: {form.errors}")
        
        if form.validate_on_submit():
            try:
                # Security: Ensure only guest/host roles can be registered
                if form.account_type.data not in ['guest', 'host']:
                    flash('Invalid account type selected.', 'danger')
                    return render_template('register.html', form=form)
                
                # Create new user (validation already handled by form validators)
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    role=UserRole.GUEST if form.account_type.data == 'guest' else UserRole.HOST
                )
                user.set_password(form.password.data)
                
                db.session.add(user)
                db.session.commit()
                
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('main.login'))
                
            except Exception as e:
                db.session.rollback()
                print(f"DEBUG: Registration error: {e}")
                flash('Registration failed. Please try again.', 'danger')
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Form data: {request.form}")
    print(f"DEBUG: Session: {session}")
    
    if request.method == 'POST':
        print(f"DEBUG: Form validation status: {form.validate()}")
        print(f"DEBUG: Form errors: {form.errors}")
        print(f"DEBUG: CSRF token in form: {form.csrf_token.data}")
        print(f"DEBUG: CSRF token in session: {session.get('csrf_token')}")
        
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Login successful. Welcome back, {}!'.format(user.username), 'success')
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                # Role-based redirect after login
                if user.is_admin:
                    return redirect(url_for('main.admin_dashboard'))
                elif user.is_host:
                    return redirect(url_for('main.host_dashboard'))
                else:
                    return redirect(url_for('main.browse'))
            else:
                flash('Invalid username or password.', 'danger')
        else:
            # Debug: Show form validation errors if form doesn't validate
            for field_name, errors in form.errors.items():
                for error in errors:
                    flash(f'{field_name}: {error}', 'danger')
    
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

@main.route('/profile')
@login_required
def profile():
    form = ProfileSettingsForm()
    # Pre-populate form with current user data
    form.username.data = current_user.username
    form.email.data = current_user.email
    return render_template('profile.html', title='Profile', Review=Review, form=form)

@main.route('/my-listings')
@host_required_unverified
def my_listings():
    if current_user.is_admin:
        # Admin can see all listings
        user_listings = Listing.query.all()
        title = 'All Listings (Admin View)'
    else:
        # Host can only see their own listings using proper foreign key
        user_listings = Listing.query.filter_by(host_id=current_user.id).all()
        title = 'My Listings'
    return render_template('my_listings.html', listings=user_listings, title=title)

@main.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    form = ProfileSettingsForm()
    if form.validate_on_submit():
        try:
            # Check if username or email is already taken by another user
            if form.username.data != current_user.username:
                existing_user = User.query.filter_by(username=form.username.data).first()
                if existing_user:
                    flash('Username already exists. Please choose a different one.', 'danger')
                    return redirect(url_for('main.profile'))
            
            if form.email.data != current_user.email:
                existing_user = User.query.filter_by(email=form.email.data).first()
                if existing_user:
                    flash('Email already exists. Please choose a different one.', 'danger')
                    return redirect(url_for('main.profile'))
            
            # Update basic information
            current_user.username = form.username.data
            current_user.email = form.email.data
            
            # Handle profile picture upload
            if form.profile_picture.data:
                pic = form.profile_picture.data
                if pic.filename:
                    # Use the new save_profile_picture function
                    picture_file = save_profile_picture(pic, current_user.id)
                    current_user.profile_picture = picture_file
            
            # Handle host NID upload
            if form.nid_file.data and form.nid_file.data.filename and current_user.role == 'host':
                try:
                    nid_filename = save_host_nid_file(form.nid_file.data, current_user.id)
                    current_user.nid_filename = nid_filename
                    flash('NID document uploaded successfully! Please wait for admin verification.', 'success')
                except Exception as e:
                    flash(f'Error uploading NID document: {str(e)}', 'danger')
                    return redirect(url_for('main.profile'))
            
            # Handle password change if provided
            password_updated = False
            if form.current_password.data and form.current_password.data.strip():
                if not check_password_hash(current_user.password_hash, form.current_password.data):
                    flash('Current password is incorrect.', 'danger')
                    return redirect(url_for('main.profile'))
                
                if form.new_password.data and form.new_password.data.strip():
                    current_user.password_hash = generate_password_hash(form.new_password.data)
                    password_updated = True
                else:
                    flash('New password is required when current password is provided.', 'danger')
                    return redirect(url_for('main.profile'))
            
            # Commit changes
            db.session.commit()
            
            # Success message
            updates = []
            if form.profile_picture.data and form.profile_picture.data.filename:
                updates.append('profile picture')
            if password_updated:
                updates.append('password')
            if form.username.data != form.username.object_data or form.email.data != form.email.object_data:
                updates.append('profile information')
            
            if updates:
                flash(f'Successfully updated: {", ".join(updates)}!', 'success')
            else:
                flash('Profile updated successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    else:
        # Form validation failed
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('main.profile'))

@main.route('/listings')
def listings():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', '')
    search = request.args.get('search', '')
    guests = request.args.get('guests', type=int)
    
    # Only show approved listings to public
    query = Listing.query.filter_by(approved=True)
    
    # Apply search if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Listing.name.ilike(search_term),
                Listing.location.ilike(search_term)
            )
        )
    
    # Apply guest filter if provided
    if guests and guests > 0:
        query = query.filter(Listing.guest_capacity >= guests)
    
    # Apply sorting
    if sort == 'asc':
        query = query.order_by(Listing.price_per_night.asc())
    elif sort == 'desc':
        query = query.order_by(Listing.price_per_night.desc())
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=5, error_out=False)
    listings = pagination.items
    
    return render_template(
        'listings.html',
        listings=listings,
        pagination=pagination,
        search=search,
        sort=sort,
        guests=guests
    )

@main.route('/add-listing', methods=['GET', 'POST'])
@host_required
def add_listing():
    form = ListingForm()
    if form.validate_on_submit():
        # Admin can directly approve listings, hosts need approval
        approved = current_user.is_admin
        
        # Create listing first without image
        listing = Listing(
            name=form.name.data,
            location=form.location.data,
            description=form.description.data,
            price_per_night=float(form.price_per_night.data),
            guest_capacity=int(form.guest_capacity.data),
            host_id=current_user.id,  # Use current user's ID
            host_name=form.host_name.data,
            image_filename=None,  # Will be updated after image upload
            approved=approved
        )
        db.session.add(listing)
        db.session.flush()  # Get the listing ID without committing
        
        # Now handle image upload with listing_id
        if form.image.data and form.image.data.filename:
            image_filename = save_listing_image(form.image.data, listing.id)
            listing.image_filename = image_filename
        
        db.session.commit()
        
        if approved:
            flash('Listing added successfully and is now live!', 'success')
        else:
            flash('Your listing has been submitted and is pending admin approval. You will be notified once it\'s reviewed.', 'info')
        
        return redirect(url_for('main.my_listings'))
    return render_template('add_listing.html', form=form)

@main.route('/edit-listing/<string:listing_id>', methods=['GET', 'POST'])
@owns_listing_or_admin
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    form = ListingForm(obj=listing)
    if form.validate_on_submit():
        form.populate_obj(listing)
        # Handle image upload with automatic renaming
        if form.image.data and form.image.data.filename:
            image_filename = save_listing_image(form.image.data, listing.id)
            listing.image_filename = image_filename
        db.session.commit()
        flash('Listing updated successfully!')
        return redirect(url_for('main.listings'))
    return render_template('edit_listing.html', form=form, listing=listing)

@main.route('/delete-listing/<string:listing_id>', methods=['POST'])
@owns_listing_or_admin
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    try:
        # Delete associated image file if it exists
        if listing.image_filename:
            image_path = os.path.join(current_app.root_path, 'static', 'images', 'listings', listing.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(listing)
        db.session.commit()
        flash('Listing deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting listing: {str(e)}', 'danger')
    
    return redirect(url_for('main.my_listings'))

@main.route('/listing/<string:listing_id>/book', methods=['GET', 'POST'])
@login_required
def book_listing(listing_id):
    # Only guests can book listings
    if current_user.role != UserRole.GUEST:
        flash('Only guests can book listings.', 'warning')
        return redirect(url_for('main.listings'))
    
    listing = Listing.query.get_or_404(listing_id)
    
    # Check if listing is approved
    if not listing.approved:
        flash('This listing is not available for booking.', 'warning')
        return redirect(url_for('main.listings'))
    
    form = BookingForm()
    
    if form.validate_on_submit():
        try:
            # Calculate total price
            from datetime import date
            nights = (form.check_out_date.data - form.check_in_date.data).days
            total_price = float(listing.price_per_night) * nights
            
            # Create booking
            booking = Booking(
                guest_id=current_user.id,
                listing_id=listing.id,
                check_in_date=form.check_in_date.data,
                check_out_date=form.check_out_date.data,
                guest_count=form.guest_count.data,
                total_price=total_price,
                status=BookingStatus.PENDING
            )
            
            # Handle NID upload if provided
            if form.nid_file.data and form.nid_file.data.filename:
                nid_filename = save_nid_file(form.nid_file.data, booking.id)
                booking.nid_filename = nid_filename
            
            db.session.add(booking)
            db.session.commit()
            
            flash('Booking submitted successfully! Please wait for host confirmation.', 'success')
            return redirect(url_for('main.booking_confirmation', booking_id=booking.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating booking: {str(e)}', 'danger')
    
    return render_template('book.html', form=form, listing=listing)

@main.route('/booking/<string:booking_id>/confirmation')
@login_required
def booking_confirmation(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.guest_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('booking_confirmation.html', booking=booking)

@main.route('/my-bookings')
@role_required('guest', 'host')
def my_bookings():
    if current_user.role == UserRole.GUEST:
        # Guests see their own bookings
        bookings = Booking.query.filter_by(guest_id=current_user.id).order_by(Booking.created_at.desc()).all()
        title = 'My Bookings'
    else:
        # Hosts see bookings for their listings
        bookings = Booking.query.join(Listing).filter(Listing.host_id == current_user.id).order_by(Booking.created_at.desc()).all()
        title = 'My Listings - Bookings'
    
    return render_template('my_bookings.html', bookings=bookings, title=title)

@main.route('/booking/<string:booking_id>/update-status', methods=['POST'])
@host_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify this booking belongs to a listing owned by the current host
    if booking.listing.host_id != current_user.id:
        flash('You can only update bookings for your own listings.', 'danger')
        return redirect(url_for('main.my_bookings'))
    
    new_status = request.form.get('status')
    
    if new_status == 'confirmed':
        booking.status = BookingStatus.CONFIRMED
        booking.confirmed_at = datetime.utcnow()
        flash('Booking confirmed!', 'success')
    elif new_status == 'cancelled':
        booking.status = BookingStatus.CANCELLED
        flash('Booking cancelled.', 'warning')
    else:
        flash('Invalid status.', 'danger')
    
    db.session.commit()
    return redirect(url_for('main.my_bookings'))

@main.route('/booking/<string:booking_id>/checkin', methods=['POST'])
@login_required
def checkin(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Only host can check in guests
    if booking.listing.host_id != current_user.id:
        flash('Only the host can perform check-in.', 'danger')
        return redirect(url_for('main.my_bookings'))
    
    if booking.status == BookingStatus.CONFIRMED:
        booking.status = BookingStatus.CHECKED_IN
        booking.checked_in_at = datetime.utcnow()
        db.session.commit()
        flash('Guest checked in successfully!', 'success')
    else:
        flash('Booking must be confirmed before check-in.', 'warning')
    
    return redirect(url_for('main.my_bookings'))

@main.route('/booking/<string:booking_id>/checkout', methods=['POST'])
@login_required
def checkout(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Only host can check out guests
    if booking.listing.host_id != current_user.id:
        flash('Only the host can perform check-out.', 'danger')
        return redirect(url_for('main.my_bookings'))
    
    if booking.status == BookingStatus.CHECKED_IN:
        booking.status = BookingStatus.CHECKED_OUT
        booking.checked_out_at = datetime.utcnow()
        db.session.commit()
        flash('Guest checked out successfully!', 'success')
    else:
        flash('Guest must be checked in before check-out.', 'warning')
    
    return redirect(url_for('main.my_bookings'))

@main.route('/review/<string:booking_id>', methods=['GET', 'POST'])
@login_required
def review_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Only the guest can review their booking
    if booking.guest_id != current_user.id:
        flash('You can only review your own bookings.', 'danger')
        return redirect(url_for('main.my_bookings'))
    
    # Check if booking is completed and can be reviewed
    if booking.status != BookingStatus.CHECKED_OUT:
        flash('You can only review completed bookings.', 'warning')
        return redirect(url_for('main.my_bookings'))
    
    # Check if review already exists
    existing_review = Review.query.filter_by(booking_id=booking.id).first()
    if existing_review:
        flash('You have already reviewed this booking.', 'info')
        return redirect(url_for('main.my_bookings'))
    
    form = ReviewForm()
    
    if form.validate_on_submit():
        try:
            review = Review(
                reviewer_id=current_user.id,
                reviewee_id=booking.listing.host_id,
                listing_id=booking.listing.id,
                booking_id=booking.id,
                rating=form.rating.data,
                comment=form.comment.data
            )
            
            db.session.add(review)
            db.session.commit()
            
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('main.my_bookings'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting review: {str(e)}', 'danger')
    
    return render_template('review.html', form=form, booking=booking)

@main.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    user_query = User.query
    if q:
        user_query = user_query.filter(
            or_(
                User.username.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%'),
                User.role.ilike(f'%{q}%')
            )
        )
    user_query = user_query.order_by(User.username.asc())
    pagination = user_query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    # Split users into hosts and guests for tables
    hosts = [u for u in users if u.role == UserRole.HOST]
    guests = [u for u in users if u.role == UserRole.GUEST]
    # Analytics
    total_users = User.query.count()
    total_hosts = User.query.filter_by(role=UserRole.HOST).count()
    total_listings = Listing.query.count()
    total_bookings = Booking.query.count()
    
    # Get recent bookings for admin review
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    # Get host verification data
    pending_hosts_count = User.query.filter_by(role=UserRole.HOST, is_verified=False).count()
    verified_hosts_count = User.query.filter_by(role=UserRole.HOST, is_verified=True).count()
    
    # Get host NID upload statistics
    hosts_with_nid = User.query.filter_by(role=UserRole.HOST).filter(User.nid_filename.isnot(None)).count()
    hosts_without_nid = User.query.filter_by(role=UserRole.HOST).filter(User.nid_filename.is_(None)).count()
    
    # Host/guest data for tables
    host_data = [
        {
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': 'Host',
            'total_listings': Listing.query.filter_by(host_id=u.id).count(),
            'is_verified': u.is_verified,
            'nid_filename': u.nid_filename
        } for u in hosts
    ]
    guest_data = [
        {
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': 'Guest',
            'total_bookings': 0  # Placeholder
        } for u in guests
    ]
    return render_template('admin_dashboard.html',
        hosts=host_data,
        guests=guest_data,
        pagination=pagination,
        q=q,
        total_users=total_users,
        total_hosts=total_hosts,
        total_listings=total_listings,
        total_bookings=total_bookings,
        recent_bookings=recent_bookings,
        pending_hosts_count=pending_hosts_count,
        verified_hosts_count=verified_hosts_count,
        hosts_with_nid=hosts_with_nid,
        hosts_without_nid=hosts_without_nid
    )

@main.route('/admin/listings/pending')
@admin_required
def admin_pending_listings():
    """Admin panel for managing pending listings"""
    pending_listings = Listing.query.filter_by(approved=False).order_by(Listing.created_at.desc()).all()
    approved_count = Listing.query.filter_by(approved=True).count()
    pending_count = len(pending_listings)
    
    return render_template('admin/pending_listings.html', 
                         listings=pending_listings,
                         approved_count=approved_count,
                         pending_count=pending_count)

@main.route('/admin/listing/<string:listing_id>/approve', methods=['POST'])
@admin_required
def admin_approve_listing(listing_id):
    """Approve a pending listing"""
    listing = Listing.query.get_or_404(listing_id)
    listing.approved = True
    listing.status = ListingStatus.APPROVED
    db.session.commit()
    flash(f'Listing "{listing.name}" has been approved and is now live!', 'success')
    return redirect(url_for('main.admin_pending_listings'))

@main.route('/admin/listing/<string:listing_id>/reject', methods=['POST'])
@admin_required  
def admin_reject_listing(listing_id):
    """Reject/delete a pending listing"""
    listing = Listing.query.get_or_404(listing_id)
    listing_name = listing.name
    
    try:
        # Delete associated image file if it exists
        if listing.image_filename:
            image_path = os.path.join(current_app.root_path, 'static', 'images', 'listings', listing.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        listing.status = ListingStatus.REJECTED
        db.session.commit()
        flash(f'Listing "{listing_name}" has been rejected.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting listing: {str(e)}', 'danger')
    
    return redirect(url_for('main.admin_pending_listings'))

@main.route('/admin/user/<string:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(original_email=user.email, obj=user)
    
    if form.validate_on_submit():
        user.email = form.email.data
        user.role = UserRole(form.role.data)
        try:
            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('main.admin_dashboard', q=request.args.get('q', '')))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    else:
        # Flash form validation errors
        for field in form:
            for error in field.errors:
                flash(f"{field.label.text}: {error}", "danger")
    
    return render_template('edit_user.html', user=user, form=form)

@main.route('/admin/user/<string:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting own account
    if user.id == current_user.id:
        flash('You cannot delete your own admin account.', 'danger')
        return redirect(url_for('main.admin_dashboard', q=request.args.get('q', '')))
    
    # Prevent deleting if this is the only admin
    if not user.can_be_deleted():
        flash('Cannot delete the only admin user. Create another admin first.', 'danger')
        return redirect(url_for('main.admin_dashboard', q=request.args.get('q', '')))
    
    username = user.username
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f'User "{username}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')
    
    return redirect(url_for('main.admin_dashboard', q=request.args.get('q', '')))

@main.route('/admin/hosts/pending')
@admin_required
def admin_pending_hosts():
    """Admin route to view pending host verifications"""
    pending_hosts = User.query.filter_by(role=UserRole.HOST, is_verified=False).order_by(User.created_at.desc()).all()
    verified_hosts = User.query.filter_by(role=UserRole.HOST, is_verified=True).count()
    
    return render_template('admin/pending_hosts.html', 
                         pending_hosts=pending_hosts,
                         verified_hosts=verified_hosts,
                         pending_count=len(pending_hosts))

@main.route('/admin/host/<string:host_id>/verify', methods=['POST'])
@admin_required
def admin_verify_host(host_id):
    """Admin route to verify a host"""
    host = User.query.get_or_404(host_id)
    
    # Security check: only verify hosts
    if host.role != UserRole.HOST:
        flash('This user is not a host account.', 'danger')
        return redirect(url_for('main.admin_pending_hosts'))
    
    # Verify the host
    host.is_verified = True
    db.session.commit()
    
    flash(f'Host "{host.username}" has been verified successfully!', 'success')
    return redirect(url_for('main.admin_pending_hosts'))

@main.route('/admin/host/<string:host_id>/unverify', methods=['POST'])
@admin_required
def admin_unverify_host(host_id):
    """Admin route to remove verification from a host"""
    host = User.query.get_or_404(host_id)
    
    # Security check: only unverify hosts
    if host.role != UserRole.HOST:
        flash('This user is not a host account.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    # Remove verification
    host.is_verified = False
    db.session.commit()
    
    flash(f'Host "{host.username}" verification has been removed.', 'warning')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/nid/<string:booking_id>')
@admin_required
def admin_view_nid(booking_id):
    """Admin route to view NID document for a booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    if not booking.nid_filename:
        flash('No NID document uploaded for this booking.', 'warning')
        return redirect(url_for('main.admin_dashboard'))
    
    # Construct file path
    file_path = os.path.join(current_app.root_path, 'static', 'nid_uploads', booking.nid_filename)
    
    if not os.path.exists(file_path):
        flash('NID document file not found.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    # Determine file type and serve appropriately
    file_ext = os.path.splitext(booking.nid_filename)[1].lower()
    
    if file_ext in ['.jpg', '.jpeg', '.png']:
        # For images, serve inline
        return send_file(file_path, mimetype='image/' + file_ext[1:])
    elif file_ext == '.pdf':
        # For PDFs, serve as download
        return send_file(file_path, as_attachment=True, download_name=booking.nid_filename)
    else:
        flash('Unsupported file type.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/host-nid/<string:user_id>')
@admin_required
def admin_view_host_nid(user_id):
    """Admin route to view NID document for a host"""
    user = User.query.get_or_404(user_id)
    
    if user.role != UserRole.HOST:
        flash('This user is not a host.', 'warning')
        return redirect(url_for('main.admin_dashboard'))
    
    if not user.nid_filename:
        flash('No NID document uploaded for this host.', 'warning')
        return redirect(url_for('main.admin_dashboard'))
    
    # Construct file path
    file_path = os.path.join(current_app.root_path, 'static', 'nid_host_uploads', user.nid_filename)
    
    if not os.path.exists(file_path):
        flash('NID document file not found.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    
    # Determine file type and serve appropriately
    file_ext = os.path.splitext(user.nid_filename)[1].lower()
    
    if file_ext in ['.jpg', '.jpeg', '.png']:
        # For images, serve inline
        return send_file(file_path, mimetype='image/' + file_ext[1:])
    elif file_ext == '.pdf':
        # For PDFs, serve as download
        return send_file(file_path, as_attachment=True, download_name=user.nid_filename)
    else:
        flash('Unsupported file type.', 'danger')
        return redirect(url_for('main.admin_dashboard'))

# Role-based redirect routes
@main.route('/host/dashboard')
@host_required
def host_dashboard():
    """Placeholder host dashboard - redirects to my listings for now"""
    return redirect(url_for('main.my_listings'))

@main.route('/browse')
def browse():
    """Placeholder browse page - redirects to listings for now"""
    return redirect(url_for('main.listings'))

@main.app_errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Roll back db session in case of database error
    return render_template('500.html'), 500

# Messaging Routes

@main.route('/messages')
@login_required
def messages():
    """Display all conversations for the current user"""
    # Get conversations using improved query
    conversations = (Conversation.query
                   .filter(db.or_(
                       Conversation.user1_id == current_user.id,
                       Conversation.user2_id == current_user.id
                   ))
                   .join(Message)  # Only show conversations that have messages
                   .order_by(Conversation.last_message_at.desc())
                   .distinct()
                   .all())
    
    # Debug information for troubleshooting
    total_unread = (Message.query
                   .join(Conversation)
                   .filter(
                       Message.recipient_id == current_user.id,
                       Message.is_read == False,
                       db.or_(
                           Conversation.user1_id == current_user.id,
                           Conversation.user2_id == current_user.id
                       )
                   ).count())
    
    print(f"DEBUG: User {current_user.username} has {len(conversations)} conversations and {total_unread} unread messages")
    
    return render_template('messages.html', conversations=conversations, total_unread=total_unread)

@main.route('/messages/<string:conversation_id>')
@login_required
def view_conversation(conversation_id):
    """Display messages for a specific conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Check if current user is part of this conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        abort(403)
    
    # Mark messages as read for current user
    conversation.mark_messages_as_read(current_user.id)
    
    # Get all messages in conversation
    messages = conversation.messages.order_by(Message.created_at.asc()).all()
    
    # Get the other user in conversation
    other_user = conversation.get_other_user(current_user.id)
    
    form = MessageForm()
    
    return render_template('conversation.html', 
                         conversation=conversation,
                         messages=messages,
                         other_user=other_user,
                         form=form)

@main.route('/messages/<string:conversation_id>/send', methods=['POST'])
@login_required
def send_message(conversation_id):
    """Send a message in a conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Check if current user is part of this conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        abort(403)
    
    form = MessageForm()
    
    if form.validate_on_submit():
        try:
            # Determine recipient
            recipient_id = conversation.user2_id if conversation.user1_id == current_user.id else conversation.user1_id
            
            # Create message
            message = Message(
                conversation_id=conversation.id,
                sender_id=current_user.id,
                recipient_id=recipient_id,
                content=form.content.data
            )
            
            db.session.add(message)
            
            # Update conversation's last_message_at
            conversation.last_message_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Message sent successfully!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error sending message: {str(e)}', 'danger')
    
    return redirect(url_for('main.view_conversation', conversation_id=conversation_id))

@main.route('/start-conversation/<string:user_id>')
@login_required
def start_conversation(user_id):
    """Start a new conversation with another user"""
    other_user = User.query.get_or_404(user_id)
    
    # Prevent starting conversation with yourself
    if other_user.id == current_user.id:
        flash('You cannot start a conversation with yourself.', 'warning')
        return redirect(url_for('main.messages'))
    
    # Check if conversation already exists
    existing_conversation = Conversation.query.filter(
        or_(
            and_(Conversation.user1_id == current_user.id, Conversation.user2_id == other_user.id),
            and_(Conversation.user1_id == other_user.id, Conversation.user2_id == current_user.id)
        )
    ).first()
    
    if existing_conversation:
        return redirect(url_for('main.view_conversation', conversation_id=existing_conversation.id))
    
    # Create new conversation
    try:
        conversation = Conversation(
            user1_id=current_user.id,
            user2_id=other_user.id
        )
        
        db.session.add(conversation)
        db.session.commit()
        
        flash(f'Started conversation with {other_user.username}!', 'success')
        return redirect(url_for('main.view_conversation', conversation_id=conversation.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error starting conversation: {str(e)}', 'danger')
        return redirect(url_for('main.messages'))