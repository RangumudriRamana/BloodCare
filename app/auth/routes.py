"""
Authentication Routes

Handles login, registration, password reset,
and logout functionality for all roles.
"""

import re
from datetime import datetime, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User
from app.extensions import db
from app.email_utils import send_email



auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# Login Handler (Reusable)
def handle_login(role, dashboard_endpoint, template):
    """Handle login logic for different user roles."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, role=role).first()

        if user:

            # CHECK IF ACCOUNT IS LOCKED
            if user.lock_until and user.lock_until > datetime.utcnow():
                flash("Account locked. Try again later.", "danger")
                return render_template(template)

            # CORRECT PASSWORD
            if check_password_hash(user.password_hash, password):
                user.failed_attempts = 0
                user.lock_until = None
                db.session.commit()

                login_user(user)
                return redirect(url_for(dashboard_endpoint))

            # WRONG PASSWORD
            else:
                user.failed_attempts += 1

                if user.failed_attempts >= 5:
                    user.lock_until = datetime.utcnow() + timedelta(minutes=15)
                    flash("Too many failed attempts. Account locked for 15 minutes.", "danger")
                else:
                    flash("Invalid credentials!", "danger")

                db.session.commit()
                return render_template(template)

        flash("Invalid credentials!", "danger")

    return render_template(template)


# Login Routes
@auth_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login route."""
    return handle_login("admin", "admin.dashboard", "admin/admin_login.html")


@auth_bp.route("/donor/login", methods=["GET", "POST"])
def donor_login():
    """Donor login route."""
    return handle_login("donor", "donor.dashboard", "donor/donor_login.html")


@auth_bp.route("/volunteer/login", methods=["GET", "POST"])
def volunteer_login():
    """Volunteer login route."""
    return handle_login("volunteer", "volunteer.dashboard", "volunteer/volunteer_login.html")


@auth_bp.route("/requester/login", methods=["GET", "POST"])
def requester_login():
    """Requester login route."""
    return handle_login("requester", "requester.dashboard", "requester/requester_login.html")

# Password Reset
@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Handle forgot password and send reset email."""
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if user:

            # Admin extra safety check
            if user.role == "admin":
                current_app.logger.warning(f"Admin reset requested for {user.email}")
                flash("Admin password reset requires manual approval.", "warning")
                return redirect(url_for("auth.admin_login"))

            token = user.get_reset_token()
            reset_url = url_for("auth.reset_password", token=token, _external=True)

            try:
                send_email(
                    subject="Password Reset - BloodCare+",
                    recipients=[user.email],
                    html_body=f"""
                        <p>Click the link below to reset your password:</p>
                        <a href="{reset_url}">{reset_url}</a>
                    """
                )
            except Exception as e:
                current_app.logger.error(f"Password reset email failed: {e}")
                flash("Email sending failed.", "danger")
                return redirect(url_for("auth.forgot_password"))

        flash("If that email exists, a reset link has been sent.", "info")
        return redirect(url_for("auth.donor_login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """Reset user password using token verification."""
    user = User.verify_reset_token(token)

    if not user:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password")

        # Strong password validation
        if (
            len(password) < 6
            or not re.search(r"[A-Z]", password)
            or not re.search(r"[a-z]", password)
            or not re.search(r"[0-9]", password)
            or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
        ):
            flash("Password must be strong.", "warning")
            return redirect(request.url)

        user.password_hash = generate_password_hash(password)
        db.session.commit()

        flash("Password reset successful. You can now login.", "success")
        return redirect(url_for("auth.donor_login"))

    return render_template("auth/reset_password.html")


# Register
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle new user registration."""
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, email):
            flash("Please enter a valid email address.", "warning")
            return redirect(url_for("auth.register"))
        password = request.form.get("password")

        # Strong password validation
        if (
            len(password) < 6
            or not re.search(r"[A-Z]", password)
            or not re.search(r"[a-z]", password)
            or not re.search(r"[0-9]", password)
            or not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
        ):
            flash(
                "Password must be at least 6 characters and include uppercase, lowercase, number, and special character.",
                "warning",
            )
            return redirect(url_for("auth.register"))
        allowed_roles = ["donor", "requester", "volunteer"]

        role = request.form.get("role")

        if role not in allowed_roles:
            return "Invalid role selected", 400

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "warning")
            if role == "donor":
                return redirect(url_for("auth.donor_login"))
            elif role == "requester":
                return redirect(url_for("auth.requester_login"))
            elif role == "volunteer":
                return redirect(url_for("auth.volunteer_login"))
            else:
                return redirect(url_for("main.index"))

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration successful!", "success")
        if role == "donor":
            return redirect(url_for("auth.donor_login"))
        elif role == "requester":
            return redirect(url_for("auth.requester_login"))
        elif role == "volunteer":
            return redirect(url_for("auth.volunteer_login"))
        else:
            return redirect(url_for("main.index"))

    return render_template("register.html")


# Logout
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Logout the currently logged-in user."""
    logout_user()
    return redirect(url_for("main.home"))