"""Form classes for admin and public forms."""
from wtforms import Form, StringField, TextAreaField, FloatField, FileField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, ValidationError
import os

def validate_image(form, field):
    """Custom validator for image files."""
    if field.data:
        filename = field.data.filename
        ext = os.path.splitext(filename)[1][1:].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            raise ValidationError('File must be an image (jpg, jpeg, png, gif, webp)')

class BaseForm(Form):
    """Base form class with CSRF protection."""
    def __init__(self, formdata=None, obj=None, prefix='', data=None, **kwargs):
        """Initialize form with improved data handling."""
        if formdata is not None and not isinstance(formdata, (dict, list, tuple)):
            formdata = dict(formdata)
        super().__init__(formdata=formdata, obj=obj, prefix=prefix, data=data, **kwargs)

class ProductForm(BaseForm):
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
        validate_image
    ])
    visible = BooleanField('Visible on store')
    featured = BooleanField('Featured on home')
    publish_at = StringField('Publish At', validators=[Optional()])

class BlogPostForm(BaseForm):
    """Form for creating/editing blog posts."""
    title = StringField('Title', validators=[DataRequired()])
    short_description = TextAreaField('Short Description', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    cover_image = FileField('Cover Image', validators=[
        Optional(),
        validate_image
    ])
    published = BooleanField('Published')
    publish_at = StringField('Publish At', validators=[Optional()])

class CustomOrderForm(BaseForm):
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
        validate_image
    ])
    pickup_date = StringField('Pickup Date', validators=[DataRequired()])
    allergies = TextAreaField('Allergies/Dietary Restrictions', validators=[Optional()])
    special_instructions = TextAreaField('Special Instructions', validators=[Optional()])

class ContactForm(BaseForm):
    """Contact form for public inquiries."""
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

class PaymentSettingsForm(BaseForm):
    """Form for admin payment gateway settings."""
    gateway = StringField('Payment Gateway', validators=[DataRequired()])
    api_key = StringField('API Key', validators=[DataRequired()])
    api_secret = StringField('API Secret', validators=[DataRequired()])
    webhook = StringField('Webhook URL', validators=[Optional()])