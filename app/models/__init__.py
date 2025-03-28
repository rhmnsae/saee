from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inisialisasi SQLAlchemy
db = SQLAlchemy()

# Inisialisasi LoginManager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini'
login_manager.login_message_category = 'info'

from app.models.user import User
from app.models.analysis import Analysis