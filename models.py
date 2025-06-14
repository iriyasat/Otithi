from config import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    role = db.Column(db.String(20), nullable=False, default='guest')  # admin, host, guest
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    preferred_language = db.Column(db.String(5), default='en')  # en, bn
    profile_picture = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships with unique backref names
    hosted_properties = db.relationship('Property', backref='host_user', lazy=True, foreign_keys='Property.host_id')
    guest_bookings = db.relationship('Booking', backref='guest_user', lazy=True, foreign_keys='Booking.user_id')
    user_reviews = db.relationship('Review', backref='review_user', lazy=True, foreign_keys='Review.user_id')
    saved_properties = db.relationship('SavedProperty', backref='saved_user', lazy=True, foreign_keys='SavedProperty.user_id')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.String(100), nullable=False)
    title_bn = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    description_bn = db.Column(db.Text, nullable=False)
    location_en = db.Column(db.String(255), nullable=False)
    location_bn = db.Column(db.String(255), nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='BDT')
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships with unique backref names
    images = db.relationship('PropertyImage', backref='property_obj', lazy=True, cascade='all, delete-orphan')
    property_bookings = db.relationship('Booking', backref='booked_property', lazy=True, foreign_keys='Booking.property_id')
    property_reviews = db.relationship('Review', backref='reviewed_property', lazy=True, foreign_keys='Review.property_id')
    saved_by = db.relationship('SavedProperty', backref='saved_property_obj', lazy=True, foreign_keys='SavedProperty.property_id')

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)  # Added for consistency
    currency = db.Column(db.String(3), default='BDT')
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, cancelled, completed
    payment_status = db.Column(db.String(20), nullable=False, default='pending')  # pending, paid, refunded
    payment_method = db.Column(db.String(20))  # bKash, Nagad, Rocket, etc.
    transaction_id = db.Column(db.String(100))
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    guest = db.relationship('User', backref='bookings')
    property = db.relationship('Property', backref='bookings')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment_en = db.Column(db.Text)
    comment_bn = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SavedProperty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'property_id', name='unique_saved_property'),)