# Routes package initialization

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    try:
        from .main import main_bp
        app.register_blueprint(main_bp)
    except ImportError:
        print("Warning: main blueprint not found")
    
    try:
        from .auth import auth_bp
        app.register_blueprint(auth_bp)
    except ImportError:
        print("Warning: auth blueprint not found")
    
    try:
        from .listings import listings_bp
        app.register_blueprint(listings_bp)
    except ImportError:
        print("Warning: listings blueprint not found")
    
    try:
        from .bookings import bookings_bp
        app.register_blueprint(bookings_bp)
    except ImportError:
        print("Warning: bookings blueprint not found")
    
    try:
        from .profile import profile_bp
        app.register_blueprint(profile_bp)
    except ImportError:
        print("Warning: profile blueprint not found")
    
    try:
        from .admin import admin_bp
        app.register_blueprint(admin_bp)
    except ImportError:
        print("Warning: admin blueprint not found")
    
    try:
        from .api import api_bp
        app.register_blueprint(api_bp)
    except ImportError:
        print("Warning: api blueprint not found")
