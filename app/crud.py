"""
CRUD Operations for Otithi Platform
Clean, reusable database operations for all models.
No test data, just pure business logic.
"""
from . import db
from .models import User, Listing, Booking, Review, Conversation, Message
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_, and_
from datetime import date, datetime
import os
from PIL import Image


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


def update_profile_picture(user_id, filename):
    """Handle profile picture upload, resize, and save to database"""
    try:
        user = User.query.get(user_id)
        if not user:
            return None
            
        # Generate new filename with user ID
        file_extension = filename.rsplit('.', 1)[1].lower()
        new_filename = f"user_{user_id}.{file_extension}"
        
        # Save to database
        user.profile_picture = new_filename
        db.session.commit()
        
        return new_filename
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


def create_listing(name, location, description, price_per_night, host_id, host_name, 
                  guest_capacity=1, image_filename=None, approved=False):
    """Create a new listing with guest capacity support"""
    try:
        listing = Listing(
            name=name,
            location=location,
            description=description,
            price_per_night=price_per_night,
            guest_capacity=guest_capacity,
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


def search_listings(query=None, location=None, guest_count=None, approved_only=True):
    """Search listings with optional filters including guest capacity"""
    try:
        listings = Listing.query
        
        if approved_only:
            listings = listings.filter_by(approved=True)
        
        if query:
            search_term = f"%{query}%"
            listings = listings.filter(
                or_(
                    Listing.name.ilike(search_term),
                    Listing.description.ilike(search_term)
                )
            )
        
        if location:
            location_term = f"%{location}%"
            listings = listings.filter(Listing.location.ilike(location_term))
            
        if guest_count:
            # Only show listings that can accommodate the requested number of guests
            listings = listings.filter(Listing.guest_capacity >= guest_count)
        
        return listings.all()
    except SQLAlchemyError:
        return []


# =============================================================================
# BOOKING OPERATIONS
# =============================================================================

def create_booking(guest_id, listing_id, check_in, check_out, guest_count=1, status='pending'):
    """Create a new booking with guest count validation"""
    try:
        # Validate guest capacity
        listing = Listing.query.get(listing_id)
        if listing and guest_count > listing.guest_capacity:
            raise ValueError(f"Guest count ({guest_count}) exceeds listing capacity ({listing.guest_capacity})")
            
        booking = Booking(
            guest_id=guest_id,
            listing_id=listing_id,
            check_in=check_in,
            check_out=check_out,
            guest_count=guest_count,
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
    """Update booking status (pending, confirmed, checked_in, checked_out, cancelled)"""
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return None
        
        valid_statuses = ['pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled']
        if status in valid_statuses:
            booking.status = status
            
            # Set actual checkout time when checking out
            if status == 'checked_out':
                booking.actual_checkout = datetime.utcnow()
                
            db.session.commit()
            return booking
        else:
            raise ValueError(f"Invalid status: {status}")
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def check_in_booking(booking_id):
    """Check in a guest to their booking"""
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return None
            
        if not booking.can_check_in():
            raise ValueError("Cannot check in to this booking")
            
        booking.status = 'checked_in'
        db.session.commit()
        return booking
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def check_out_booking(booking_id):
    """Check out a guest from their booking"""
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            return None
            
        if not booking.can_check_out():
            raise ValueError("Cannot check out from this booking")
            
        booking.status = 'checked_out'
        booking.actual_checkout = datetime.utcnow()
        db.session.commit()
        return booking
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
    """Get all reviews received by a user (real-time data only)"""
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


def get_latest_reviews(limit=2, min_rating=4):
    """Get latest high-quality reviews for homepage display"""
    try:
        return (Review.query
                .filter(Review.rating >= min_rating)
                .filter(Review.comment.isnot(None))
                .filter(Review.comment != '')
                .order_by(Review.created_at.desc())
                .limit(limit)
                .all())
    except SQLAlchemyError:
        return []


def delete_review_by_id(review_id):
    """Delete a review by ID (admin function)"""
    try:
        review = Review.query.get(review_id)
        if not review:
            return False
            
        db.session.delete(review)
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_pending_reviews():
    """Get bookings that can be reviewed but haven't been yet"""
    try:
        today = date.today()
        bookings_ready_for_review = []
        
        # Get all completed bookings
        completed_bookings = Booking.query.filter(
            or_(
                Booking.status == 'checked_out',
                and_(Booking.status == 'confirmed', Booking.check_out <= today)
            )
        ).all()
        
        # Filter out bookings that already have reviews
        for booking in completed_bookings:
            has_guest_review = Review.query.filter_by(
                booking_id=booking.id, 
                reviewer_id=booking.guest_id
            ).first()
            has_host_review = Review.query.filter_by(
                booking_id=booking.id, 
                reviewer_id=booking.listing.host_id
            ).first()
            
            if not has_guest_review or not has_host_review:
                bookings_ready_for_review.append(booking)
                
        return bookings_ready_for_review
    except SQLAlchemyError:
        return []


# =============================================================================
# MESSAGING OPERATIONS
# =============================================================================

def start_conversation(sender_id, recipient_id):
    """Start a new conversation or get existing one"""
    try:
        # Check if conversation already exists
        existing = Conversation.query.filter(
            or_(
                and_(Conversation.user1_id == sender_id, Conversation.user2_id == recipient_id),
                and_(Conversation.user1_id == recipient_id, Conversation.user2_id == sender_id)
            )
        ).first()
        
        if existing:
            return existing
            
        # Create new conversation
        conversation = Conversation(
            user1_id=sender_id,
            user2_id=recipient_id
        )
        db.session.add(conversation)
        db.session.commit()
        return conversation
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_user_conversations(user_id):
    """Get all conversations for a user"""
    try:
        return (Conversation.query
                .filter(or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id))
                .order_by(Conversation.last_message_at.desc())
                .all())
    except SQLAlchemyError:
        return []


def send_message(conversation_id, sender_id, content):
    """Send a message in a conversation"""
    try:
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")
            
        # Determine recipient
        recipient_id = (conversation.user2_id if conversation.user1_id == sender_id 
                       else conversation.user1_id)
        
        message = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content
        )
        
        # Update conversation last message time
        conversation.last_message_at = datetime.utcnow()
        
        db.session.add(message)
        db.session.commit()
        return message
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def get_conversation_messages(conversation_id, mark_as_read=False, reader_id=None):
    """Get all messages in a conversation"""
    try:
        messages = (Message.query
                   .filter_by(conversation_id=conversation_id)
                   .order_by(Message.created_at.asc())
                   .all())
        
        # Mark messages as read if requested
        if mark_as_read and reader_id:
            unread_messages = [m for m in messages if not m.is_read and m.recipient_id == reader_id]
            for message in unread_messages:
                message.is_read = True
            if unread_messages:
                db.session.commit()
                
        return messages
    except SQLAlchemyError:
        return []


