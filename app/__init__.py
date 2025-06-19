from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import click
from flask_login import LoginManager
import os
import secrets
from flask_wtf.csrf import CSRFProtect
from config import Config

# Global extensions
db = SQLAlchemy()
migrate = Migrate()  # <-- Ensure this is global
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    
    # Load config from config.py
    app.config.from_object(config_class)
    
    # Security and CSRF settings
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable CSRF token timeout for development
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROFILE_PIC_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # <-- Register Flask-Migrate
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(user_id)

    from app.routes import main as main_blueprint, get_profile_image_url, get_listing_image_url
    app.register_blueprint(main_blueprint)

    # Register custom Jinja2 filters
    from markupsafe import Markup, escape

    def nl2br(value):
        """Convert newlines in text to HTML line breaks"""
        if not value:
            return ''
        return Markup("<br>").join(escape(value).split("\n"))

    app.jinja_env.filters['nl2br'] = nl2br

    # Add helper functions to template context
    app.jinja_env.globals.update(get_profile_image_url=get_profile_image_url)
    app.jinja_env.globals.update(get_listing_image_url=get_listing_image_url)
    
    # Add message notification count to template context
    @app.context_processor
    def inject_unread_message_count():
        from flask_login import current_user
        if current_user.is_authenticated:
            from app.models import Message, Conversation
            # Only count messages that are part of actual conversations
            unread_count = (db.session.query(Message)
                          .join(Conversation)
                          .filter(
                              Message.recipient_id == current_user.id,
                              Message.is_read == False,
                              db.or_(
                                  Conversation.user1_id == current_user.id,
                                  Conversation.user2_id == current_user.id
                              )
                          ).count())
            return {'new_message_count': unread_count}
        return {'new_message_count': 0}
    
    # Add current year to template context
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}

    @app.cli.command('init-db')
    def init_db_command():
        db.create_all()
        click.echo('Database initialized!')

    return app