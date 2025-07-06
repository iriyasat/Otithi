from datetime import datetime
from app.database import db


class Location:
    def __init__(self, location_id, address, city, country, latitude=0.0, longitude=0.0, postal_code=None, created_at=None):
        self.location_id = location_id
        self.address = address
        self.city = city
        self.country = country
        self.latitude = latitude
        self.longitude = longitude
        self.postal_code = postal_code
        self.created_at = created_at or datetime.now()
    
    @staticmethod
    def create(address, city, country, latitude=0.0, longitude=0.0, postal_code=None):
        """Create a new location"""
        query = """
        INSERT INTO locations (address, city, country, latitude, longitude, postal_code, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        result = db.execute_insert(query, (address, city, country, latitude, longitude, postal_code, datetime.now()))
        if result:
            return Location.get(result)
        return None
    
    @staticmethod
    def get(location_id):
        """Get location by ID"""
        query = "SELECT * FROM locations WHERE location_id = %s"
        result = db.execute_query(query, (location_id,))
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
        return None
    
    @staticmethod
    def find_or_create(address, city, country, latitude=0.0, longitude=0.0, postal_code=None):
        """Find existing location or create new one"""
        # Try to find existing location
        query = """
        SELECT * FROM locations 
        WHERE address = %s AND city = %s AND country = %s
        LIMIT 1
        """
        result = db.execute_query(query, (address, city, country))
        
        if result:
            data = result[0]
            location = Location(
                location_id=data['location_id'],
                address=data['address'],
                city=data['city'],
                country=data['country'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                postal_code=data['postal_code'],
                created_at=data['created_at']
            )
            # Update coordinates if provided
            if latitude != 0.0 or longitude != 0.0:
                location.update_coordinates(latitude, longitude)
            return location
        else:
            # Create new location
            return Location.create(address, city, country, latitude, longitude, postal_code)
    
    def update_coordinates(self, latitude, longitude):
        """Update location coordinates"""
        query = "UPDATE locations SET latitude = %s, longitude = %s WHERE location_id = %s"
        if db.execute_update(query, (latitude, longitude, self.location_id)):
            self.latitude = latitude
            self.longitude = longitude
            return True
        return False


class ListingImage:
    def __init__(self, image_id, listing_id, image_filename, image_order=1, created_at=None):
        self.image_id = image_id
        self.listing_id = listing_id
        self.image_filename = image_filename
        self.image_order = image_order
        self.created_at = created_at or datetime.now()
    
    @staticmethod
    def create(listing_id, image_filename, image_order=1):
        """Add an image to a listing"""
        query = """
        INSERT INTO listing_images (listing_id, image_filename, image_order, uploaded_at)
        VALUES (%s, %s, %s, %s)
        """
        result = db.execute_insert(query, (listing_id, image_filename, image_order, datetime.now()))
        if result:
            return ListingImage.get(result)
        return None
    
    @staticmethod
    def get(image_id):
        """Get image by ID"""
        query = "SELECT * FROM listing_images WHERE image_id = %s"
        result = db.execute_query(query, (image_id,))
        if result:
            data = result[0]
            return ListingImage(
                image_id=data['image_id'],
                listing_id=data['listing_id'],
                image_filename=data['image_filename'],
                image_order=data['image_order'],
                created_at=data['uploaded_at']  # Map uploaded_at to created_at for consistency
            )
        return None
    
    @staticmethod
    def get_by_listing(listing_id):
        """Get all images for a listing"""
        query = """
        SELECT * FROM listing_images 
        WHERE listing_id = %s 
        ORDER BY image_order ASC, uploaded_at ASC
        """
        results = db.execute_query(query, (listing_id,))
        images = []
        if results:
            for data in results:
                images.append(ListingImage(
                    image_id=data['image_id'],
                    listing_id=data['listing_id'],
                    image_filename=data['image_filename'],
                    image_order=data['image_order'],
                    created_at=data['uploaded_at']  # Map uploaded_at to created_at for consistency
                ))
        return images
    
    @staticmethod
    def delete_by_listing(listing_id):
        """Delete all images for a listing"""
        query = "DELETE FROM listing_images WHERE listing_id = %s"
        return db.execute_update(query, (listing_id,))
    
    def delete(self):
        """Delete this image"""
        query = "DELETE FROM listing_images WHERE image_id = %s"
        return db.execute_update(query, (self.image_id,))
