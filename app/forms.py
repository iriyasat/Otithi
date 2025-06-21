from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, PasswordField, SubmitField, SelectField, IntegerField, DateField, BooleanField, FloatField
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo, Optional
from flask_wtf.file import FileField, FileAllowed
from datetime import date, timedelta

class RegisterForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Register As', choices=[
        ('guest', 'Guest'),
        ('host', 'Host')
    ], validators=[DataRequired()])
    phone = StringField('Phone Number (Optional)', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ListingForm(FlaskForm):
    """Form for creating and editing listings"""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=120, message='Title must be between 5 and 120 characters')
    ])
    location = StringField('Location', validators=[
        DataRequired(),
        Length(min=3, max=120, message='Location must be between 3 and 120 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=20, max=1000, message='Description must be between 20 and 1000 characters')
    ])
    price_per_night = FloatField('Price per Night (৳)', validators=[
        DataRequired(),
        NumberRange(min=100, max=50000, message='Price must be between 100 and 50000')
    ])
    guest_capacity = IntegerField('Guest Capacity', validators=[
        DataRequired(),
        NumberRange(min=1, max=20, message='Guest capacity must be between 1 and 20')
    ])
    bedrooms = IntegerField('Number of Bedrooms', validators=[
        DataRequired(),
        NumberRange(min=1, max=10, message='Bedrooms must be between 1 and 10')
    ])
    bathrooms = IntegerField('Number of Bathrooms', validators=[
        DataRequired(),
        NumberRange(min=1, max=10, message='Bathrooms must be between 1 and 10')
    ])
    house_rules = TextAreaField('House Rules', validators=[Length(max=500)])
    image = FileField('Listing Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'JPG and PNG images only!')])
    submit = SubmitField('Save Listing')

class BookingForm(FlaskForm):
    """Form for creating bookings"""
    check_in_date = StringField('Check-in Date', validators=[DataRequired()])
    check_out_date = StringField('Check-out Date', validators=[DataRequired()])
    guest_count = IntegerField('Number of Guests', validators=[
        DataRequired(),
        NumberRange(min=1, max=20, message='Guest count must be between 1 and 20')
    ])
    special_requests = TextAreaField('Special Requests', validators=[Length(max=500)])
    submit = SubmitField('Book Now')

    def validate_check_in_date(self, field):
        if field.data < date.today():
            raise ValueError('Check-in date cannot be in the past')

    def validate_check_out_date(self, field):
        if field.data <= self.check_in_date.data:
            raise ValueError('Check-out date must be after check-in date')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(5, '5 - Excellent'), (4, '4 - Very Good'), (3, '3 - Good'), (2, '2 - Fair'), (1, '1 - Poor')], coerce=int, validators=[DataRequired()])
    comment = TextAreaField('Review Comment', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit Review')

class MessageForm(FlaskForm):
    """Form for sending messages"""
    content = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=1, max=1000, message='Message must be between 1 and 1000 characters')
    ])
    submit = SubmitField('Send Message')

class SearchForm(FlaskForm):
    """Form for searching listings"""
    search = StringField('Search', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])
    min_price = DecimalField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = DecimalField('Max Price', validators=[Optional(), NumberRange(min=0)])
    guests = IntegerField('Guests', validators=[Optional(), NumberRange(min=1)])
    check_in = DateField('Check-in', validators=[Optional()])
    check_out = DateField('Check-out', validators=[Optional()])
    submit = SubmitField('Search')

class AdminListingApprovalForm(FlaskForm):
    """Form for admin to approve/reject listings"""
    status = SelectField('Status', choices=[
        ('approved', 'Approve'),
        ('rejected', 'Reject'),
        ('inactive', 'Mark Inactive')
    ], validators=[DataRequired()])
    admin_notes = TextAreaField('Admin Notes (Optional)', validators=[Optional()])
    submit = SubmitField('Update Status')

class UserProfileForm(FlaskForm):
    """Form for updating user profile"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    profile_image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'JPG and PNG images only!')])
    submit = SubmitField('Update Profile') 