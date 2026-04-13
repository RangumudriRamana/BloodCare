"""
Utility Functions

Contains helper functions for blood compatibility,
admin initialization, and role-based access control.
"""

from functools import wraps
from flask import abort
from flask_login import current_user
from werkzeug.security import generate_password_hash

from .models import User
from .extensions import db

# BLOOD GROUP COMPATIBILITY
def get_compatible_blood_groups(blood_group):
    """Return a list of compatible donor blood groups for a given blood group."""
    compatibility = {
        "A+": ["A+", "A-", "O+", "O-"],
        "A-": ["A-", "O-"],
        "B+": ["B+", "B-", "O+", "O-"],
        "B-": ["B-", "O-"],
        "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
        "AB-": ["A-", "B-", "AB-", "O-"],
        "O+": ["O+", "O-"],
        "O-": ["O-"],
    }
    return compatibility.get(blood_group, [])

# Auto Create Default Admin
def create_admin():
    """
    Create a default admin user if one  does not already exists.
    This runs during application startup.
    """
    if not User.query.filter_by(email="bloodcareplus06@gmail.com").first():
        admin = User(
            name="Admin",
            email="bloodcareplus06@gmail.com",
            password_hash=generate_password_hash("Bloodcareplus@2026"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()

# Role-Based Access Control decorator
def role_required(role):
    """
    Restrict access to users with a specific role.
    uage: @role_required("admin")
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role != role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator