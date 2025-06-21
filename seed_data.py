#!/usr/bin/env python3
"""
Seed data script for Othiti Flask app
Creates sample users and listings for testing
"""

from app import create_app, db
from app.models import User, Listing, ListingStatus, UserRole
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_data():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create sample users
        print("Creating sample users...")
        
        # Admin user
        admin = User(
            username='admin',
            email='admin@othiti.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_verified=True,
            phone='+8801234567890',
            created_at=datetime.utcnow()
        )
        
        # Host user
        host = User(
            username='host1',
            email='host1@othiti.com',
            password_hash=generate_password_hash('host123'),
            role='host',
            is_verified=True,
            phone='+8801234567891',
            created_at=datetime.utcnow()
        )
        
        # Guest user
        guest = User(
            username='guest1',
            email='guest1@othiti.com',
            password_hash=generate_password_hash('guest123'),
            role='guest',
            is_verified=True,
            phone='+8801234567892',
            created_at=datetime.utcnow()
        )
        
        # Add users to session
        db.session.add(admin)
        db.session.add(host)
        db.session.add(guest)
        db.session.commit()
        
        print(f"Created users: {admin.username}, {host.username}, {guest.username}")
        
        # Create sample listings
        print("Creating sample listings...")
        
        listings_data = [
            {
                'title': 'Cozy Apartment in Dhaka',
                'location': 'Gulshan, Dhaka',
                'description': 'Beautiful 2-bedroom apartment in the heart of Gulshan with modern amenities and great views.',
                'price_per_night': 2500.0,
                'guest_capacity': 4,
                'bedrooms': 2,
                'bathrooms': 2,
                'house_rules': 'No smoking, No pets, Quiet hours after 10 PM',
                'status': ListingStatus.APPROVED,
                'user_id': host.id
            },
            {
                'title': 'Luxury Villa in Chittagong',
                'location': 'Patenga, Chittagong',
                'description': 'Spacious 4-bedroom villa near the beach with private pool and garden.',
                'price_per_night': 5000.0,
                'guest_capacity': 8,
                'bedrooms': 4,
                'bathrooms': 3,
                'house_rules': 'No parties, No smoking, Respect neighbors',
                'status': ListingStatus.APPROVED,
                'user_id': host.id
            },
            {
                'title': 'Modern Studio in Sylhet',
                'location': 'Zindabazar, Sylhet',
                'description': 'Fully furnished studio apartment perfect for solo travelers or couples.',
                'price_per_night': 1500.0,
                'guest_capacity': 2,
                'bedrooms': 1,
                'bathrooms': 1,
                'house_rules': 'No smoking, Keep clean',
                'status': ListingStatus.APPROVED,
                'user_id': host.id
            },
            {
                'title': 'Heritage House in Old Dhaka',
                'location': 'Lalbagh, Dhaka',
                'description': 'Beautifully restored heritage house with traditional architecture and modern comforts.',
                'price_per_night': 3000.0,
                'guest_capacity': 6,
                'bedrooms': 3,
                'bathrooms': 2,
                'house_rules': 'Respect the heritage, No loud music',
                'status': ListingStatus.APPROVED,
                'user_id': host.id
            },
            {
                'title': 'Beachfront Cottage in Cox\'s Bazar',
                'location': 'Cox\'s Bazar Beach',
                'description': 'Charming cottage steps away from the longest beach in the world.',
                'price_per_night': 4000.0,
                'guest_capacity': 4,
                'bedrooms': 2,
                'bathrooms': 1,
                'house_rules': 'No shoes inside, Respect the beach',
                'status': ListingStatus.APPROVED,
                'user_id': host.id
            },
            {
                'title': 'Mountain Retreat in Bandarban',
                'location': 'Bandarban Hill District',
                'description': 'Peaceful retreat in the hills with stunning mountain views and fresh air.',
                'price_per_night': 2000.0,
                'guest_capacity': 4,
                'bedrooms': 2,
                'bathrooms': 1,
                'house_rules': 'No littering, Respect nature',
                'status': ListingStatus.APPROVED,
                'user_id': host.id
            },
            {
                'title': 'Riverside Bungalow in Barisal',
                'location': 'Barisal City',
                'description': 'Charming bungalow on the banks of the Kirtankhola River with boat access.',
                'price_per_night': 1800.0,
                'guest_capacity': 5,
                'bedrooms': 2,
                'bathrooms': 2,
                'house_rules': 'No fishing without permission, Life jackets provided',
                'status': ListingStatus.APPROVED,
                'user_id': host.id
            },
            {
                'title': 'Urban Loft in Dhanmondi',
                'location': 'Dhanmondi, Dhaka',
                'description': 'Modern loft-style apartment in trendy Dhanmondi with rooftop access.',
                'price_per_night': 2200.0,
                'guest_capacity': 3,
                'bedrooms': 1,
                'bathrooms': 1,
                'house_rules': 'No parties, Rooftop access until 11 PM',
                'status': ListingStatus.APPROVED,
                'user_id': host.id
            },
            {
                'title': 'Tea Garden Cottage in Srimangal',
                'location': 'Srimangal, Sylhet',
                'description': 'Cozy cottage surrounded by tea gardens with guided tours available.',
                'price_per_night': 1600.0,
                'guest_capacity': 3,
                'bedrooms': 1,
                'bathrooms': 1,
                'house_rules': 'Respect tea garden rules, No plucking tea leaves',
                'status': ListingStatus.APPROVED,
                'user_id': host.id
            }
        ]
        
        for listing_data in listings_data:
            listing = Listing(**listing_data)
            db.session.add(listing)
        
        db.session.commit()
        
        print(f"Created {len(listings_data)} sample listings")
        
        # Print summary
        print("\n=== Database Seeded Successfully ===")
        print(f"Users: {User.query.count()}")
        print(f"Total Listings: {Listing.query.count()}")
        print(f"Approved Listings: {Listing.query.filter_by(status=ListingStatus.APPROVED).count()}")
        print("\nSample login credentials:")
        print("Admin: admin@othiti.com / admin123")
        print("Host: host1@othiti.com / host123")
        print("Guest: guest1@othiti.com / guest123")

if __name__ == '__main__':
    seed_data() 