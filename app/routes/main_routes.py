from flask import Blueprint, render_template, request, jsonify

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    """Homepage - displays the beautiful Bangladeshi themed homepage"""
    return render_template('index.html')

@main.route('/about')
def about():
    """About page - information about Othiti platform"""
    return render_template('about.html')

@main.route('/listings')
@main.route('/explore')
def listings():
    """Listings page - shows all available properties"""
    return render_template('listing.html')

@main.route('/search')
def search():
    """Search functionality for properties"""
    location = request.args.get('location', '')
    price_range = request.args.get('price', '')
    
    # Basic search parameters (for future implementation)
    search_params = {
        'location': location,
        'price_range': price_range
    }
    
    # For now, redirect to listings page with search parameters
    return render_template('listing.html', search_params=search_params)

@main.route('/api/search')
def api_search():
    """API endpoint for search functionality"""
    query = request.args.get('q', '')
    location = request.args.get('location', '')
    
    # Mock data for demonstration
    mock_properties = [
        {
            'id': 1,
            'title': 'Modern Apartment in Gulshan',
            'location': 'Gulshan, Dhaka',
            'price': 5500,
            'image': 'property-01.jpg',
            'type': 'Apartment'
        },
        {
            'id': 2,
            'title': 'Heritage House in Old Dhaka',
            'location': 'Old Dhaka',
            'price': 3200,
            'image': 'property-02.jpg',
            'type': 'House'
        },
        {
            'id': 3,
            'title': 'Beachfront Villa in Cox\'s Bazar',
            'location': 'Cox\'s Bazar',
            'price': 8000,
            'image': 'property-03.jpg',
            'type': 'Villa'
        },
        {
            'id': 4,
            'title': 'Tea Garden Resort in Sylhet',
            'location': 'Sylhet',
            'price': 4500,
            'image': 'deals-01.jpg',
            'type': 'Resort'
        },
        {
            'id': 5,
            'title': 'Riverside Cottage in Chittagong',
            'location': 'Chittagong',
            'price': 3800,
            'image': 'deals-02.jpg',
            'type': 'Cottage'
        }
    ]
    
    # Simple filtering
    filtered_properties = mock_properties
    if location and location != 'Select Location':
        filtered_properties = [p for p in filtered_properties if location.lower() in p['location'].lower()]
    
    if query:
        filtered_properties = [p for p in filtered_properties if query.lower() in p['title'].lower() or query.lower() in p['location'].lower()]
    
    return jsonify(filtered_properties)

# Health check endpoint
@main.route('/health')
def health_check():
    """Simple health check"""
    return jsonify({'status': 'healthy', 'message': 'Othiti is running!'})

# Test route for development
@main.route('/test')
def test():
    """Test route to verify everything is working"""
    return """
    <h1>Othiti is Working!</h1>
    <p>The Flask application is running successfully.</p>
    <ul>
        <li><a href="/">Home Page</a></li>
        <li><a href="/about">About Page</a></li>
        <li><a href="/listings">Listings/Explore Page</a></li>
        <li><a href="/search?location=Dhaka">Search Test</a></li>
    </ul>
    """ 