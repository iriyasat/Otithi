# Othiti - Hotel Booking Management System

Othiti is a comprehensive hotel booking management system built with Python Flask, designed to streamline the process of hotel bookings and management. The system provides separate interfaces for guests, hosts, and administrators, each with their specific functionalities.

## Features

### Guest Features
- User registration and authentication
- Browse available properties
- Book accommodations
- View booking history
- Manage personal profile
- View and manage bookings

### Host Features
- Property management
- Booking management
- Guest communication
- Revenue tracking
- Property availability management

### Admin Features
- User management
- Property verification
- System monitoring
- Booking oversight
- Content management

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with MySQL
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login
- **Payment Integration**: Multiple payment gateways support

## Prerequisites

- Python 3.x
- MySQL Server
- XAMPP (for local development)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/iriyasat/Atithi.git
   cd Atithi
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database:
   - Create a MySQL database
   - Update the database configuration in `config.py`

5. Initialize the database:
   ```bash
   flask db upgrade
   python seed.py
   ```

6. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

```
Atithi/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── models.py           # Database models
├── extensions.py       # Flask extensions
├── payment_gateways.py # Payment integration
├── migrations/         # Database migrations
├── static/            # Static files
│   ├── assets/       # Images and other assets
│   ├── css/         # Stylesheets
│   └── js/          # JavaScript files
└── templates/        # HTML templates
    ├── admin/       # Admin templates
    ├── guest/       # Guest templates
    └── host/        # Host templates
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter)

Project Link: [https://github.com/iriyasat/Atithi](https://github.com/iriyasat/Atithi) 