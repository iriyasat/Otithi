"""
Routes package for Othiti Flask application.
Organizes routes into logical blueprints for better maintainability.
"""

from .auth_routes import auth_bp
from .public_routes import public_bp
from .user_routes import user_bp
from .host_routes import host_bp
from .admin_routes import admin_bp
from .listings_routes import listings_bp
from .messages_routes import messages_bp

# List of all blueprints for easy registration
blueprints = [
    auth_bp,
    public_bp,
    user_bp,
    host_bp,
    admin_bp,
    listings_bp,
    messages_bp
] 