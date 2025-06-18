from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import click
from flask_login import LoginManager
import os
import secrets
from flask_wtf.csrf import CSRFProtect

# Global extensions
db = SQLAlchemy()
migrate = Migrate()  # <-- Ensure this is global
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Load config from config.py
    from config import Config
    app.config.from_object(Config)
    
    # Override database URI for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3307/otithi_db'
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-for-otithi-platform')
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable CSRF token timeout for development
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROFILE_PIC_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)  # <-- Register Flask-Migrate
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'main.login'

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.cli.command('init-db')
    def init_db_command():
        db.create_all()
        click.echo('Database initialized!')

    return app