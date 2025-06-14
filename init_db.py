from app import app, db
from models import User, Property, PropertyImage, Booking, Review, SavedProperty, CulturalExperience, MealOption, TransportOption, CommunityVerification, FestivalSeason
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@atithi.com').first()
        if not admin:
            # Create admin user
            admin = User(
                email='admin@atithi.com',
                password=generate_password_hash('admin123'),
                first_name='Admin',
                last_name='User',
                role='admin',
                preferred_language='en'
            )
            db.session.add(admin)
            
            # Create a test host
            host = User(
                email='host@atithi.com',
                password=generate_password_hash('host123'),
                first_name='Test',
                last_name='Host',
                role='host',
                preferred_language='en'
            )
            db.session.add(host)
            
            # Create a test guest
            guest = User(
                email='guest@atithi.com',
                password=generate_password_hash('guest123'),
                first_name='Test',
                last_name='Guest',
                role='guest',
                preferred_language='en'
            )
            db.session.add(guest)
            
            # Commit the users
            db.session.commit()
            
            # Create a sample property
            property = Property(
                host_id=host.id,
                title_en='Traditional Bengali Homestay',
                title_bn='ঐতিহ্যবাহী বাংলা হোমস্টে',
                description_en='Experience authentic Bengali hospitality in this traditional homestay.',
                description_bn='এই ঐতিহ্যবাহী হোমস্টেতে সত্যিকারের বাংলা আতিথেয়তা অনুভব করুন।',
                location_en='Dhaka, Bangladesh',
                location_bn='ঢাকা, বাংলাদেশ',
                price_per_night=2500,
                max_guests=4,
                property_type='Homestay',
                region='Dhaka',
                amenities=['WiFi', 'Air Conditioning', 'Traditional Meals', 'Cultural Activities'],
                cultural_features=['Traditional Architecture', 'Local Art', 'Cultural Workshops'],
                safety_features=['24/7 Security', 'First Aid Kit', 'Emergency Contact']
            )
            db.session.add(property)
            db.session.commit()
            
            # Add a sample cultural experience
            experience = CulturalExperience(
                property_id=property.id,
                title_en='Traditional Bengali Cooking Class',
                title_bn='ঐতিহ্যবাহী বাংলা রান্নার ক্লাস',
                description_en='Learn to cook authentic Bengali dishes from local chefs.',
                description_bn='স্থানীয় শেফদের কাছ থেকে সত্যিকারের বাংলা খাবার রান্না শিখুন।',
                price=1500,
                duration=120,
                max_participants=6
            )
            db.session.add(experience)
            
            # Add a sample meal option
            meal = MealOption(
                property_id=property.id,
                name_en='Traditional Bengali Breakfast',
                name_bn='ঐতিহ্যবাহী বাংলা সকালের নাস্তা',
                description_en='Enjoy a traditional Bengali breakfast with local delicacies.',
                description_bn='স্থানীয় সুস্বাদু খাবার সহ ঐতিহ্যবাহী বাংলা সকালের নাস্তা উপভোগ করুন।',
                price=300,
                meal_type='breakfast',
                dietary_info={'vegetarian': True, 'halal': True}
            )
            db.session.add(meal)
            
            # Add a sample transport option
            transport = TransportOption(
                property_id=property.id,
                type='CNG',
                description_en='Air-conditioned CNG auto-rickshaw service',
                description_bn='এয়ার-কন্ডিশনড সিএনজি অটো-রিকশা পরিষেবা',
                price=200,
                is_available=True
            )
            db.session.add(transport)
            
            # Add a sample festival season
            festival = FestivalSeason(
                name_en='Pohela Boishakh',
                name_bn='পহেলা বৈশাখ',
                description_en='Bengali New Year celebration',
                description_bn='বাংলা নববর্ষ উদযাপন',
                start_date='2024-04-14',
                end_date='2024-04-15',
                region='All'
            )
            db.session.add(festival)
            
            # Commit all changes
            db.session.commit()
            
            print("Database initialized with sample data!")
        else:
            print("Database already initialized!")

if __name__ == '__main__':
    init_db() 