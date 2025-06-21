from flask import Blueprint, render_template
from ..models import User, Listing, Booking, Review

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Home page"""
    return render_template('public/index.html')

@public_bp.route('/about')
def about():
    """About page"""
    # Get platform statistics
    total_users = User.query.count()
    total_hosts = User.query.filter_by(role='host').count()
    total_guests = User.query.filter_by(role='guest').count()
    total_listings = Listing.query.filter_by(status='APPROVED').count()
    total_bookings = Booking.query.count()
    
    # Calculate average rating
    reviews = Review.query.all()
    if reviews:
        avg_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    # Get unique locations
    unique_locations = Listing.query.with_entities(Listing.location).distinct().count()
    
    return render_template('public/about.html',
                         total_users=total_users,
                         total_hosts=total_hosts,
                         total_guests=total_guests,
                         total_listings=total_listings,
                         total_bookings=total_bookings,
                         avg_rating=round(avg_rating, 1),
                         unique_locations=unique_locations) 