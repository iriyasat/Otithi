from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

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