import os
import uuid
from datetime import datetime, timedelta
from flask_login import current_user, login_required
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.json_store import read_json, write_json
from utils.email_utils import send_email

bp = Blueprint('public', __name__)

@bp.route('/')
def home():
    products = read_json('products.json', [])
    featured = [p for p in products if p.get('featured')][:8]
    return render_template('public/home.html', featured=featured)

@bp.route('/products')
def products_page():
    products = read_json('products.json', [])
    visible = [p for p in products if p.get('visible', True)]
    return render_template('public/products.html', products=visible)

@bp.route('/products/<product_id>')
def product_detail(product_id):
    products = read_json('products.json', [])
    product = next((p for p in products if p.get('id') == product_id and p.get('visible', True)), None)
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('public.products_page'))
    
    # Get all images for the product
    images = [product.get('image')] if product.get('image') else []
    additional_images = product.get('additional_images', [])
    if additional_images:
        images.extend(additional_images)
        
    return render_template('public/product_detail.html', product=product, images=images)


@bp.route('/blog')
def blog_page():
    """List published blog posts with pagination."""
    # Get pagination parameters
    page = int(request.args.get('page', 1))
    per_page = 10
    
    # Get blog posts
    posts = read_json('blog.json', [])
    published = [p for p in posts if p.get('published', True)]
    
    # Sort by publish_at or created_at
    published.sort(
        key=lambda x: x.get('publish_at') or x.get('created_at') or '',
        reverse=True
    )
    
    # Get unique categories
    categories = set()
    for post in published:
        if post.get('categories'):
            categories.update(post['categories'])
    
    # Paginate posts
    start = (page - 1) * per_page
    end = start + per_page
    paginated = published[start:end]
    
    return render_template(
        'public/blog.html',
        posts=paginated,
        categories=sorted(categories),
        page=page,
        pages=(len(published) + per_page - 1) // per_page
    )


@bp.route('/blog/post/<post_id>')
def blog_post(post_id):
    """Display a single blog post."""
    posts = read_json('blog.json', [])
    post = next(
        (p for p in posts 
         if p.get('id') == post_id and p.get('published')),
        None
    )
    
    if not post:
        flash('Post not found', 'error')
        return redirect(url_for('public.blog_page'))
    
    return render_template('public/blog_post.html', post=post)


@bp.route('/order', methods=['GET', 'POST'])
@login_required
def order_form():
    if request.method == 'POST':
        # Process the form data
        data = request.form.to_dict()
        
        # Generate unique order ID and set metadata
        data['id'] = str(uuid.uuid4())
        data['status'] = 'pending'
        data['created_at'] = datetime.now().isoformat()
        data['user_id'] = current_user.id
        data['payment_status'] = 'pending'
        
        # Handle file upload
        if 'reference_image' in request.files:
            file = request.files['reference_image']
            if file and file.filename:
                # Generate secure filename
                ext = os.path.splitext(file.filename)[1]
                filename = f"order_{data['id']}{ext}"
                
                # Ensure uploads directory exists
                os.makedirs('static/uploads/orders', exist_ok=True)
                
                # Save the file
                file_path = os.path.join('static/uploads/orders', filename)
                file.save(file_path)
                data['reference_image'] = f'/static/uploads/orders/{filename}'
        
        # Save to custom_orders.json
        orders = read_json('custom_orders.json', [])
        orders.append(data)
        write_json('custom_orders.json', orders)
        
        # Prepare email content
        ref_img_text = ''
        if 'reference_image' in data:
            base_url = 'http://localhost:5000'
            img_url = f"{base_url}{data['reference_image']}"
            ref_img_text = f"- Reference Image: {img_url}"
            
        subject = f"New Custom Cake Order from {data['name']}"
        body = f"""New custom cake order received:

Personal Information:
- Name: {data['name']}
- Email: {data['email']}
- Phone: {data.get('phone', 'Not provided')}
- Pickup Date: {data['pickup_date']}

Cake Details:
- Size: {data['size']}
- Flavor: {data['flavor']}
- Filling: {data.get('filling', 'None')}
- Frosting: {data['frosting']}

Design Details:
- Message on Cake: {data.get('message', 'None')}
- Design Description: {data['design_details']}
{ref_img_text}

Additional Information:
- Allergies: {data.get('allergies', 'None')}
- Special Instructions: {data.get('special_instructions', 'None')}

View order in admin dashboard: http://localhost:5000/admin/orders"""

        success_msg = 'Order received! We will contact you to confirm details.'
        info_msg = 'Order saved. Our team will review and contact you shortly.'
        
        if send_email(subject, body):
            flash(success_msg, 'success')
        else:
            flash(info_msg, 'info')
            
        return redirect(url_for('public.home'))
    
    # For GET requests, calculate available dates
    min_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    max_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    return render_template(
        'public/order.html',
        min_date=min_date,
        max_date=max_date
    )


@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing their orders."""
    # Get user's orders
    standard_orders = read_json('orders.json', [])
    custom_orders = read_json('custom_orders.json', [])
    
    # Filter orders for current user
    user_standard = [o for o in standard_orders if o.get('user_id') == current_user.id]
    user_custom = [o for o in custom_orders if o.get('user_id') == current_user.id]
    
    # Combine and sort by creation date
    all_orders = []
    for order in user_standard:
        order['type'] = 'standard'
        all_orders.append(order)
    for order in user_custom:
        order['type'] = 'custom'
        all_orders.append(order)
    
    all_orders.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template('public/dashboard.html', orders=all_orders)


@bp.route('/cart')
@login_required
def cart():
    """Shopping cart page."""
    return render_template('public/cart.html')


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page."""
    if request.method == 'POST':
        data = request.form.to_dict()
        subject = f"Contact Form: {data.get('subject', 'General Inquiry')}"
        body = f"""Contact form submission:
        
From: {data['name']} ({data['email']})
Phone: {data.get('phone', 'Not provided')}

Message:
{data['message']}"""
        
        if send_email(subject, body):
            flash('Message sent! We will get back to you soon.', 'success')
        else:
            flash('Could not send message. Please try again later.', 'error')
        
        return redirect(url_for('public.contact'))
    
    store = {
        'name': os.getenv('STORE_NAME', "Annie's Bakery"),
        'address': os.getenv('STORE_ADDRESS', '123 Baker Street'),
        'phone': os.getenv('STORE_PHONE', '(555) 123-4567'),
        'email': os.getenv('STORE_EMAIL', 'hello@example.com'),
        'maps_key': os.getenv('GOOGLE_MAPS_EMBED_KEY', '')
    }
    return render_template('public/contact.html', store=store)
