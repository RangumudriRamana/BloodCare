"""
Requester Routes

Handles requester dashboard, new blood request creation,
and viewing submitted requests.
"""

import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from ..utils import role_required
from ..models import BloodRequest
from ..extensions import db

requester_bp = Blueprint('requester', __name__, url_prefix='/requester')


# Requester Dashboard
@requester_bp.route("/dashboard")
@login_required
@role_required("requester")
def dashboard():
    """Display requester dashboard with total request count."""

    total_requests = BloodRequest.query.filter_by(
        requester_user_id=current_user.id
    ).count()

    return render_template(
        "requester/requester_dashboard.html",
        total_requests=total_requests
    )


# Create New Blood Request
@requester_bp.route("/new", methods=["GET", "POST"])
@login_required
@role_required("requester")
def new_request():
    """Create a new blood request with input validation."""

    if request.method == "POST":

        patient_name = request.form.get("patient_name", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        blood_group_needed = request.form.get("blood_group_needed")
        city = request.form.get("city", "").strip()
        pincode = request.form.get("pincode", "").strip()
        is_emergency = True if request.form.get("is_emergency") == "on" else False

        # Patient name validation
        if not re.match(r"^[A-Za-z ]+$", patient_name):
            flash("Patient name must contain only letters.", "warning")
            return redirect(url_for("requester.new_request"))

        if len(patient_name) < 3:
            flash("Patient name must be at least 3 characters.", "warning")
            return redirect(url_for("requester.new_request"))

        # Contact number validation
        if not contact_number.isdigit() or len(contact_number) != 10:
            flash("Enter a valid 10-digit contact number.", "warning")
            return redirect(url_for("requester.new_request"))

        # City validation
        if not re.match(r"^[A-Za-z ]+$", city):
            flash("City must contain only letters.", "warning")
            return redirect(url_for("requester.new_request"))

        # Pincode validation
        if not pincode.isdigit() or len(pincode) != 6 or pincode == "000000":
            flash("Enter a valid 6-digit pincode.", "warning")
            return redirect(url_for("requester.new_request"))

        req = BloodRequest(
            requester_user_id=current_user.id,
            patient_name=patient_name,
            contact_number=contact_number,
            blood_group_needed=blood_group_needed,
            city=city,
            pincode=pincode,
            is_emergency=is_emergency
        )

        db.session.add(req)
        db.session.commit()

        flash("Request submitted successfully!", "success")
        return redirect(url_for("requester.my_requests"))

    return render_template("requester/new_request.html")


# View My Requests
@requester_bp.route("/my")
@login_required
@role_required("requester")
def my_requests():
    """Display all requests submitted by the logged-in requester."""

    requests_list = BloodRequest.query.filter_by(
        requester_user_id=current_user.id
    ).order_by(BloodRequest.requested_at.desc()).all()

    return render_template(
        "requester/my_requests.html",
        requests_list=requests_list
    )