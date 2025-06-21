from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user

def role_required(*roles):
    """
    Decorator that requires the current user to have one of the specified roles.
    Usage: @role_required('admin', 'host')
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def admin_required(f):
    """
    Decorator that requires the current user to be an admin.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapped

def host_required(f):
    """
    Decorator that requires the current user to be a verified host.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if current_user.role != 'host':
            flash('Access denied. Host privileges required.', 'danger')
            return redirect(url_for('public.home'))
        
        if not current_user.is_verified:
            flash('Please complete verification before accessing host features.', 'warning')
            return redirect(url_for('user.profile'))
        
        return f(*args, **kwargs)
    return wrapped

def host_required_unverified(f):
    """
    Decorator that requires the current user to be a host (verified or not).
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if current_user.role != 'host':
            flash('Access denied. Host privileges required.', 'danger')
            return redirect(url_for('public.home'))
        
        return f(*args, **kwargs)
    return wrapped

def guest_required(f):
    """
    Decorator that requires the current user to be a guest.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        if current_user.role != 'guest':
            flash('Access denied. Guest privileges required.', 'danger')
            return redirect(url_for('public.home'))
        return f(*args, **kwargs)
    return wrapped

def owns_listing_or_admin(f):
    """
    Decorator that requires the current user to own the listing or be an admin.
    Expects listing_id or id as a parameter.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        from .models import Listing
        
        if not current_user.is_authenticated:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        
        # Get listing_id from kwargs or args
        listing_id = kwargs.get('listing_id') or kwargs.get('id')
        if not listing_id and args:
            listing_id = args[0]
        
        if listing_id:
            listing = Listing.query.get_or_404(listing_id)
            if not current_user.is_admin and listing.host_id != current_user.id:
                abort(403)
        
        return f(*args, **kwargs)
    return wrapped 