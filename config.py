import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mi-clave-secreta-12345'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/cpx_users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 86400
    ADMIN_EMAIL = 'admin@cpx.com'
    ADMIN_PASSWORD = 'admin123'