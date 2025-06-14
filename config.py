from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from datetime import timedelta

app = Flask(__name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/static')
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3307/atithi_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, Property, Booking 

class Config:
    # Basic Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:@localhost:3307/atithi_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Internationalization
    LANGUAGES = ['en', 'bn']
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'Asia/Dhaka'
    
    # Payment gateway configuration
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    
    # bKash configuration
    BKASH_API_KEY = os.environ.get('BKASH_API_KEY')
    BKASH_API_SECRET = os.environ.get('BKASH_API_SECRET')
    BKASH_API_URL = os.environ.get('BKASH_API_URL', 'https://api.bkash.com/v1')
    BKASH_MERCHANT_ID = os.environ.get('BKASH_MERCHANT_ID')
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Security configuration
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Cache configuration
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300 