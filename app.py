from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, send_from_directory, g, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config, db
import os
from functools import wraps
from datetime import datetime, timedelta, UTC
from flask_migrate import Migrate
import stripe
import json
from payment_gateways import PaymentGateway
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session expires after 7 days
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookie over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Protect against CSRF
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
db.init_app(app)
CORS(app)
csrf = CSRFProtect(app)

# Exempt API routes from CSRF protection
# @csrf.exempt
# @app.route('/api/login', methods=['GET', 'POST'])
# def api_login():
#     if request.method == 'GET':
#         if current_user.is_authenticated:
#             return redirect(url_for('dashboard'))
#         return render_template('login.html')
# 
#     if current_user.is_authenticated:
#         return jsonify({
#             "status": "error",
#             "message": _("You are already logged in")
#         }), 400
# 
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({
#                 "status": "error",
#                 "message": _("No data provided")
#             }), 400
# 
#         email = data.get('email')
#         password = data.get('password')
#         
#         if not email or not password:
#             return jsonify({
#                 "status": "error",
#                 "message": _("Email and password are required")
#             }), 400
# 
#         user = User.query.filter_by(email=email).first()
#         
#         if not user:
#             return jsonify({
#                 "status": "error",
#                 "message": _("Invalid email or password")
#             }), 401
#         
#         if not user.check_password(password):
#             return jsonify({
#                 "status": "error",
#                 "message": _("Invalid email or password")
#             }), 401
#             
#         if not user.is_active:
#             return jsonify({
#                 "status": "error",
#                 "message": _("Your account has been deactivated. Please contact support.")
#             }), 403
#             
#         login_user(user, remember=data.get('remember', False))
#         session['user_id'] = user.id
#         
#         # Redirect to the dashboard
#         redirect_url = url_for('dashboard')
#         
#         return jsonify({
#             "status": "success",
#             "message": _("Login successful"),
#             "redirect_url": redirect_url,
#             "user": {
#                 "role": user.role,
#                 "name": user.name,
#                 "preferred_language": user.preferred_language
#             }
#         })
#         
#     except Exception as e:
#         app.logger.error(f"Login error: {str(e)}")
#         return jsonify({
#             "status": "error",
#             "message": _("An error occurred during login. Please try again.")
#         }), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}_dashboard'))
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": _("No data provided")
            }), 400

        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                "status": "error",
                "message": _("Email and password are required")
            }), 400

        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                "status": "error",
                "message": _("Invalid email or password")
            }), 401
        
        if not user.check_password(password):
            return jsonify({
                "status": "error",
                "message": _("Invalid email or password")
            }), 401
            
        if not user.is_active:
            return jsonify({
                "status": "error",
                "message": _("Your account has been deactivated. Please contact support.")
            }), 403
            
        login_user(user, remember=data.get('remember', False))
        session['user_id'] = user.id
        
        # Redirect to the dashboard
        redirect_url = url_for('dashboard')
        
        return jsonify({
            "status": "success",
            "message": _("Login successful"),
            "redirect_url": redirect_url,
            "user": {
                "role": user.role,
                "name": user.name,
                "preferred_language": user.preferred_language
            }
        })
    return render_template('guest/login.html')

def get_locale():
    if current_user.is_authenticated:
        return current_user.preferred_language
    return request.accept_languages.best_match(['en', 'bn'])

babel = Babel(app, locale_selector=get_locale)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

# Initialize payment gateways
stripe.api_key = app.config['STRIPE_SECRET_KEY']

# Initialize payment gateway
payment_gateway = PaymentGateway()

