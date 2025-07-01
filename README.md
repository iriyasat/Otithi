# Otithi - Bangladeshi Hospitality Platform

Otithi is a Flask-based web application inspired by Airbnb, designed specifically for the Bangladeshi market. The platform allows users to discover and book unique accommodations across Bangladesh while providing hosts with tools to share their spaces and earn extra income.

## Features

- **Modern UI/UX**: Bootstrap 5-based responsive design with Bangladeshi green color scheme
- **Property Listings**: Browse and search accommodations across Bangladesh
- **User Authentication**: Secure login and registration system
- **Host Dashboard**: Tools for property owners to list and manage their spaces
- **Search & Filters**: Advanced search with location and date filters
- **Responsive Design**: Mobile-first approach for all screen sizes

## Project Structure

```
Othiti/
├── app/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── search.html
│   │   ├── listing_detail.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── become_host.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── img/
│   │       ├── demo_listing_1.jpg
│   │       └── user-gear.png
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Applications/XAMPP/xamppfiles/htdocs/Othiti
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables (optional):**
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export DATABASE_URL="sqlite:///otithi.db"
   ```

## Running the Application

1. **Start the Flask development server:**
   ```bash
   python run.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Design System

### Colors
- **Primary**: #006a4e (Bangladeshi Green)
- **Secondary**: #ffffff (White)
- **Text**: #333333 (Dark Gray)
- **Accent**: #ff5722 (Orange)

### Typography
- **Font Family**: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
- **Headings**: Bold weights with proper hierarchy
- **Body Text**: Regular weight with 1.6 line height

### Components
- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Primary green with hover effects
- **Forms**: Clean inputs with focus states
- **Navigation**: Sticky header with search integration

## Key Pages

1. **Homepage** (`/`): Hero section with search, featured listings, and promotional content
2. **Search Results** (`/search`): Filterable grid of property listings
3. **Property Details** (`/listing/<id>`): Detailed view with booking form
4. **Authentication** (`/login`, `/register`): User login and registration
5. **Become a Host** (`/host`): Information and onboarding for hosts

## Features Implemented

### Frontend
- ✅ Responsive design with Bootstrap 5
- ✅ Custom CSS with Bangladeshi branding
- ✅ Interactive JavaScript components
- ✅ Form validation and user feedback
- ✅ Image optimization and lazy loading

### Backend
- ✅ Flask application structure
- ✅ Route handling and templates
- ✅ Model definitions for core entities
- ✅ Configuration management
- ✅ Error handling

### UI Components
- ✅ Navigation with search integration
- ✅ Property cards with ratings and pricing
- ✅ Filter system for search results
- ✅ Booking form with date selection
- ✅ Host profile and verification badges
- ✅ Review system display

## Development Notes

### CSS Architecture
- Custom properties for consistent theming
- Mobile-first responsive design
- Component-based styling approach
- Utility classes for common patterns

### JavaScript Features
- Event delegation for dynamic content
- Form validation and submission handling
- Interactive UI components (filters, wishlist)
- API integration structure

### Template System
- Jinja2 templating with template inheritance
- Component-based template structure
- SEO-friendly markup
- Accessibility considerations

## Future Enhancements

### Database Integration
- SQLAlchemy ORM setup
- User authentication with Flask-Login
- Property management system
- Booking and payment processing

### Advanced Features
- Real-time messaging system
- Email notifications
- Payment gateway integration
- Administrative dashboard
- Multi-language support (Bengali/English)

### Performance Optimizations
- Image compression and CDN integration
- Caching layer implementation
- Database query optimization
- Asset minification

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Design inspiration from Airbnb
- Bootstrap 5 for responsive components
- Flask framework for backend structure
- Bangladeshi cultural elements and color scheme

---

**Made with ❤️ in Bangladesh for the Bangladeshi hospitality community**
