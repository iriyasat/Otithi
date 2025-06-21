from . import db
from flask_login import UserMixin
from datetime import datetime
from enum import Enum

class BookingStatus(Enum):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CHECKED_IN = 'CHECKED_IN'
    CHECKED_OUT = 'CHECKED_OUT'
    CANCELLED = 'CANCELLED'
    COMPLETED = 'COMPLETED'

class ListingStatus(Enum):
    DRAFT = 'DRAFT'
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    INACTIVE = 'INACTIVE'

class UserRole(Enum):
    GUEST = 'guest'
    HOST = 'host'
    ADMIN = 'admin'

class User(UserMixin, db.Model):
    """User model for authentication and user management"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='guest')  # 'admin', 'host', 'guest'
    is_verified = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    profile_image = db.Column(db.String(255))
    nid_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    listings = db.relationship('Listing', backref='user', lazy=True)
    bookings = db.relationship('Booking', backref='user', foreign_keys='Booking.user_id', lazy=True)
    sent_messages = db.relationship('Message', backref='sender', foreign_keys='Message.sender_id', lazy=True)
    received_messages = db.relationship('Message', backref='recipient', foreign_keys='Message.recipient_id', lazy=True)
    reviews = db.relationship('Review', backref='user', foreign_keys='Review.user_id', lazy=True)
    
    # Conversation relationships
    conversations_as_user1 = db.relationship('Conversation', backref='user1', foreign_keys='Conversation.user1_id', lazy=True)
    conversations_as_user2 = db.relationship('Conversation', backref='user2', foreign_keys='Conversation.user2_id', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def is_admin(self):
        """Check if user is an admin"""
        return self.role == 'admin'

    @property
    def is_host(self):
        """Check if user is a host"""
        return self.role == 'host'

    @property
    def is_guest(self):
        """Check if user is a guest"""
        return self.role == 'guest'

class Listing(db.Model):
    """Listing model for property listings"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    guest_capacity = db.Column(db.Integer)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    house_rules = db.Column(db.Text)
    image_filename = db.Column(db.String(255))  # Primary image
    status = db.Column(db.Enum(ListingStatus), default=ListingStatus.DRAFT)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    bookings = db.relationship('Booking', backref='listing', lazy=True)
    images = db.relationship('ListingImage', backref='listing', lazy=True)
    reviews = db.relationship('Review', backref='listing', lazy=True)

    def __repr__(self):
        return f'<Listing {self.title} in {self.location}>'

class Booking(db.Model):
    """Booking model for reservations"""
    id = db.Column(db.Integer, primary_key=True)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    guest_count = db.Column(db.Integer)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING)
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Relationships
    messages = db.relationship('Message', backref='booking', lazy=True)

    def __repr__(self):
        return f'<Booking {self.id} for {self.listing.title}>'

class Conversation(db.Model):
    """Conversation model for organizing messages between users"""
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy=True)

    def __repr__(self):
        return f'<Conversation between {self.user1.username} and {self.user2.username}>'

class Message(db.Model):
    """Message model for communication between guests and hosts"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))

    def __repr__(self):
        return f'<Message from {self.sender.username} to {self.recipient.username}>'

class ListingImage(db.Model):
    """ListingImage model for multiple images per listing"""
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    image_path = db.Column(db.String(255))

    def __repr__(self):
        return f'<ListingImage {self.id} for listing {self.listing_id}>'

class Review(db.Model):
    """Review model for guest and host reviews"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} by {self.user.username} for listing {self.listing_id}>' 