from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory storage for demonstration (in production, use a database)
users_db = {}
listings_db = {}
reviews_db = {}
bookings_db = {}

class User(UserMixin):
    def __init__(self, id, full_name, email, phone=None, bio=None, user_type='guest'):
        self.id = id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.bio = bio
        self.user_type = user_type  # 'guest' or 'host'
        self.profile_photo = None
        self.joined_date = datetime.now()
        self.verified = False
        self.password_hash = None
        
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check if provided password matches the hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return the user ID as a string (required by Flask-Login)"""
        return str(self.id)
    
    @staticmethod
    def get(user_id):
        """Get user by ID"""
        return users_db.get(int(user_id))
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        for user in users_db.values():
            if user.email.lower() == email.lower():
                return user
        return None
    
    @staticmethod
    def create(full_name, email, password, phone=None, bio=None, user_type='guest'):
        """Create a new user"""
        # Check if email already exists
        if User.get_by_email(email):
            return None
        
        # Generate new user ID
        user_id = len(users_db) + 1
        
        # Create new user
        user = User(user_id, full_name, email, phone, bio, user_type)
        user.set_password(password)
        
        # Store in database
        users_db[user_id] = user
        
        return user
    
    def save(self):
        """Save user to database"""
        users_db[self.id] = self
        
    def to_dict(self):
        """Convert user to dictionary (useful for templates)"""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'bio': self.bio,
            'user_type': self.user_type,
            'profile_photo': self.profile_photo,
            'joined_date': self.joined_date,
            'verified': self.verified
        }

class Listing:
    def __init__(self, id, title, description, location, price, host_id, property_type='apartment'):
        self.id = id
        self.title = title
        self.description = description
        self.location = location
        self.price = price
        self.host_id = host_id
        self.property_type = property_type
        self.created_date = datetime.now()
        self.rating = 0.0
        self.reviews_count = 0
        self.amenities = []
        self.images = []
        self.guests = 1
        self.bedrooms = 1
        self.bathrooms = 1
        self.available = True
        self.address = ""
        self.city = ""
        self.country = "Bangladesh"
        
    @staticmethod
    def get(listing_id):
        """Get listing by ID"""
        return listings_db.get(int(listing_id))
    
    @staticmethod
    def get_by_host(host_id):
        """Get all listings by a host"""
        return [listing for listing in listings_db.values() if listing.host_id == host_id]
    
    @staticmethod
    def get_all():
        """Get all active listings"""
        return [listing for listing in listings_db.values() if listing.available]
    
    @staticmethod
    def create(title, description, location, price, host_id, property_type='apartment', 
               guests=1, bedrooms=1, bathrooms=1, amenities=None, address="", city="", country="Bangladesh"):
        """Create a new listing"""
        # Generate new listing ID
        listing_id = len(listings_db) + 1
        
        # Create new listing
        listing = Listing(listing_id, title, description, location, price, host_id, property_type)
        listing.guests = guests
        listing.bedrooms = bedrooms
        listing.bathrooms = bathrooms
        listing.amenities = amenities or []
        listing.address = address
        listing.city = city
        listing.country = country
        
        # Store in database
        listings_db[listing_id] = listing
        
        return listing
    
    def is_available(self, check_in, check_out):
        """Check if listing is available for given dates"""
        if not self.available:
            return False
            
        # Get all confirmed bookings for this listing
        bookings = Booking.get_by_listing(self.id)
        confirmed_bookings = [b for b in bookings if b.status == 'confirmed']
        
        # Check for date overlaps
        for booking in confirmed_bookings:
            if (check_in < booking.check_out and check_out > booking.check_in):
                return False
        
        return True
    
    def get_unavailable_dates(self):
        """Get list of unavailable date ranges"""
        bookings = Booking.get_by_listing(self.id)
        confirmed_bookings = [b for b in bookings if b.status == 'confirmed']
        
        unavailable_ranges = []
        for booking in confirmed_bookings:
            unavailable_ranges.append({
                'start': booking.check_in.isoformat(),
                'end': booking.check_out.isoformat()
            })
        
        return unavailable_ranges
    
    def calculate_total_price(self, check_in, check_out, guests):
        """Calculate total price for a booking"""
        from datetime import timedelta
        
        if check_out <= check_in:
            return 0
            
        nights = (check_out - check_in).days
        base_price = self.price * nights
        
        # Additional charges (simplified)
        cleaning_fee = self.price * 0.1  # 10% cleaning fee
        service_fee = base_price * 0.05   # 5% service fee
        
        total = base_price + cleaning_fee + service_fee
        
        return {
            'nights': nights,
            'base_price': base_price,
            'cleaning_fee': cleaning_fee,
            'service_fee': service_fee,
            'total': total
        }
    
    def save(self):
        """Save listing to database"""
        listings_db[self.id] = self

class Review:
    def __init__(self, id, listing_id, user_id, rating, comment):
        self.id = id
        self.listing_id = listing_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment
        self.created_date = datetime.now()
        
    @staticmethod
    def get_by_listing(listing_id):
        """Get all reviews for a listing"""
        return [review for review in reviews_db.values() if review.listing_id == listing_id]
    
    @staticmethod
    def create(listing_id, user_id, rating, comment):
        """Create a new review"""
        review_id = len(reviews_db) + 1
        review = Review(review_id, listing_id, user_id, rating, comment)
        reviews_db[review_id] = review
        
        # Update listing rating
        listing = Listing.get(listing_id)
        if listing:
            reviews = Review.get_by_listing(listing_id)
            listing.rating = sum(r.rating for r in reviews) / len(reviews)
            listing.reviews_count = len(reviews)
            listing.save()
        
        return review
    
    def save(self):
        """Save review to database"""
        reviews_db[self.id] = self

class Booking:
    def __init__(self, id, listing_id, user_id, check_in, check_out, guests, total_price):
        self.id = id
        self.listing_id = listing_id
        self.user_id = user_id
        self.check_in = check_in
        self.check_out = check_out
        self.guests = guests
        self.total_price = total_price
        self.status = 'pending'  # pending, confirmed, cancelled
        self.created_date = datetime.now()
        
    @staticmethod
    def get_by_user(user_id):
        """Get all bookings by a user"""
        return [booking for booking in bookings_db.values() if booking.user_id == user_id]
    
    @staticmethod
    def get_by_host(host_id):
        """Get all bookings for a host's listings"""
        host_listings = [listing.id for listing in listings_db.values() if listing.host_id == host_id]
        return [booking for booking in bookings_db.values() if booking.listing_id in host_listings]
    
    @staticmethod
    def get_by_listing(listing_id):
        """Get all bookings for a specific listing"""
        return [booking for booking in bookings_db.values() if booking.listing_id == listing_id]
    
    @staticmethod
    def create(listing_id, user_id, check_in, check_out, guests):
        """Create a new booking"""
        listing = Listing.get(listing_id)
        if not listing:
            return None
            
        # Check availability
        if not listing.is_available(check_in, check_out):
            return None
            
        # Calculate price
        price_breakdown = listing.calculate_total_price(check_in, check_out, guests)
        total_price = price_breakdown['total']
        
        # Generate new booking ID
        booking_id = len(bookings_db) + 1
        
        # Create booking
        booking = Booking(booking_id, listing_id, user_id, check_in, check_out, guests, total_price)
        bookings_db[booking_id] = booking
        
        return booking
    
    def confirm(self):
        """Confirm a pending booking"""
        if self.status == 'pending':
            self.status = 'confirmed'
            self.save()
            return True
        return False
    
    def cancel(self):
        """Cancel a booking"""
        if self.status in ['pending', 'confirmed']:
            self.status = 'cancelled'
            self.save()
            return True
        return False
    
    def get_listing(self):
        """Get the listing for this booking"""
        return Listing.get(self.listing_id)
    
    def get_guest(self):
        """Get the guest user for this booking"""
        return User.get(self.user_id)
    
    def save(self):
        """Save booking to database"""
        bookings_db[self.id] = self

