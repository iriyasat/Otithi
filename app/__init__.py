from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

def create_app():
    app = Flask(__name__)

    # Enhanced Configuration for Security
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Session Security Configuration
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # CSRF Protection
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize CSRF Protection
    csrf = CSRFProtect()
    csrf.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Point directly to auth blueprint
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'  # Enhanced session protection

    @login_manager.user_loader
    def load_user(user_id):
        try:
            from app.models import User
            if user_id is None or user_id == 'None':
                return None
            return User.get(int(user_id))
        except (ValueError, TypeError):
            return None

    # Register all blueprints
    blueprints_registered = False
    try:
        from app.routes import register_blueprints
        num_blueprints = register_blueprints(app)
        blueprints_registered = num_blueprints > 0
        print(f"✓ Blueprints registered successfully ({num_blueprints} blueprints)")
    except ImportError as e:
        print(f"Warning: Could not register blueprints: {e}")
        blueprints_registered = False
    except Exception as e:
        print(f"Error registering blueprints: {e}")
        blueprints_registered = False

    # Fallback to monolithic routes if blueprints failed
    if not blueprints_registered:
        try:
            from app.routes.legacy_routes import bp as fallback_bp
            app.register_blueprint(fallback_bp)
            print("✓ Fallback to monolithic legacy routes")
        except ImportError:
            print("⚠ Legacy routes not available, using basic routes")
            # Last resort - basic routes
            @app.route('/')
            def index():
                try:
                    return render_template('index.html', listings=[], reviews=[], hosting_stats={})
                except Exception:
                    return "Welcome to Otithi!"

            @app.route('/test')
            def test():
                return "Flask app is running!"

    # Error handlers with fallback (only define once)
    @app.errorhandler(404)
    def not_found_error(error):
        try:
            return render_template('errors/404.html'), 404
        except Exception:
            return "404 Not Found", 404

    @app.errorhandler(500)
    def internal_error(error):
        try:
            return render_template('errors/500.html'), 500
        except Exception:
            return "500 Internal Server Error", 500

    @app.errorhandler(403)
    def forbidden_error(error):
        try:
            return render_template('errors/403.html'), 403
        except Exception:
            return "403 Forbidden", 403

    # Context processors
    @app.context_processor
    def inject_user():
        from flask_login import current_user
        return dict(current_user=current_user)

    return app
