from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import User, Review, Listing

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
