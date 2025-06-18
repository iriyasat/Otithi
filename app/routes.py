import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Listing, User, Booking, Review, Conversation, Message
from . import db
from .forms import ListingForm, RegisterForm, LoginForm, BookingForm, ReviewForm, EditUserForm, ProfileSettingsForm, MessageForm
from .decorators import role_required, admin_required, host_required, guest_required, owns_listing_or_admin
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
                    role=form.account_type.data,
                    is_admin=False,  # Explicitly set to False for security
                    password_hash=generate_password_hash(form.password.data)
                )
                
                db.session.add(user)
                db.session.commit()
                
                flash(f'Registration successful as a {form.account_type.data.title()}! Please log in.', 'success')
                return redirect(url_for('main.login'))
                
            except Exception as e:
                db.session.rollback()
                print(f"DEBUG: Database error during registration: {str(e)}")
                flash('An error occurred during registration. Please try again.', 'danger')
                return render_template('register.html', form=form)
        else:
            # Form validation failed - show specific errors
            print(f"DEBUG: Form validation failed with errors: {form.errors}")
            flash('Please correct the errors below and try again.', 'danger')
    
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful. Welcome back, {}!'.format(current_user.username), 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            # Role-based redirect after login
            if current_user.is_admin:
                return redirect(url_for('main.admin_dashboard'))
            elif current_user.role == 'host':
                return redirect(url_for('main.host_dashboard'))
            else:
                return redirect(url_for('main.browse'))
        else:
            flash('Invalid username or password.', 'danger')
    else:
        # Debug: Show form validation errors if form doesn't validate
        if request.method == 'POST':
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
@role_required('host', 'admin')
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
@role_required('host', 'admin')
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

@main.route('/edit-listing/<int:listing_id>', methods=['GET', 'POST'])
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

@main.route('/delete-listing/<int:listing_id>', methods=['POST'])
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

@main.route('/listing/<int:listing_id>/book', methods=['GET', 'POST'])
@login_required
def book_listing(listing_id):
    # Only guests can book listings
    if current_user.role != 'guest':
        flash('Only guests can book listings!', 'danger')
        return redirect(url_for('main.browse'))
    
    form = BookingForm()
    listing = Listing.query.get_or_404(listing_id)
    
    # Check if listing is approved
    if not listing.approved:
        flash('This listing is not available for booking.', 'danger')
        return redirect(url_for('main.browse'))
    
    # Check if user is trying to book their own listing
    if listing.host_id == current_user.id:
        flash('You cannot book your own listing!', 'danger')
        return redirect(url_for('main.browse'))
    
    if form.validate_on_submit():
        # Validate check-in and check-out dates
        if form.check_out.data <= form.check_in.data:
            flash('Check-out date must be after check-in date!', 'danger')
            return render_template('book.html', form=form, listing=listing)
        
        # Validate check-in is not in the past
        if form.check_in.data < date.today():
            flash('Check-in date cannot be in the past!', 'danger')
            return render_template('book.html', form=form, listing=listing)
        
        # Validate guest count doesn't exceed listing capacity
        if form.guest_count.data > listing.guest_capacity:
            flash(f'This listing can accommodate maximum {listing.guest_capacity} guests. Please reduce the number of guests.', 'danger')
            return render_template('book.html', form=form, listing=listing)
        
        # Check for conflicting bookings
        existing_booking = Booking.query.filter(
            Booking.listing_id == listing.id,
            Booking.status.in_(['pending', 'confirmed']),
            Booking.check_in < form.check_out.data,
            Booking.check_out > form.check_in.data
        ).first()
        
        if existing_booking:
            flash('These dates are not available. Please select different dates.', 'danger')
            return render_template('book.html', form=form, listing=listing)
        
        # Calculate cost
        days = (form.check_out.data - form.check_in.data).days
        total_cost = days * listing.price_per_night
        
        # Create booking
        booking = Booking(
            guest_id=current_user.id,
            listing_id=listing.id,
            check_in=form.check_in.data,
            check_out=form.check_out.data,
            guest_count=form.guest_count.data
        )
        db.session.add(booking)
        db.session.commit()
        
        flash(f'Booking request sent for {form.guest_count.data} guests, {days} nights (৳{total_cost:.2f} total)! The host will review your request.', 'success')
        return redirect(url_for('main.my_bookings'))

    return render_template('book.html', form=form, listing=listing)

