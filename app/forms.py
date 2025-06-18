from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, PasswordField, SubmitField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo, ValidationError, Optional
from flask_wtf.file import FileField, FileAllowed
from .models import User

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    account_type = SelectField('Account Type', choices=[('guest', 'Guest'), ('host', 'Host')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different username.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists. Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ListingForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(),
        Length(min=3, max=120, message='Name must be between 3 and 120 characters')
    ])
    location = StringField('Location', validators=[
        DataRequired(),
        Length(min=3, max=120, message='Location must be between 3 and 120 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, message='Description must be at least 10 characters')
    ])
    price_per_night = DecimalField('Price per Night (৳)', validators=[
        DataRequired(),
        NumberRange(min=0, message='Price must be positive')
    ])
    host_name = StringField('Host Name', validators=[
        DataRequired(),
        Length(min=2, max=120, message='Host name must be between 2 and 120 characters')
    ])
    image = FileField('Listing Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'JPG and PNG images only!')])

class BookingForm(FlaskForm):
    check_in = DateField('Check-in Date', validators=[DataRequired()])
    check_out = DateField('Check-out Date', validators=[DataRequired()])
    submit = SubmitField('Request Booking')

class ReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators=[
        DataRequired(message='Please select a rating'),
        NumberRange(min=1, max=5, message='Rating must be between 1 and 5 stars')
    ])
    comment = TextAreaField('Comment', validators=[
        Length(max=500, message='Comment must be less than 500 characters')
    ])
    submit = SubmitField('Submit Review')

class ProfileSettingsForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    profile_picture = FileField('Upload Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')
    ])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        Optional(), EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Profile')
    
    def validate_new_password(self, field):
        """Validate that if current password is provided, new password is also required"""
        if self.current_password.data and self.current_password.data.strip():
            if not field.data or not field.data.strip():
                raise ValidationError('New password is required when current password is provided.')
    
    def validate_current_password(self, field):
        """Validate that if new password is provided, current password is also required"""
        if self.new_password.data and self.new_password.data.strip():
            if not field.data or not field.data.strip():
                raise ValidationError('Current password is required when changing password.')

class EditUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField('Role', choices=[('guest', 'Guest'), ('host', 'Host')], validators=[DataRequired()])
    submit = SubmitField('Save Changes')
    
    def __init__(self, original_email=None, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_email = original_email
    
    def validate_email(self, email):
        """Check if email already exists (excluding current user)"""
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already exists. Please use a different email address.') 