from flask import Flask, request
import os

def create_app(config_name=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'your-secret-key-change-this'
    app.config['APP_NAME'] = 'Othiti'
    app.config['APP_DESCRIPTION'] = 'Bangladeshi Hospitality Platform'
    
    # Register blueprints - only the ones we need for now
    from app.routes.main_routes import main
    from app.routes.auth_routes import auth
    from app.routes.user_routes import user
    from app.routes.host_routes import host
    from app.routes.admin_routes import admin
    from app.routes.messages_routes import messages
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(host, url_prefix='/host')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(messages, url_prefix='/messages')
    
    # Basic error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return """
        <h1>Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <p><a href="/">Return to Home</a></p>
        """, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return """
        <h1>Internal Server Error</h1>
        <p>Something went wrong on our end.</p>
        <p><a href="/">Return to Home</a></p>
        """, 500
    
    # Context processors for templates
    @app.context_processor
    def inject_app_info():
        return {
            'app_name': app.config.get('APP_NAME', 'Othiti'),
            'app_description': app.config.get('APP_DESCRIPTION', 'Bangladeshi Hospitality Platform'),
            'request': request
        }
    
    # Template filters
    @app.template_filter('currency')
    def currency_filter(amount):
        """Format currency in BDT"""
        return f"৳ {amount:,.0f}"
    
    @app.template_filter('dateformat')
    def dateformat_filter(date, format='%B %d, %Y'):
        """Format date"""
        if date is None:
            return ""
        return date.strftime(format)
    
    return app 