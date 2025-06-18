from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import click
from flask_login import LoginManager
import os
import secrets
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3307/otithi_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = secrets.token_hex(16)  # Secure random secret key
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'images')

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # Enable CSRF protection globally
    login_manager.login_view = 'main.login'

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register Blueprints here
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database."""
        db.create_all()
        click.echo('Database initialized!')

    return app 