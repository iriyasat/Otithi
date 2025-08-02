from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import User, Booking, Listing, Review
import os

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    # Redirect admin users to admin profile
    if current_user.user_type == 'admin':
        return redirect(url_for('admin.profile'))
        
    stats = {
        'total_bookings': 0,
        'average_rating': 0.0,
        'favorites': 0,
        'reviews_given': 0
    }
    
    # Get user bookings
    bookings = Booking.get_by_user(current_user.id)
    stats['total_bookings'] = len(bookings) if bookings else 0
    
    # Get user reviews given
    reviews = Review.get_by_user(current_user.id)
    stats['reviews_given'] = len(reviews) if reviews else 0
    
    # Calculate average rating received (for hosts)
    if current_user.user_type == 'host':
        host_listings = Listing.get_by_host(current_user.id)
        if host_listings:
            total_rating = 0
            total_reviews = 0
            for listing in host_listings:
                if hasattr(listing, 'rating') and listing.rating > 0:
                    total_rating += listing.rating * (listing.reviews_count if hasattr(listing, 'reviews_count') else 1)
                    total_reviews += (listing.reviews_count if hasattr(listing, 'reviews_count') else 1)
            if total_reviews > 0:
                stats['average_rating'] = total_rating / total_reviews
    
    recent_activities = []
    
    return render_template('profile.html', 
                         edit_mode=False, 
                         stats=stats, 
                         recent_activities=recent_activities)

@profile_bp.route('/profile/edit', methods=['GET'])
@login_required
def edit_profile():
    """Edit profile page"""
    return render_template('profile.html', edit_mode=True)

@profile_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()
        
        # Update user data
        if current_user.update_profile(full_name=full_name, phone=phone, bio=bio):
            flash('Profile updated successfully!', 'success')
        else:
            flash('Error updating profile. Please try again.', 'error')
            
    except Exception as e:
        flash(f'Error updating profile: {str(e)}', 'error')
    
    return redirect(url_for('profile.profile'))

@profile_bp.route('/my-listings')
@login_required
def my_listings():
    """Display user's listings (for hosts)"""
    if current_user.user_type not in ['host', 'admin']:
        flash('Access denied. Only hosts can view listings.', 'error')
        return redirect(url_for('main.dashboard'))
    
    user_listings = Listing.get_by_host(current_user.id)
    host_bookings = Booking.get_by_host(current_user.id)
    
    return render_template('host/my_listings.html', 
                         listings=user_listings,
                         bookings=host_bookings,
                         user=current_user)
