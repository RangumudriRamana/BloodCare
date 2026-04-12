from flask import Blueprint, render_template
from ..models import Donor, BloodRequest, Volunteer

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def home():
    total_donors = Donor.query.count()
    total_requests = BloodRequest.query.count()
    total_volunteers = Volunteer.query.count()
    completed_requests = BloodRequest.query.filter_by(status="Completed").count()

    return render_template(
        "index.html",
        total_donors=total_donors,
        total_requests=total_requests,
        total_volunteers=total_volunteers,
        completed_requests=completed_requests
    )

@main_bp.route("/gallery")
def gallery():
    images = [
        f"gallery{i}.jpg" for i in range(1, 20)
    ]
    return render_template("gallery.html", images=images)

@main_bp.route("/faq")
def faq():
    return render_template("faq.html")