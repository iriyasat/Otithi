"""
WTF Forms for secure authentication with CSRF protection
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from wtforms.widgets import TextArea
from app.models import User


class LoginForm(FlaskForm):
    """Secure login form with CSRF protection"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ])
    remember_me = BooleanField('Remember Me')
    
    def validate_email(self, email):
        """Custom validation for email format"""
        if not email.data or '@' not in email.data:
            raise ValidationError('Please enter a valid email address.')


class RegistrationForm(FlaskForm):
    """Secure registration form with CSRF protection"""
    full_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required.'),
        Length(min=2, max=100, message='Full name must be between 2 and 100 characters.')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
    phone = StringField('Phone Number', validators=[
        Length(max=20, message='Phone number must be less than 20 characters.')
    ])
    bio = TextAreaField('Bio', validators=[
        Length(max=500, message='Bio must be less than 500 characters.')
    ])
    user_type = SelectField('Account Type', choices=[
        ('guest', 'Guest - I want to book accommodations'),
        ('host', 'Host - I want to list my property')
    ], validators=[DataRequired()])
    profile_photo = FileField('Profile Photo')
    terms_agreement = BooleanField('I agree to the Terms of Service and Privacy Policy', validators=[
        DataRequired(message='You must agree to the Terms of Service and Privacy Policy.')
    ])
    
    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.get_by_email(email.data.lower().strip())
        if user:
            raise ValidationError('An account with this email already exists. Please use a different email.')
    
    def validate_phone(self, phone):
        """Validate phone number format"""
        if phone.data:
            # Remove all non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, phone.data))
            if len(digits_only) < 10:
                raise ValidationError('Please enter a valid phone number.')


class PasswordResetRequestForm(FlaskForm):
    """Password reset request form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.')
    ])


class PasswordResetForm(FlaskForm):
    """Password reset form"""
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords must match.')
    ])