@main.route('/booking/<int:booking_id>/confirmation')
@login_required
def booking_confirmation(booking_id):
    """Show booking confirmation page"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Only the guest who made the booking can view this
    if booking.guest_id != current_user.id:
        abort(403)
    
    return render_template('booking_confirmation.html', booking=booking)

@main.route('/my-bookings')
@role_required('guest', 'host')
def my_bookings():
    if current_user.role == 'guest':
        # Show bookings made by this guest
        bookings = Booking.query.filter_by(guest_id=current_user.id).order_by(Booking.created_at.desc()).all()
        title = "My Bookings"
    else:
        # Show bookings for listings owned by this host using proper join
        bookings = Booking.query \
            .join(Listing, Booking.listing_id == Listing.id) \
            .filter(Listing.host_id == current_user.id) \
            .order_by(Booking.created_at.desc()) \
            .all()
        title = "Booking Requests"
    
    # Pass current date for template logic
    today = date.today()
    return render_template('my_bookings.html', bookings=bookings, title=title, today=today)

@main.route('/booking/<int:booking_id>/update-status', methods=['POST'])
@role_required('host', 'admin')
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    listing = booking.listing
    
    # Only the host of the listing or admin can update booking status
    if not current_user.is_admin and listing.host_id != current_user.id:
        abort(403)
    
    new_status = request.form.get('status')
    if new_status in ['confirmed', 'cancelled']:
        old_status = booking.status
        booking.status = new_status
        db.session.commit()
        
        # Notify guest about status change
        action = "confirmed" if new_status == 'confirmed' else "cancelled"
        flash(f'Booking request {action} successfully! Guest will be notified.', 'success')
        
        # Add notification logic here if needed
        
    else:
        flash('Invalid status update!', 'danger')
    
    return redirect(url_for('main.my_bookings'))

@main.route('/booking/<int:booking_id>/checkin', methods=['POST'])
@login_required
def checkin(booking_id):
    """Allow guest to check in to their booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Only the guest can check in
    if booking.guest_id != current_user.id:
        abort(403)
    
    # Check if check-in is allowed
    if not booking.can_check_in():
        flash('Check-in is not available for this booking. Please ensure it is confirmed and within the check-in period.', 'warning')
        return redirect(url_for('main.my_bookings'))
    
    booking.status = 'checked_in'
    db.session.commit()
    flash('You have checked in successfully! Enjoy your stay.', 'success')
    return redirect(url_for('main.my_bookings'))

@main.route('/booking/<int:booking_id>/checkout', methods=['POST'])
@login_required
def checkout(booking_id):
    """Allow guest to check out of their booking"""
    booking = Booking.query.get_or_404(booking_id)
    
    # Only the guest can check out
    if booking.guest_id != current_user.id:
        abort(403)
    
    # Check if check-out is allowed
    if not booking.can_check_out():
        flash('Check-out is not available. You must be checked in first.', 'warning')
        return redirect(url_for('main.my_bookings'))
    
    booking.status = 'checked_out'
    booking.actual_checkout = datetime.utcnow()
    db.session.commit()
    flash('You have checked out successfully! Thank you for your stay. Please consider leaving a review.', 'success')
    return redirect(url_for('main.my_bookings'))

