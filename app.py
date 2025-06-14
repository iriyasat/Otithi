from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, send_from_directory, g, session
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_babel import Babel, gettext as _
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config, db
import os
from functools import wraps
from datetime import datetime, timedelta
from flask_migrate import Migrate
import stripe
import json
from payment_gateways import PaymentGateway
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename

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
@csrf.exempt
@app.route('/api/login', methods=['GET', 'POST'])
def api_login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('login.html')

    if current_user.is_authenticated:
        return jsonify({
            "status": "error",
            "message": _("You are already logged in")
        }), 400

    try:
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
        
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": _("An error occurred during login. Please try again.")
        }), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('login.html')

    if current_user.is_authenticated:
        return jsonify({
            "status": "error",
            "message": _("You are already logged in")
        }), 400

    try:
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
        
    except Exception as e:
        app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": _("An error occurred during login. Please try again.")
        }), 500

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

from models import User, Property, Booking, SavedProperty, Review, PropertyImage

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
    featured_properties = Property.query.filter_by(is_available=True).order_by(Property.created_at.desc()).limit(6).all()
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
    return render_template('index.html', featured_properties=featured_properties, testimonials=testimonials)

@app.route('/browse')
def browse_properties():
    properties = Property.query.filter_by(is_available=True).order_by(Property.created_at.desc()).all()
    return render_template('browse_properties.html', properties=properties)

@app.route('/registration')
def registration_page():
    if current_user.is_authenticated:
        return redirect(url_for(f'{current_user.role}_dashboard'))
    return render_template('registration.html')

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    # Get statistics based on user role
    stats = {}
    activities = []
    
    if current_user.role == 'admin':
        # Admin statistics
        stats = {
            'total_users': User.query.count(),
            'total_properties': Property.query.count(),
            'total_bookings': Booking.query.count(),
            'total_revenue': db.session.query(db.func.sum(Booking.total_amount)).scalar() or 0
        }
        # Get admin activities
        activities = get_admin_activities()
        
    elif current_user.role == 'host':
        # Host statistics
        host_properties = Property.query.filter_by(host_id=current_user.id).all()
        property_ids = [p.id for p in host_properties]
        
        stats = {
            'total_properties': len(host_properties),
            'active_bookings': Booking.query.filter(
                Booking.property_id.in_(property_ids),
                Booking.status == 'confirmed'
            ).count(),
            'average_rating': db.session.query(db.func.avg(Review.rating))
                .filter(Review.property_id.in_(property_ids))
                .scalar() or 0,
            'total_earnings': db.session.query(db.func.sum(Booking.total_amount))
                .filter(Booking.property_id.in_(property_ids))
                .scalar() or 0
        }
        # Get host activities
        activities = get_host_activities(current_user.id)
        
    else:  # Guest role
        # Guest statistics
        stats = {
            'total_bookings': Booking.query.filter_by(guest_id=current_user.id).count(),
            'total_reviews': Review.query.filter_by(user_id=current_user.id).count(),
            'total_spent': db.session.query(db.func.sum(Booking.total_amount))
                .filter_by(guest_id=current_user.id)
                .scalar() or 0,
            'saved_properties': SavedProperty.query.filter_by(user_id=current_user.id).count()
        }
        # Get guest activities
        activities = get_guest_activities(current_user.id)
    
    return render_template('dashboard.html',
                         stats=stats,
                         activities=activities)

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
@app.route('/api/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return redirect(url_for(f'{current_user.role}_dashboard'))
        return render_template('registration.html')

    if current_user.is_authenticated:
        return jsonify({
            "status": "error",
            "message": _("You are already logged in")
        }), 400

    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'name', 'userType']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "status": "error",
                "message": _(f"{field} is required")
            }), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({
            "status": "error",
            "message": _("Email already registered")
        }), 400
    
    # Validate password
    if len(data.get('password')) < 8:
        return jsonify({
            "status": "error",
            "message": _("Password must be at least 8 characters long")
        }), 400
    
    # Create user
    user = User(
        email=data.get('email'),
        name=data.get('name'),
        role=data.get('userType'),
        preferred_language=data.get('preferred_language', 'en'),
        is_active=True
    )
    user.set_password(data.get('password'))
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Log the user in after successful registration
        login_user(user)
        session['user_id'] = user.id
        
        # Determine the redirect URL based on user role
        if user.role == 'admin':
            redirect_url = '/admin/dashboard'
        elif user.role == 'host':
            redirect_url = '/host-dashboard'
        else:  # guest
            redirect_url = '/guest-dashboard'
        
        return jsonify({
            "status": "success",
            "message": _("Registration successful"),
            "redirect_url": redirect_url,
            "user": {
                "role": user.role,
                "name": user.name,
                "preferred_language": user.preferred_language
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": _("An error occurred during registration")
        }), 500

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
    
    query = Property.query.filter_by(is_available=True)
    
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
            "city": p.city,
            "price_per_night": p.price_per_night,
            "currency": p.currency,
            "max_guests": p.max_guests,
            "bedrooms": p.bedrooms,
            "bathrooms": p.bathrooms,
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
        "properties": [{
            "id": p.id,
            "title": p.title,
            "location": p.location,
            "price_per_night": p.price_per_night,
            "user_id": p.host_id,
            "status": p.status
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
            "total_amount": b.total_amount
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
        comment_bn=data.get('comment_bn')
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

@app.route('/guest/dashboard')
@login_required
@guest_required
def guest_dashboard():
    total_bookings = Booking.query.filter_by(user_id=current_user.id).count()
    saved_properties = SavedProperty.query.filter_by(user_id=current_user.id).count()
    total_reviews = Review.query.filter_by(user_id=current_user.id).count()
    total_spent = db.session.query(db.func.sum(Booking.total_amount)).filter_by(
        user_id=current_user.id,
        status='completed'
    ).scalar() or 0

    recent_activities = get_guest_activities(current_user.id)
    
    return render_template('dashboard.html',
                         total_bookings=total_bookings,
                         saved_properties=saved_properties,
                         total_reviews=total_reviews,
                         total_spent=total_spent,
                         recent_activities=recent_activities)

@app.route('/guest/bookings')
@login_required
@guest_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/guest/saved-properties')
@login_required
@guest_required
def saved_properties():
    saved_properties = SavedProperty.query.filter_by(user_id=current_user.id).order_by(SavedProperty.created_at.desc()).all()
    return render_template('saved_properties.html', saved_properties=saved_properties)

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

if __name__ == '__main__':
    with app.app_context():
        # Create admin user if not exists
        admin = User.query.filter_by(email='admin@atithi.com').first()
        if not admin:
            admin = User(
                email='admin@atithi.com',
                name='Admin',
                role='admin'
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True, port=5000)