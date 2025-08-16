from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.database import db

class User(UserMixin):
    def __init__(self, id, full_name, email, password_hash, phone=None, bio=None, user_type='guest', 
                 profile_photo=None, joined_date=None, verified=False):
        self.id = id
        self.full_name = full_name
        self.first_name = full_name.split()[0] if full_name else ""
        self.last_name = " ".join(full_name.split()[1:]) if full_name and len(full_name.split()) > 1 else ""
        self.name = full_name  # Alias for compatibility
        self.email = email
        self.password_hash = password_hash
        self.phone = phone
        self.bio = bio
        self.user_type = user_type
        self.profile_photo = profile_photo
        self.profile_picture_path = profile_photo  # Alias for template compatibility
        self.joined_date = joined_date or datetime.now()
        self.date_created = self.joined_date  # Alias for template compatibility
        self.join_date = self.joined_date  # Alias for compatibility
        self.verified = verified
        self.is_verified = verified  # Alias for template compatibility
        self.email_notifications = True  # Default value
        
        # Lazy-loaded properties for relationships
        self._listings = None
        self._guest_bookings = None
        self._host_bookings = None
        self._favorites = None
    
    @property
    def listings(self):
        """Get user's listings (for hosts)"""
        if self._listings is None and self.user_type == 'host':
            from app.models import Listing
            self._listings = Listing.get_by_host(self.id)
        return self._listings or []
    
    @property
    def guest_bookings(self):
        """Get user's bookings as a guest"""
        if self._guest_bookings is None:
            from app.models import Booking
            self._guest_bookings = Booking.get_by_user(self.id)
        return self._guest_bookings or []
    
    @property
    def host_bookings(self):
        """Get bookings for user's listings (for hosts)"""
        if self._host_bookings is None and self.user_type == 'host':
            from app.models import Booking
            self._host_bookings = Booking.get_by_host(self.id)
        return self._host_bookings or []
    
    @property
    def favorites(self):
        """Get user's favorite listings"""
        if self._favorites is None:
            from app.models import Favorite
            self._favorites = Favorite.get_by_user(self.id)
        return self._favorites or []
    
    def get_id(self):
        """Required by Flask-Login for session management"""
        return str(self.id)
    
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
            print(f"DEBUG: Found user data for {email}: {user_data}")  # Debug line
            return User(
                id=user_data['user_id'],
                full_name=user_data['name'],  # Use 'name' column as per your schema
                email=user_data['email'],
                password_hash=user_data['password_hash'] or '',
                phone=user_data['phone'] or '',
                bio=user_data['bio'] or '',
                user_type=user_data['user_type'] or 'guest',
                profile_photo=user_data['profile_photo'] or '',
                joined_date=user_data['join_date'] or datetime.now(),
                verified=bool(user_data['verified'])
            )
        return None
    
    @staticmethod
    def create(full_name, email, password, phone=None, bio=None, user_type='guest'):
        """Create a new user"""
        password_hash = generate_password_hash(password)
        
        query = """
            INSERT INTO users (name, email, password_hash, phone, bio, user_type, join_date)
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
    
    def update_profile(self, full_name=None, phone=None, profile_photo=None, bio=None):
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
            
        if bio is not None:
            update_fields.append("bio = %s")
            update_values.append(bio)
            self.bio = bio
        
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
    
    def update_verification_status(self, verified_status):
        """Update user verification status"""
        query = "UPDATE users SET verified = %s WHERE user_id = %s"
        if db.execute_update(query, (verified_status, self.id)):
            self.verified = verified_status
            return True
        return False
        
    def delete(self):
        """Delete user and all associated data"""
        try:
            print(f"DEBUG: Starting delete for user ID {self.id}")
            
            # Delete associated reviews
            print(f"DEBUG: Deleting reviews for user {self.id}")
            db.execute_update("DELETE FROM reviews WHERE user_id = %s", (self.id,))
            
            # Delete associated bookings
            print(f"DEBUG: Deleting bookings for user {self.id}")
            db.execute_update("DELETE FROM bookings WHERE user_id = %s", (self.id,))
            
            # Delete listings if user is a host
            print(f"DEBUG: Checking listings for user {self.id}")
            listings = Listing.get_by_host(self.id)
            for listing in listings:
                print(f"DEBUG: Deleting listing {listing.id}")
                listing.delete()
            
            # Delete user
            print(f"DEBUG: Deleting user record for {self.id}")
            db.execute_update("DELETE FROM users WHERE user_id = %s", (self.id,))
            print(f"DEBUG: User {self.id} deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            import traceback
            traceback.print_exc()
            return False


class Location:
    def __init__(self, location_id, address, city, country, latitude=None, longitude=None, postal_code=None, created_at=None):
        self.id = location_id
        self.address = address
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.postal_code = postal_code
        self.created_at = created_at

    @staticmethod
    def create(address, city, country, latitude=None, longitude=None, postal_code=None):
        """Create a new location"""
        query = """
            INSERT INTO locations (address, city, country, latitude, longitude, postal_code, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        location_id = db.execute_insert(query, (address, city, country, latitude, longitude, postal_code, datetime.now()))
        
        if location_id:
            return Location.get(location_id)
        return None

    @staticmethod
    def get(location_id):
        """Get location by ID"""
        query = "SELECT * FROM locations WHERE location_id = %s"
        result = db.execute_query(query, (location_id,))
        if result:
            loc = result[0]
            return Location(
                location_id=loc['location_id'],
                address=loc['address'],
                city=loc['city'],
                country=loc['country'],
                latitude=float(loc['latitude']) if loc['latitude'] else None,
                longitude=float(loc['longitude']) if loc['longitude'] else None,
                postal_code=loc['postal_code'],
                created_at=loc['created_at']
            )
        return None
    
    @staticmethod
    def find_or_create(address, city, country, latitude=0.0, longitude=0.0, postal_code=None):
        """Find existing location or create a new one"""
        # First try to find existing location with same address and city
        query = """
        SELECT * FROM locations 
        WHERE address = %s AND city = %s AND country = %s
        """
        result = db.execute_query(query, (address, city, country))
        
        if result:
            data = result[0]
            return Location(
                location_id=data['location_id'],
                address=data['address'],
                city=data['city'],
                country=data['country'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                postal_code=data['postal_code'],
                created_at=data['created_at']
            )
        else:
            # Create new location
            return Location.create(address, city, country, latitude, longitude, postal_code)
        

class ListingImage:
    def __init__(self, image_id, listing_id, image_filename, image_order=1, is_primary=False, uploaded_at=None):
        self.id = image_id
        self.listing_id = listing_id
        self.image_filename = image_filename
        self.image_order = image_order
        self.is_primary = is_primary
        self.uploaded_at = uploaded_at

    @staticmethod
    def create(listing_id, image_filename, image_order=1, is_primary=False):
        """Create a new listing image"""
        query = """
            INSERT INTO listing_images (listing_id, image_filename, image_order, is_primary, uploaded_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        image_id = db.execute_insert(query, (listing_id, image_filename, image_order, is_primary, datetime.now()))
        
        if image_id:
            return ListingImage.get(image_id)
        return None

    @staticmethod
    def get(image_id):
        """Get image by ID"""
        query = "SELECT * FROM listing_images WHERE image_id = %s"
        result = db.execute_query(query, (image_id,))
        if result:
            img = result[0]
            return ListingImage(
                image_id=img['image_id'],
                listing_id=img['listing_id'],
                image_filename=img['image_filename'],
                image_order=img['image_order'],
                is_primary=bool(img['is_primary']),
                uploaded_at=img['uploaded_at']
            )
        return None

    @staticmethod
    def get_by_listing(listing_id):
        """Get all images for a listing, ordered by image_order"""
        query = """
            SELECT * FROM listing_images 
            WHERE listing_id = %s 
            ORDER BY is_primary DESC, image_order ASC
        """
        results = db.execute_query(query, (listing_id,))
        images = []
        for img in results:
            images.append(ListingImage(
                image_id=img['image_id'],
                listing_id=img['listing_id'],
                image_filename=img['image_filename'],
                image_order=img['image_order'],
                is_primary=bool(img['is_primary']),
                uploaded_at=img['uploaded_at']
            ))
        return images

    @staticmethod
    def set_primary(listing_id, image_id):
        """Set an image as primary (and unset others)"""
        # First, unset all primary images for this listing
        query1 = "UPDATE listing_images SET is_primary = FALSE WHERE listing_id = %s"
        db.execute_update(query1, (listing_id,))
        
        # Then set the specified image as primary
        query2 = "UPDATE listing_images SET is_primary = TRUE WHERE image_id = %s AND listing_id = %s"
        return db.execute_update(query2, (image_id, listing_id))

    def delete(self):
        """Delete this image"""
        query = "DELETE FROM listing_images WHERE image_id = %s"
        return db.execute_update(query, (self.id,))


class Listing:
    def __init__(self, id, title, description, location, price, host_id, property_type='entire_place',
                 guests=1, bedrooms=1, bathrooms=1, amenities=None, address='', city='', country='Bangladesh',
                 created_date=None, rating=0.0, reviews_count=0, available=True, images=None, 
                 latitude=None, longitude=None):
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
        self.latitude = latitude
        self.longitude = longitude
    
    @staticmethod
    def get(listing_id):
        """Get listing by ID with location and images"""
        query = """
            SELECT l.*, loc.address as location_address, loc.city as location_city, 
                   loc.country as location_country, loc.latitude, loc.longitude 
            FROM listings l 
            LEFT JOIN locations loc ON l.location_id = loc.location_id 
            WHERE l.listing_id = %s
        """
        result = db.execute_query(query, (listing_id,))
        if result:
            listing_data = result[0]
            
            # Get listing images
            images = ListingImage.get_by_listing(listing_id)
            
            return Listing(
                id=listing_data['listing_id'],
                title=listing_data['title'],
                description=listing_data['description'],
                location=f"{listing_data['location_city']}, {listing_data['location_country']}" if listing_data['location_city'] else f"{listing_data['city']}, {listing_data['country']}",
                price=float(listing_data['price_per_night']),
                host_id=listing_data['host_id'],
                property_type=listing_data['room_type'],
                guests=listing_data['max_guests'],
                bedrooms=listing_data['bedrooms'] or 1,
                bathrooms=listing_data['bathrooms'] or 1,
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                address=listing_data['location_address'] or listing_data['address'],
                city=listing_data['location_city'] or listing_data['city'],
                country=listing_data['location_country'] or listing_data['country'],
                created_date=listing_data['created_at'],
                rating=0.0,  # Will be calculated from reviews
                reviews_count=0,  # Will be calculated from reviews
                available=True,  # Default
                images=[img.image_filename for img in images],
                latitude=float(listing_data['latitude']) if listing_data['latitude'] else None,
                longitude=float(listing_data['longitude']) if listing_data['longitude'] else None
            )
        return None
    
    @staticmethod
    def get_all():
        """Get all listings with location and images"""
        query = """
            SELECT l.*, loc.address as location_address, loc.city as location_city, 
                   loc.country as location_country, loc.latitude, loc.longitude 
            FROM listings l 
            LEFT JOIN locations loc ON l.location_id = loc.location_id 
            ORDER BY l.created_at DESC
        """
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
            
            # Get listing images
            images = ListingImage.get_by_listing(listing_data['listing_id'])
            
            listing = Listing(
                id=listing_data['listing_id'],
                title=listing_data['title'],
                description=listing_data['description'],
                location=f"{listing_data['location_city']}, {listing_data['location_country']}" if listing_data['location_city'] else f"{listing_data['city']}, {listing_data['country']}",
                price=float(listing_data['price_per_night']),
                host_id=listing_data['host_id'],
                property_type=listing_data['room_type'],
                guests=listing_data['max_guests'],
                bedrooms=listing_data['bedrooms'] or 1,
                bathrooms=listing_data['bathrooms'] or 1,
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                address=listing_data['location_address'] or listing_data['address'],
                city=listing_data['location_city'] or listing_data['city'],
                country=listing_data['location_country'] or listing_data['country'],
                created_date=listing_data['created_at'],
                rating=avg_rating,
                reviews_count=review_count,
                available=True,
                images=[img.image_filename for img in images],
                latitude=float(listing_data['latitude']) if listing_data['latitude'] else None,
                longitude=float(listing_data['longitude']) if listing_data['longitude'] else None
            )
            listings.append(listing)
        return listings
    
    @staticmethod
    def get_by_host(host_id):
        """Get all listings by a host"""
        query = """
            SELECT l.*, loc.address, loc.city, loc.country, loc.latitude, loc.longitude 
            FROM listings l 
            LEFT JOIN locations loc ON l.location_id = loc.location_id 
            WHERE l.host_id = %s 
            ORDER BY l.created_at DESC
        """
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
                available=True,
                latitude=float(listing_data['latitude']) if listing_data['latitude'] else None,
                longitude=float(listing_data['longitude']) if listing_data['longitude'] else None
            )
            listings.append(listing)
        return listings
    
    @staticmethod
    def create(title, description, location, price, host_id, property_type='entire_place',
               guests=1, bedrooms=1, bathrooms=1, amenities=None, location_id=None):
        """Create a new listing with proper location_id reference"""
        amenities_str = ','.join(amenities) if amenities else ''
        
        # Validate that location_id is provided
        if not location_id:
            print("Error: location_id is required for creating listings")
            return None
        
        # Create the listing with the new schema (no location fields)
        listing_query = """
            INSERT INTO listings (host_id, title, description, room_type, price_per_night, 
                                max_guests, bedrooms, bathrooms, amenities, location_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        listing_id = db.execute_insert(listing_query, (
            host_id, title, description, property_type, price, guests, 
            bedrooms, bathrooms, amenities_str, location_id, datetime.now()
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
            try:
                # Get the date values
                check_in_date = booking['check_in']
                check_out_date = booking['check_out']
                
                # Convert datetime to date if needed
                if hasattr(check_in_date, 'date') and not isinstance(check_in_date, date):
                    check_in_date = check_in_date.date()
                if hasattr(check_out_date, 'date') and not isinstance(check_out_date, date):
                    check_out_date = check_out_date.date()
                
                # Generate all dates in the range using date arithmetic
                current = check_in_date
                one_day = timedelta(days=1)  # Use the module-level import
                
                while current < check_out_date:
                    unavailable_dates.append(current.strftime('%Y-%m-%d'))
                    current = current + one_day
                    
            except Exception:
                # Skip any problematic booking records
                continue
                
        return unavailable_dates
    
    def calculate_total_price(self, check_in, check_out, guests=1):
        """Calculate total price for booking"""
        nights = (check_out - check_in).days
        base_price = self.price * nights
        cleaning_fee = 500  # Fixed cleaning fee
        service_fee = base_price * 0.15  # 15% service fee
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
        """Get all reviews for a listing with user names and profile photos"""
        query = """
            SELECT r.*, u.name as user_name, u.profile_photo 
            FROM reviews r 
            LEFT JOIN users u ON r.reviewer_id = u.user_id 
            WHERE r.listing_id = %s 
            ORDER BY r.review_date DESC
        """
        results = db.execute_query(query, (listing_id,))
        reviews = []
        for review_data in results:
            review = Review(
                id=review_data['review_id'],
                listing_id=review_data['listing_id'],
                user_id=review_data['reviewer_id'],
                rating=float(review_data['rating']),
                comment=review_data['comments'],
                created_date=review_data['review_date']
            )
            # Add user name and profile photo as attributes
            review.user_name = review_data['user_name']
            review.user_profile_photo = review_data['profile_photo']
            reviews.append(review)
        return reviews
    
    @staticmethod
    def get_by_user(user_id):
        """Get all reviews written by a user"""
        query = "SELECT * FROM reviews WHERE reviewer_id = %s ORDER BY review_date DESC"
        results = db.execute_query(query, (user_id,))
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
                 status='pending', created_date=None, confirmed_by=None, confirmed_at=None):
        self.id = id
        self.booking_id = id  # Alias for consistency
        self.listing_id = listing_id
        self.user_id = user_id
        self.check_in = check_in
        self.check_out = check_out
        self.total_price = total_price
        self.status = status
        self.created_date = created_date or datetime.now()
        self.created_at = created_date or datetime.now()  # Alias for consistency
        self.confirmed_by = confirmed_by
        self.confirmed_at = confirmed_at
    
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
                created_date=booking_data['created_at'],
                confirmed_by=booking_data['confirmed_by'],
                confirmed_at=booking_data['confirmed_at']
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
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_at'],
                confirmed_by=booking_data['confirmed_by'],
                confirmed_at=booking_data['confirmed_at']
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
                created_date=booking_data['created_at'],
                confirmed_by=booking_data['confirmed_by'],
                confirmed_at=booking_data['confirmed_at']
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
    
    @staticmethod
    def get_by_guest(user_id):
        """Get all bookings by a guest user (alias for get_by_user)"""
        return Booking.get_by_user(user_id)
    
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


class Favorite:
    """Favorite listing model"""
    def __init__(self, id, user_id, listing_id, created_date=None):
        self.id = id
        self.user_id = user_id
        self.listing_id = listing_id
        self.created_date = created_date or datetime.now()
    
    @staticmethod
    def get_by_user(user_id):
        """Get all favorites for a user"""
        query = "SELECT * FROM favorites WHERE user_id = %s ORDER BY created_at DESC"
        results = db.execute_query(query, (user_id,))
        favorites = []
        for fav_data in results:
            favorites.append(Favorite(
                id=fav_data['favorite_id'],
                user_id=fav_data['user_id'],
                listing_id=fav_data['listing_id'],
                created_date=fav_data['created_at']
            ))
        return favorites
    
    @staticmethod
    def add(user_id, listing_id):
        """Add a listing to favorites"""
        # Check if already favorited
        query = "SELECT * FROM favorites WHERE user_id = %s AND listing_id = %s"
        existing = db.execute_query(query, (user_id, listing_id))
        if existing:
            return False  # Already favorited
        
        query = "INSERT INTO favorites (user_id, listing_id, created_at) VALUES (%s, %s, %s)"
        favorite_id = db.execute_insert(query, (user_id, listing_id, datetime.now()))
        return favorite_id is not None
    
    @staticmethod
    def remove(user_id, listing_id):
        """Remove a listing from favorites"""
        query = "DELETE FROM favorites WHERE user_id = %s AND listing_id = %s"
        return db.execute_update(query, (user_id, listing_id))
    
    @staticmethod
    def is_favorited(user_id, listing_id):
        """Check if a listing is favorited by a user"""
        query = "SELECT * FROM favorites WHERE user_id = %s AND listing_id = %s"
        result = db.execute_query(query, (user_id, listing_id))
        return len(result) > 0
