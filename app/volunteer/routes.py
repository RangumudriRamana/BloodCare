"""
Volunteer Routes

Handles volunteer dashboard, profile management,
assigned tasks, and task status updates.
"""

import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from ..utils import role_required
from ..models import Volunteer, Assignment, Donor, DonationHistory
from ..extensions import db

volunteer_bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')


# Volunteer Dashboard
@volunteer_bp.route("/dashboard")
@login_required
@role_required("volunteer")
def dashboard():
    """Display volunteer dashboard."""

    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()

    return render_template("volunteer/volunteer_dashboard.html", volunteer=volunteer)


# Volunteer Profile
@volunteer_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("volunteer")
def profile():
    """Create or update volunteer profile."""

    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":

        phone = request.form.get("phone", "").strip()
        city = request.form.get("city", "").strip()
        status = request.form.get("status")

        # Phone validation
        if not phone.isdigit() or len(phone) != 10:
            flash("Enter valid 10-digit phone number.", "warning")
            return redirect(url_for("volunteer.profile"))

        # City validation
        if not re.match(r"^[A-Za-z ]+$", city):
            flash("City must contain only letters.", "warning")
            return redirect(url_for("volunteer.profile"))

        volunteer.phone = phone
        volunteer.city = city
        volunteer.status = status

        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("volunteer.profile"))

    return render_template("volunteer/volunteer_profile.html", volunteer=volunteer)


# Volunteer Tasks
@volunteer_bp.route("/tasks")
@login_required
@role_required("volunteer")
def task():
    """Display assigned tasks for the volunteer."""

    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()

    if not volunteer:
        flash("Please complete your profile first.", "warning")
        return redirect(url_for("volunteer.dashboard"))

    tasks = Assignment.query.filter_by(
        volunteer_id=volunteer.volunteer_id
    ).all()

    return render_template("volunteer/volunteer_tasks.html", tasks=tasks)


# Update Task Status
@volunteer_bp.route("/update_task_status/<int:assignment_id>", methods=["POST"])
@login_required
@role_required("volunteer")
def update_task_status(assignment_id):
    """Update status of assigned task."""

    assignment = Assignment.query.get_or_404(assignment_id)

    # Ensure volunteer can update only their own assignment
    volunteer = Volunteer.query.filter_by(user_id=current_user.id).first()
    if not volunteer or assignment.volunteer_id != volunteer.volunteer_id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("volunteer.task"))

    assignment.task_status = request.form.get("task_status")

    if assignment.task_status == "Completed":

        # Mark main request as completed
        assignment.request.status = "Completed"

        # Log first matching donor for academic tracking
        donor = Donor.query.filter_by(
            blood_group=assignment.request.blood_group_needed,
            city=assignment.request.city
        ).first()

        if donor:
            donation = DonationHistory(
                donor_id=donor.donor_id,
                request_id=assignment.request.request_id
            )
            db.session.add(donation)

    db.session.commit()

    flash("Task updated!", "success")
    return redirect(url_for("volunteer.task"))