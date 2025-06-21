from flask import Blueprint

# Import all blueprints
from .public_routes import public_bp
from .auth_routes import auth_bp
from .user_routes import user_bp
from .host_routes import host_bp
from .admin_routes import admin_bp
from .listings_routes import listings_bp
from .messages_routes import messages_bp

# List of all blueprints to register
blueprints = [
    public_bp,
    auth_bp,
    user_bp,
    host_bp,
    admin_bp,
    listings_bp,
    messages_bp
] 