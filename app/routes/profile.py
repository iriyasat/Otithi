from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/profile")
@login_required
def profile():
    """User profile page for all user types"""
    return render_template('profile.html', user=current_user)

@profile_bp.route("/my_listings")
@login_required
def my_listings():
    """User's property listings (for hosts)"""
    if current_user.user_type == 'host':
        # Get user's listings logic here
        return render_template('host/my_listings.html', user=current_user)
    else:
        return redirect(url_for('profile.profile'))