# Sample data for development
def create_sample_data():
    """Create sample users and listings for development"""
    if not users_db:  # Only create if database is empty
        
        # Create sample users
        user1 = User.create(
            full_name="Ahmed Rahman",
            email="ahmed@example.com",
            password="password123",
            phone="+8801711123456",
            bio="Experienced host in Dhaka, loves sharing local culture.",
            user_type="host"
        )
        
        user2 = User.create(
            full_name="Sarah Johnson",
            email="sarah@example.com", 
            password="password123",
            phone="+8801911234567",
            bio="Travel enthusiast exploring Bangladesh.",
            user_type="guest"
        )
        
        user3 = User.create(
            full_name="Fatima Khan",
            email="fatima@example.com",
            password="password123", 
            phone="+8801811345678",
            bio="Hospitality professional in Chittagong.",
            user_type="host"
        )
        
        # Create sample listings
        listing1 = Listing(
            id=1,
            title="Beautiful Apartment in Dhaka",
            description="Experience the heart of Dhaka in this beautiful apartment located in the prestigious Gulshan area.",
            location="Gulshan, Dhaka",
            price=5000,
            host_id=1,
            property_type="apartment"
        )
        listing1.guests = 4
        listing1.bedrooms = 2
        listing1.bathrooms = 2
        listing1.rating = 4.8
        listing1.reviews_count = 24
        listing1.amenities = ['WiFi', 'Air Conditioning', 'Kitchen', 'Parking', 'TV', 'Washing Machine']
        listing1.save()
        
        listing2 = Listing(
            id=2,
            title="Cozy House in Chittagong",
            description="A cozy house perfect for families visiting Chittagong.",
            location="Panchlaish, Chittagong", 
            price=3500,
            host_id=3,
            property_type="house"
        )
        listing2.guests = 6
        listing2.bedrooms = 3
        listing2.bathrooms = 2
        listing2.rating = 4.6
        listing2.reviews_count = 18
        listing2.save()
        
        listing3 = Listing(
            id=3,
            title="Modern Studio in Sylhet",
            description="A modern studio apartment in the heart of Sylhet.",
            location="Zindabazar, Sylhet",
            price=2500, 
            host_id=1,
            property_type="studio"
        )
        listing3.guests = 2
        listing3.bedrooms = 1
        listing3.bathrooms = 1
        listing3.rating = 4.9
        listing3.reviews_count = 31
        listing3.save()

# Initialize sample data
create_sample_data()
