"""
Admin Routes

Handles dashboard statistics, request approval,
donor notification, and volunteer assignment.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from sqlalchemy.orm import joinedload
import threading

from ..models import BloodRequest, Donor, Volunteer, Assignment, User
from ..extensions import db
from ..utils import get_compatible_blood_groups, role_required
from ..email_utils import send_email, build_email_template

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Background Email Function
def send_bulk_emails(app, donors, req):
    """Send emails in background (no timeout)."""
    with app.app_context():
        for donor in donors:
            # Send Donor Email
            content = f"""
            Hello {donor.user.name},

            <p>An urgent blood requirement has been approved that matches your blood group.</p>

            <table style="width:100%; border-collapse:collapse; margin-top:15px;">
                <tr><td><strong>Patient Name:</strong></td><td>{req.patient_name}</td></tr>
                <tr><td><strong>Blood Group Needed:</strong></td><td>{req.blood_group_needed}</td></tr>
                <tr><td><strong>City:</strong></td><td>{req.city}</td></tr>
                <tr><td><strong>Pincode:</strong></td><td>{req.pincode}</td></tr>
                <tr><td><strong>Contact:</strong></td><td>{req.contact_number}</td></tr>
            </table>

            <p style="margin-top:15px;">
            Your contribution can save a life. Please respond as soon as possible.
            </p>
            """

            html_body = build_email_template(
                title="Urgent Blood Match Found",
                content=content,
                button_text="Call Patient",
                button_link=f"tel:{req.contact_number}",
                is_emergency=req.is_emergency
            )

            try:
                send_email(
                    subject="BloodCare+ | Urgent Blood Match Found",
                    recipients=[donor.user.email],
                    html_body=html_body
                )

            except Exception as e:
                current_app.logger.error(f"Email sending failed: {e}")



# Admin Dashboard
@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    """Display admin dashboard with system statistics."""

    total_users = User.query.count()
    total_requests = BloodRequest.query.count()
    total_donors = Donor.query.count()
    total_volunteers = Volunteer.query.count()

    pending_requests = BloodRequest.query.filter_by(status="Pending").count()
    approved_requests = BloodRequest.query.filter_by(status="Approved").count()
    waiting_requests = BloodRequest.query.filter_by(status="Waiting").count()
    completed_requests = BloodRequest.query.filter_by(status="Completed").count()

    recent_requests = BloodRequest.query.order_by(
        BloodRequest.requested_at.desc()
    ).limit(5).all()

    blood_groups = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    blood_group_counts = [
        Donor.query.filter_by(blood_group=bg).count()
        for bg in blood_groups
    ]

    status_labels = ["Pending", "Approved", "Waiting", "Completed"]
    status_counts = [
        pending_requests,
        approved_requests,
        waiting_requests,
        completed_requests
    ]

    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        total_requests=total_requests,
        total_donors=total_donors,
        total_volunteers=total_volunteers,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        waiting_requests=waiting_requests,
        completed_requests=completed_requests,
        recent_requests=recent_requests,
        blood_groups=blood_groups,
        blood_group_counts=blood_group_counts,
        status_labels=status_labels,
        status_counts=status_counts
    )


# Admin All Requests
@admin_bp.route("/requests")
@login_required
@role_required("admin")
def requests():
    """Displays all blood requests."""

    requests_list = BloodRequest.query.order_by(
        BloodRequest.is_emergency.desc(),
        BloodRequest.requested_at.desc()
    ).all()

    return render_template("admin/admin_requests.html", requests_list=requests_list)


# View Donors
@admin_bp.route("/donors")
@login_required
@role_required("admin")
def donors():
    """Display all registered donors."""

    donors = Donor.query.options(joinedload(Donor.user)).all()
    return render_template("admin/admin_donors.html", donors=donors)


# View Volunteer
@admin_bp.route("/volunteers")
@login_required
@role_required("admin")
def volunteers():
    """Display all registered volunteers."""

    volunteers = Volunteer.query.options(joinedload(Volunteer.user)).all()
    return render_template("admin/admin_volunteers.html", volunteers=volunteers)


# Request Details
@admin_bp.route("/request/<int:request_id>")
@login_required
@role_required("admin")
def request_details(request_id):
    """View detailed information about a specific request."""

    req = BloodRequest.query.get_or_404(request_id)

    compatible_groups = get_compatible_blood_groups(req.blood_group_needed)

    compatible_donors = Donor.query.filter(
        Donor.blood_group.in_(compatible_groups)
    ).all()

    matched_donors = Donor.query.filter_by(
        blood_group=req.blood_group_needed,
        city=req.city,
        availability=True
    ).all()

    volunteers = Volunteer.query.filter_by(status="Active").all()

    return render_template(
        "admin/request_details.html",
        request=req,
        matched_donors=matched_donors,
        volunteers=volunteers,
        compatible_donors=compatible_donors
    )


# Approve Request
@admin_bp.route("/approve/<int:request_id>")
@login_required
@role_required("admin")

def approve(request_id):
    """Approve a pending blood request and notify donors."""

    req = BloodRequest.query.get_or_404(request_id)

    if req.status != "Pending":
        flash("This request has already been processed.", "warning")
        return redirect(url_for("admin.request_details", request_id=request_id))

    try:
        req.status = "Approved"
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Something went wrong while approving request.", "danger")
        return redirect(url_for("admin.request_details", request_id=request_id))
    
    # Find Donors
    strict_donors = Donor.query.options(joinedload(Donor.user)).filter_by(
        blood_group=req.blood_group_needed,
        city=req.city,
        availability=True
    ).all()

    compatible_groups = get_compatible_blood_groups(req.blood_group_needed)

    compatible_donors = Donor.query.options(joinedload(Donor.user)).filter(
        Donor.blood_group.in_(compatible_groups),
        Donor.availability.is_(True)
    ).all()

    final_donors = strict_donors if strict_donors else compatible_donors

    # Send emails in background
    threading.Thread(
        target=send_bulk_emails,
        args=(current_app._get_current_object(), final_donors, req)
    ).start()

    flash("Request approved and donors notified!", "success")
    return redirect(url_for("admin.request_details", request_id=request_id))


# Assign Volunteer
@admin_bp.route("/assign/<int:request_id>", methods=["POST"])
@login_required
@role_required("admin")
def assign(request_id):
    """Assign a volunteer to a request and notify them."""

    volunteer_id = request.form.get("volunteer_id")
    volunteer = Volunteer.query.options(joinedload(Volunteer.user)).get(volunteer_id)

    if not volunteer:
        flash("Invalid volunteer selected.", "danger")
        return redirect(url_for("admin.request_details", request_id=request_id))

    req = BloodRequest.query.get_or_404(request_id)

    assignment = Assignment(
        request_id=request_id,
        volunteer_id=volunteer_id
    )

    try:
        db.session.add(assignment)
        req.status = "Waiting"
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Something went wrong while assigning volunteer.", "danger")
        return redirect(url_for("admin.request_details", request_id=request_id))

    # Send volunteer email
    content = f"""
    <p>Hello <strong>{volunteer.user.name}</strong>,</p>

    <p>You have been assigned a new blood request.</p>

    <table style="width:100%; border-collapse:collapse; margin-top:15px;">
        <tr><td><strong>Request ID:</strong></td><td>{req.request_id}</td></tr>
        <tr><td><strong>Patient Name:</strong></td><td>{req.patient_name}</td></tr>
        <tr><td><strong>Blood Group:</strong></td><td>{req.blood_group_needed}</td></tr>
        <tr><td><strong>City:</strong></td><td>{req.city}</td></tr>
        <tr><td><strong>Pincode:</strong></td><td>{req.pincode}</td></tr>
        <tr><td><strong>Contact:</strong></td><td>{req.contact_number}</td></tr>
    </table>

    <p style="margin-top:15px;">Please login to your dashboard and update task status.</p>
    """

    html_body = build_email_template(
        title="New Volunteer Task Assigned",
        content=content,
        button_text="View Dashboard",
        button_link=url_for("volunteer.dashboard", _external=True),
        is_emergency=req.is_emergency
    )

    try:
        send_email(
            subject="BloodCare+ | New Volunteer Task Assigned",
            recipients=[volunteer.user.email],
            html_body=html_body
        )
    except Exception as e:
        current_app.logger.error(f"Email sending failed: {e}")
        flash("Volunteer assigned, but email notification failed.", "warning")

    flash("Volunteer assigned successfully!", "success")
    return redirect(url_for("admin.request_details", request_id=request_id))