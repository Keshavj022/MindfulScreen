import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

def get_database_url():
    """Get database URL, converting postgres:// to postgresql:// for SQLAlchemy 2.0+"""
    url = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/data/mindfulscreen.db')
    # Render uses postgres:// but SQLAlchemy 2.0+ requires postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,    # Recycle connections every 5 minutes
    }

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'default-encryption-key-change-in-production')

    MAX_CONTENT_LENGTH = 500 * 1024 * 1024
    UPLOAD_FOLDER = BASE_DIR / 'data' / 'uploads'
    FRAMES_FOLDER = BASE_DIR / 'data' / 'frames'
    KNOWLEDGE_GRAPH_FOLDER = BASE_DIR / 'data' / 'knowledge_graphs'

    FRAME_EXTRACTION_RATE = 2
    MAX_FRAMES_PER_SESSION = 300

    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.webm', '.mov', '.avi', '.mkv'}

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600

    ENCRYPT_FRAMES = True
    ENCRYPT_ANALYSIS_DATA = True
    AUTO_DELETE_FRAMES_AFTER_DAYS = 30

    PRIVACY_POLICY_VERSION = '1.0'
    TERMS_VERSION = '1.0'

    RATE_LIMIT_ENABLED = True
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_ATTEMPT_WINDOW = 900

    # Email/SMTP Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@mindfulscreen.com')

    # OTP Configuration
    OTP_EXPIRY_MINUTES = int(os.getenv('OTP_EXPIRY_MINUTES', 10))
    OTP_MAX_ATTEMPTS = int(os.getenv('OTP_MAX_ATTEMPTS', 3))

    @staticmethod
    def init_app(app):
        data_folder = BASE_DIR / 'data'
        data_folder.mkdir(parents=True, exist_ok=True)

        for folder in [Config.UPLOAD_FOLDER, Config.FRAMES_FOLDER, Config.KNOWLEDGE_GRAPH_FOLDER]:
            folder.mkdir(parents=True, exist_ok=True)
