"""
Donor Routes

Handles donor dashboard, profile management,
availability toggle, and donation history.
"""

import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from ..utils import role_required
from ..models import Donor
from ..extensions import db


donor_bp = Blueprint('donor', __name__, url_prefix='/donor')


# Donor Dashboard
@donor_bp.route("/dashboard")
@login_required
@role_required("donor")
def dashboard():
    """Display donor dashboard."""

    donor = Donor.query.filter_by(user_id=current_user.id).first()

    return render_template("donor/donor_dashboard.html", donor=donor)

# Donor Profile
@donor_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("donor")
def profile():
    """Create or update donor profile information."""

    donor = Donor.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":

        blood_group = request.form.get("blood_group")
        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        pincode = request.form.get("pincode", "").strip()
        availability = True if request.form.get("availability") == "Active" else False

        # Phone validation
        if not phone.isdigit() or len(phone) != 10:
            flash("Enter valid 10-digit phone number.", "warning")
            return redirect(url_for("donor.profile"))

        # City validation
        if not re.match(r"^[A-Za-z ]+$", city):
            flash("City must contain only letters.", "warning")
            return redirect(url_for("donor.profile"))

        # Pincode validation
        if not pincode.isdigit() or len(pincode) != 6:
            flash("Enter valid 6-digit pincode.", "warning")
            return redirect(url_for("donor.profile"))

        # Save or update donor profile
        if donor:
            donor.blood_group = blood_group
            donor.phone = phone
            donor.city = city
            donor.pincode = pincode
            donor.availability = availability
        else:
            donor = Donor(
                user_id=current_user.id,
                blood_group=blood_group,
                phone=phone,
                city=city,
                pincode=pincode,
                availability=availability
            )
            db.session.add(donor)

        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("donor.profile"))

    # Get request
    return render_template("donor/donor_profile.html", donor=donor)


# Toggle Availability
@donor_bp.route("/toggle_availability")
@login_required
@role_required("donor")
def toggle_availability():
    """Toggle donor availability status."""


    donor = Donor.query.filter_by(user_id=current_user.id).first()

    if donor:
        donor.availability = not donor.availability
        db.session.commit()
        flash("Availability status updated!", "success")

    return redirect(url_for("donor.dashboard"))


# Donation History
@donor_bp.route("/history")
@login_required
@role_required("donor")
def history():
    """Display donor donation history."""

    donor = Donor.query.filter_by(user_id=current_user.id).first()
    donations = donor.donations if donor else []

    return render_template("donor/donor_history.html", donations=donations)