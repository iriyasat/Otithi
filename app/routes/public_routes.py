"""
Public routes for homepage and public pages.
"""

from flask import Blueprint, render_template
from flask_login import current_user
from sqlalchemy import desc
from ..models import Listing, ListingStatus, User

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    """Home page with featured listings"""
    featured_listings = Listing.query.filter_by(status=ListingStatus.APPROVED).order_by(desc(Listing.created_at)).limit(6).all()
    total_listings = Listing.query.filter_by(status=ListingStatus.APPROVED).count()
    total_hosts = User.query.filter_by(role='host').count()
    total_guests = User.query.filter_by(role='guest').count()
    
    return render_template('public/index.html', 
                         featured_listings=featured_listings,
                         total_listings=total_listings,
                         total_hosts=total_hosts,
                         total_guests=total_guests)

@public_bp.route('/about')
def about():
    """About page"""
    return render_template('public/about.html') 