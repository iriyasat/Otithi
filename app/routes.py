import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Listing, User
from . import db
from .forms import ListingForm, RegisterForm, LoginForm
import uuid
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists.')
            return render_template('register.html', form=form)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Logged in successfully!')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.home'))

@main.route('/test-db')
def test_db():
    from .models import Listing
    try:
        listings = Listing.query.all()
        return 'Database connected successfully'
    except Exception as e:
        return f'Database connection failed: {e}'

@main.route('/listings')
def listings():
    page = request.args.get('page', 1, type=int)
    sort = request.args.get('sort', '')
    search = request.args.get('search', '')
    
    query = Listing.query
    
    # Apply search if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Listing.name.ilike(search_term),
                Listing.location.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort == 'asc':
        query = query.order_by(Listing.price_per_night.asc())
    elif sort == 'desc':
        query = query.order_by(Listing.price_per_night.desc())
    
    # Apply pagination
    pagination = query.paginate(page=page, per_page=5, error_out=False)
    listings = pagination.items
    
    return render_template(
        'listings.html',
        listings=listings,
        pagination=pagination,
        search=search,
        sort=sort
    )

@main.route('/add-listing', methods=['GET', 'POST'])
@login_required
def add_listing():
    form = ListingForm()
    if form.validate_on_submit():
        image_filename = None
        if form.image.data:
            image_file = form.image.data
            if image_file.filename:
                ext = os.path.splitext(secure_filename(image_file.filename))[1]
                unique_name = f"{uuid.uuid4().hex}{ext}"
                image_path = os.path.join(current_app.root_path, 'static', 'images', unique_name)
                image_file.save(image_path)
                image_filename = unique_name
        listing = Listing(
            name=form.name.data,
            location=form.location.data,
            description=form.description.data,
            price_per_night=float(form.price_per_night.data),
            host_name=form.host_name.data,
            image_filename=image_filename
        )
        db.session.add(listing)
        db.session.commit()
        flash('Listing added successfully!')
        return redirect(url_for('main.listings'))
    return render_template('add_listing.html', form=form)

@main.route('/edit-listing/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_listing(id):
    listing = Listing.query.get_or_404(id)
    form = ListingForm(obj=listing)
    if form.validate_on_submit():
        form.populate_obj(listing)
        if form.image.data:
            image_file = form.image.data
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(current_app.root_path, 'static', 'images', filename)
            image_file.save(image_path)
            listing.image_filename = filename
        db.session.commit()
        flash('Listing updated successfully!')
        return redirect(url_for('main.listings'))
    return render_template('edit_listing.html', form=form, listing=listing)

@main.route('/delete-listing/<int:id>', methods=['POST'])
@login_required
def delete_listing(id):
    listing = Listing.query.get_or_404(id)
    # Delete associated image file if it exists
    if listing.image_filename:
        image_path = os.path.join(current_app.root_path, 'static', 'images', listing.image_filename)
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
        except Exception as e:
            flash(f'Image file could not be deleted: {e}', 'warning')
    db.session.delete(listing)
    db.session.commit()
    flash('Listing deleted successfully!')
    return redirect(url_for('main.listings'))

@main.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Roll back db session in case of database error
    return render_template('500.html'), 500 