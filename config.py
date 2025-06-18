import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost:3307/otithi_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PROFILE_PIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'images', 'profiles')
    LISTING_PIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'images', 'listings')
    UI_IMAGE_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'images', 'ui')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 