@main.route('/review/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def review_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    
    # Verify user is either guest or host of this booking
    if current_user.id != booking.guest_id and current_user.id != booking.listing.host_id:
        abort(403)
    
    # Check if review is allowed - allow for checked_out status immediately
    if booking.status != 'checked_out':
        flash('You can only review this booking after checking out.', 'warning')
        return redirect(url_for('main.my_bookings'))
    
    form = ReviewForm()

    if form.validate_on_submit():
        # Prevent duplicate reviews for same booking and same direction
        existing = Review.query.filter_by(booking_id=booking.id, reviewer_id=current_user.id).first()
        if existing:
            flash('You already submitted a review for this booking.', 'info')
            return redirect(url_for('main.my_bookings'))

        # Determine who is being reviewed
        if current_user.id == booking.guest_id:
            # Guest is reviewing the host
            reviewed_user_id = booking.listing.host_id
            reviewer_type = 'guest'
            reviewed_type = 'host'
        else:
            # Host is reviewing the guest
            reviewed_user_id = booking.guest_id
            reviewer_type = 'host'
            reviewed_type = 'guest'

        review = Review(
            reviewer_id=current_user.id,
            reviewed_id=reviewed_user_id,
            booking_id=booking.id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        flash(f'Review submitted successfully! You rated the {reviewed_type}.', 'success')
        return redirect(url_for('main.my_bookings'))

    # Determine who is being reviewed for display
    if current_user.id == booking.guest_id:
        reviewed_user = booking.listing.host
        review_target = 'host'
    else:
        reviewed_user = booking.guest
        review_target = 'guest'

    return render_template('review.html', form=form, booking=booking, reviewed_user=reviewed_user, review_target=review_target)

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
    hosts = [u for u in users if u.role == 'host']
    guests = [u for u in users if u.role == 'guest']
    # Analytics
    total_users = User.query.count()
    total_hosts = User.query.filter_by(role='host').count()
    total_listings = Listing.query.count()
    # Host/guest data for tables
    host_data = [
        {
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': 'Host',
            'total_listings': Listing.query.filter_by(host_id=u.id).count()
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
        total_listings=total_listings
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

@main.route('/admin/listing/<int:listing_id>/approve', methods=['POST'])
@admin_required
def admin_approve_listing(listing_id):
    """Approve a pending listing"""
    listing = Listing.query.get_or_404(listing_id)
    listing.approved = True
    db.session.commit()
    flash(f'Listing "{listing.name}" has been approved and is now live!', 'success')
    return redirect(url_for('main.admin_pending_listings'))

@main.route('/admin/listing/<int:listing_id>/reject', methods=['POST'])
@admin_required  
def admin_reject_listing(listing_id):
    """Reject/delete a pending listing"""
    listing = Listing.query.get_or_404(listing_id)
    listing_name = listing.name
    
    try:
        # Delete associated image file if it exists
        if listing.image_filename:
            image_path = os.path.join(current_app.root_path, 'static', 'images', listing.image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(listing)
        db.session.commit()
        flash(f'Listing "{listing_name}" has been rejected and removed.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting listing: {str(e)}', 'danger')
    
    return redirect(url_for('main.admin_pending_listings'))

@main.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(original_email=user.email, obj=user)
    
    if form.validate_on_submit():
        user.email = form.email.data
        user.role = form.role.data
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

@main.route('/admin/user/<int:user_id>/delete', methods=['POST'])
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

@main.route('/messages/<int:conversation_id>')
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

@main.route('/messages/<int:conversation_id>/send', methods=['POST'])
@login_required
def send_message(conversation_id):
    """Send a message in a conversation"""
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Check if current user is part of this conversation
    if conversation.user1_id != current_user.id and conversation.user2_id != current_user.id:
        abort(403)
    
    form = MessageForm()
    
    if form.validate_on_submit():
        # Determine recipient
        recipient_id = conversation.user2_id if conversation.user1_id == current_user.id else conversation.user1_id
        
        # Create new message
        message = Message(
            conversation_id=conversation.id,
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=form.content.data
        )
        
        # Update conversation last message time
        conversation.last_message_at = datetime.utcnow()
        
        db.session.add(message)
        db.session.commit()
        
        flash('Message sent successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{error}', 'danger')
    
    return redirect(url_for('main.view_conversation', conversation_id=conversation_id))

@main.route('/start-conversation/<int:user_id>')
@login_required
def start_conversation(user_id):
    """Start a new conversation with another user"""
    other_user = User.query.get_or_404(user_id)
    
    # Don't allow messaging yourself
    if other_user.id == current_user.id:
        flash('You cannot message yourself!', 'danger')
        return redirect(url_for('main.messages'))
    
    # Check if conversation already exists
    existing_conversation = current_user.get_conversation_with(other_user.id)
    
    if existing_conversation:
        return redirect(url_for('main.view_conversation', conversation_id=existing_conversation.id))
    
    # Create new conversation
    conversation = Conversation(
        user1_id=min(current_user.id, other_user.id),  # Keep user1_id as the smaller ID for consistency
        user2_id=max(current_user.id, other_user.id)
    )
    
    db.session.add(conversation)
    db.session.commit()
    
    flash(f'Started conversation with {other_user.username}!', 'success')
    return redirect(url_for('main.view_conversation', conversation_id=conversation.id))