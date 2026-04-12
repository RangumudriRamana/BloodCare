"""
Extensions Module

Initializes Flask extensions without binding them to the app.
They will be initialized inside the application factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from flask_migrate import Migrate

# Database instance
db = SQLAlchemy()

# Authentication manager
login_manager = LoginManager()

# Email service
mail = Mail()

# CSRF protection
csrf = CSRFProtect()

# Database migration tool
migrate = Migrate()