from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import shortuuid
import enum

db = SQLAlchemy()

def generate_uuid():
    """Generate a short, secure UUID for database records"""
    return shortuuid.uuid()

class UserRole(enum.Enum):
    """User role enumeration for type safety"""
    GUEST = 'guest'
    HOST = 'host'
    ADMIN = 'admin'

class BookingStatus(enum.Enum):
    """Booking status enumeration"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CHECKED_IN = 'checked_in'
    CHECKED_OUT = 'checked_out'
    CANCELLED = 'cancelled'

class ListingStatus(enum.Enum):
    """Listing status enumeration"""
    DRAFT = 'draft'
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    INACTIVE = 'inactive'

class User(UserMixin, db.Model):
    """
    User model with UUID primary key and optimized structure
    Supports guests, hosts, and admins with proper role-based access
    """
    __tablename__ = 'users'
    
    # Primary key using UUID for security and scalability
    id = db.Column(db.String(22), primary_key=True, default=generate_uuid)
    
    # Authentication fields
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role and verification
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.GUEST, index=True)
    is_verified = db.Column(db.Boolean, default=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Profile information
    profile_picture = db.Column(db.String(255), nullable=True)
    nid_filename = db.Column(db.String(255), nullable=True)  # Host NID document
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    listings = db.relationship('Listing', backref='host', lazy='dynamic', cascade='all, delete-orphan')
    bookings_as_guest = db.relationship('Booking', backref='guest', lazy='dynamic', 
                                       foreign_keys='Booking.guest_id', cascade='all, delete-orphan')
    reviews_given = db.relationship('Review', backref='reviewer', lazy='dynamic', 
                                   foreign_keys='Review.reviewer_id', cascade='all, delete-orphan')
    reviews_received = db.relationship('Review', backref='reviewee', lazy='dynamic', 
                                      foreign_keys='Review.reviewee_id', cascade='all, delete-orphan')
    
    # Conversation relationships
    conversations_as_user1 = db.relationship('Conversation', backref='user1', lazy='dynamic',
                                            foreign_keys='Conversation.user1_id', cascade='all, delete-orphan')
    conversations_as_user2 = db.relationship('Conversation', backref='user2', lazy='dynamic',
                                            foreign_keys='Conversation.user2_id', cascade='all, delete-orphan')
    
    # Messages sent
    messages_sent = db.relationship('Message', backref='sender', lazy='dynamic',
                                   foreign_keys='Message.sender_id', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if not self.id:
            self.id = generate_uuid()
    
    def set_password(self, password):
        """Hash and set user password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify user password"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    @property
    def is_host(self):
        """Check if user is host"""
        return self.role == UserRole.HOST
    
    @property
    def is_guest(self):
        """Check if user is guest"""
        return self.role == UserRole.GUEST
    
    def can_be_deleted(self):
        """Check if user can be safely deleted"""
        if self.is_admin:
            # Don't delete if this is the only admin
            admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
            return admin_count > 1
        return True
    
    def get_profile_image_url(self):
        """Get profile image URL with fallback"""
        if self.profile_picture:
            return f'/static/images/profiles/{self.profile_picture}'
        return '/static/images/ui/default_avatar.png'
    
    def get_role_label(self):
        """Get human-readable role label"""
        return self.role.value.title()
    
    def average_rating(self):
        """Calculate average rating for the user"""
        reviews = self.reviews_received.filter(Review.rating.isnot(None)).all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)
    
    def total_reviews(self):
        """Get total number of reviews received"""
        return self.reviews_received.count()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Listing(db.Model):
    """
    Property listing model with UUID and optimized structure
    Supports multiple statuses and proper host relationships
    """
    __tablename__ = 'listings'
    
    # Primary key using UUID
    id = db.Column(db.String(22), primary_key=True, default=generate_uuid)
    
    # Basic information
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False, index=True)
    
    # Pricing and capacity
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False, index=True)
    guest_capacity = db.Column(db.Integer, nullable=False, default=1)
    
    # Status and approval
    status = db.Column(db.Enum(ListingStatus), default=ListingStatus.PENDING, nullable=False, index=True)
    approved = db.Column(db.Boolean, default=False, index=True)
    
    # Media
    image_filename = db.Column(db.String(255), nullable=True)
    
    # Relationships
    host_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False, index=True)
    bookings = db.relationship('Booking', backref='listing', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='listing', lazy='dynamic', cascade='all, delete-orphan')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Listing, self).__init__(**kwargs)
        if not self.id:
            self.id = generate_uuid()
    
    @property
    def is_available(self):
        """Check if listing is available for booking"""
        return self.approved and self.status == ListingStatus.APPROVED
    
    def get_image_url(self):
        """Get listing image URL with fallback"""
        if self.image_filename:
            return f'/static/images/listings/{self.image_filename}'
        return '/static/images/ui/default_listing.jpg'
    
    def get_average_rating(self):
        """Calculate average rating for the listing"""
        reviews = self.reviews.filter(Review.rating.isnot(None)).all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)
    
    def get_review_count(self):
        """Get total number of reviews"""
        return self.reviews.count()
    
    def get_status_label(self):
        """Get human-readable status label"""
        return self.status.name.title()
    
    def __repr__(self):
        return f'<Listing {self.name}>'

