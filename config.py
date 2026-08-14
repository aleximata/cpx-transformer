import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mi-clave-secreta-12345'
    
    # Usar /tmp para Railway (única carpeta con permisos de escritura)
    # SQLITE: Los datos se pierden al reiniciar el contenedor
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/cpx_users.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = 86400  # 24 horas
    ADMIN_EMAIL = 'admin@cpx.com'
    ADMIN_PASSWORD = 'admin123'