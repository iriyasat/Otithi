from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.database import db

class User(UserMixin):
    def __init__(self, id, full_name, email, password_hash, phone=None, bio=None, user_type='guest', 
                 profile_photo=None, joined_date=None, verified=False):
        self.id = id
        self.full_name = full_name
        self.name = full_name  # Alias for compatibility
        self.email = email
        self.password_hash = password_hash
        self.phone = phone
        self.bio = bio
        self.user_type = user_type
        self.profile_photo = profile_photo
        self.joined_date = joined_date or datetime.now()
        self.verified = verified
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    @staticmethod
    def get(user_id):
        """Get user by ID"""
        query = "SELECT * FROM users WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        if result:
            user_data = result[0]
            return User(
                id=user_data['id'],
                full_name=user_data['full_name'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                phone=user_data['phone'],
                bio=user_data['bio'],
                user_type=user_data['user_type'],
                profile_photo=user_data['profile_photo'],
                joined_date=user_data['joined_date'],
                verified=bool(user_data['verified'])
            )
        return None
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        query = "SELECT * FROM users WHERE email = %s"
        result = db.execute_query(query, (email,))
        if result:
            user_data = result[0]
            return User(
                id=user_data['id'],
                full_name=user_data['full_name'],
                email=user_data['email'],
                password_hash=user_data['password_hash'],
                phone=user_data['phone'],
                bio=user_data['bio'],
                user_type=user_data['user_type'],
                profile_photo=user_data['profile_photo'],
                joined_date=user_data['joined_date'],
                verified=bool(user_data['verified'])
            )
        return None
    
    @staticmethod
    def create(full_name, email, password, phone=None, bio=None, user_type='guest'):
        """Create a new user"""
        password_hash = generate_password_hash(password)
        query = """
            INSERT INTO users (full_name, email, password_hash, phone, bio, user_type, joined_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        user_id = db.execute_insert(query, (
            full_name, email, password_hash, phone, bio, user_type, datetime.now()
        ))
        
        if user_id:
            return User.get(user_id)
        return None
    
    def save(self):
        """Save user changes to database"""
        query = """
            UPDATE users 
            SET full_name = %s, phone = %s, bio = %s, profile_photo = %s, verified = %s
            WHERE id = %s
        """
        return db.execute_update(query, (
            self.full_name, self.phone, self.bio, self.profile_photo, self.verified, self.id
        ))

class Listing:
    def __init__(self, id, title, description, location, price, host_id, property_type='apartment',
                 guests=1, bedrooms=1, bathrooms=1, amenities=None, address='', city='', country='Bangladesh',
                 created_date=None, rating=0.0, reviews_count=0, available=True, images=None):
        self.id = id
        self.title = title
        self.description = description
        self.location = location
        self.price = price
        self.host_id = host_id
        self.property_type = property_type
        self.guests = guests
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.amenities = amenities or []
        self.address = address
        self.city = city
        self.country = country
        self.created_date = created_date or datetime.now()
        self.rating = rating
        self.reviews_count = reviews_count
        self.available = available
        self.images = images or []
    
    @staticmethod
    def get(listing_id):
        """Get listing by ID"""
        query = "SELECT * FROM listings WHERE id = %s"
        result = db.execute_query(query, (listing_id,))
        if result:
            listing_data = result[0]
            return Listing(
                id=listing_data['id'],
                title=listing_data['title'],
                description=listing_data['description'],
                location=listing_data['location'],
                price=float(listing_data['price']),
                host_id=listing_data['host_id'],
                property_type=listing_data['property_type'],
                guests=listing_data['guests'],
                bedrooms=listing_data['bedrooms'],
                bathrooms=listing_data['bathrooms'],
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                address=listing_data['address'],
                city=listing_data['city'],
                country=listing_data['country'],
                created_date=listing_data['created_date'],
                rating=float(listing_data['rating']) if listing_data['rating'] else 0.0,
                reviews_count=listing_data['reviews_count'] or 0,
                available=bool(listing_data['available'])
            )
        return None
    
    @staticmethod
    def get_all():
        """Get all listings"""
        query = "SELECT * FROM listings WHERE available = 1 ORDER BY created_date DESC"
        results = db.execute_query(query)
        listings = []
        for listing_data in results:
            listings.append(Listing(
                id=listing_data['id'],
                title=listing_data['title'],
                description=listing_data['description'],
                location=listing_data['location'],
                price=float(listing_data['price']),
                host_id=listing_data['host_id'],
                property_type=listing_data['property_type'],
                guests=listing_data['guests'],
                bedrooms=listing_data['bedrooms'],
                bathrooms=listing_data['bathrooms'],
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                address=listing_data['address'],
                city=listing_data['city'],
                country=listing_data['country'],
                created_date=listing_data['created_date'],
                rating=float(listing_data['rating']) if listing_data['rating'] else 0.0,
                reviews_count=listing_data['reviews_count'] or 0,
                available=bool(listing_data['available'])
            ))
        return listings
    
    @staticmethod
    def get_by_host(host_id):
        """Get all listings by a host"""
        query = "SELECT * FROM listings WHERE host_id = %s ORDER BY created_date DESC"
        results = db.execute_query(query, (host_id,))
        listings = []
        for listing_data in results:
            listings.append(Listing(
                id=listing_data['id'],
                title=listing_data['title'],
                description=listing_data['description'],
                location=listing_data['location'],
                price=float(listing_data['price']),
                host_id=listing_data['host_id'],
                property_type=listing_data['property_type'],
                guests=listing_data['guests'],
                bedrooms=listing_data['bedrooms'],
                bathrooms=listing_data['bathrooms'],
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                address=listing_data['address'],
                city=listing_data['city'],
                country=listing_data['country'],
                created_date=listing_data['created_date'],
                rating=float(listing_data['rating']) if listing_data['rating'] else 0.0,
                reviews_count=listing_data['reviews_count'] or 0,
                available=bool(listing_data['available'])
            ))
        return listings
    
    @staticmethod
    def create(title, description, location, price, host_id, property_type='apartment',
               guests=1, bedrooms=1, bathrooms=1, amenities=None, address='', city='', country='Bangladesh'):
        """Create a new listing"""
        amenities_str = ','.join(amenities) if amenities else ''
        query = """
            INSERT INTO listings (title, description, location, price, host_id, property_type,
                                guests, bedrooms, bathrooms, amenities, address, city, country, created_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        listing_id = db.execute_insert(query, (
            title, description, location, price, host_id, property_type,
            guests, bedrooms, bathrooms, amenities_str, address, city, country, datetime.now()
        ))
        
        if listing_id:
            return Listing.get(listing_id)
        return None
    
    def is_available(self, check_in, check_out):
        """Check if listing is available for given dates"""
        query = """
            SELECT COUNT(*) as count FROM bookings 
            WHERE listing_id = %s AND status != 'cancelled' 
            AND ((check_in <= %s AND check_out > %s) OR (check_in < %s AND check_out >= %s))
        """
        result = db.execute_query(query, (self.id, check_in, check_in, check_out, check_out))
        return result[0]['count'] == 0 if result else False
    
    def get_unavailable_dates(self):
        """Get list of unavailable dates"""
        query = """
            SELECT check_in, check_out FROM bookings 
            WHERE listing_id = %s AND status != 'cancelled'
        """
        results = db.execute_query(query, (self.id,))
        unavailable_dates = []
        for booking in results:
            current_date = booking['check_in']
            while current_date < booking['check_out']:
                unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
                current_date += date.timedelta(days=1)
        return unavailable_dates
    
    def calculate_total_price(self, check_in, check_out, guests):
        """Calculate total price for booking"""
        nights = (check_out - check_in).days
        base_price = self.price * nights
        cleaning_fee = 500  # Fixed cleaning fee
        service_fee = base_price * 0.1  # 10% service fee
        total = base_price + cleaning_fee + service_fee
        
        return {
            'nights': nights,
            'base_price': base_price,
            'cleaning_fee': cleaning_fee,
            'service_fee': service_fee,
            'total': total
        }

class Review:
    def __init__(self, id, listing_id, user_id, rating, comment, created_date=None):
        self.id = id
        self.listing_id = listing_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment
        self.created_date = created_date or datetime.now()
    
    @staticmethod
    def get_all():
        """Get all reviews"""
        query = "SELECT * FROM reviews ORDER BY created_date DESC"
        results = db.execute_query(query)
        reviews = []
        for review_data in results:
            reviews.append(Review(
                id=review_data['id'],
                listing_id=review_data['listing_id'],
                user_id=review_data['user_id'],
                rating=review_data['rating'],
                comment=review_data['comment'],
                created_date=review_data['created_date']
            ))
        return reviews
    
    @staticmethod
    def get_by_listing(listing_id):
        """Get all reviews for a listing"""
        query = "SELECT * FROM reviews WHERE listing_id = %s ORDER BY created_date DESC"
        results = db.execute_query(query, (listing_id,))
        reviews = []
        for review_data in results:
            reviews.append(Review(
                id=review_data['id'],
                listing_id=review_data['listing_id'],
                user_id=review_data['user_id'],
                rating=review_data['rating'],
                comment=review_data['comment'],
                created_date=review_data['created_date']
            ))
        return reviews
    
    @staticmethod
    def create(listing_id, user_id, rating, comment):
        """Create a new review"""
        query = """
            INSERT INTO reviews (listing_id, user_id, rating, comment, created_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        review_id = db.execute_insert(query, (listing_id, user_id, rating, comment, datetime.now()))
        
        if review_id:
            # Update listing rating
            Review.update_listing_rating(listing_id)
            return Review.get(review_id)
        return None
    
    @staticmethod
    def get(review_id):
        """Get review by ID"""
        query = "SELECT * FROM reviews WHERE id = %s"
        result = db.execute_query(query, (review_id,))
        if result:
            review_data = result[0]
            return Review(
                id=review_data['id'],
                listing_id=review_data['listing_id'],
                user_id=review_data['user_id'],
                rating=review_data['rating'],
                comment=review_data['comment'],
                created_date=review_data['created_date']
            )
        return None
    
    @staticmethod
    def update_listing_rating(listing_id):
        """Update listing average rating and review count"""
        query = """
            SELECT AVG(rating) as avg_rating, COUNT(*) as review_count 
            FROM reviews WHERE listing_id = %s
        """
        result = db.execute_query(query, (listing_id,))
        if result:
            avg_rating = float(result[0]['avg_rating']) if result[0]['avg_rating'] else 0.0
            review_count = result[0]['review_count']
            
            update_query = """
                UPDATE listings SET rating = %s, reviews_count = %s WHERE id = %s
            """
            db.execute_update(update_query, (avg_rating, review_count, listing_id))

class Booking:
    def __init__(self, id, listing_id, user_id, check_in, check_out, guests, total_price, 
                 status='pending', created_date=None):
        self.id = id
        self.listing_id = listing_id
        self.user_id = user_id
        self.check_in = check_in
        self.check_out = check_out
        self.guests = guests
        self.total_price = total_price
        self.status = status
        self.created_date = created_date or datetime.now()
    
    @staticmethod
    def get_all():
        """Get all bookings"""
        query = "SELECT * FROM bookings ORDER BY created_date DESC"
        results = db.execute_query(query)
        bookings = []
        for booking_data in results:
            bookings.append(Booking(
                id=booking_data['id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                guests=booking_data['guests'],
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_date']
            ))
        return bookings
    
    @staticmethod
    def get_by_user(user_id):
        """Get all bookings by a user"""
        query = "SELECT * FROM bookings WHERE user_id = %s ORDER BY created_date DESC"
        results = db.execute_query(query, (user_id,))
        bookings = []
        for booking_data in results:
            bookings.append(Booking(
                id=booking_data['id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                guests=booking_data['guests'],
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_date']
            ))
        return bookings
    
    @staticmethod
    def get_by_host(host_id):
        """Get all bookings for a host's listings"""
        query = """
            SELECT b.* FROM bookings b
            JOIN listings l ON b.listing_id = l.id
            WHERE l.host_id = %s
            ORDER BY b.created_date DESC
        """
        results = db.execute_query(query, (host_id,))
        bookings = []
        for booking_data in results:
            bookings.append(Booking(
                id=booking_data['id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                guests=booking_data['guests'],
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_date']
            ))
        return bookings
    
    @staticmethod
    def get_by_listing(listing_id):
        """Get all bookings for a specific listing"""
        query = "SELECT * FROM bookings WHERE listing_id = %s ORDER BY created_date DESC"
        results = db.execute_query(query, (listing_id,))
        bookings = []
        for booking_data in results:
            bookings.append(Booking(
                id=booking_data['id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                guests=booking_data['guests'],
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_date']
            ))
        return bookings
    
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
        
        query = """
            INSERT INTO bookings (listing_id, user_id, check_in, check_out, guests, total_price, created_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        booking_id = db.execute_insert(query, (
            listing_id, user_id, check_in, check_out, guests, total_price, datetime.now()
        ))
        
        if booking_id:
            return Booking.get(booking_id)
        return None
    
    @staticmethod
    def get(booking_id):
        """Get booking by ID"""
        query = "SELECT * FROM bookings WHERE id = %s"
        result = db.execute_query(query, (booking_id,))
        if result:
            booking_data = result[0]
            return Booking(
                id=booking_data['id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                guests=booking_data['guests'],
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_date']
            )
        return None
    
    def confirm(self):
        """Confirm a pending booking"""
        if self.status == 'pending':
            query = "UPDATE bookings SET status = 'confirmed' WHERE id = %s"
            return db.execute_update(query, (self.id,))
        return False
    
    def cancel(self):
        """Cancel a booking"""
        query = "UPDATE bookings SET status = 'cancelled' WHERE id = %s"
        return db.execute_update(query, (self.id,))
