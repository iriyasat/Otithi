"""
Listings routes for browsing, searching, and viewing listings.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from sqlalchemy import and_, or_, desc
from ..models import Listing, ListingStatus, User

listings_bp = Blueprint('listings', __name__)

@listings_bp.route('/listings')
def listings():
    """Browse all listings with search and filter"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    guests = request.args.get('guests', type=int)
    sort = request.args.get('sort', 'newest')
    
    query = Listing.query.filter_by(status=ListingStatus.APPROVED)
    
    if search:
        query = query.filter(
            or_(
                Listing.title.contains(search),
                Listing.description.contains(search)
            )
        )
    
    if location:
        query = query.filter(Listing.location.contains(location))
    
    if min_price is not None:
        query = query.filter(Listing.price_per_night >= min_price)
    
    if max_price is not None:
        query = query.filter(Listing.price_per_night <= max_price)
    
    if guests:
        query = query.filter(Listing.max_guests >= guests)
    
    if sort == 'price_asc':
        query = query.order_by(Listing.price_per_night.asc())
    elif sort == 'price_desc':
        query = query.order_by(Listing.price_per_night.desc())
    elif sort == 'oldest':
        query = query.order_by(Listing.created_at.asc())
    else:
        query = query.order_by(desc(Listing.created_at))
    
    pagination = query.paginate(page=page, per_page=12, error_out=False)
    
    return render_template('listings/listings.html', 
                         listings=pagination.items,
                         pagination=pagination,
                         search=search,
                         location=location,
                         min_price=min_price,
                         max_price=max_price,
                         guests=guests,
                         sort=sort)

@listings_bp.route('/listing/<int:id>')
def listing_detail(id):
    """View individual listing details"""
    listing = Listing.query.get_or_404(id)
    
    if (listing.status != ListingStatus.APPROVED and 
        (not current_user.is_authenticated or 
         (current_user.id != listing.user_id and current_user.role != 'admin'))):
        flash('This listing is not available.', 'warning')
        return redirect(url_for('listings.listings'))
    
    # Get host information
    host = User.query.get(listing.user_id)
    
    # Get similar listings in the same location
    similar_listings = Listing.query.filter(
        and_(
            Listing.status == ListingStatus.APPROVED,
            Listing.id != listing.id,
            Listing.location.contains(listing.location.split(',')[0])
        )
    ).limit(3).all()
    
    return render_template('listings/listing_detail.html', 
                         listing=listing,
                         host=host,
                         similar_listings=similar_listings)

@listings_bp.route('/search')
def search():
    """Advanced search page"""
    return render_template('listings/search.html') 