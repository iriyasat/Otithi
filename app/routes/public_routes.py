from flask import Blueprint, render_template, request, flash, redirect, url_for
from ..models import User, Listing, Booking, Review

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Home page"""
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
    
    # Get featured listings (approved listings with images, limited to 6)
    featured_listings = Listing.query.filter_by(status='APPROVED').filter(
        Listing.image_filename.isnot(None)
    ).limit(6).all()
    
    return render_template('home.html',
                         total_users=total_users,
                         total_hosts=total_hosts,
                         total_guests=total_guests,
                         total_listings=total_listings,
                         total_bookings=total_bookings,
                         avg_rating=round(avg_rating, 1),
                         unique_locations=unique_locations,
                         featured_listings=featured_listings)

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
    
    return render_template('about.html',
                         total_users=total_users,
                         total_hosts=total_hosts,
                         total_guests=total_guests,
                         total_listings=total_listings,
                         total_bookings=total_bookings,
                         avg_rating=round(avg_rating, 1),
                         unique_locations=unique_locations)

@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Here you would typically send an email or save to database
        # For now, just flash a success message
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('public.contact'))
    
    return render_template('contact.html') 