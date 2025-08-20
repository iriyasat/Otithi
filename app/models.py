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
        """Get user by ID - Updated for new schema with user_details table"""
        query = """
            SELECT u.*, ud.profile_photo, ud.phone, ud.bio, 
                   ud.user_type, ud.join_date, ud.verified, ud.is_active,
                   ud.created_at, ud.updated_at
            FROM users u
            LEFT JOIN user_details ud ON u.user_id = ud.user_id
            WHERE u.user_id = %s
        """
        result = db.execute_query(query, (user_id,))
        if result:
            user_data = result[0]
            return User(
                id=user_data['user_id'],
                full_name=user_data['name'],
                email=user_data['email'],
                password_hash=user_data.get('password_hash', ''),
                phone=user_data.get('phone', ''),
                bio=user_data.get('bio', ''),
                user_type=user_data.get('user_type', 'guest'),
                profile_photo=user_data.get('profile_photo', ''),
                joined_date=user_data.get('join_date'),
                verified=user_data.get('verified', False)
            )
        return None
    
    @staticmethod
    def get_by_email(email):
        """Get user by email - Updated for new schema"""
        query = """
            SELECT u.*, ud.profile_photo, ud.phone, ud.bio, 
                   ud.user_type, ud.join_date, ud.verified, ud.is_active,
                   ud.created_at, ud.updated_at
            FROM users u
            LEFT JOIN user_details ud ON u.user_id = ud.user_id
            WHERE u.email = %s
        """
        result = db.execute_query(query, (email,))
        if result:
            user_data = result[0]
            return User(
                id=user_data['user_id'],
                full_name=user_data['name'],
                email=user_data['email'],
                password_hash=user_data.get('password_hash', ''),
                phone=user_data.get('phone', ''),
                bio=user_data.get('bio', ''),
                user_type=user_data.get('user_type', 'guest'),
                profile_photo=user_data.get('profile_photo', ''),
                joined_date=user_data.get('join_date'),
                verified=user_data.get('verified', False)
            )
        return None
    
    @staticmethod
    def create(full_name, email, password, phone=None, bio=None, user_type='guest'):
        """Create a new user - Updated for new schema with user_details table"""
        password_hash = generate_password_hash(password)
        
        try:
            # First create user in users table
            user_query = """
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
            """
            user_id = db.execute_insert(user_query, (full_name, email, password_hash))
            
            if user_id:
                # Then create user details
                details_query = """
                    INSERT INTO user_details (user_id, phone, bio, user_type, join_date, verified, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                db.execute_insert(details_query, (
                    user_id, phone, bio, user_type, datetime.now(), False, True
                ))
                
                return User.get(user_id)
        except Exception as e:
            print(f"Error creating user: {e}")
        
        return None
    
    def save(self):
        """Save user changes to database - Updated for new schema"""
        try:
            # Update users table
            user_query = """
                UPDATE users 
                SET name = %s, email = %s
                WHERE user_id = %s
            """
            db.execute_update(user_query, (self.full_name, self.email, self.id))
            
            # Update user_details table
            details_query = """
                UPDATE user_details 
                SET phone = %s, bio = %s, profile_photo = %s, updated_at = %s
                WHERE user_id = %s
            """
            return db.execute_update(details_query, (
                self.phone, self.bio, self.profile_photo, datetime.now(), self.id
            ))
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    @staticmethod
    def get_all():
        """Get all users - Updated for new schema"""
        query = """
            SELECT u.*, ud.profile_photo, ud.phone, ud.bio, 
                   ud.user_type, ud.join_date, ud.verified, ud.is_active,
                   ud.created_at, ud.updated_at
            FROM users u
            LEFT JOIN user_details ud ON u.user_id = ud.user_id
            ORDER BY ud.join_date DESC
        """
        results = db.execute_query(query)
        users = []
        for user_data in results:
            user = User(
                id=user_data['user_id'],
                full_name=user_data['name'],
                email=user_data['email'],
                password_hash=user_data.get('password_hash', ''),
                phone=user_data.get('phone', ''),
                bio=user_data.get('bio', ''),
                user_type=user_data.get('user_type', 'guest'),
                profile_photo=user_data.get('profile_photo', ''),
                joined_date=user_data.get('join_date'),
                verified=user_data.get('verified', False)
            )
            users.append(user)
        return users
    
    def update_user_type(self, new_user_type):
        """Update user type (for admin use) - Updated for new schema"""
        query = "UPDATE user_details SET user_type = %s, updated_at = %s WHERE user_id = %s"
        if db.execute_update(query, (new_user_type, datetime.now(), self.id)):
            self.user_type = new_user_type
            return True
        return False
    
    def update_profile(self, full_name=None, phone=None, profile_photo=None, bio=None):
        """Update user profile - Updated for new schema"""
        user_updates = []
        user_values = []
        details_updates = []
        details_values = []
        
        if full_name:
            user_updates.append("name = %s")
            user_values.append(full_name)
            self.full_name = full_name
            self.name = full_name
            
        if phone is not None:
            details_updates.append("phone = %s")
            details_values.append(phone)
            self.phone = phone
            
        if profile_photo is not None:
            details_updates.append("profile_photo = %s")
            details_values.append(profile_photo)
            self.profile_photo = profile_photo
            
        if bio is not None:
            details_updates.append("bio = %s")
            details_values.append(bio)
            self.bio = bio
        
        success = True
        
        # Update users table if needed
        if user_updates:
            query = f"UPDATE users SET {', '.join(user_updates)} WHERE user_id = %s"
            user_values.append(self.id)
            success = db.execute_update(query, tuple(user_values))
        
        # Update user_details table if needed
        if details_updates and success:
            details_updates.append("updated_at = %s")
            details_values.extend([datetime.now(), self.id])
            query = f"UPDATE user_details SET {', '.join(details_updates)} WHERE user_id = %s"
            success = db.execute_update(query, tuple(details_values))
        
        return success
    
    def update_password(self, new_password):
        """Update user password"""
        password_hash = generate_password_hash(new_password)
        query = "UPDATE users SET password_hash = %s WHERE user_id = %s"
        return db.execute_update(query, (password_hash, self.id))
    
    def update_verification_status(self, verified_status):
        """Update user verification status - Updated for new schema"""
        query = "UPDATE user_details SET verified = %s, updated_at = %s WHERE user_id = %s"
        if db.execute_update(query, (verified_status, datetime.now(), self.id)):
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
    def __init__(self, location_id, address, city, country, latitude=None, longitude=None, postal_code=None, created_at=None, listing_id=None):
        self.id = location_id
        self.location_id = location_id  # Alias for consistency
        self.address = address
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.postal_code = postal_code
        self.created_at = created_at
        self.listing_id = listing_id

    @staticmethod
    def create(address, city, country, latitude=None, longitude=None, postal_code=None):
        """Create a new location"""
        query = """
            INSERT INTO locations (address, city, country, latitude, longitude, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        location_id = db.execute_insert(query, (address, city, country, latitude, longitude, datetime.now()))
        
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
                postal_code=None,  # Not in schema
                created_at=loc['created_at'],
                listing_id=loc.get('listing_id')  # New field
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
                postal_code=None,  # Not in schema
                created_at=data['created_at'],
                listing_id=data.get('listing_id')  # New field
            )
        else:
            # Create new location
            return Location.create(address, city, country, latitude, longitude, postal_code)
        

