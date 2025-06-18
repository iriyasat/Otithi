import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://username:password@localhost/otithi_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    PROFILE_PIC_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'profiles')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 