from models import User, Property, Booking, SavedProperty, Review, PropertyImage, CulturalExperience, MealOption, TransportOption, FestivalSeason, CommunityVerification

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash(_('You do not have permission to access this page.'), 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def host_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'host':
            flash(_('You do not have permission to access this page.'), 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def guest_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'guest':
            flash(_('You do not have permission to access this page.'), 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Main routes
@app.route('/')
def index():
    featured_properties = Property.query.filter_by(is_featured=True).limit(6).all()
    testimonials = [
        {
            'user_name': 'John Doe',
            'user_image': url_for('static', filename='assets/images/default-avatar.png'),
            'rating': 5,
            'comment': 'Amazing experience! The property was exactly as described and the host was very helpful.'
        },
        {
            'user_name': 'Jane Smith',
            'user_image': url_for('static', filename='assets/images/default-avatar.png'),
            'rating': 5,
            'comment': 'Great location and beautiful property. Will definitely book again!'
        },
        {
            'user_name': 'Mike Johnson',
            'user_image': url_for('static', filename='assets/images/default-avatar.png'),
            'rating': 4,
            'comment': 'Very comfortable stay. The amenities were perfect for our needs.'
        }
    ]
    return render_template('guest/index.html', featured_properties=featured_properties, testimonials=testimonials)

@app.route('/browse')
def browse_properties():
    properties = Property.query.order_by(Property.created_at.desc()).all()
    return render_template('guest/browse_properties.html', properties=properties)

@app.route('/registration')
def registration_page():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}_dashboard'))
    return render_template('guest/registration.html')

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    """Redirect to role-specific dashboard"""
    return redirect(url_for(f'{current_user.role}_dashboard'))

@app.route('/guest/dashboard')
@login_required
@guest_required
def guest_dashboard():
    """Guest dashboard view"""
    # Get user's bookings
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    
    # Get user's saved properties
    saved_properties = SavedProperty.query.filter_by(user_id=current_user.id).all()
    
    return render_template('guest/dashboard.html', 
                         bookings=bookings,
                         saved_properties=saved_properties)

@app.route('/host/dashboard')
@login_required
@host_required
def host_dashboard():
    """Host dashboard view"""
    # Get host's properties
    properties = Property.query.filter_by(host_id=current_user.id).all()
    property_ids = [p.id for p in properties]
    
    # Calculate statistics
    total_bookings = Booking.query.filter(Booking.property_id.in_(property_ids)).count()
    total_revenue = db.session.query(db.func.sum(Booking.total_amount)).filter(
        Booking.property_id.in_(property_ids),
        Booking.status == 'confirmed'
    ).scalar() or 0
    
    # Get recent bookings
    recent_bookings = Booking.query.filter(
        Booking.property_id.in_(property_ids)
    ).order_by(Booking.created_at.desc()).limit(5).all()
    
    # Get recent reviews
    recent_reviews = Review.query.filter(
        Review.property_id.in_(property_ids)
    ).order_by(Review.created_at.desc()).limit(5).all()
    
    return render_template('host/dashboard.html',
                         properties=properties,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue,
                         recent_bookings=recent_bookings,
                         recent_reviews=recent_reviews)

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard view"""
    # Get total users
    total_users = User.query.count()
    total_properties = Property.query.count()
    total_bookings = Booking.query.count()
    
    # Get recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_properties = Property.query.order_by(Property.created_at.desc()).limit(5).all()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_properties=total_properties,
                         total_bookings=total_bookings,
                         recent_users=recent_users,
                         recent_properties=recent_properties,
                         recent_bookings=recent_bookings)

def calculate_growth(model, field, property_ids=None):
    """Calculate growth percentage for a given model and field"""
    now = datetime.now(UTC)
    last_month = now - timedelta(days=30)
    
    # Base query
    current_query = model.query
    last_month_query = model.query
    
    # Apply property filter if property_ids is provided
    if property_ids is not None:
        if model == Property:
            current_query = current_query.filter(model.id.in_(property_ids))
            last_month_query = last_month_query.filter(model.id.in_(property_ids))
        elif model == Booking:
            current_query = current_query.filter(model.property_id.in_(property_ids))
            last_month_query = last_month_query.filter(model.property_id.in_(property_ids))
        elif model == Review:
            current_query = current_query.filter(model.property_id.in_(property_ids))
            last_month_query = last_month_query.filter(model.property_id.in_(property_ids))
    
    # Get current and last month counts
    current_count = current_query.filter(getattr(model, field) >= last_month).count()
    last_month_count = last_month_query.filter(
        getattr(model, field) >= last_month - timedelta(days=30),
        getattr(model, field) < last_month
    ).count()
    
    # Calculate growth percentage
    if last_month_count == 0:
        return 100 if current_count > 0 else 0
    return ((current_count - last_month_count) / last_month_count) * 100

def calculate_revenue_growth():
    """Calculate revenue growth percentage over the last month"""
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    
    current_revenue = db.session.query(db.func.sum(Booking.total_price)).scalar() or 0
    previous_revenue = db.session.query(db.func.sum(Booking.total_price))\
        .filter(Booking.created_at < month_ago)\
        .scalar() or 0
    
    if previous_revenue == 0:
        return 100 if current_revenue > 0 else 0
    
    return round(((current_revenue - previous_revenue) / previous_revenue) * 100, 1)

def calculate_earnings_growth(property_ids):
    """Calculate earnings growth percentage for a host over the last month"""
    now = datetime.now(UTC)
    last_month = now - timedelta(days=30)
    
    # Get current and last month earnings
    current_earnings = db.session.query(db.func.sum(Booking.total_price))\
        .filter(Booking.property_id.in_(property_ids))\
        .filter(Booking.created_at >= last_month)\
        .scalar() or 0
    
    last_month_earnings = db.session.query(db.func.sum(Booking.total_price))\
        .filter(Booking.property_id.in_(property_ids))\
        .filter(Booking.created_at >= last_month - timedelta(days=30))\
        .filter(Booking.created_at < last_month)\
        .scalar() or 0
    
    # Calculate growth percentage
    if last_month_earnings == 0:
        return 100 if current_earnings > 0 else 0
    return ((current_earnings - last_month_earnings) / last_month_earnings) * 100

def calculate_spending_growth():
    """Calculate spending growth percentage for a guest over the last month"""
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    
    current_spending = db.session.query(db.func.sum(Booking.total_price))\
        .filter_by(guest_id=current_user.id)\
        .scalar() or 0
    previous_spending = db.session.query(db.func.sum(Booking.total_price))\
        .filter_by(guest_id=current_user.id)\
        .filter(Booking.created_at < month_ago)\
        .scalar() or 0
    
    if previous_spending == 0:
        return 100 if current_spending > 0 else 0
    
    return round(((current_spending - previous_spending) / previous_spending) * 100, 1)

def calculate_rating_change(property_ids):
    """Calculate rating change percentage for a host over the last month"""
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    
    current_rating = db.session.query(db.func.avg(Review.rating))\
        .join(Property)\
        .filter(Property.host_id == current_user.id)\
        .filter(Property.id.in_(property_ids))\
        .scalar() or 0
    previous_rating = db.session.query(db.func.avg(Review.rating))\
        .join(Property)\
        .filter(Property.host_id == current_user.id)\
        .filter(Review.created_at < month_ago)\
        .filter(Property.id.in_(property_ids))\
        .scalar() or 0
    
    if previous_rating == 0:
        return 100 if current_rating > 0 else 0
    
    return round(((current_rating - previous_rating) / previous_rating) * 100, 1)

def get_admin_activities():
    activities = []
    
    # Get recent user registrations
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    for user in recent_users:
        activities.append({
            'date': user.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'New user registered: {user.name}',
            'status': 'New',
            'status_color': 'success',
            'action_url': url_for('admin_users')
        })
    
    # Get recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    for booking in recent_bookings:
        activities.append({
            'date': booking.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'New booking for {booking.property.name}',
            'status': booking.status.capitalize(),
            'status_color': 'primary' if booking.status == 'active' else 'success' if booking.status == 'completed' else 'warning',
            'action_url': url_for('admin_bookings')
        })
    
    return sorted(activities, key=lambda x: x['date'], reverse=True)[:10]

def get_host_activities(host_id):
    activities = []
    
    # Get recent bookings for host's properties
    recent_bookings = Booking.query.join(Property).filter(
        Property.host_id == host_id
    ).order_by(Booking.created_at.desc()).limit(5).all()
    
    for booking in recent_bookings:
        activities.append({
            'date': booking.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'New booking for {booking.property.name}',
            'status': booking.status.capitalize(),
            'status_color': 'primary' if booking.status == 'active' else 'success' if booking.status == 'completed' else 'warning',
            'action_url': url_for('host_bookings')
        })
    
    # Get recent reviews
    recent_reviews = Review.query.join(Property).filter(
        Property.host_id == host_id
    ).order_by(Review.created_at.desc()).limit(5).all()
    
    for review in recent_reviews:
        activities.append({
            'date': review.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'New review for {review.property.name}',
            'status': f'{review.rating} stars',
            'status_color': 'warning',
            'action_url': url_for('property_reviews', property_id=review.property_id)
        })
    
    return sorted(activities, key=lambda x: x['date'], reverse=True)[:10]

def get_guest_activities(user_id):
    activities = []
    
    # Get recent bookings
    recent_bookings = Booking.query.filter_by(
        user_id=user_id
    ).order_by(Booking.created_at.desc()).limit(5).all()
    
    for booking in recent_bookings:
        activities.append({
            'date': booking.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'Booking for {booking.property.name}',
            'status': booking.status.capitalize(),
            'status_color': 'primary' if booking.status == 'active' else 'success' if booking.status == 'completed' else 'warning',
            'action_url': url_for('my_bookings')
        })
    
    # Get recent reviews
    recent_reviews = Review.query.filter_by(
        user_id=user_id
    ).order_by(Review.created_at.desc()).limit(5).all()
    
    for review in recent_reviews:
        activities.append({
            'date': review.created_at.strftime('%Y-%m-%d %H:%M'),
            'description': f'Review for {review.property.name}',
            'status': f'{review.rating} stars',
            'status_color': 'warning',
            'action_url': url_for('property_reviews', property_id=review.property_id)
        })
    
    return sorted(activities, key=lambda x: x['date'], reverse=True)[:10]

# API routes
def validate_email_format(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}_dashboard'))
    
    if request.method == 'POST':
        try:
            # Handle both form data and JSON data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()

            # Validate required fields
            required_fields = ['name', 'email', 'password', 'confirm_password', 'role']
            for field in required_fields:
                if not data.get(field):
                    if request.is_json:
                        return jsonify({
                            'status': 'error',
                            'message': f'{field.replace("_", " ").title()} is required'
                        }), 400
                    flash(f'{field.replace("_", " ").title()} is required', 'error')
                    return redirect(url_for('register'))

            # Check if passwords match
            if data['password'] != data['confirm_password']:
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Passwords do not match'
                    }), 400
                flash('Passwords do not match', 'error')
                return redirect(url_for('register'))

            # Check if email already exists
            if User.query.filter_by(email=data['email']).first():
                if request.is_json:
                    return jsonify({
                        'status': 'error',
                        'message': 'Email already registered'
                    }), 400
                flash('Email already registered', 'error')
                return redirect(url_for('register'))

            # Create new user
            new_user = User(
                name=data['name'],
                email=data['email'],
                role=data['role']
            )
            new_user.set_password(data['password'])

            db.session.add(new_user)
            db.session.commit()

            if request.is_json:
                return jsonify({
                    'status': 'success',
                    'message': 'Registration successful',
                    'redirect_url': url_for('login')
                })
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Registration error: {str(e)}")
            if request.is_json:
                return jsonify({
                    'status': 'error',
                    'message': 'An error occurred during registration'
                }), 500
            flash('An error occurred during registration', 'error')
            return redirect(url_for('register'))

    return render_template('guest/register.html')

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    
    # Check if the request is an API call
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            "status": "success",
            "message": _("Successfully logged out"),
            "redirect_url": url_for('login')
        })
    
    # For regular requests, redirect directly
    return redirect(url_for('login'))

@app.route('/api/properties', methods=['GET'])
def get_properties():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    city = request.args.get('city', '')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    query = Property.query
    
    if search:
        query = query.filter(
            (Property.title_en.ilike(f'%{search}%')) |
            (Property.title_bn.ilike(f'%{search}%')) |
            (Property.description_en.ilike(f'%{search}%')) |
            (Property.description_bn.ilike(f'%{search}%'))
        )
    
    if city:
        query = query.filter(Property.city.ilike(f'%{city}%'))
    
    if min_price:
        query = query.filter(Property.price_per_night >= min_price)
    
    if max_price:
        query = query.filter(Property.price_per_night <= max_price)
    
    properties = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        "properties": [{
            "id": p.id,
            "title": p.title_en if g.get('lang') == 'en' else p.title_bn,
            "description": p.description_en if g.get('lang') == 'en' else p.description_bn,
            "location": p.location_en if g.get('lang') == 'en' else p.location_bn,
            "city": getattr(p, 'city', ''),
            "price_per_night": p.price_per_night,
            "currency": getattr(p, 'currency', 'BDT'),
            "max_guests": p.max_guests,
            "bedrooms": getattr(p, 'bedrooms', None),
            "bathrooms": getattr(p, 'bathrooms', None),
            "property_type": p.property_type,
            "amenities": p.amenities,
            "images": [img.image_url for img in p.images],
            "rating": sum(r.rating for r in p.reviews) / len(p.reviews) if p.reviews else 0
        } for p in properties.items],
        "total": properties.total,
        "pages": properties.pages,
        "current_page": properties.page
    })

@app.route('/api/properties/<int:property_id>', methods=['GET'])
def get_property(property_id):
    property = Property.query.get_or_404(property_id)
    return jsonify({
        "id": property.id,
        "title": property.title_en if g.get('lang') == 'en' else property.title_bn,
        "description": property.description_en if g.get('lang') == 'en' else property.description_bn,
        "location": property.location_en if g.get('lang') == 'en' else property.location_bn,
        "address": property.address,
        "city": property.city,
        "district": property.district,
        "price_per_night": property.price_per_night,
        "currency": property.currency,
        "max_guests": property.max_guests,
        "bedrooms": property.bedrooms,
        "bathrooms": property.bathrooms,
        "property_type": property.property_type,
        "amenities": property.amenities,
        "rules": property.rules,
        "images": [img.image_url for img in property.images],
        "owner": {
            "name": property.host_user.name,
            "phone": property.host_user.phone
        },
        "reviews": [{
            "rating": r.rating,
            "comment": r.comment_en if g.get('lang') == 'en' else r.comment_bn,
            "author": r.review_user.name,
            "created_at": r.created_at.isoformat()
        } for r in property.reviews]
    })

@app.route('/api/bookings', methods=['POST'])
@login_required
def create_booking():
    data = request.get_json()
    property = Property.query.get_or_404(data.get('property_id'))
    
    # Check if property is available for the selected dates
    existing_booking = Booking.query.filter(
        Booking.property_id == property.id,
        Booking.status.in_(['confirmed', 'pending']),
        ((Booking.check_in <= data.get('check_in') <= Booking.check_out) |
         (Booking.check_in <= data.get('check_out') <= Booking.check_out))
    ).first()
    
    if existing_booking:
        return jsonify({
            "status": "error",
            "message": _("Property is not available for the selected dates")
        }), 400
    
    # Calculate total price
    check_in = datetime.strptime(data.get('check_in'), '%Y-%m-%d').date()
    check_out = datetime.strptime(data.get('check_out'), '%Y-%m-%d').date()
    nights = (check_out - check_in).days
    total_price = property.price_per_night * nights
    
    booking = Booking(
        property_id=property.id,
        user_id=current_user.id,
        check_in=check_in,
        check_out=check_out,
        guests=data.get('guests', 1),
        total_price=total_price,
        currency=property.currency,
        special_requests=data.get('special_requests')
    )
    
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "message": _("Booking created successfully"),
        "booking_id": booking.id,
        "total_price": total_price,
        "currency": property.currency
    })

@app.route('/api/payments/verify', methods=['POST'])
@login_required
def verify_payment():
    data = request.get_json()
    booking = Booking.query.get_or_404(data.get('booking_id'))
    
    if booking.user_id != current_user.id:
        return jsonify({"status": "error", "message": _("Unauthorized")}), 403
    
    try:
        return jsonify({
            "status": "error",
            "message": _("Payment verification failed")
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@app.route('/api/payments/bkash/create', methods=['POST'])
@login_required
def create_bkash_payment():
    data = request.get_json()
    booking_id = data.get('booking_id')
    amount = data.get('amount')
    currency = data.get('currency', 'BDT')

    if not booking_id or not amount:
        return jsonify({'error': _('Missing required parameters')}), 400

    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': _('Booking not found')}), 404

    if booking.user_id != current_user.id:
        return jsonify({'error': _('Unauthorized')}), 403

    result = payment_gateway.create_payment('bkash', amount, currency, booking_id)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    return jsonify(result)

@app.route('/api/payments/bkash/verify', methods=['POST'])
@login_required
def verify_bkash_payment():
    data = request.get_json()
    payment_id = data.get('payment_id')
    
    if not payment_id:
        return jsonify({'error': _('Missing payment ID')}), 400

    result = payment_gateway.verify_payment('bkash', payment_id)
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    # Update booking status if payment is successful
    if result.get('status') == 'COMPLETED':
        booking_id = result.get('merchant_order_id').split('_')[1]
        booking = Booking.query.get(booking_id)
        if booking:
            booking.payment_status = 'completed'
            booking.payment_method = 'bkash'
            booking.payment_id = payment_id
            db.session.commit()
    
    return jsonify(result)

@app.route('/api/payments/bkash/callback', methods=['POST'])
def bkash_callback():
    """
    Handle bKash payment callback
    """
    data = request.get_json()
    
    # Verify the callback signature
    # Add your signature verification logic here
    
    payment_id = data.get('paymentID')
    status = data.get('status')
    
    if status == 'COMPLETED':
        booking_id = data.get('merchantOrderID').split('_')[1]
        booking = Booking.query.get(booking_id)
        if booking:
            booking.payment_status = 'completed'
            booking.payment_method = 'bkash'
            booking.payment_id = payment_id
            db.session.commit()
    
    return jsonify({'status': 'success'})

# Admin API endpoints
@app.route('/api/check-admin')
@login_required
def check_admin():
    return jsonify({
        "is_admin": current_user.role == 'admin'
    })

@app.route('/api/admin/properties')
@login_required
@admin_required
def admin_properties():
    properties = Property.query.all()
    return jsonify({
        "status": "success",
        "data": [{
            "id": p.id,
            "title": p.title_en,
            "location": p.location_en,
            "host": p.host.name,
            "price": p.price_per_night,
            "status": "Active" if p.verifications else "Pending",
            "created_at": p.created_at.strftime('%Y-%m-%d %H:%M')
        } for p in properties]
    })

@app.route('/api/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return jsonify({
        "users": [{
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for u in users]
    })

@app.route('/api/admin/bookings')
@login_required
@admin_required
def admin_bookings():
    bookings = Booking.query.all()
    return jsonify({
        "bookings": [{
            "id": b.id,
            "property_id": b.property_id,
            "guest_id": b.guest_id,
            "check_in": b.check_in_date.strftime('%Y-%m-%d'),
            "check_out": b.check_out_date.strftime('%Y-%m-%d'),
            "status": b.status,
            "total_price": b.total_price
        } for b in bookings]
    })

@app.route('/api/check-role')
@login_required
def check_role():
    return jsonify({
        "role": current_user.role
    })

# Saved Properties API
@app.route('/api/guest/saved-properties', methods=['GET'])
@login_required
def get_saved_properties():
    saved_properties = SavedProperty.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        "properties": [{
            "id": sp.saved_property_obj.id,
            "title": sp.saved_property_obj.title_en if g.get('lang') == 'en' else sp.saved_property_obj.title_bn,
            "description": sp.saved_property_obj.description_en if g.get('lang') == 'en' else sp.saved_property_obj.description_bn,
            "location": sp.saved_property_obj.location_en if g.get('lang') == 'en' else sp.saved_property_obj.location_bn,
            "price_per_night": sp.saved_property_obj.price_per_night,
            "currency": sp.saved_property_obj.currency,
            "image_url": sp.saved_property_obj.images[0].image_url if sp.saved_property_obj.images else None,
            "rating": sum(r.rating for r in sp.saved_property_obj.property_reviews) / len(sp.saved_property_obj.property_reviews) if sp.saved_property_obj.property_reviews else 0
        } for sp in saved_properties]
    })

@app.route('/api/guest/saved-properties/<int:property_id>', methods=['POST'])
@login_required
def toggle_saved_property(property_id):
    saved_property = SavedProperty.query.filter_by(
        user_id=current_user.id,
        property_id=property_id
    ).first()
    
    if saved_property:
        db.session.delete(saved_property)
        action = 'removed'
    else:
        saved_property = SavedProperty(
            user_id=current_user.id,
            property_id=property_id
        )
        db.session.add(saved_property)
        action = 'added'
    
    try:
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": f"Property {action} from saved properties",
            "action": action
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "An error occurred"
        }), 500

# Reviews API
@app.route('/api/properties/<int:property_id>/reviews', methods=['GET'])
def get_property_reviews(property_id):
    reviews = Review.query.filter_by(property_id=property_id).order_by(Review.created_at.desc()).all()
    return jsonify({
        "reviews": [{
            "id": r.id,
            "rating": r.rating,
            "comment": r.comment_en if g.get('lang') == 'en' else r.comment_bn,
            "author": {
                "name": r.review_user.name,
                "profile_picture": r.review_user.profile_picture
            },
            "created_at": r.created_at.isoformat()
        } for r in reviews]
    })

@app.route('/api/properties/<int:property_id>/reviews', methods=['POST'])
@login_required
def create_property_review(property_id):
    data = request.get_json()
    
    # Check if user has completed a booking for this property
    booking = Booking.query.filter_by(
        property_id=property_id,
        user_id=current_user.id,
        status='completed'
    ).first()
    
    if not booking:
        return jsonify({
            "status": "error",
            "message": _("You can only review properties you have stayed at")
        }), 403
    
    # Check if user has already reviewed this property
    existing_review = Review.query.filter_by(
        property_id=property_id,
        user_id=current_user.id
    ).first()
    
    if existing_review:
        return jsonify({
            "status": "error",
            "message": _("You have already reviewed this property")
        }), 400
    
    review = Review(
        property_id=property_id,
        user_id=current_user.id,
        rating=data.get('rating'),
        comment_en=data.get('comment_en'),
        comment_bn=data.get('comment_bn'),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC)
    )
    
    try:
        db.session.add(review)
        db.session.commit()
        return jsonify({
            "status": "success",
            "message": _("Review submitted successfully"),
            "review": {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment_en if g.get('lang') == 'en' else review.comment_bn,
                "author": {
                    "name": review.review_user.name,
                    "profile_picture": review.review_user.profile_picture
                },
                "created_at": review.created_at.isoformat()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": _("An error occurred while submitting the review")
        }), 500

# Property Images API
@app.route('/api/properties/<int:property_id>/images', methods=['GET'])
def get_property_images(property_id):
    images = PropertyImage.query.filter_by(property_id=property_id).all()
    return jsonify({
        "images": [{
            "id": img.id,
            "url": img.image_url,
            "is_primary": img.is_primary
        } for img in images]
    })

@app.route('/api/properties/<int:property_id>/images', methods=['POST'])
@login_required
def upload_property_image(property_id):
    property = Property.query.get_or_404(property_id)
    
    # Check if user is the property owner
    if property.host_id != current_user.id:
        return jsonify({
            "status": "error",
            "message": _("You do not have permission to upload images for this property")
        }), 403
    
    if 'image' not in request.files:
        return jsonify({
            "status": "error",
            "message": _("No image file provided")
        }), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({
            "status": "error",
            "message": _("No selected file")
        }), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'properties', str(property_id))
        os.makedirs(file_path, exist_ok=True)
        file.save(os.path.join(file_path, filename))
        
        image_url = f"/static/uploads/properties/{property_id}/{filename}"
        is_primary = request.form.get('is_primary', 'false').lower() == 'true'
        
        # If this is the first image or marked as primary, update other images
        if is_primary:
            PropertyImage.query.filter_by(property_id=property_id).update({'is_primary': False})
        
        image = PropertyImage(
            property_id=property_id,
            image_url=image_url,
            is_primary=is_primary
        )
        
        try:
            db.session.add(image)
            db.session.commit()
            return jsonify({
                "status": "success",
                "message": _("Image uploaded successfully"),
                "image": {
                    "id": image.id,
                    "url": image.image_url,
                    "is_primary": image.is_primary
                }
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": _("An error occurred while uploading the image")
            }), 500
    
    return jsonify({
        "status": "error",
        "message": _("Invalid file type")
    }), 400

@app.route('/api/properties/<int:property_id>/images/<int:image_id>', methods=['DELETE'])
@login_required
def delete_property_image(property_id, image_id):
    property = Property.query.get_or_404(property_id)
    
    # Check if user is the property owner
    if property.host_id != current_user.id:
        return jsonify({
            "status": "error",
            "message": _("You do not have permission to delete images for this property")
        }), 403
    
    image = PropertyImage.query.get_or_404(image_id)
    
    try:
        # Delete the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'properties', str(property_id), os.path.basename(image.image_url))
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the database record
        db.session.delete(image)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "message": _("Image deleted successfully")
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": _("An error occurred while deleting the image")
        }), 500

# Helper function for file uploads
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/guest/bookings')
@login_required
@guest_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('guest/my_bookings.html', bookings=bookings)

@app.route('/guest/saved-properties')
@login_required
@guest_required
def saved_properties():
    saved_properties = SavedProperty.query.filter_by(user_id=current_user.id).order_by(SavedProperty.created_at.desc()).all()
    return render_template('guest/saved_properties.html', saved_properties=saved_properties)

# Custom template filters
@app.template_filter('number_format')
def number_format(value):
    if value is None:
        return '৳0'
    try:
        # Format the number with commas and add the taka sign
        return f'৳{value:,.2f}'
    except (ValueError, TypeError):
        return '৳0'

@app.template_filter('currency')
def currency_filter(value):
    """Format value as currency"""
    if value is None:
        return '৳0'
    return f'৳{value:,.2f}'

# Cultural Experiences Routes
@app.route('/api/properties/<int:property_id>/experiences', methods=['GET'])
def get_property_experiences(property_id):
    try:
        experiences = CulturalExperience.query.filter_by(property_id=property_id).all()
        return jsonify({
            "status": "success",
            "experiences": [{
                "id": exp.id,
                "title_en": exp.title_en,
                "title_bn": exp.title_bn,
                "description_en": exp.description_en,
                "description_bn": exp.description_bn,
                "price": exp.price,
                "duration": exp.duration,
                "max_participants": exp.max_participants,
                "is_available": exp.is_available
            } for exp in experiences]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/properties/<int:property_id>/experiences', methods=['POST'])
@login_required
@host_required
def create_property_experience(property_id):
    try:
        property = Property.query.get_or_404(property_id)
        if property.host_id != current_user.id:
            return jsonify({"status": "error", "message": _("Unauthorized")}), 403

        data = request.get_json()
        experience = CulturalExperience(
            property_id=property_id,
            title_en=data['title_en'],
            title_bn=data['title_bn'],
            description_en=data['description_en'],
            description_bn=data['description_bn'],
            price=data['price'],
            duration=data.get('duration'),
            max_participants=data.get('max_participants'),
            is_available=True
        )
        db.session.add(experience)
        db.session.commit()
        return jsonify({"status": "success", "message": _("Experience created successfully")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Meal Options Routes
@app.route('/api/properties/<int:property_id>/meals', methods=['GET'])
def get_property_meals(property_id):
    try:
        meals = MealOption.query.filter_by(property_id=property_id).all()
        return jsonify({
            "status": "success",
            "meals": [{
                "id": meal.id,
                "name_en": meal.name_en,
                "name_bn": meal.name_bn,
                "description_en": meal.description_en,
                "description_bn": meal.description_bn,
                "price": meal.price,
                "meal_type": meal.meal_type,
                "dietary_info": meal.dietary_info
            } for meal in meals]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/properties/<int:property_id>/meals', methods=['POST'])
@login_required
@host_required
def create_property_meal(property_id):
    try:
        property = Property.query.get_or_404(property_id)
        if property.host_id != current_user.id:
            return jsonify({"status": "error", "message": _("Unauthorized")}), 403

        data = request.get_json()
        meal = MealOption(
            property_id=property_id,
            name_en=data['name_en'],
            name_bn=data['name_bn'],
            description_en=data.get('description_en'),
            description_bn=data.get('description_bn'),
            price=data['price'],
            meal_type=data['meal_type'],
            dietary_info=data.get('dietary_info', {})
        )
        db.session.add(meal)
        db.session.commit()
        return jsonify({"status": "success", "message": _("Meal option created successfully")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Transport Options Routes
@app.route('/api/properties/<int:property_id>/transport', methods=['GET'])
def get_property_transport(property_id):
    try:
        transport_options = TransportOption.query.filter_by(property_id=property_id).all()
        return jsonify({
            "status": "success",
            "transport_options": [{
                "id": opt.id,
                "type": opt.type,
                "description_en": opt.description_en,
                "description_bn": opt.description_bn,
                "price": opt.price,
                "is_available": opt.is_available
            } for opt in transport_options]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/properties/<int:property_id>/transport', methods=['POST'])
@login_required
@host_required
def create_property_transport(property_id):
    try:
        property = Property.query.get_or_404(property_id)
        if property.host_id != current_user.id:
            return jsonify({"status": "error", "message": _("Unauthorized")}), 403

        data = request.get_json()
        transport = TransportOption(
            property_id=property_id,
            type=data['type'],
            description_en=data.get('description_en'),
            description_bn=data.get('description_bn'),
            price=data['price'],
            is_available=True
        )
        db.session.add(transport)
        db.session.commit()
        return jsonify({"status": "success", "message": _("Transport option created successfully")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Festival Seasons Routes
@app.route('/api/festivals', methods=['GET'])
def get_festivals():
    try:
        festivals = FestivalSeason.query.all()
        return jsonify({
            "status": "success",
            "festivals": [{
                "id": fest.id,
                "name_en": fest.name_en,
                "name_bn": fest.name_bn,
                "start_date": fest.start_date.isoformat(),
                "end_date": fest.end_date.isoformat(),
                "description_en": fest.description_en,
                "description_bn": fest.description_bn,
                "region": fest.region
            } for fest in festivals]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/festivals', methods=['POST'])
@login_required
@admin_required
def create_festival():
    try:
        data = request.get_json()
        festival = FestivalSeason(
            name_en=data['name_en'],
            name_bn=data['name_bn'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            description_en=data.get('description_en'),
            description_bn=data.get('description_bn'),
            region=data.get('region', 'all')
        )
        db.session.add(festival)
        db.session.commit()
        return jsonify({"status": "success", "message": _("Festival season created successfully")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Community Verification Routes
@app.route('/api/properties/<int:property_id>/verify', methods=['POST'])
@login_required
def create_verification(property_id):
    try:
        data = request.get_json()
        verification = CommunityVerification(
            property_id=property_id,
            verifier_id=current_user.id,
            verification_type=data['verification_type'],
            status='pending',
            comments=data.get('comments')
        )
        db.session.add(verification)
        db.session.commit()
        return jsonify({"status": "success", "message": _("Verification request submitted successfully")})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/properties/<int:property_id>/verifications', methods=['GET'])
def get_property_verifications(property_id):
    try:
        verifications = CommunityVerification.query.filter_by(property_id=property_id).all()
        return jsonify({
            "status": "success",
            "verifications": [{
                "id": ver.id,
                "verifier_id": ver.verifier_id,
                "verification_type": ver.verification_type,
                "status": ver.status,
                "comments": ver.comments,
                "created_at": ver.created_at.isoformat()
            } for ver in verifications]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/properties/<int:property_id>')
def property_details(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('host/properties/details/property_details.html', property=property)

@app.route('/properties/<int:property_id>/experiences')
def property_experiences(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('host/properties/experiences/cultural_experiences.html', property=property)

@app.route('/properties/<int:property_id>/meals')
def property_meals(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('host/properties/meals/meal_options.html', property=property)

@app.route('/properties/<int:property_id>/transport')
def property_transport(property_id):
    property = Property.query.get_or_404(property_id)
    return render_template('host/properties/transport/transport_options.html', property=property)

@app.route('/festivals')
def festivals():
    return render_template('host/festivals/index.html')

def get_last_12_months():
    """Get labels for the last 12 months"""
    now = datetime.now(UTC)
    months = []
    for i in range(11, -1, -1):
        month = now - timedelta(days=30*i)
        months.append(month.strftime('%b %Y'))
    return months

def get_monthly_stats(model, field, property_ids=None):
    """Get monthly statistics for a model"""
    now = datetime.now(UTC)
    stats = []
    
    for i in range(11, -1, -1):
        start_date = now - timedelta(days=30*(i+1))
        end_date = now - timedelta(days=30*i)
        
        query = model.query.filter(
            getattr(model, field) >= start_date,
            getattr(model, field) < end_date
        )
        
        # Apply property filter if provided
        if property_ids is not None:
            if model == Property:
                query = query.filter(model.id.in_(property_ids))
            elif model == Booking:
                query = query.filter(model.property_id.in_(property_ids))
            elif model == Review:
                query = query.filter(model.property_id.in_(property_ids))
        
        count = query.count()
        stats.append(count)
    
    return stats

def get_monthly_earnings(property_ids):
    """Get monthly earnings for a host"""
    now = datetime.now(UTC)
    earnings = []
    
    for i in range(11, -1, -1):
        start_date = now - timedelta(days=30*(i+1))
        end_date = now - timedelta(days=30*i)
        
        monthly_earnings = db.session.query(db.func.sum(Booking.total_price))\
            .filter(Booking.property_id.in_(property_ids))\
            .filter(Booking.created_at >= start_date)\
            .filter(Booking.created_at < end_date)\
            .scalar() or 0
            
        earnings.append(float(monthly_earnings))
    
    return earnings

def get_monthly_spending():
    """Get monthly spending for a guest"""
    now = datetime.now(UTC)
    spending = []
    
    for i in range(11, -1, -1):
        start_date = now - timedelta(days=30*(i+1))
        end_date = now - timedelta(days=30*i)
        
        monthly_spending = db.session.query(db.func.sum(Booking.total_price))\
            .filter_by(user_id=current_user.id)\
            .filter(Booking.created_at >= start_date)\
            .filter(Booking.created_at < end_date)\
            .scalar() or 0
            
        spending.append(float(monthly_spending))
    
    return spending

def cleanup_duplicate_admins():
    """Remove duplicate admin accounts, keeping only the first one"""
    admins = User.query.filter_by(role='admin').all()
    if len(admins) > 1:
        # Sort by creation date to keep the oldest admin
        admins.sort(key=lambda x: x.created_at)
        # Keep the first admin, delete the rest
        for admin in admins[1:]:
            db.session.delete(admin)
        db.session.commit()
        print(f"Removed {len(admins)-1} duplicate admin accounts")

# Call the cleanup function when the app starts
with app.app_context():
    cleanup_duplicate_admins()

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update user information"""
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        if 'email' in data:
            if not validate_email_format(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            if User.query.filter(User.email == data['email'], User.id != user_id).first():
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'preferred_language' in data:
            user.preferred_language = data['preferred_language']
        
        if 'password' in data:
            is_strong, message = validate_password_strength(data['password'])
            if not is_strong:
                return jsonify({'error': message}), 400
            user.set_password(data['password'])
        
        user.updated_at = datetime.now(UTC)
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'preferred_language': user.preferred_language
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    """Delete a user account"""
    if not current_user.is_admin and current_user.id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def init_db():
    """Initialize the database with default data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if any users exist
        if User.query.first() is None:
            # Create default users only if no users exist
            users = [
                User(
                    email='admin@otithi.com',
                    first_name='Admin',
                    last_name='User',
                    role='admin',
                    preferred_language='en'
                ),
                User(
                    email='host@otithi.com',
                    first_name='Host',
                    last_name='User',
                    role='host',
                    preferred_language='en'
                ),
                User(
                    email='guest@otithi.com',
                    first_name='Guest',
                    last_name='User',
                    role='guest',
                    preferred_language='en'
                )
            ]
            
            # Set passwords
            users[0].set_password('admin123')
            users[1].set_password('host123')
            users[2].set_password('guest123')
            
            # Add users to database
            for user in users:
                db.session.add(user)
            db.session.commit()
            print("Default users created successfully!")

# Initialize database when app starts
with app.app_context():
    init_db()

@app.route('/about')
def about():
    return render_template('common/about.html')

@app.route('/contact')
def contact():
    return render_template('common/contact.html')

@app.route('/faq')
def faq():
    return render_template('common/faq.html')

@app.route('/terms')
def terms():
    return render_template('common/terms.html')

@app.route('/privacy')
def privacy():
    return render_template('common/privacy.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)