from config import db
from datetime import datetime, UTC
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='guest')  # guest, host, admin
    preferred_language = db.Column(db.String(2), nullable=False, default='en')  # en, bn
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    hosted_properties = db.relationship('Property', back_populates='host', lazy=True)
    bookings = db.relationship('Booking', back_populates='guest', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    saved_properties = db.relationship('SavedProperty', backref='user', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title_en = db.Column(db.String(200), nullable=False)
    title_bn = db.Column(db.String(200), nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    description_bn = db.Column(db.Text, nullable=False)
    location_en = db.Column(db.String(200), nullable=False)
    location_bn = db.Column(db.String(200), nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    amenities = db.Column(db.JSON, nullable=False, default=list)
    cultural_features = db.Column(db.JSON, nullable=False, default=list)
    safety_features = db.Column(db.JSON, nullable=False, default=list)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    host = db.relationship('User', back_populates='hosted_properties', lazy=True)
    bookings = db.relationship('Booking', back_populates='property', lazy=True)
    images = db.relationship('PropertyImage', backref='property', lazy=True)
    reviews = db.relationship('Review', backref='property', lazy=True)
    saved_by = db.relationship('SavedProperty', backref='property', lazy=True)
    cultural_experiences = db.relationship('CulturalExperience', backref='property', lazy=True)
    meal_options = db.relationship('MealOption', backref='property', lazy=True)
    transport_options = db.relationship('TransportOption', backref='property', lazy=True)
    verifications = db.relationship('CommunityVerification', backref='property', lazy=True)

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, cancelled, completed
    payment_status = db.Column(db.String(20), nullable=False, default='pending')  # pending, paid, refunded
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    property = db.relationship('Property', back_populates='bookings', lazy=True)
    guest = db.relationship('User', back_populates='bookings', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment_en = db.Column(db.Text)
    comment_bn = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class SavedProperty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    __table_args__ = (db.UniqueConstraint('user_id', 'property_id', name='unique_saved_property'),)

class CulturalExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    title_en = db.Column(db.String(100), nullable=False)
    title_bn = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    description_bn = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer)  # Duration in minutes
    max_participants = db.Column(db.Integer)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class MealOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    name_bn = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.Text)
    description_bn = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    meal_type = db.Column(db.String(20))  # breakfast, lunch, dinner
    dietary_info = db.Column(db.JSON)  # vegetarian, halal, etc.
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class TransportOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # rickshaw, CNG, boat, etc.
    description_en = db.Column(db.Text)
    description_bn = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class CommunityVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    verifier_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    verification_type = db.Column(db.String(50))  # neighborhood, safety, cultural
    status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

class FestivalSeason(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_bn = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description_en = db.Column(db.Text)
    description_bn = db.Column(db.Text)
    region = db.Column(db.String(50))  # Specific region or 'all' for nationwide
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))