# =============================================================================
# DASHBOARD STATISTICS
# =============================================================================

def get_total_users():
    """Get total number of registered users"""
    try:
        return User.query.count()
    except SQLAlchemyError:
        return 0


def get_total_hosts():
    """Get number of users who are hosts"""
    try:
        return User.query.filter_by(role='host').count()
    except SQLAlchemyError:
        return 0


def get_total_guests():
    """Get number of users who are guests"""
    try:
        return User.query.filter_by(role='guest').count()
    except SQLAlchemyError:
        return 0


def get_total_listings():
    """Get total number of approved listings"""
    try:
        return Listing.query.filter_by(approved=True).count()
    except SQLAlchemyError:
        return 0


def get_total_bookings():
    """Get total number of bookings"""
    try:
        return Booking.query.count()
    except SQLAlchemyError:
        return 0


def get_completed_bookings():
    """Get number of completed bookings"""
    try:
        return Booking.query.filter_by(status='checked_out').count()
    except SQLAlchemyError:
        return 0


def get_average_rating():
    """Get platform-wide average rating"""
    try:
        result = db.session.query(func.avg(Review.rating)).scalar()
        return float(result) if result else 0.0
    except SQLAlchemyError:
        return 0.0


def get_unique_locations():
    """Get number of unique listing locations"""
    try:
        result = db.session.query(func.count(func.distinct(Listing.location))).scalar()
        return result if result else 0
    except SQLAlchemyError:
        return 0


