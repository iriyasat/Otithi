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
        query = "SELECT * FROM users WHERE user_id = %s"
        result = db.execute_query(query, (user_id,))
        if result:
            user_data = result[0]
            return User(
                id=user_data['user_id'],
                full_name=user_data['name'],
                email=user_data['email'],
                password_hash=user_data.get('password_hash', ''),  # May not exist in schema
                phone=user_data['phone'],
                bio=user_data.get('bio', ''),
                user_type=user_data['user_type'],
                profile_photo=user_data['profile_photo'],
                joined_date=user_data['join_date'],
                verified=user_data.get('verified', False)
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
                id=user_data['user_id'],
                full_name=user_data['name'],
                email=user_data['email'],
                password_hash=user_data.get('password_hash', ''),
                phone=user_data['phone'],
                bio=user_data.get('bio', ''),
                user_type=user_data['user_type'],
                profile_photo=user_data['profile_photo'],
                joined_date=user_data['join_date'],
                verified=user_data.get('verified', False)
            )
        return None
    
    @staticmethod
    def create(full_name, email, password, phone=None, bio=None, user_type='guest'):
        """Create a new user"""
        password_hash = generate_password_hash(password)
        # First add password_hash column if it doesn't exist
        try:
            db.execute_update("ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)")
        except:
            pass  # Column might already exist
        
        query = """
            INSERT INTO users (name, email, password_hash, phone, user_type, join_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        user_id = db.execute_insert(query, (
            full_name, email, password_hash, phone, user_type, datetime.now()
        ))
        
        if user_id:
            return User.get(user_id)
        return None
    
    def save(self):
        """Save user changes to database"""
        query = """
            UPDATE users 
            SET name = %s, phone = %s, profile_photo = %s
            WHERE user_id = %s
        """
        return db.execute_update(query, (
            self.full_name, self.phone, self.profile_photo, self.id
        ))
    
    @staticmethod
    def get_all():
        """Get all users"""
        query = "SELECT * FROM users ORDER BY join_date DESC"
        results = db.execute_query(query)
        users = []
        for user_data in results:
            user = User(
                id=user_data['user_id'],
                full_name=user_data['name'],
                email=user_data['email'],
                password_hash=user_data.get('password_hash', ''),
                phone=user_data['phone'],
                bio=user_data.get('bio', ''),
                user_type=user_data['user_type'],
                profile_photo=user_data['profile_photo'],
                joined_date=user_data['join_date'],
                verified=user_data.get('verified', False)
            )
            users.append(user)
        return users
    
    def update_user_type(self, new_user_type):
        """Update user type (for admin use)"""
        query = "UPDATE users SET user_type = %s WHERE user_id = %s"
        return db.execute_update(query, (new_user_type, self.id))
    
    def update_profile(self, full_name=None, phone=None, profile_photo=None):
        """Update user profile"""
        update_fields = []
        update_values = []
        
        if full_name:
            update_fields.append("name = %s")
            update_values.append(full_name)
            self.full_name = full_name
            
        if phone:
            update_fields.append("phone = %s")
            update_values.append(phone)
            self.phone = phone
            
        if profile_photo:
            update_fields.append("profile_photo = %s")
            update_values.append(profile_photo)
            self.profile_photo = profile_photo
        
        if update_fields:
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE user_id = %s"
            update_values.append(self.id)
            return db.execute_update(query, tuple(update_values))
        return True
    
    def update_password(self, new_password):
        """Update user password"""
        password_hash = generate_password_hash(new_password)
        query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        return db.execute_update(query, (password_hash, self.id))
        
    def delete(self):
        """Delete user and all associated data"""
        try:
            # Delete associated reviews
            db.execute_update("DELETE FROM reviews WHERE user_id = %s", (self.id,))
            
            # Delete associated bookings
            db.execute_update("DELETE FROM bookings WHERE user_id = %s", (self.id,))
            
            # Delete listings if user is a host
            listings = Listing.get_by_host(self.id)
            for listing in listings:
                listing.delete()
            
            # Delete user
            db.execute_update("DELETE FROM users WHERE user_id = %s", (self.id,))
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

class Listing:
    def __init__(self, id, title, description, location, price, host_id, property_type='entire_place',
                 guests=1, bedrooms=1, bathrooms=1, amenities=None, address='', city='', country='Bangladesh',
                 created_date=None, rating=0.0, reviews_count=0, available=True, images=None):
        self.id = id
        self.title = title
        self.description = description
        self.location = f"{city}, {country}" if city and country else location
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
        query = "SELECT * FROM listings WHERE listing_id = %s"
        result = db.execute_query(query, (listing_id,))
        if result:
            listing_data = result[0]
            return Listing(
                id=listing_data['listing_id'],
                title=listing_data['title'],
                description=listing_data['description'],
                location=f"{listing_data['city']}, {listing_data['country']}",
                price=float(listing_data['price_per_night']),
                host_id=listing_data['host_id'],
                property_type=listing_data['room_type'],
                guests=listing_data['max_guests'],
                bedrooms=1,  # Default, not in schema
                bathrooms=1,  # Default, not in schema
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                address=listing_data['address'],
                city=listing_data['city'],
                country=listing_data['country'],
                created_date=listing_data['created_at'],
                rating=0.0,  # Will be calculated from reviews
                reviews_count=0,  # Will be calculated from reviews
                available=True  # Default
            )
        return None
    
    @staticmethod
    def get_all():
        """Get all listings"""
        query = "SELECT * FROM listings ORDER BY created_at DESC"
        results = db.execute_query(query)
        listings = []
        for listing_data in results:
            # Calculate rating and review count
            rating_query = """
                SELECT AVG(rating) as avg_rating, COUNT(*) as review_count 
                FROM reviews WHERE listing_id = %s
            """
            rating_result = db.execute_query(rating_query, (listing_data['listing_id'],))
            avg_rating = float(rating_result[0]['avg_rating']) if rating_result[0]['avg_rating'] else 0.0
            review_count = rating_result[0]['review_count']
            
            listing = Listing(
                id=listing_data['listing_id'],
                title=listing_data['title'],
                description=listing_data['description'],
                location=f"{listing_data['city']}, {listing_data['country']}",
                price=float(listing_data['price_per_night']),
                host_id=listing_data['host_id'],
                property_type=listing_data['room_type'],
                guests=listing_data['max_guests'],
                bedrooms=1,
                bathrooms=1,
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                address=listing_data['address'],
                city=listing_data['city'],
                country=listing_data['country'],
                created_date=listing_data['created_at'],
                rating=avg_rating,
                reviews_count=review_count,
                available=True
            )
            listings.append(listing)
        return listings
    
    @staticmethod
    def get_by_host(host_id):
        """Get all listings by a host"""
        query = "SELECT * FROM listings WHERE host_id = %s ORDER BY created_at DESC"
        results = db.execute_query(query, (host_id,))
        listings = []
        for listing_data in results:
            listing = Listing(
                id=listing_data['listing_id'],
                title=listing_data['title'],
                description=listing_data['description'],
                location=f"{listing_data['city']}, {listing_data['country']}",
                price=float(listing_data['price_per_night']),
                host_id=listing_data['host_id'],
                property_type=listing_data['room_type'],
                guests=listing_data['max_guests'],
                bedrooms=1,
                bathrooms=1,
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                address=listing_data['address'],
                city=listing_data['city'],
                country=listing_data['country'],
                created_date=listing_data['created_at'],
                rating=0.0,
                reviews_count=0,
                available=True
            )
            listings.append(listing)
        return listings
    
    @staticmethod
    def create(title, description, location, price, host_id, property_type='entire_place',
               guests=1, bedrooms=1, bathrooms=1, amenities=None, address='', city='', country='Bangladesh'):
        """Create a new listing"""
        amenities_str = ','.join(amenities) if amenities else ''
        query = """
            INSERT INTO listings (host_id, title, description, address, city, country, 
                                room_type, price_per_night, max_guests, amenities, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        listing_id = db.execute_insert(query, (
            host_id, title, description, address, city, country, 
            property_type, price, guests, amenities_str, datetime.now()
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
    
    def calculate_total_price(self, check_in, check_out, guests=1):
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
    
    def update(self, title=None, description=None, price=None, property_type=None, guests=None, amenities=None):
        """Update listing details"""
        update_fields = []
        update_values = []
        
        if title:
            update_fields.append("title = %s")
            update_values.append(title)
            self.title = title
            
        if description:
            update_fields.append("description = %s")
            update_values.append(description)
            self.description = description
            
        if price:
            update_fields.append("price_per_night = %s")
            update_values.append(price)
            self.price = price
            
        if property_type:
            update_fields.append("room_type = %s")
            update_values.append(property_type)
            self.property_type = property_type
            
        if guests:
            update_fields.append("max_guests = %s")
            update_values.append(guests)
            self.guests = guests
            
        if amenities:
            amenities_str = ','.join(amenities) if isinstance(amenities, list) else amenities
            update_fields.append("amenities = %s")
            update_values.append(amenities_str)
            self.amenities = amenities if isinstance(amenities, list) else amenities.split(',')
        
        if update_fields:
            query = f"UPDATE listings SET {', '.join(update_fields)} WHERE listing_id = %s"
            update_values.append(self.id)
            return db.execute_update(query, tuple(update_values))
        return True
    
    def delete(self):
        """Delete listing and all associated data"""
        try:
            # Delete associated reviews
            db.execute_update("DELETE FROM reviews WHERE listing_id = %s", (self.id,))
            
            # Delete associated bookings
            db.execute_update("DELETE FROM bookings WHERE listing_id = %s", (self.id,))
            
            # Delete listing
            db.execute_update("DELETE FROM listings WHERE listing_id = %s", (self.id,))
            return True
        except Exception as e:
            print(f"Error deleting listing: {e}")
            return False
    
    def approve(self):
        """Approve listing (admin function)"""
        # Add approved status column if it doesn't exist
        try:
            db.execute_update("ALTER TABLE listings ADD COLUMN approved BOOLEAN DEFAULT FALSE")
        except:
            pass
        
        query = "UPDATE listings SET approved = TRUE WHERE listing_id = %s"
        return db.execute_update(query, (self.id,))

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
        query = "SELECT * FROM reviews ORDER BY review_date DESC"
        results = db.execute_query(query)
        reviews = []
        for review_data in results:
            reviews.append(Review(
                id=review_data['review_id'],
                listing_id=review_data['listing_id'],
                user_id=review_data['reviewer_id'],
                rating=float(review_data['rating']),
                comment=review_data['comments'],
                created_date=review_data['review_date']
            ))
        return reviews
    
    @staticmethod
    def get_by_listing(listing_id):
        """Get all reviews for a listing"""
        query = "SELECT * FROM reviews WHERE listing_id = %s ORDER BY review_date DESC"
        results = db.execute_query(query, (listing_id,))
        reviews = []
        for review_data in results:
            reviews.append(Review(
                id=review_data['review_id'],
                listing_id=review_data['listing_id'],
                user_id=review_data['reviewer_id'],
                rating=float(review_data['rating']),
                comment=review_data['comments'],
                created_date=review_data['review_date']
            ))
        return reviews
    
    @staticmethod
    def create(listing_id, user_id, rating, comment):
        """Create a new review"""
        query = """
            INSERT INTO reviews (reviewer_id, listing_id, rating, comments, review_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        review_id = db.execute_insert(query, (user_id, listing_id, rating, comment, datetime.now()))
        
        if review_id:
            return Review.get(review_id)
        return None
    
    @staticmethod
    def get(review_id):
        """Get review by ID"""
        query = "SELECT * FROM reviews WHERE review_id = %s"
        result = db.execute_query(query, (review_id,))
        if result:
            review_data = result[0]
            return Review(
                id=review_data['review_id'],
                listing_id=review_data['listing_id'],
                user_id=review_data['reviewer_id'],
                rating=float(review_data['rating']),
                comment=review_data['comments'],
                created_date=review_data['review_date']
            )
        return None

class Booking:
    def __init__(self, id, listing_id, user_id, check_in, check_out, total_price, 
                 status='pending', created_date=None):
        self.id = id
        self.listing_id = listing_id
        self.user_id = user_id
        self.check_in = check_in
        self.check_out = check_out
        self.total_price = total_price
        self.status = status
        self.created_date = created_date or datetime.now()
    
    @staticmethod
    def get_all():
        """Get all bookings"""
        query = "SELECT * FROM bookings ORDER BY created_at DESC"
        results = db.execute_query(query)
        bookings = []
        for booking_data in results:
            bookings.append(Booking(
                id=booking_data['booking_id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_at']
            ))
        return bookings
    
    @staticmethod
    def get_by_user(user_id):
        """Get all bookings by a user"""
        query = "SELECT * FROM bookings WHERE user_id = %s ORDER BY created_at DESC"
        results = db.execute_query(query, (user_id,))
        bookings = []
        for booking_data in results:
            bookings.append(Booking(
                id=booking_data['booking_id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                guests=1,
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_at']
            ))
        return bookings
    
    @staticmethod
    def get_by_host(host_id):
        """Get all bookings for a host's listings"""
        query = """
            SELECT b.* FROM bookings b
            JOIN listings l ON b.listing_id = l.listing_id
            WHERE l.host_id = %s
            ORDER BY b.created_at DESC
        """
        results = db.execute_query(query, (host_id,))
        bookings = []
        for booking_data in results:
            bookings.append(Booking(
                id=booking_data['booking_id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_at']
            ))
        return bookings
    
    @staticmethod
    def get_by_listing(listing_id):
        """Get all bookings for a specific listing"""
        query = "SELECT * FROM bookings WHERE listing_id = %s ORDER BY created_at DESC"
        results = db.execute_query(query, (listing_id,))
        bookings = []
        for booking_data in results:
            bookings.append(Booking(
                id=booking_data['booking_id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_at']
            ))
        return bookings
    
    @staticmethod
    def create(listing_id, user_id, check_in, check_out):
        """Create a new booking"""
        listing = Listing.get(listing_id)
        if not listing:
            return None
        
        # Check availability
        if not listing.is_available(check_in, check_out):
            return None
        
        # Calculate price (using default guests=1 for calculation)
        price_breakdown = listing.calculate_total_price(check_in, check_out, 1)
        total_price = price_breakdown['total']
        
        query = """
            INSERT INTO bookings (user_id, listing_id, check_in, check_out, total_price, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        booking_id = db.execute_insert(query, (
            user_id, listing_id, check_in, check_out, total_price, datetime.now()
        ))
        
        if booking_id:
            return Booking.get(booking_id)
        return None
    
    @staticmethod
    def get(booking_id):
        """Get booking by ID"""
        query = "SELECT * FROM bookings WHERE booking_id = %s"
        result = db.execute_query(query, (booking_id,))
        if result:
            booking_data = result[0]
            return Booking(
                id=booking_data['booking_id'],
                listing_id=booking_data['listing_id'],
                user_id=booking_data['user_id'],
                check_in=booking_data['check_in'],
                check_out=booking_data['check_out'],
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_at']
            )
        return None
    
    def confirm(self):
        """Confirm a pending booking"""
        if self.status == 'pending':
            query = "UPDATE bookings SET status = 'confirmed' WHERE booking_id = %s"
            return db.execute_update(query, (self.id,))
        return False
    
    def cancel(self):
        """Cancel a booking"""
        query = "UPDATE bookings SET status = 'cancelled' WHERE booking_id = %s"
        return db.execute_update(query, (self.id,))
    
    def update_status(self, new_status):
        """Update booking status"""
        if new_status in ['pending', 'confirmed', 'cancelled']:
            query = "UPDATE bookings SET status = %s WHERE booking_id = %s"
            if db.execute_update(query, (new_status, self.id)):
                self.status = new_status
                return True
        return False
