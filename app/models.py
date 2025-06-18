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
    
    # Messaging relationships
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic', cascade='all, delete-orphan')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    conversations_as_user1 = db.relationship('Conversation', foreign_keys='Conversation.user1_id', backref='user1', lazy='dynamic', cascade='all, delete-orphan')
    conversations_as_user2 = db.relationship('Conversation', foreign_keys='Conversation.user2_id', backref='user2', lazy='dynamic')
    
    # Messaging relationships
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic', cascade='all, delete-orphan')
    received_messages = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')
    conversations_as_user1 = db.relationship('Conversation', foreign_keys='Conversation.user1_id', backref='user1', lazy='dynamic', cascade='all, delete-orphan')
    conversations_as_user2 = db.relationship('Conversation', foreign_keys='Conversation.user2_id', backref='user2', lazy='dynamic')

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

    def get_conversations(self):
        """Get all conversations for this user"""
        conversations = db.session.query(Conversation).filter(
            db.or_(Conversation.user1_id == self.id, Conversation.user2_id == self.id)
        ).order_by(Conversation.last_message_at.desc()).all()
        return conversations
    
    def get_conversation_with(self, other_user_id):
        """Get conversation between this user and another user"""
        return Conversation.query.filter(
            db.or_(
                db.and_(Conversation.user1_id == self.id, Conversation.user2_id == other_user_id),
                db.and_(Conversation.user1_id == other_user_id, Conversation.user2_id == self.id)
            )
        ).first()

    def get_conversations(self):
        """Get all conversations for this user"""
        conversations = db.session.query(Conversation).filter(
            db.or_(Conversation.user1_id == self.id, Conversation.user2_id == self.id)
        ).order_by(Conversation.last_message_at.desc()).all()
        return conversations
    
    def get_conversation_with(self, other_user_id):
        """Get conversation between this user and another user"""
        return Conversation.query.filter(
            db.or_(
                db.and_(Conversation.user1_id == self.id, Conversation.user2_id == other_user_id),
                db.and_(Conversation.user1_id == other_user_id, Conversation.user2_id == self.id)
            )
        ).first()
    
    def get_unread_message_count(self):
        """Get count of unread messages for this user from valid conversations only"""
        return (db.session.query(Message)
               .join(Conversation)
               .filter(
                   Message.recipient_id == self.id,
                   Message.is_read == False,
                   db.or_(
                       Conversation.user1_id == self.id,
                       Conversation.user2_id == self.id
                   )
               ).count())

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    guest_capacity = db.Column(db.Integer, nullable=False, default=1)
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    host_name = db.Column(db.String(120), nullable=False)  # Keep for display purposes
    image_filename = db.Column(db.String(255), nullable=True)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='listing', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Listing {self.name} in {self.location} (Sleeps {self.guest_capacity})>'
    
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
    guest_count = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, checked_in, checked_out, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    actual_checkout = db.Column(db.DateTime, nullable=True)  # When user actually checked out
    
    # Relationships
    reviews = db.relationship('Review', backref='booking', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking {self.id} - Guest: {self.guest_id}, Listing: {self.listing_id}, Guests: {self.guest_count}>'
    
    def is_completed(self):
        """Check if booking is completed (checked out)"""
        return self.status == 'checked_out'
    
    def can_be_reviewed(self):
        """Check if this booking can be reviewed - immediately after checkout or after checkout date"""
        from datetime import date
        # Allow review if manually checked out OR checkout date has passed
        if self.actual_checkout:
            return True  # Immediately after manual checkout
        elif self.check_out <= date.today():
            return True  # After planned checkout date
        else:
            return False  # Still before checkout
    
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

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='conversation', lazy='dynamic', cascade='all, delete-orphan', order_by='Message.created_at')
    
    def __repr__(self):
        return f'<Conversation {self.id} between User {self.user1_id} and User {self.user2_id}>'
    
    def get_other_user(self, current_user_id):
        """Get the other user in this conversation"""
        if self.user1_id == current_user_id:
            return self.user2
        else:
            return self.user1
    
    def get_last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.order_by(Message.created_at.desc()).first()
    
    def mark_messages_as_read(self, user_id):
        """Mark all messages in this conversation as read for a specific user"""
        unread_messages = self.messages.filter_by(recipient_id=user_id, is_read=False).all()
        for message in unread_messages:
            message.is_read = True
        if unread_messages:
            db.session.commit()
    
    def get_unread_count(self, user_id):
        """Get count of unread messages for a specific user"""
        return self.messages.filter_by(recipient_id=user_id, is_read=False).count()

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Message {self.id} from User {self.sender_id} to User {self.recipient_id}>'
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
        db.session.commit()