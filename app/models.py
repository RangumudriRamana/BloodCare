"""
Database Models

Defines all database tables and relationships used in the application.
"""

from datetime import datetime
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

from .extensions import db

# User Model
class User(UserMixin, db.Model):
    """User model representing admin, donor, volunteer, and requester role."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # roles: admin, donor, volunteer, requester
    role = db.Column(db.String(30), nullable=False, default="donor")

    failed_attempts = db.Column(db.Integer, default=0)
    lock_until = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_valid_role(self):
        """Check if the assigned role is valid."""
        return self.role in ["admin", "donor", "requester", "volunteer"]

    def get_reset_token(self):
        """Generate password reset token."""
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps(self.email, salt="password-reset-salt")

    @staticmethod
    def verify_reset_token(token, expires_sec=900):
        """Verify password reset token and return associated user."""
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            email = serializer.loads(
                token,
                salt="password-reset-salt",
                max_age=expires_sec
            )
        except Exception:
            return None

        return User.query.filter_by(email=email).first()

# Donor Model
class Donor(db.Model):
    """Donor profile linked to a user."""
    __tablename__ = "donors"

    donor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    blood_group = db.Column(db.String(10), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)

    availability = db.Column(db.Boolean, default=True)
    last_donated_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship(
        "User",
        backref=db.backref("donor_profile", uselist=False)
    )

# Volunteer Model
class Volunteer(db.Model):
    """Volunteer profile linked to a user"""
    __tablename__ = "volunteers"

    volunteer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(100), nullable=False)

    # status: Active / Inactive
    status = db.Column(db.String(20), default="Active")

    user = db.relationship(
        "User",
        backref=db.backref("volunteer_profile", uselist=False)
    )

# Blood Request model
class BloodRequest(db.Model):
    """Blood request created by a requester."""
    __tablename__ = "blood_requests"

    request_id = db.Column(db.Integer, primary_key=True)
    requester_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    patient_name = db.Column(db.String(120), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)

    blood_group_needed = db.Column(db.String(10), nullable=False)

    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)

    # status: Pending / Approved / Waiting / Completed
    status = db.Column(db.String(20), default="Pending")
    is_emergency = db.Column(db.Boolean, default=False)

    requested_at = db.Column(db.DateTime, default=datetime.utcnow)

    requester = db.relationship(
        "User",
        backref=db.backref("requests", lazy=True)
    )

# Assignment Model
class Assignment(db.Model):
    """Assignment of volunteer to a blood request."""
    __tablename__ = "assignments"

    assignment_id = db.Column(db.Integer, primary_key=True)

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("blood_requests.request_id"),
        nullable=False
    )

    volunteer_id = db.Column(
        db.Integer,
        db.ForeignKey("volunteers.volunteer_id"),
        nullable=False
    )

    task_status = db.Column(db.String(30), default="Assigned")
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    request = db.relationship("BloodRequest", backref="assignments")
    volunteer = db.relationship("Volunteer", backref="assignments")

# Donation History Model
class DonationHistory(db.Model):
    """Tracks completed blood donations."""
    __tablename__ = "donation_history"

    donation_id = db.Column(db.Integer, primary_key=True)

    donor_id = db.Column(
        db.Integer,
        db.ForeignKey("donors.donor_id"),
        nullable=False
    )

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("blood_requests.request_id"),
        nullable=False
    )

    donation_date = db.Column(db.DateTime, default=datetime.utcnow)

    donor = db.relationship("Donor", backref="donations")
    request = db.relationship("BloodRequest", backref="donation_record")