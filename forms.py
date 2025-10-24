"""Form classes for admin and public forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, FileField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, NumberRange
from flask_wtf.file import FileAllowed

class ProductForm(FlaskForm):
    """Form for creating/editing products."""
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    short_description = TextAreaField('Short Description', validators=[Optional()])
    price = FloatField('Price', validators=[
        DataRequired(),
        NumberRange(min=0, message='Price cannot be negative')
    ])
    category = StringField('Category', validators=[DataRequired()])
    image = FileField('Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    visible = BooleanField('Visible on store')
    featured = BooleanField('Featured on home')
    publish_at = StringField('Publish At', validators=[Optional()])

class BlogPostForm(FlaskForm):
    """Form for creating/editing blog posts."""
    title = StringField('Title', validators=[DataRequired()])
    short_description = TextAreaField('Short Description', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    cover_image = FileField('Cover Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    published = BooleanField('Published')
    publish_at = StringField('Publish At', validators=[Optional()])

class CustomOrderForm(FlaskForm):
    """Form for custom cake/pastry orders."""
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    size = StringField('Size', validators=[DataRequired()])
    flavor = StringField('Flavor', validators=[DataRequired()])
    filling = StringField('Filling', validators=[Optional()])
    frosting = StringField('Frosting', validators=[DataRequired()])
    message = TextAreaField('Message on Cake', validators=[Optional()])
    design_details = TextAreaField('Design Details', validators=[DataRequired()])
    reference_image = FileField('Reference Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    pickup_date = StringField('Pickup Date', validators=[DataRequired()])
    allergies = TextAreaField('Allergies/Dietary Restrictions', validators=[Optional()])
    special_instructions = TextAreaField('Special Instructions', validators=[Optional()])

class ContactForm(FlaskForm):
    """Contact form for public inquiries."""
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

class PaymentSettingsForm(FlaskForm):
    """Form for admin payment gateway settings."""
    gateway = StringField('Payment Gateway', validators=[DataRequired()])
    api_key = StringField('API Key', validators=[DataRequired()])
    api_secret = StringField('API Secret', validators=[DataRequired()])
    webhook = StringField('Webhook URL', validators=[Optional()])