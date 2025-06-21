"""
Permission decorators for role-based access control.
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('public.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def host_required(f):
    """Decorator to require host role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role not in ['host', 'admin']:
            flash('Access denied. Host privileges required.', 'danger')
            return redirect(url_for('public.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def guest_required(f):
    """Decorator to require guest role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role not in ['guest', 'host', 'admin']:
            flash('Access denied. Guest privileges required.', 'danger')
            return redirect(url_for('public.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def verified_host_required(f):
    """Decorator to require verified host role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role == 'admin':
            return f(*args, **kwargs)
        
        if current_user.role != 'host':
            flash('Access denied. Host privileges required.', 'danger')
            return redirect(url_for('public.index'))
        
        if not current_user.is_verified:
            flash('Your account needs to be verified by admin to access this feature.', 'warning')
            return redirect(url_for('host.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function 