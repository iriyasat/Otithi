from config import app
from extensions import db
from models import User, Property, Booking
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

db.init_app(app)

def seed_database():
    with app.app_context():
        # Clear existing data
        Booking.query.delete()
        Property.query.delete()
        User.query.delete()
        
        # Create sample users
        users = [
            User(
                email='admin@atithi.com',
                name='Admin User',
                role='admin'
            ),
            User(
                email='host@atithi.com',
                name='Host User',
                role='host'
            ),
            User(
                email='guest@atithi.com',
                name='Guest User',
                role='guest'
            )
        ]
        
        # Set passwords for users
        users[0].set_password('admin123')
        users[1].set_password('host123')
        users[2].set_password('guest123')
        
        # Add users to database
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        # Create sample properties
        properties = [
            Property(
                user_id=2,  # Host user
                title='Cozy Apartment in Dhaka',
                description='Modern apartment in the heart of Dhaka with great city views',
                location='Gulshan, Dhaka',
                price_per_night=5000.00
            ),
            Property(
                user_id=2,  # Host user
                title='Beach House in Cox\'s Bazar',
                description='Beautiful beach house with direct access to the beach',
                location='Cox\'s Bazar',
                price_per_night=8000.00
            ),
            Property(
                user_id=2,  # Host user
                title='Tea Garden Cottage in Sylhet',
                description='Peaceful cottage surrounded by tea gardens',
                location='Sylhet',
                price_per_night=6000.00
            )
        ]
        
        # Add properties to database
        for property in properties:
            db.session.add(property)
        db.session.commit()
        
        # Create sample bookings
        bookings = [
            Booking(
                property_id=1,
                user_id=3,  # Guest user
                check_in=datetime.now().date(),
                check_out=(datetime.now() + timedelta(days=3)).date(),
                guests=2,
                total_price=15000.00,
                status='confirmed'
            ),
            Booking(
                property_id=2,
                user_id=3,  # Guest user
                check_in=(datetime.now() + timedelta(days=7)).date(),
                check_out=(datetime.now() + timedelta(days=10)).date(),
                guests=4,
                total_price=24000.00,
                status='pending'
            )
        ]
        
        # Add bookings to database
        for booking in bookings:
            db.session.add(booking)
        db.session.commit()
        
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database() 