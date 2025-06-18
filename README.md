# Otithi - Bangladesh Accommodation Platform

## Project Overview

**Otithi** is a Flask-based web application that serves as an accommodation booking platform specifically designed for Bangladesh. The name "Otithi" means "guest" in Bengali, reflecting the platform's focus on hospitality and guest accommodation services. The platform functions similarly to Airbnb, allowing users to browse, search, and manage accommodation listings across Bangladesh.

## Features

### Core Functionality
- **User Authentication System**: Complete registration, login, and logout functionality with secure password hashing
- **Role-Based Access Control**: Support for different user roles (admin, host, guest)
- **Listing Management**: Full CRUD operations for accommodation listings
- **Search & Filter**: Advanced search functionality with location-based filtering and price sorting
- **Image Upload**: Support for listing images with secure file handling
- **Pagination**: Efficient browsing of listings with paginated results

### User Roles
1. **Guests**: Can browse and search listings
2. **Hosts**: Can add, edit, and delete their own listings
3. **Admins**: Complete platform management including user management and oversight

### Admin Features
- **Admin Dashboard**: Comprehensive admin panel for platform management
- **User Management**: View, edit, and delete user accounts
- **Analytics**: Basic statistics including total users, hosts, and listings
- **Search Users**: Admin can search through users by username, email, or role

## Technical Architecture

### Backend Technology Stack
- **Framework**: Flask 2.0.1 (Python web framework)
- **Database**: MySQL with PyMySQL connector
- **ORM**: SQLAlchemy for database operations
- **Authentication**: Flask-Login for session management
- **Forms**: Flask-WTF for form handling and validation
- **Security**: CSRF protection and secure password hashing
- **File Handling**: Werkzeug for secure file uploads
- **Database Migrations**: Flask-Migrate for schema management

### Database Schema
The application uses two primary models:

1. **User Model**:
   - User authentication and profile information
   - Role-based permissions (admin, host, guest)
   - Unique username and email constraints

2. **Listing Model**:
   - Accommodation details (name, location, description)
   - Pricing information
   - Host information and image storage

### Frontend Architecture
- **Template Engine**: Jinja2 templating
- **Styling**: Bootstrap-based responsive design
- **User Interface**: Modern, Airbnb-inspired design
- **Interactive Elements**: Search forms, pagination, and file uploads

## Project Structure

```
Othiti/
├── app/                          # Main application package
│   ├── __init__.py              # Flask app factory and configuration
│   ├── models.py                # Database models (User, Listing)
│   ├── routes.py                # Application routes and view functions
│   ├── forms.py                 # WTForms for user input validation
│   ├── static/                  # Static assets
│   │   ├── css/style.css        # Custom styling
│   │   ├── js/main.js           # JavaScript functionality
│   │   └── images/              # Uploaded listing images
│   └── templates/               # Jinja2 HTML templates
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── run.py                      # Application entry point
├── add_admin.py                # Admin user creation script
└── setup.py                   # Setup configuration
```

## Installation & Setup

### Prerequisites
- Python 3.7+
- MySQL Server
- XAMPP (as indicated by the workspace path)

### Dependencies
Key dependencies include:
- Flask and Flask extensions (SQLAlchemy, Login, WTF, Migrate)
- PyMySQL for MySQL connectivity
- Werkzeug for security utilities
- Email validator for form validation

### Database Configuration
- **Database**: `otithi_db` (MySQL)
- **Connection**: MySQL running on port 3307 (XAMPP configuration)
- **User**: root with no password (development setup)

## Current Status

Based on the git status, the project has been actively developed with recent modifications to:
- Core application files (models, routes, initialization)
- Frontend templates and styling
- Admin dashboard functionality
- User management features

## Future Work & Enhancements

### 1. Booking System
- **Reservation Management**: Implement a complete booking system with date availability
- **Calendar Integration**: Add date picker with availability calendar
- **Booking Confirmation**: Email confirmation and booking reference systems
- **Payment Integration**: Integrate with payment gateways (bKash, Nagad, SSL Commerz)
- **Booking History**: User dashboard showing past and upcoming bookings

