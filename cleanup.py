from app import create_app, db
from app.models import User, Listing, Booking, Review, Conversation, Message
from sqlalchemy import or_

app = create_app()

with app.app_context():
    try:
        # Delete sample messages and conversations
        sample_conversations = Conversation.query.join(User, or_(
            Conversation.user1_id == User.id,
            Conversation.user2_id == User.id
        )).filter(or_(
            User.username.like('sample%'),
            User.username.like('test%')
        )).all()
        
        for conv in sample_conversations:
            Message.query.filter_by(conversation_id=conv.id).delete()
            db.session.delete(conv)

        # Delete sample reviews
        sample_reviews = Review.query.join(User, Review.reviewer_id == User.id).filter(or_(
            User.username.like('sample%'),
            User.username.like('test%')
        )).all()
        
        for review in sample_reviews:
            db.session.delete(review)

        # Delete sample bookings
        sample_bookings = Booking.query.join(User, Booking.guest_id == User.id).filter(or_(
            User.username.like('sample%'),
            User.username.like('test%')
        )).all()
        
        for booking in sample_bookings:
            db.session.delete(booking)

        # Delete sample listings
        sample_listings = Listing.query.filter(or_(
            Listing.name.like('Sample%'),
            Listing.name.like('Test%'),
            Listing.name.like('Beautiful Beach%')
        )).all()
        
        for listing in sample_listings:
            db.session.delete(listing)

        # Delete sample users
        sample_users = User.query.filter(or_(
            User.username.like('sample%'),
            User.username.like('test%')
        )).all()
        
        for user in sample_users:
            if user.can_be_deleted():  # Don't delete if it's the only admin
                db.session.delete(user)

        # Commit changes
        db.session.commit()
        print("Successfully cleaned up sample data!")
        
        # Print summary
        print("\nCurrent Database Status:")
        print(f"Users: {User.query.count()}")
        print(f"Listings: {Listing.query.count()}")
        print(f"Bookings: {Booking.query.count()}")
        print(f"Reviews: {Review.query.count()}")
        print(f"Conversations: {Conversation.query.count()}")
        print(f"Messages: {Message.query.count()}")

    except Exception as e:
        db.session.rollback()
        print(f"Error cleaning up sample data: {str(e)}")
        raise 