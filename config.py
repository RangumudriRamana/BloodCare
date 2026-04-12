"""
Application Configuration
Contains all configuration settings for the Flask application.
"""

import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base configuration class."""

    # Secret key for session management and security
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "database", "blood_donation.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail server Configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # Mail authentication credentials
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # Default sender email
    MAIL_DEFAULT_SENDER = MAIL_USERNAME