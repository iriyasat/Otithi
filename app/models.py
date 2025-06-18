from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(10), nullable=False, default='guest')  # guest or host
    profile_picture = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='guest', lazy=True, cascade='all, delete-orphan')
    listings = db.relationship('Listing', backref='host', lazy=True, cascade='all, delete-orphan')
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy='dynamic', cascade='all, delete-orphan')
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewed_id', backref='reviewed', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def average_rating(self):
        """Calculate the average rating received by this user"""
        reviews = self.reviews_received.all()
        if not reviews:
            return 0
        return sum(review.rating for review in reviews) / len(reviews)
    
    def total_reviews(self):
        """Get total number of reviews received"""
        return self.reviews_received.count()
    
    def can_be_deleted(self):
        """Check if user can be safely deleted (not the only admin)"""
        if not self.is_admin:
            return True
        admin_count = User.query.filter_by(is_admin=True).count()
        return admin_count > 1

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    host_name = db.Column(db.String(120), nullable=False)  # Keep for display purposes
    image_filename = db.Column(db.String(255), nullable=True)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='listing', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Listing {self.name} in {self.location}>'
    
    def get_status(self):
        """Get listing approval status for display"""
        return "Approved" if self.approved else "Pending Approval"
    
    def get_status_badge_class(self):
        """Get CSS class for status badge"""
        return "bg-success" if self.approved else "bg-warning"
    
    def pending_bookings_count(self):
        """Count of pending bookings for this listing"""
        return len([b for b in self.bookings if b.status == 'pending'])
    
    def confirmed_bookings_count(self):
        """Count of confirmed bookings for this listing"""
        return len([b for b in self.bookings if b.status == 'confirmed'])

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, checked_in, checked_out, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='booking', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking {self.id} - Guest: {self.guest_id}, Listing: {self.listing_id}>'
    
    def is_completed(self):
        """Check if booking is completed (checked out)"""
        return self.status == 'checked_out'
    
    def can_be_reviewed(self):
        """Check if this booking can be reviewed (checked out and no existing review by user)"""
        return self.status == 'checked_out'
    
    def can_check_in(self):
        """Check if guest can check in today"""
        from datetime import date
        today = date.today()
        return (self.status == 'confirmed' and 
                self.check_in <= today <= self.check_out)
    
    def can_check_out(self):
        """Check if guest can check out"""
        return self.status == 'checked_in'
    
    def get_status_badge_class(self):
        """Get CSS class for booking status badge"""
        status_classes = {
            'pending': 'bg-warning',
            'confirmed': 'bg-info',
            'checked_in': 'bg-primary',
            'checked_out': 'bg-success',
            'cancelled': 'bg-danger'
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    def get_host(self):
        """Get the host user for this booking"""
        return self.listing.host
    
    def has_review_from_user(self, user_id):
        """Check if a specific user has already reviewed this booking"""
        return self.reviews.filter_by(reviewer_id=user_id).first() is not None
    
    def days_stayed(self):
        """Calculate number of days for this booking"""
        return (self.check_out - self.check_in).days
    
    def total_cost(self):
        """Calculate total cost of booking"""
        return self.days_stayed() * self.listing.price_per_night

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1–5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} - Rating: {self.rating}>'
    
    def get_reviewer_role(self):
        """Get the role of the person who wrote this review"""
        return self.reviewer.role
    
    def get_reviewed_role(self):
        """Get the role of the person being reviewed"""
        return self.reviewed.role 