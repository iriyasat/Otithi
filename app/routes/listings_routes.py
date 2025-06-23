from flask import Blueprint, render_template, request, redirect, url_for
from ..models import Listing, ListingStatus

listings_bp = Blueprint('listings', __name__)

@listings_bp.route('/listings')
def listings():
    """All listings page with pagination, search, and filtering"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    sort = request.args.get('sort', 'newest')
    
    # Start with approved listings
    query = Listing.query.filter_by(status=ListingStatus.APPROVED)
    
    # Apply search filter
    if search:
        query = query.filter(
            Listing.title.contains(search) | 
            Listing.description.contains(search)
        )
    
    # Apply location filter
    if location:
        query = query.filter(Listing.location.contains(location))
    
    # Apply sorting
    if sort == 'oldest':
        query = query.order_by(Listing.created_at.asc())
    elif sort == 'price_asc':
        query = query.order_by(Listing.price_per_night.asc())
    elif sort == 'price_desc':
        query = query.order_by(Listing.price_per_night.desc())
    else:  # newest (default)
        query = query.order_by(Listing.created_at.desc())
    
    # Get all listings
    listings = query.all()
    
    return render_template('property/listings.html', 
                         listings=listings,
                         search=search,
                         location=location,
                         sort=sort)

@listings_bp.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    """Listing detail page"""
    listing = Listing.query.get_or_404(listing_id)
    return render_template('property/detail.html', listing=listing)

@listings_bp.route('/search')
def search():
    """Search listings (legacy route - now handled by main listings route)"""
    return redirect(url_for('listings.listings')) 