### 2. Enhanced Search & Discovery
- **Advanced Filters**: Price range, amenities, property type, guest capacity
- **Map Integration**: Google Maps integration for location-based search
- **Geolocation Services**: Auto-detect user location for nearby listings
- **Recommendation Engine**: AI-powered recommendations based on user preferences
- **Photo Gallery**: Multiple image uploads with image carousel

### 3. Communication Features
- **Messaging System**: Host-guest communication platform
- **Real-time Chat**: WebSocket-based instant messaging
- **Automated Notifications**: Email/SMS notifications for bookings and updates
- **Review System**: Guest reviews and host ratings
- **Q&A Section**: Pre-booking question and answer system

### 4. Advanced User Management
- **User Profiles**: Detailed user profiles with photos and verification
- **Identity Verification**: Document upload and verification system
- **Host Verification**: Enhanced vetting process for hosts
- **Social Login**: Facebook, Google authentication integration
- **Two-Factor Authentication**: Enhanced security for user accounts

### 5. Mobile & API Development
- **REST API**: Complete API for mobile app development
- **Mobile App**: React Native or Flutter mobile application
- **Progressive Web App**: PWA for better mobile experience
- **API Documentation**: Swagger/OpenAPI documentation
- **Rate Limiting**: API rate limiting and authentication

### 6. Business Intelligence & Analytics
- **Advanced Dashboard**: Comprehensive analytics for admins and hosts
- **Revenue Tracking**: Financial reporting and commission management
- **User Behavior Analytics**: Google Analytics integration
- **Performance Metrics**: Booking conversion rates and platform KPIs
- **Data Export**: CSV/Excel export functionality

### 7. Content Management
- **CMS Integration**: Admin content management system
- **Blog System**: Travel guides and local information
- **Multilingual Support**: Bengali and English language support
- **SEO Optimization**: Meta tags, sitemaps, and search optimization
- **Content Moderation**: Automated content filtering and moderation

### 8. Infrastructure & DevOps
- **Docker Containerization**: Docker setup for easy deployment
- **CI/CD Pipeline**: Automated testing and deployment
- **Cloud Deployment**: AWS/DigitalOcean deployment configuration
- **Database Optimization**: Query optimization and caching
- **Load Balancing**: Horizontal scaling capabilities

### 9. Security Enhancements
- **OAuth2 Implementation**: Secure API authentication
- **Data Encryption**: Enhanced data protection
- **Audit Logging**: User action logging and monitoring
- **Security Headers**: HTTPS enforcement and security headers
- **Input Sanitization**: Enhanced XSS and injection protection

### 10. Legal & Compliance
- **Terms of Service**: Legal documentation
- **Privacy Policy**: GDPR-compliant privacy policies
- **Tax Management**: Tax calculation and reporting
- **Regulatory Compliance**: Tourism and hospitality regulations
- **Dispute Resolution**: Conflict resolution system

### 11. Integration & Partnerships
- **Tourism Board Integration**: Bangladesh Tourism Board partnerships
- **Transportation APIs**: Bus/train booking integration
- **Local Services**: Restaurant and activity recommendations
- **Weather API**: Local weather information
- **Currency Exchange**: Multi-currency support

### 12. Performance & Optimization
- **Caching System**: Redis caching implementation
- **CDN Integration**: Content delivery network for images
- **Database Indexing**: Query performance optimization
- **Image Optimization**: Automatic image compression and resizing
- **Lazy Loading**: Frontend performance improvements

## Contributing
The project follows standard Flask development practices with clear separation of concerns between models, views, and templates. The modular structure makes it easy to add new features and maintain existing functionality.

## License
[Specify license information]

---

**Last Updated**: [Current Date]
**Version**: 1.0.0
**Status**: Active Development 