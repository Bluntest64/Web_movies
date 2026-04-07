import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:137946@localhost:5432/cinegest')
    # Render uses postgres:// but psycopg2 needs postgresql://
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
