# Routes package initialization

from .main import main_bp
from .auth import auth_bp
from .listings import listings_bp
from .bookings import bookings_bp
from .profile import profile_bp
from .admin import admin_bp
from .api import api_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
