# অ. Otithi - Experience Bangladeshi Hospitality

A Flask-based home-sharing platform connecting guests and hosts with authentic Bangladeshi hospitality.

## 🚀 Features

- **User Authentication**: Registration and login with Flask-Login
- **Listing Management**: Create, edit, and delete property listings
- **Image Upload**: Support for listing images with automatic file management
- **Search & Filter**: Search listings by title or location
- **Pagination**: Browse listings with pagination
- **User Roles**: Admin and regular user roles
- **Responsive Design**: Modern, mobile-friendly UI

## 📋 Requirements

- Python 3.8+
- MySQL 5.7+
- XAMPP (for local development)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Othiti
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Using the Initialization Script
```bash
python init_db.py
```

#### Option B: Manual Setup with Flask-Migrate
```bash
# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 5. Start the Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 🗄️ Database Schema

### User Model
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `role`: User role ('user' or 'admin')
- `created_at`: Account creation timestamp

### Listing Model
- `id`: Primary key
- `title`: Listing title
- `location`: Property location
- `description`: Property description
- `price`: Price per night
- `image_filename`: Optional uploaded image filename
- `user_id`: Foreign key to User (listing owner)
- `created_at`: Listing creation timestamp
- `updated_at`: Last update timestamp

## 👤 Default Admin Account

After running the initialization script, you can log in with:
- **Username**: `admin`
- **Password**: `admin123`

## 📁 Project Structure

```
Othiti/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── forms.py             # WTForms definitions
│   ├── routes.py            # Application routes
│   ├── static/
│   │   ├── css/             # Stylesheets
│   │   ├── js/              # JavaScript files
│   │   ├── images/          # Static images
│   │   └── uploads/         # User uploaded images
│   └── templates/           # Jinja2 templates
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── run.py                 # Application entry point
├── init_db.py             # Database initialization script
└── README.md              # This file
```

## 🔧 Configuration

The application uses the following configuration:

- **Database**: MySQL via XAMPP (localhost:3307)
- **Database Name**: `otithi_db`
- **Upload Folder**: `app/static/uploads/`
- **Secret Key**: Auto-generated secure key

## 🎯 Key Features Explained

### User Authentication
- Secure password hashing with Werkzeug
- Session management with Flask-Login
- CSRF protection with Flask-WTF

### Listing Management
- CRUD operations for listings
- Automatic user assignment as listing owner
- Image upload with unique filename generation
- Permission-based editing (owners and admins only)

### Search & Pagination
- Full-text search on title and location
- Price-based sorting (ascending/descending)
- Pagination with 6 listings per page

### Image Handling
- Automatic file upload to `static/uploads/`
- Unique filename generation to prevent conflicts
- Default SVG placeholder for listings without images
- Automatic cleanup of old images when updated

## 🚨 Security Features

- CSRF protection on all forms
- Secure password hashing
- Input validation with WTForms
- File upload restrictions (JPG, PNG only)
- User permission checks for listing operations

## 🐛 Troubleshooting

### Database Connection Issues
1. Ensure XAMPP MySQL service is running
2. Check database credentials in `app/__init__.py`
3. Verify database `otithi_db` exists

### Image Upload Issues
1. Ensure `app/static/uploads/` directory exists
2. Check file permissions on upload directory
3. Verify image file format (JPG, PNG only)

### Migration Issues
1. Delete `migrations/` folder if corrupted
2. Run `flask db init` to reinitialize
3. Create new migration with `flask db migrate`

## 📝 Development Notes

- The app uses Flask-Migrate for database versioning
- All user inputs are validated with WTForms
- Images are stored with UUID-based filenames
- The app includes comprehensive error handling
- Templates use Bootstrap 5 for responsive design

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**অ. Otithi** - Experience authentic Bangladeshi hospitality! 🇧🇩 