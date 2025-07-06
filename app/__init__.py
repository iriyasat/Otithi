from flask import Flask
from flask_login import LoginManager
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Ensure session configuration
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # False for HTTP, True for HTTPS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'  # Add session protection
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        try:
            print(f"DEBUG: User loader called with ID: {user_id} (type: {type(user_id)})")
            # Convert to int if it's a string
            if isinstance(user_id, str):
                user_id = int(user_id)
            user = User.get(user_id)
            if user:
                print(f"DEBUG: User loader found: {user.name} (ID: {user.id})")
            else:
                print(f"DEBUG: User loader - no user found for ID: {user_id}")
            return user
        except (ValueError, TypeError) as e:
            print(f"DEBUG: User loader error for ID {user_id}: {e}")
            return None
        except Exception as e:
            print(f"DEBUG: Unexpected user loader error: {e}")
            return None
    
    from app.routes.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
