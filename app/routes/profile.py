from flask import Blueprint
profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
def profile():
    return "Profile page - temporarily working"
