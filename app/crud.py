"""
CRUD Operations for Otithi Platform
Clean, reusable database operations for all models.
No test data, just pure business logic.
"""
from . import db
from .models import User, Listing, Booking, Review
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from datetime import date


# =============================================================================
# USER OPERATIONS
# =============================================================================

def get_user_by_id(user_id):
    """Get user by ID"""
    try:
        return User.query.get(user_id)
    except SQLAlchemyError:
        return None


def create_user(username, email, role, password, is_admin=False):
    """Create a new user"""
    try:
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role,
            is_admin=is_admin
        )
        db.session.add(user)
        db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def update_user(user_id, **kwargs):
    """Update user with provided fields"""
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        
        # Handle password separately
        if 'password' in kwargs:
            user.password_hash = generate_password_hash(kwargs.pop('password'))
        
        # Update other fields
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def delete_user(user_id):
    """Delete user if allowed"""
    try:
        user = User.query.get(user_id)
        if not user:
            return False
        
        # Use the model's safety check
        if not user.can_be_deleted():
            return False
        
        db.session.delete(user)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


# =============================================================================
# LISTING OPERATIONS
# =============================================================================

def get_listing_by_id(listing_id):
    """Get listing by ID"""
    try:
        return Listing.query.get(listing_id)
    except SQLAlchemyError:
        return None


def create_listing(name, location, description, price_per_night, host_id, host_name, image_filename=None, approved=False):
    """Create a new listing"""
    try:
        listing = Listing(
            name=name,
            location=location,
            description=description,
            price_per_night=price_per_night,
            host_id=host_id,
            host_name=host_name,
            image_filename=image_filename,
            approved=approved
        )
        db.session.add(listing)
        db.session.commit()
        return listing
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def update_listing(listing_id, **kwargs):
    """Update listing with provided fields"""
    try:
        listing = Listing.query.get(listing_id)
        if not listing:
            return None
        
        for key, value in kwargs.items():
            if hasattr(listing, key):
                setattr(listing, key, value)
        
        db.session.commit()
        return listing
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def delete_listing(listing_id):
    """Delete listing and associated data"""
    try:
        listing = Listing.query.get(listing_id)
        if not listing:
            return False
        
        db.session.delete(listing)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def approve_listing(listing_id):
    """Approve a pending listing"""
    try:
        listing = Listing.query.get(listing_id)
        if not listing:
            return None
        
        listing.approved = True
        db.session.commit()
        return listing
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_approved_listings():
    """Get all approved listings"""
    try:
        return Listing.query.filter_by(approved=True).all()
    except SQLAlchemyError:
        return []


def get_listings_by_host(host_id):
    """Get all listings by host ID"""
    try:
        return Listing.query.filter_by(host_id=host_id).all()
    except SQLAlchemyError:
        return []


# =============================================================================
# BOOKING OPERATIONS
# =============================================================================

def create_booking(guest_id, listing_id, check_in, check_out, status='pending'):
    """Create a new booking"""
    try:
        booking = Booking(
            guest_id=guest_id,
            listing_id=listing_id,
            check_in=check_in,
            check_out=check_out,
            status=status
        )
        db.session.add(booking)
        db.session.commit()
        return booking
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_bookings_by_guest(guest_id):
    """Get all bookings made by a guest"""
    try:
        return Booking.query.filter_by(guest_id=guest_id).order_by(Booking.created_at.desc()).all()
    except SQLAlchemyError:
        return []


def get_bookings_by_host(host_id):
    """Get all booking requests for listings owned by host"""
    try:
        return db.session.query(Booking).join(Listing).filter(
            Listing.host_id == host_id
        ).order_by(Booking.created_at.desc()).all()
    except SQLAlchemyError:
        return []


def update_booking_status(booking_id, status):
    """Update booking status (pending, confirmed, cancelled)"""
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return None
        
        if status in ['pending', 'confirmed', 'cancelled']:
            booking.status = status
            db.session.commit()
            return booking
        else:
            raise ValueError(f"Invalid status: {status}")
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_booking_by_id(booking_id):
    """Get booking by ID"""
    try:
        return Booking.query.get(booking_id)
    except SQLAlchemyError:
        return None


# =============================================================================
# REVIEW OPERATIONS
# =============================================================================

def create_review(from_user_id, to_user_id, booking_id, rating, comment=None):
    """Create a new review"""
    try:
        # Verify booking exists and is completed
        booking = Booking.query.get(booking_id)
        if not booking or not booking.can_be_reviewed():
            raise ValueError("Booking cannot be reviewed")
        
        # Check for duplicate review
        existing = Review.query.filter_by(
            booking_id=booking_id,
            reviewer_id=from_user_id
        ).first()
        if existing:
            raise ValueError("Review already exists for this booking")
        
        review = Review(
            reviewer_id=from_user_id,
            reviewed_id=to_user_id,
            booking_id=booking_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review)
        db.session.commit()
        return review
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_reviews_for_user(user_id):
    """Get all reviews received by a user"""
    try:
        return Review.query.filter_by(reviewed_id=user_id).order_by(Review.created_at.desc()).all()
    except SQLAlchemyError:
        return []