class ListingImage:
    def __init__(self, image_id, listing_id, image_filename, image_order=1, is_primary=False, uploaded_at=None):
        self.id = image_id
        self.image_id = image_id  # Alias for consistency
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
    def __init__(self, id, title, description, price, host_id, location_id, property_type='entire_place',
                 guests=1, amenities=None, created_date=None, rating=0.0, reviews_count=0, 
                 available=True, images=None, is_active=True):
        self.id = id
        self.listing_id = id  # Alias for consistency
        self.title = title
        self.description = description
        self.price = price
        self.host_id = host_id
        self.location_id = location_id
        self.property_type = property_type
        self.room_type = property_type  # Alias for schema
        self.guests = guests
        self.max_guests = guests  # Alias for schema
        self.amenities = amenities or []
        self.created_date = created_date or datetime.now()
        self.created_at = created_date or datetime.now()  # Alias for schema
        self.rating = rating
        self.reviews_count = reviews_count
        self.available = available
        self.is_active = is_active
        self.images = images or []
        
        # Location will be loaded separately via location_id
        self.location = None
        self.address = None
        self.city = None
        self.country = None
        self.latitude = None
        self.longitude = None
    
    @staticmethod
    def get(listing_id):
        """Get listing by ID with location details"""
        query = """
            SELECT l.*, loc.address, loc.city, loc.country, loc.latitude, loc.longitude 
            FROM listings l 
            LEFT JOIN locations loc ON l.location_id = loc.location_id 
            WHERE l.listing_id = %s AND l.is_active = 1
        """
        result = db.execute_query(query, (listing_id,))
        if result:
            listing_data = result[0]
            
            # Get listing images
            images = ListingImage.get_by_listing(listing_id)
            
            # Create listing object
            listing = Listing(
                id=listing_data['listing_id'],
                title=listing_data['title'],
                description=listing_data['description'],
                price=float(listing_data['price_per_night']),
                host_id=listing_data['host_id'],
                location_id=listing_data['location_id'],
                property_type=listing_data['room_type'],
                guests=listing_data['max_guests'],
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                created_date=listing_data['created_at'],
                is_active=listing_data['is_active']
            )
            
            # Set location details from joined data
            if listing_data['address']:
                listing.address = listing_data['address']
                listing.city = listing_data['city']
                listing.country = listing_data['country']
                listing.location = f"{listing_data['city']}, {listing_data['country']}"
                listing.latitude = float(listing_data['latitude']) if listing_data['latitude'] else None
                listing.longitude = float(listing_data['longitude']) if listing_data['longitude'] else None
            
            # Set images
            listing.images = [img.image_filename for img in images]
            
            return listing
        return None
    
    @staticmethod
    def get_all():
        """Get all active listings with location and images"""
        query = """
            SELECT l.*, loc.address as location_address, loc.city as location_city, 
                   loc.country as location_country, loc.latitude, loc.longitude 
            FROM listings l 
            LEFT JOIN locations loc ON l.location_id = loc.location_id 
            WHERE l.is_active = 1
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
                price=float(listing_data['price_per_night']),
                host_id=listing_data['host_id'],
                location_id=listing_data['location_id'],
                property_type=listing_data['room_type'],
                guests=listing_data['max_guests'],
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                created_date=listing_data['created_at'],
                rating=avg_rating,
                reviews_count=review_count,
                available=True,
                images=[img.image_filename for img in images],
                is_active=bool(listing_data.get('is_active', 1))
            )
            
            # Add location details as separate attributes
            listing.address = listing_data['location_address'] or listing_data.get('address', '')
            listing.city = listing_data['location_city'] or listing_data.get('city', '')
            listing.country = listing_data['location_country'] or listing_data.get('country', '')
            listing.location = f"{listing.city}, {listing.country}" if listing.city and listing.country else ""
            listing.latitude = float(listing_data['latitude']) if listing_data['latitude'] else None
            listing.longitude = float(listing_data['longitude']) if listing_data['longitude'] else None
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
            # Calculate rating and review count
            rating_query = """
                SELECT AVG(rating) as avg_rating, COUNT(*) as review_count 
                FROM reviews WHERE listing_id = %s
            """
            rating_result = db.execute_query(rating_query, (listing_data['listing_id'],))
            avg_rating = float(rating_result[0]['avg_rating']) if rating_result and rating_result[0]['avg_rating'] else 0.0
            review_count = rating_result[0]['review_count'] if rating_result else 0
            
            # Get listing images
            images = ListingImage.get_by_listing(listing_data['listing_id'])
            
            listing = Listing(
                id=listing_data['listing_id'],
                title=listing_data['title'],
                description=listing_data['description'],
                price=float(listing_data['price_per_night']),
                host_id=listing_data['host_id'],
                location_id=listing_data['location_id'],
                property_type=listing_data['room_type'],
                guests=listing_data['max_guests'],
                amenities=listing_data['amenities'].split(',') if listing_data['amenities'] else [],
                created_date=listing_data['created_at'],
                rating=avg_rating,
                reviews_count=review_count,
                available=bool(listing_data.get('is_active', 1)),
                images=[img.image_filename for img in images],
                is_active=bool(listing_data.get('is_active', 1))
            )
            
            # Add location details as separate attributes
            listing.address = listing_data.get('address', '')
            listing.city = listing_data.get('city', '')
            listing.country = listing_data.get('country', '')
            listing.location = f"{listing.city}, {listing.country}" if listing.city and listing.country else ""
            listing.latitude = float(listing_data['latitude']) if listing_data['latitude'] else None
            listing.longitude = float(listing_data['longitude']) if listing_data['longitude'] else None
            listings.append(listing)
        return listings
    
    @staticmethod
    def create(title, description, price, host_id, location_id, property_type='entire_place',
               guests=1, amenities=None):
        """Create a new listing with proper location_id reference"""
        # Add debug logging
        with open('/tmp/otithi_debug.log', 'a') as f:
            f.write(f"\n--- Listing.create() called ---\n")
            f.write(f"Parameters received:\n")
            f.write(f"  title: {title}\n")
            f.write(f"  description: {description[:50] if description else 'None'}...\n")
            f.write(f"  price: {price}\n")
            f.write(f"  host_id: {host_id}\n")
            f.write(f"  location_id: {location_id}\n")
            f.write(f"  property_type: {property_type}\n")
            f.write(f"  guests: {guests}\n")
            
        amenities_str = ','.join(amenities) if amenities else ''
        
        # Validate that location_id is provided
        if not location_id:
            with open('/tmp/otithi_debug.log', 'a') as f:
                f.write("ERROR: location_id is required for creating listings\\n")
            print("Error: location_id is required for creating listings")
            return None
        
        # Create the listing with the simplified schema
        listing_query = """
            INSERT INTO listings (host_id, title, description, room_type, price_per_night, 
                                max_guests, amenities, location_id, created_at, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            with open('/tmp/otithi_debug.log', 'a') as f:
                f.write(f"Executing SQL query with parameters:\\n")
                f.write(f"  host_id: {host_id}\\n")
                f.write(f"  title: {title}\\n")
                f.write(f"  description: {description}\\n")
                f.write(f"  room_type: {property_type}\\n")
                f.write(f"  price_per_night: {price}\\n")
                f.write(f"  max_guests: {guests}\\n")
                f.write(f"  amenities: {amenities_str}\\n")
                f.write(f"  location_id: {location_id}\\n")
                f.write(f"  created_at: {datetime.now()}\\n")
                f.write(f"  is_active: True\\n")
                
            listing_id = db.execute_insert(listing_query, (
                host_id, title, description, property_type, price, guests, 
                amenities_str, location_id, datetime.now(), True
            ))
            
            with open('/tmp/otithi_debug.log', 'a') as f:
                f.write(f"SQL execution result: listing_id = {listing_id}\\n")
            
            if listing_id:
                # Update the location with the listing_id to create bidirectional relationship
                try:
                    update_location_query = "UPDATE locations SET listing_id = %s WHERE location_id = %s"
                    rows_updated = db.execute_update(update_location_query, (listing_id, location_id))
                    
                    with open('/tmp/otithi_debug.log', 'a') as f:
                        f.write(f"Updated location {location_id} with listing_id {listing_id}. Rows affected: {rows_updated}\\n")
                    
                    if rows_updated > 0:
                        with open('/tmp/otithi_debug.log', 'a') as f:
                            f.write(f"SUCCESS: Listing created with ID {listing_id} and location updated\\n")
                        return Listing.get(listing_id)
                    else:
                        with open('/tmp/otithi_debug.log', 'a') as f:
                            f.write(f"WARNING: Listing created but location update failed\\n")
                        return Listing.get(listing_id)  # Still return the listing even if location update fails
                        
                except Exception as update_error:
                    with open('/tmp/otithi_debug.log', 'a') as f:
                        f.write(f"ERROR updating location with listing_id: {str(update_error)}\\n")
                    # Still return the listing even if location update fails
                    return Listing.get(listing_id)
            else:
                with open('/tmp/otithi_debug.log', 'a') as f:
                    f.write("ERROR: No listing_id returned from database\\n")
                return None
                
        except Exception as e:
            with open('/tmp/otithi_debug.log', 'a') as f:
                f.write(f"EXCEPTION in Listing.create(): {str(e)}\\n")
                f.write(f"Exception type: {type(e).__name__}\\n")
            print(f"Exception in Listing.create(): {e}")
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
    def __init__(self, id, listing_id, user_id, rating, comment, created_date=None, booking_id=None):
        self.id = id
        self.review_id = id  # Alias for consistency
        self.listing_id = listing_id
        self.user_id = user_id
        self.reviewer_id = user_id  # Alias for schema
        self.rating = rating
        self.comment = comment
        self.comments = comment  # Alias for schema
        self.created_date = created_date or datetime.now()
        self.review_date = created_date or datetime.now()  # Alias for schema
        self.booking_id = booking_id
    
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
            SELECT r.*, u.name as user_name, ud.profile_photo 
            FROM reviews r 
            LEFT JOIN users u ON r.reviewer_id = u.user_id 
            LEFT JOIN user_details ud ON u.user_id = ud.user_id
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
    def create(listing_id, user_id, rating, comment, booking_id=None):
        """Create a new review"""
        query = """
            INSERT INTO reviews (reviewer_id, listing_id, booking_id, rating, comments, review_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        review_id = db.execute_insert(query, (user_id, listing_id, booking_id, rating, comment, datetime.now()))
        
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
                created_date=review_data['review_date'],
                booking_id=review_data.get('booking_id')
            )
        return None

class Booking:
    def __init__(self, id, listing_id, user_id, check_in, check_out, total_price, 
                 guests=1, status='pending', created_date=None, confirmed_by=None, confirmed_at=None):
        self.id = id
        self.booking_id = id  # Alias for consistency
        self.listing_id = listing_id
        self.user_id = user_id
        self.check_in = check_in
        self.check_out = check_out
        self.guests = guests
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
                guests=booking_data.get('guests', 1),
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
                guests=booking_data.get('guests', 1),
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
                guests=booking_data.get('guests', 1),
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
                guests=booking_data.get('guests', 1),
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_at']
            ))
        return bookings
    
    @staticmethod
    def create(listing_id, user_id, check_in, check_out, guests=1):
        """Create a new booking"""
        listing = Listing.get(listing_id)
        if not listing:
            return None
        
        # Check availability
        if not listing.is_available(check_in, check_out):
            return None
        
        # Calculate price with proper guest count
        price_breakdown = listing.calculate_total_price(check_in, check_out, guests)
        total_price = price_breakdown['total']
        
        query = """
            INSERT INTO bookings (user_id, listing_id, check_in, check_out, guests, total_price, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        booking_id = db.execute_insert(query, (
            user_id, listing_id, check_in, check_out, guests, total_price, datetime.now()
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
                guests=booking_data.get('guests', 1),
                total_price=float(booking_data['total_price']),
                status=booking_data['status'],
                created_date=booking_data['created_at']
            )
        return None
    
    @staticmethod
    def get_by_guest(user_id):
        """Get all bookings by a guest user (alias for get_by_user)"""
        return Booking.get_by_user(user_id)
    
    def confirm(self, confirmed_by_user_id=None):
        """Confirm a pending booking"""
        if self.status == 'pending':
            query = "UPDATE bookings SET status = 'confirmed', confirmed_by = %s, confirmed_at = %s WHERE booking_id = %s"
            return db.execute_update(query, (confirmed_by_user_id, datetime.now(), self.id))
        return False
    
    def cancel(self):
        """Cancel a booking"""
        query = "UPDATE bookings SET status = 'cancelled', updated_at = %s WHERE booking_id = %s"
        return db.execute_update(query, (datetime.now(), self.id))
    
    def complete(self):
        """Mark booking as completed"""
        query = "UPDATE bookings SET status = 'completed', updated_at = %s WHERE booking_id = %s"
        return db.execute_update(query, (datetime.now(), self.id))
    
    def update_status(self, new_status, confirmed_by_user_id=None):
        """Update booking status"""
        if new_status in ['pending', 'confirmed', 'cancelled', 'completed']:
            update_fields = ["status = %s", "updated_at = %s"]
            update_values = [new_status, datetime.now()]
            
            if new_status == 'confirmed' and confirmed_by_user_id:
                update_fields.append("confirmed_by = %s")
                update_fields.append("confirmed_at = %s")
                update_values.extend([confirmed_by_user_id, datetime.now()])
            
            query = f"UPDATE bookings SET {', '.join(update_fields)} WHERE booking_id = %s"
            update_values.append(self.id)
            
            if db.execute_update(query, tuple(update_values)):
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


class Message:
    """Message model for real-time messaging - Updated for new schema"""
    
    def __init__(self, id, sender_id, receiver_id, content, message_type='text', 
                 listing_id=None, booking_id=None, attachment_filename=None,
                 is_read=False, read_at=None, created_at=None):
        self.id = id
        self.message_id = id  # Alias for compatibility
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.message_content = content  # Alias for schema
        self.message_type = message_type
        self.listing_id = listing_id
        self.booking_id = booking_id
        self.attachment_filename = attachment_filename
        self.is_read = is_read
        self.read_at = read_at
        self.created_at = created_at or datetime.now()
        
        # For compatibility with frontend
        self.sender_name = None
        self.sender_photo = None
        
        # Legacy compatibility
        self.conversation_id = f"{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"
    
    @staticmethod
    def create(sender_id, receiver_id, content, message_type='text', 
               listing_id=None, booking_id=None, attachment_filename=None):
        """Create a new message"""
        query = """
            INSERT INTO messages (sender_id, receiver_id, message_content, message_type,
                                listing_id, booking_id, attachment_filename, is_read, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        message_id = db.execute_insert(query, (
            sender_id, receiver_id, content, message_type, 
            listing_id, booking_id, attachment_filename, False, datetime.now()
        ))
        
        if message_id:
            return Message.get(message_id)
        return None
    
    @staticmethod
    def get(message_id):
        """Get message by ID"""
        query = """
            SELECT m.*, u.name as sender_name, ud.profile_photo as sender_photo
            FROM messages m
            JOIN users u ON m.sender_id = u.user_id
            LEFT JOIN user_details ud ON u.user_id = ud.user_id
            WHERE m.message_id = %s
        """
        result = db.execute_query(query, (message_id,))
        if result:
            data = result[0]
            message = Message(
                id=data['message_id'],
                sender_id=data['sender_id'],
                receiver_id=data['receiver_id'],
                content=data['message_content'],
                message_type=data['message_type'],
                listing_id=data['listing_id'],
                booking_id=data['booking_id'],
                attachment_filename=data['attachment_filename'],
                is_read=data['is_read'],
                read_at=data['read_at'],
                created_at=data['created_at']
            )
            message.sender_name = data['sender_name']
            message.sender_photo = data['sender_photo']
            return message
        return None
    
    # Legacy compatibility method
    @staticmethod
    def get_by_id(message_id):
        """Legacy compatibility method"""
        return Message.get(message_id)
    
    @staticmethod
    def get_conversation_messages(user1_id, user2_id, limit=50):
        """Get messages between two users"""
        query = """
            SELECT m.*, u.name as sender_name, ud.profile_photo as sender_photo
            FROM messages m
            JOIN users u ON m.sender_id = u.user_id
            LEFT JOIN user_details ud ON u.user_id = ud.user_id
            WHERE (m.sender_id = %s AND m.receiver_id = %s)
               OR (m.sender_id = %s AND m.receiver_id = %s)
            ORDER BY m.created_at ASC
            LIMIT %s
        """
        results = db.execute_query(query, (user1_id, user2_id, user2_id, user1_id, limit))
        
        messages = []
        for data in results:
            message = Message(
                id=data['message_id'],
                sender_id=data['sender_id'],
                receiver_id=data['receiver_id'],
                content=data['message_content'],
                message_type=data['message_type'],
                listing_id=data['listing_id'],
                booking_id=data['booking_id'],
                attachment_filename=data['attachment_filename'],
                is_read=data['is_read'],
                read_at=data['read_at'],
                created_at=data['created_at']
            )
            message.sender_name = data['sender_name']
            message.sender_photo = data['sender_photo']
            messages.append(message)
        
        return messages
    
    @staticmethod
    def mark_as_read(message_id):
        """Mark a message as read"""
        query = "UPDATE messages SET is_read = %s, read_at = %s WHERE message_id = %s"
        return db.execute_update(query, (True, datetime.now(), message_id))
    
    @staticmethod
    def mark_conversation_as_read(user1_id, user2_id, reader_id):
        """Mark all messages in a conversation as read for the reader"""
        query = """
            UPDATE messages 
            SET is_read = %s, read_at = %s 
            WHERE ((sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s))
            AND receiver_id = %s
            AND is_read = %s
        """
        return db.execute_update(query, (
            True, datetime.now(), user1_id, user2_id, user2_id, user1_id, reader_id, False
        ))
    
    @staticmethod
    def get_user_conversations(user_id):
        """Get all conversations for a user"""
        query = """
            SELECT DISTINCT
                CASE 
                    WHEN m.sender_id = %s THEN m.receiver_id 
                    ELSE m.sender_id 
                END as other_user_id,
                MAX(m.created_at) as last_message_time,
                (SELECT message_content FROM messages m2 
                 WHERE (m2.sender_id = %s OR m2.receiver_id = %s)
                 AND (m2.sender_id = other_user_id OR m2.receiver_id = other_user_id)
                 ORDER BY m2.created_at DESC LIMIT 1) as last_message_content,
                (SELECT sender_id FROM messages m3 
                 WHERE (m3.sender_id = %s OR m3.receiver_id = %s)
                 AND (m3.sender_id = other_user_id OR m3.receiver_id = other_user_id)
                 ORDER BY m3.created_at DESC LIMIT 1) as last_sender_id,
                COUNT(CASE WHEN m.receiver_id = %s AND m.is_read = 0 THEN 1 END) as unread_count
            FROM messages m
            WHERE m.sender_id = %s OR m.receiver_id = %s
            GROUP BY other_user_id
            ORDER BY last_message_time DESC
        """
        return db.execute_query(query, (
            user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id
        ))
    
    @staticmethod
    def get_unread_count(user_id):
        """Get total unread message count for a user"""
        query = "SELECT COUNT(*) as count FROM messages WHERE receiver_id = %s AND is_read = 0"
        result = db.execute_query(query, (user_id,))
        return result[0]['count'] if result else 0
    
    def to_dict(self):
        """Convert message to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'message_content': self.message_content,
            'message_type': self.message_type,
            'listing_id': self.listing_id,
            'booking_id': self.booking_id,
            'attachment_filename': self.attachment_filename,
            'is_read': self.is_read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'conversation_id': self.conversation_id
        }