def get_platform_stats():
    """Get comprehensive platform statistics"""
    try:
        stats = {
            'total_users': get_total_users(),
            'total_hosts': get_total_hosts(),
            'total_guests': get_total_guests(),
            'total_listings': get_total_listings(),
            'total_bookings': get_total_bookings(),
            'completed_bookings': get_completed_bookings(),
            'average_rating': get_average_rating(),
            'unique_locations': get_unique_locations(),
            'pending_listings': len(get_pending_listings()),
        }
        return stats
    except SQLAlchemyError:
        return {}


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
            or_(
                Booking.status == 'checked_out',
                and_(Booking.status == 'confirmed', Booking.check_out < today)
            )
        ).all()
    except SQLAlchemyError:
        return []


# =============================================================================
# EXPORTABLE FUNCTIONS FOR ROUTES
# =============================================================================

__all__ = [
    # Users
    'get_user_by_id', 'create_user', 'update_user', 'delete_user', 'update_profile_picture',

    # Listings
    'get_listing_by_id', 'create_listing', 'update_listing', 'delete_listing',
    'approve_listing', 'get_approved_listings', 'get_listings_by_host',
    'get_pending_listings', 'search_listings',

    # Bookings
    'create_booking', 'get_bookings_by_guest', 'get_bookings_by_host',
    'update_booking_status', 'get_booking_by_id', 'check_in_booking', 'check_out_booking',
    'get_completed_bookings_by_user',

    # Reviews
    'create_review', 'get_reviews_for_user', 'get_reviews_written_by_user',
    'get_latest_reviews', 'delete_review_by_id', 'get_pending_reviews',
    
    # Messaging
    'start_conversation', 'get_user_conversations', 'send_message', 'get_conversation_messages',
    
    # Dashboard Stats
    'get_total_users', 'get_total_hosts', 'get_total_guests', 'get_total_listings',
    'get_total_bookings', 'get_completed_bookings', 'get_average_rating',
    'get_unique_locations', 'get_platform_stats',
]


# =============================================================================
# USAGE EXAMPLES FOR ROUTES
# =============================================================================

"""
Quick Reference for Routes/Views:

# Import what you need:
from app.crud import (
    create_user, get_user_by_id, update_profile_picture,
    create_listing, get_approved_listings, search_listings,
    create_booking, check_in_booking, check_out_booking,
    create_review, get_latest_reviews,
    start_conversation, send_message,
    get_platform_stats
)

# User Operations:
user = create_user("amir", "amir@email.com", "host", "secret123")
user = get_user_by_id(1)
updated_user = update_user(1, username="new_name")
filename = update_profile_picture(1, "profile.jpg")

# Listing Operations with Guest Capacity:
listing = create_listing("Cozy Home", "Dhaka", "Nice place", 2500.0, 
                        host_id=1, host_name="Amir", guest_capacity=4)
listings = search_listings(query="cozy", location="dhaka", guest_count=2)
host_listings = get_listings_by_host(host_id=1)

# Booking Operations with Check-in/Check-out:
booking = create_booking(guest_id=2, listing_id=1, check_in=date(2025,6,1), 
                        check_out=date(2025,6,5), guest_count=2)
checked_in = check_in_booking(booking_id=1)
checked_out = check_out_booking(booking_id=1)

# Review Operations (Real Data Only):
review = create_review(from_user_id=2, to_user_id=1, booking_id=1, 
                      rating=5, comment="Great host!")
latest_reviews = get_latest_reviews(limit=2, min_rating=4)
pending_reviews = get_pending_reviews()

# Messaging Operations:
conversation = start_conversation(sender_id=1, recipient_id=2)
message = send_message(conversation.id, sender_id=1, content="Hello!")
messages = get_conversation_messages(conversation.id, mark_as_read=True, reader_id=2)
user_conversations = get_user_conversations(user_id=1)

# Dashboard Statistics:
stats = get_platform_stats()
total_users = get_total_users()
avg_rating = get_average_rating()

# Admin Operations:
pending = get_pending_listings()
approved_listing = approve_listing(listing_id=1)
deleted_review = delete_review_by_id(review_id=1)
""" 