from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import User, Review, Listing
import json

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/check-email')
def check_email():
    email = request.args.get('email', '').strip()
    if email:
        user = User.get_by_email(email)
        return jsonify({'available': user is None})
    return jsonify({'available': False})

@api_bp.route('/user/reviews')
@login_required
def get_user_reviews():
    """API endpoint to get all reviews posted by the current user"""
    try:
        user_reviews = Review.get_by_user(current_user.id)
        
        reviews_data = []
        for review in user_reviews:
            listing = Listing.get(review.listing_id)
            
            review_data = {
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'created_date': review.created_date.strftime('%B %d, %Y') if review.created_date else '',
                'listing_title': listing.title if listing else 'Listing not found',
                'listing_location': listing.location if listing else '',
                'listing_id': review.listing_id
            }
            reviews_data.append(review_data)
        
        reviews_data.sort(key=lambda x: x['created_date'], reverse=True)
        
        return jsonify({
            'success': True,
            'reviews': reviews_data,
            'total_count': len(reviews_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching reviews: {str(e)}'
        }), 500

@api_bp.route('/favorites', methods=['POST'])
@login_required
def toggle_favorite():
    """API endpoint to add or remove a listing from favorites"""
    try:
        data = request.get_json()
        listing_id = data.get('listing_id')
        action = data.get('action')  # 'add' or 'remove'
        
        if not listing_id or not action:
            return jsonify({
                'success': False,
                'error': 'Missing listing_id or action'
            }), 400
        
        # Check if listing exists
        listing = Listing.get(listing_id)
        if not listing:
            return jsonify({
                'success': False,
                'error': 'Listing not found'
            }), 404
        
        # Get current user's favorites
        user_favorites = current_user.favorites if hasattr(current_user, 'favorites') and current_user.favorites else []
        
        if isinstance(user_favorites, str):
            try:
                user_favorites = json.loads(user_favorites)
            except:
                user_favorites = []
        
        listing_id_int = int(listing_id)
        
        if action == 'add':
            if listing_id_int not in user_favorites:
                user_favorites.append(listing_id_int)
                message = 'Added to favorites'
            else:
                message = 'Already in favorites'
        elif action == 'remove':
            if listing_id_int in user_favorites:
                user_favorites.remove(listing_id_int)
                message = 'Removed from favorites'
            else:
                message = 'Not in favorites'
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid action. Use "add" or "remove"'
            }), 400
        
        # Update user's favorites in database
        # Note: This assumes you have a favorites field in your User model
        # You might need to adjust this based on your actual database schema
        current_user.favorites = json.dumps(user_favorites)
        # You'll need to implement a save method or use your ORM's save method
        # current_user.save()
        
        return jsonify({
            'success': True,
            'message': message,
            'is_favorited': listing_id_int in user_favorites,
            'favorites_count': len(user_favorites)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error updating favorites: {str(e)}'
        }), 500

@api_bp.route('/favorites/check/<int:listing_id>')
@login_required
def check_favorite_status(listing_id):
    """API endpoint to check if a listing is in user's favorites"""
    try:
        # Get current user's favorites
        user_favorites = current_user.favorites if hasattr(current_user, 'favorites') and current_user.favorites else []
        
        if isinstance(user_favorites, str):
            try:
                user_favorites = json.loads(user_favorites)
            except:
                user_favorites = []
        
        is_favorited = int(listing_id) in user_favorites
        
        return jsonify({
            'success': True,
            'is_favorited': is_favorited,
            'listing_id': listing_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error checking favorite status: {str(e)}'
        }), 500

@api_bp.route('/favorites')
@login_required
def get_favorites():
    """API endpoint to get all favorite listings for the current user"""
    try:
        # Get current user's favorites
        user_favorites = current_user.favorites if hasattr(current_user, 'favorites') and current_user.favorites else []
        
        if isinstance(user_favorites, str):
            try:
                user_favorites = json.loads(user_favorites)
            except:
                user_favorites = []
        
        # Get listing details for each favorite
        favorite_listings = []
        for listing_id in user_favorites:
            listing = Listing.get(listing_id)
            if listing:
                listing_data = {
                    'id': listing.id,
                    'title': listing.title,
                    'location': listing.location,
                    'price_per_night': listing.price,
                    'image': 'demo_listing_1.jpg',  # Default image, update based on your schema
                    'rating': 0.0,  # Calculate if you have reviews
                    'room_type': listing.property_type
                }
                favorite_listings.append(listing_data)
        
        return jsonify({
            'success': True,
            'favorites': favorite_listings,
            'total_count': len(favorite_listings)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error fetching favorites: {str(e)}'
        }), 500