def get_reviews_written_by_user(user_id):
    """Get all reviews written by a user"""
    try:
        return Review.query.filter_by(reviewer_id=user_id).order_by(Review.created_at.desc()).all()
    except SQLAlchemyError:
        return []


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_pending_listings():
    """Get all listings pending approval"""
    try:
        return Listing.query.filter_by(approved=False).order_by(Listing.created_at.desc()).all()
    except SQLAlchemyError:
        return []


def get_completed_bookings_by_user(user_id):
    """Get completed bookings for review reminders"""
    try:
        today = date.today()
        return Booking.query.filter(
            Booking.guest_id == user_id,
            Booking.status == 'confirmed',
            Booking.check_out < today
        ).all()
    except SQLAlchemyError:
        return []


def search_listings(query=None, location=None, approved_only=True):
    """Search listings with optional filters"""
    try:
        listings = Listing.query
        
        if approved_only:
            listings = listings.filter_by(approved=True)
        
        if query:
            search_term = f"%{query}%"
            listings = listings.filter(
                db.or_(
                    Listing.name.ilike(search_term),
                    Listing.description.ilike(search_term)
                )
            )
        
        if location:
            location_term = f"%{location}%"
            listings = listings.filter(Listing.location.ilike(location_term))
        
        return listings.all()
    except SQLAlchemyError:
        return []


# =============================================================================
# TEST SECTION (for development only)
# =============================================================================

if __name__ == '__main__':
    """
    Test CRUD operations - run with: python -m app.crud
    """
    from app import create_app
    
    app = create_app()
    with app.app_context():
        print("🧪 Testing CRUD Operations...")
        print("=" * 40)
        
        # Test user operations
        users = User.query.all()
        print(f"📊 Total Users: {len(users)}")
        
        if users:
            first_user = users[0]
            print(f"👤 First User: {first_user.username} ({first_user.role})")
        
        # Test listing operations
        approved_listings = get_approved_listings()
        pending_listings = get_pending_listings()
        print(f"🏠 Approved Listings: {len(approved_listings)}")
        print(f"⏳ Pending Listings: {len(pending_listings)}")
        
        # Test booking operations
        all_bookings = Booking.query.all()
        print(f"📅 Total Bookings: {len(all_bookings)}")
        
        # Test review operations
        all_reviews = Review.query.all()
        print(f"⭐ Total Reviews: {len(all_reviews)}")
        
        print("\n✅ CRUD module is working correctly!")
        print("💡 Import this module in routes.py, admin.py, etc.")


# =============================================================================
# EXPORTABLE FUNCTIONS FOR ROUTES
# =============================================================================

__all__ = [
    # Users
    'get_user_by_id', 'create_user', 'update_user', 'delete_user',

    # Listings
    'get_listing_by_id', 'create_listing', 'update_listing', 'delete_listing',
    'approve_listing', 'get_approved_listings', 'get_listings_by_host',
    'get_pending_listings', 'search_listings',

    # Bookings
    'create_booking', 'get_bookings_by_guest', 'get_bookings_by_host',
    'update_booking_status', 'get_booking_by_id',
    'get_completed_bookings_by_user',

    # Reviews
    'create_review', 'get_reviews_for_user', 'get_reviews_written_by_user',
]

# =============================================================================
# USAGE EXAMPLES FOR ROUTES
# =============================================================================

"""
Quick Reference for Routes/Views:

# Import what you need:
from app.crud import (
    create_user, get_user_by_id,
    create_listing, get_approved_listings,
    create_booking, get_bookings_by_guest,
    create_review
)

# User Operations:
user = create_user("amir", "amir@email.com", "host", "secret123")
user = get_user_by_id(1)
updated_user = update_user(1, username="new_name")

# Listing Operations:
listing = create_listing("Cozy Home", "Dhaka", "Nice place", 2500.0, host_id=1, host_name="Amir")
listings = get_approved_listings()
host_listings = get_listings_by_host(host_id=1)
results = search_listings(query="cozy", location="dhaka")

# Booking Operations:
booking = create_booking(guest_id=2, listing_id=1, check_in=date(2025,6,1), check_out=date(2025,6,5))
guest_bookings = get_bookings_by_guest(guest_id=2)
host_bookings = get_bookings_by_host(host_id=1)
updated_booking = update_booking_status(booking_id=1, status='confirmed')

# Review Operations:
review = create_review(from_user_id=2, to_user_id=1, booking_id=1, rating=5, comment="Great host!")
user_reviews = get_reviews_for_user(user_id=1)
written_reviews = get_reviews_written_by_user(user_id=2)

# Admin Operations:
pending = get_pending_listings()
approved_listing = approve_listing(listing_id=1)
""" 