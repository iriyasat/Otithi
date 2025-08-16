"""
Authentication utilities and decorators for role-based access control
"""
from functools import wraps
from flask import flash, redirect, url_for, abort
from flask_login import current_user


def role_required(*roles):
    """
    Decorator to require specific user roles for route access
    
    Usage:
        @role_required('admin')
        @role_required('host', 'admin')  # Allow multiple roles
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.user_type not in roles:
                flash('You do not have permission to access this page.', 'error')
                return abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.user_type != 'admin':
            flash('Admin access required.', 'error')
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def host_required(f):
    """Decorator to require host role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.user_type != 'host':
            flash('Host access required.', 'error')
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def guest_required(f):
    """Decorator to require guest role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.user_type != 'guest':
            flash('Guest access required.', 'error')
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def host_or_admin_required(f):
    """Decorator to require host or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.user_type not in ['host', 'admin']:
            flash('Host or admin access required.', 'error')
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def owner_or_admin_required(resource_owner_id_field='user_id'):
    """
    Decorator to require resource ownership or admin role
    
    Args:
        resource_owner_id_field: The field name that contains the owner ID
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Admin can access anything
            if current_user.user_type == 'admin':
                return f(*args, **kwargs)
            
            # Check if user owns the resource
            resource_owner_id = kwargs.get(resource_owner_id_field) or args[0] if args else None
            
            if resource_owner_id and str(current_user.id) == str(resource_owner_id):
                return f(*args, **kwargs)
            
            flash('You can only access your own resources.', 'error')
            return abort(403)
        
        return decorated_function
    return decorator