class Booking(db.Model):
    """
    Booking model with UUID and comprehensive status tracking
    Links guests to listings with full booking lifecycle
    """
    __tablename__ = 'bookings'
    
    # Primary key using UUID
    id = db.Column(db.String(22), primary_key=True, default=generate_uuid)
    
    # Relationships
    guest_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False, index=True)
    listing_id = db.Column(db.String(22), db.ForeignKey('listings.id'), nullable=False, index=True)
    
    # Booking details
    check_in_date = db.Column(db.Date, nullable=False, index=True)
    check_out_date = db.Column(db.Date, nullable=False, index=True)
    guest_count = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Status and verification
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    nid_filename = db.Column(db.String(255), nullable=True)  # Guest NID document
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    checked_in_at = db.Column(db.DateTime, nullable=True)
    checked_out_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    review = db.relationship('Review', backref='booking', uselist=False, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Booking, self).__init__(**kwargs)
        if not self.id:
            self.id = generate_uuid()
    
    def calculate_total_price(self):
        """Calculate total price based on nights and listing price"""
        from datetime import date
        nights = (self.check_out_date - self.check_in_date).days
        return float(self.listing.price_per_night) * nights
    
    def get_status_badge_class(self):
        """Get Bootstrap badge class for status"""
        status_classes = {
            BookingStatus.PENDING: 'bg-warning',
            BookingStatus.CONFIRMED: 'bg-success',
            BookingStatus.CHECKED_IN: 'bg-info',
            BookingStatus.CHECKED_OUT: 'bg-secondary',
            BookingStatus.CANCELLED: 'bg-danger'
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    def get_status_label(self):
        """Get human-readable status label"""
        return self.status.name.title()
    
    def can_be_cancelled(self):
        """Check if booking can be cancelled"""
        return self.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED]
    
    def can_be_checked_in(self):
        """Check if booking can be checked in"""
        return self.status == BookingStatus.CONFIRMED
    
    def can_be_checked_out(self):
        """Check if booking can be checked out"""
        return self.status == BookingStatus.CHECKED_IN
    
    def __repr__(self):
        return f'<Booking {self.id}>'

class Review(db.Model):
    """
    Review model with UUID and comprehensive rating system
    Links reviewers to listings with detailed feedback
    """
    __tablename__ = 'reviews'
    
    # Primary key using UUID
    id = db.Column(db.String(22), primary_key=True, default=generate_uuid)
    
    # Relationships
    reviewer_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False, index=True)
    reviewee_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False, index=True)
    listing_id = db.Column(db.String(22), db.ForeignKey('listings.id'), nullable=False, index=True)
    booking_id = db.Column(db.String(22), db.ForeignKey('bookings.id'), nullable=False, unique=True)
    
    # Review content
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Review, self).__init__(**kwargs)
        if not self.id:
            self.id = generate_uuid()
    
    def get_star_rating(self):
        """Get star rating display"""
        return '★' * self.rating + '☆' * (5 - self.rating)
    
    def __repr__(self):
        return f'<Review {self.id}>'

class Conversation(db.Model):
    """
    Conversation model with UUID for messaging system
    Links two users in a conversation thread
    """
    __tablename__ = 'conversations'
    
    # Primary key using UUID
    id = db.Column(db.String(22), primary_key=True, default=generate_uuid)
    
    # Relationships
    user1_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False, index=True)
    user2_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', 
                              cascade='all, delete-orphan', order_by='Message.created_at')
    
    def __init__(self, **kwargs):
        super(Conversation, self).__init__(**kwargs)
        if not self.id:
            self.id = generate_uuid()
    
    def get_other_user(self, current_user_id):
        """Get the other user in the conversation"""
        if self.user1_id == current_user_id:
            return User.query.get(self.user2_id)
        return User.query.get(self.user1_id)
    
    def mark_messages_as_read(self, user_id):
        """Mark all messages as read for a user"""
        unread_messages = self.messages.filter_by(recipient_id=user_id, is_read=False).all()
        for message in unread_messages:
            message.is_read = True
        db.session.commit()
    
    def get_unread_count(self, user_id):
        """Get unread message count for a user"""
        return self.messages.filter_by(recipient_id=user_id, is_read=False).count()
    
    def __repr__(self):
        return f'<Conversation {self.id}>'

class Message(db.Model):
    """
    Message model with UUID for conversation messages
    Links to conversations with read status tracking
    """
    __tablename__ = 'messages'
    
    # Primary key using UUID
    id = db.Column(db.String(22), primary_key=True, default=generate_uuid)
    
    # Relationships
    conversation_id = db.Column(db.String(22), db.ForeignKey('conversations.id'), nullable=False, index=True)
    sender_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False, index=True)
    recipient_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Message content
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)
        if not self.id:
            self.id = generate_uuid()
    
    def __repr__(self):
        return f'<Message {self.id}>'