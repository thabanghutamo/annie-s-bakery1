from datetime import datetime, timezone
from pathlib import Path
import os
from typing import Dict, Any, List, Optional, cast, TypedDict
from decimal import Decimal

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from dotenv import set_key, load_dotenv
from utils.decorators import admin_required
from werkzeug.datastructures import FileStorage

from forms import ProductForm
from utils.json_store import read_json, write_json, JsonStore
from utils.files import save_uploaded_file, save_multiple_files


class ProductFormData(TypedDict):
    """Type definition for product form data."""
    title: str
    description: str
    short_description: str
    price: float
    category: str
    visible: bool
    featured: bool
    publish_at: Optional[str]


class Product(TypedDict):
    """Type definition for product data."""
    id: str
    title: str
    description: str
    short_description: str
    price: float
    category: str
    visible: bool
    featured: bool
    created_at: str
    publish_at: Optional[str]
    image: Optional[str]
    additional_images: Optional[list[str]]


class BlogPost(TypedDict):
    """Type definition for blog post data."""
    id: str
    title: str
    short_description: str
    content: str
    cover_image: Optional[str]
    images: Optional[list[str]]
    published: bool
    publish_at: Optional[str]
    created_at: str


def extract_product_form_data(form: ProductForm) -> Product:
    """Extract and validate data from a ProductForm into a Product dict.
    
    Args:
        form: The form to extract data from
        
    Returns:
        Product dict with validated data
    """
    base_data = ProductFormData(
        title=str(form.title.data or ''),
        description=str(form.description.data or ''),
        short_description=str(form.short_description.data or ''),
        price=float(form.price.data or 0.0),
        category=str(form.category.data or ''),
        visible=bool(form.visible.data),
        featured=bool(form.featured.data),
        publish_at=str(form.publish_at.data) if form.publish_at.data else None
    )
    # Convert ProductFormData to Product
    return cast(Product, {
        'id': '',  # Set by caller
        'created_at': current_utc_iso(),
        'image': None,
        'additional_images': [],  # Initialize empty additional images array
        **base_data
    })


def current_utc_iso() -> str:
    """Get current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


# Type aliases for collections
Products = List[Product]
Posts = List[BlogPost]
Orders = List[Dict[str, Any]]
CustomOrders = List[Dict[str, Any]]

class OrderItem(TypedDict):
    """Type definition for an order item."""
    product_id: str
    quantity: int
    price: float
    title: str


class Order(TypedDict):
    """Type definition for standard order data."""
    id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str]
    items: List[OrderItem]
    total: float
    status: str
    payment_status: str
    created_at: str
    updated_at: Optional[str]
    notes: Optional[str]


class CustomOrderDetails(TypedDict):
    """Type definition for custom order details."""
    size: str
    flavor: str
    filling: Optional[str]
    frosting: str
    message: Optional[str]
    design_details: str
    reference_image: Optional[str]
    pickup_date: str
    allergies: Optional[str]
    special_instructions: Optional[str]


class CustomOrder(TypedDict):
    """Type definition for custom cake/pastry order."""
    id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str]
    details: CustomOrderDetails
    status: str
    payment_status: str
    created_at: str
    updated_at: Optional[str]
    notes: Optional[str]


# Valid order statuses
ORDER_STATUSES = [
    'pending',
    'confirmed',
    'in_progress',
    'ready',
    'completed',
    'cancelled'
]

PAYMENT_STATUSES = [
    'pending',
    'paid',
    'refunded',
    'cancelled'
]


bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard showing overview of products, posts, and orders."""
    # Load all data
    products = cast(Products, read_json('products.json', []))
    posts = cast(Posts, read_json('blog.json', []))
    orders = cast(List[Dict[str, Any]], read_json('orders.json', []))
    custom_orders = cast(
        List[Dict[str, Any]],
        read_json('custom_orders.json', [])
    )
    
    # Get recent items (last 5)
    recent_orders = sorted(
        orders + custom_orders,
        key=lambda x: x.get('created_at', ''),  # Default to empty string if no created_at
        reverse=True
    )[:5]
    
    recent_posts = sorted(
        posts,
        key=lambda x: x.get('created_at', ''),  # Use created_at instead of date
        reverse=True
    )[:5]
    
    return render_template(
        'admin/dashboard.html',
        product_count=len(products),
        post_count=len(posts),
        order_count=len(orders),
        custom_order_count=len(custom_orders),
        recent_orders=recent_orders,
        recent_posts=recent_posts
    )


@bp.route('/products')
@admin_required
def products():
    """List all products."""
    products = cast(Products, read_json('products.json', []))
    return render_template('admin/products.html', products=products)


@bp.route('/products/new', methods=['GET', 'POST'])
@admin_required
def products_new():
    """Create a new product."""
    form = ProductForm(request.form)
    if request.method == 'GET':
        return render_template('admin/edit_product.html', form=form)

    if not form.validate():
        flash('Please correct the errors below', 'error')
        return render_template('admin/edit_product.html', form=form)
    
        products = cast(Products, read_json('products.json', []))
        
        # Extract and validate form data
        new_product = extract_product_form_data(form)
        
        # Set the product ID
        new_product['id'] = f"prod-{len(products)+1}"
        
        # Handle main image upload if present
        if form.image.data:
            image_url = save_uploaded_file(
                cast(FileStorage, form.image.data),
                'products'
            )
            if image_url:
                new_product['image'] = image_url
            else:
                flash('Failed to upload main image', 'error')
                return render_template(
                    'admin/edit_product.html',
                    form=form
                )
        
        # Handle additional images
        additional_images = request.files.getlist('additional_images[]')
        if additional_images:
            saved_urls = save_multiple_files(additional_images, 'products')
            if saved_urls:
                new_product['additional_images'] = saved_urls
        
        # Save the new product
        products.append(new_product)
        write_json('products.json', products)
        flash('Product created successfully', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/edit_product.html', form=form)


@bp.route('/products/edit/<product_id>', methods=['GET', 'POST'])
@admin_required
def products_edit(product_id: str):
    """Edit an existing product."""
    products = cast(Products, read_json('products.json', []))
    product = next((p for p in products if p.get('id') == product_id), None)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('admin.products'))
    
    form = ProductForm(request.form if request.method == 'POST' else None)
    if request.method == 'GET':
        # Populate form with product data
        form = ProductForm(data={
            'title': product.get('title', ''),
            'description': product.get('description', ''),
            'short_description': product.get('short_description', ''),
            'price': product.get('price', 0.0),
            'category': product.get('category', ''),
            'visible': product.get('visible', False),
            'featured': product.get('featured', False),
            'publish_at': product.get('publish_at')
        })

    if request.method == 'GET':
        return render_template('admin/edit_product.html', form=form, product=product)
    
    print(f"Form submitted. Files: {request.files}")
    print(f"Form data: {request.form}")
    
    if not form.validate():
        print(f"Form validation errors: {form.errors}")
        flash('Please correct the errors below', 'error')
        return render_template('admin/edit_product.html', form=form, product=product)
    
    # Form validated successfully
        print(f"Processing edit form for product: {product_id}")
        # Get form data with type safety
        product_data = extract_product_form_data(form)
        print(f"Extracted form data: {product_data}")
        
        # Keep existing fields
        product_data['id'] = product_id
        product_data['created_at'] = product.get(
            'created_at', current_utc_iso()
        )
        product_data['image'] = product.get('image')
        product_data['additional_images'] = product.get('additional_images', [])
        
        # Update the product
        product.update(product_data)
        
        # Handle main image upload if new image provided
        if form.image.data:
            print(f"New main image provided: {form.image.data.filename}")
            image_url = save_uploaded_file(form.image.data, 'products')
            print(f"Save result: {image_url}")
            if image_url:
                # Delete old image file if it exists
                if 'image' in product:
                    old_path = Path('static') / product['image'].lstrip('/')
                    try:
                        if old_path.is_file():
                            print(f"Deleting old image: {old_path}")
                            old_path.unlink()
                    except Exception as e:
                        print(f"Error deleting old image: {e}")
                product['image'] = image_url
                print(f"Updated product image to: {image_url}")
            else:
                print("Failed to save main image")
                flash('Failed to upload main image', 'error')
                return render_template(
                    'admin/edit_product.html',
                    form=form,
                    product=product
                )

        # Handle additional images
        additional_images = request.files.getlist('additional_images[]')
        if additional_images:
            # Delete old additional images
            if 'additional_images' in product:
                for old_img in product['additional_images']:
                    try:
                        old_path = Path('static') / old_img.lstrip('/')
                        if old_path.is_file():
                            old_path.unlink()
                    except Exception:
                        pass  # Ignore errors in old file cleanup

            # Save new additional images
            saved_urls = save_multiple_files(additional_images, 'products')
            if saved_urls:
                product['additional_images'] = saved_urls
            else:
                # Keep existing images if upload fails
                product['additional_images'] = product.get('additional_images', [])
                flash('Some additional images failed to upload', 'warning')
                return render_template(
                    'admin/edit_product.html',
                    form=form,
                    product=product
                )
        
        # Save changes
        write_json('products.json', products)
        flash('Product updated successfully', 'success')
        return redirect(url_for('admin.products'))
        
    return render_template(
        'admin/edit_product.html',
        form=form,
        product=product
    )


@bp.route('/products/delete/<product_id>', methods=['POST'])
@admin_required
def products_delete(product_id: str):
    """Delete a product by ID.
    
    Args:
        product_id: The ID of the product to delete
    """
    products = cast(Products, read_json('products.json', []))
    products = [p for p in products if p['id'] != product_id]
    write_json('products.json', products)
    flash('Product deleted successfully', 'success')
    return redirect(url_for('admin.products'))


@bp.route('/blog')
@admin_required
def blog():
    """List all blog posts."""
    posts = cast(Posts, read_json('blog.json', []))
    return render_template('admin/blog.html', posts=posts)


def extract_blog_form_data(
    form_data: Dict[str, str],
    files: Dict[str, FileStorage],
    post_id: Optional[str] = None
) -> BlogPost:
    """Extract and validate blog post data from form.
    
    Args:
        form_data: Form data from request
        files: File data from request
        post_id: Optional post ID for existing posts
        
    Returns:
        Validated blog post data
    """
    post = BlogPost(
        id=post_id or '',  # Set by caller if new post
        title=str(form_data.get('title', '')),
        short_description=str(form_data.get('short_description', '')),
        content=str(form_data.get('content', '')),
        cover_image=None,
        images=None,
        published=form_data.get('published') == 'on',
        publish_at=str(form_data.get('publish_at')) if form_data.get('publish_at') else None,
        created_at=current_utc_iso()
    )
    
    # Handle cover image
    if 'cover_image' in files:
        f = files['cover_image']
        if f.filename:
            image_url = save_uploaded_file(f, 'blog')
            if image_url:
                post['cover_image'] = image_url
    
    # Handle additional images
    blog_images = files.getlist('blog_images[]')
    if blog_images:
        saved_urls = save_multiple_files(blog_images, 'blog')
        if saved_urls:
            post['images'] = saved_urls
    
    return post


@bp.route('/blog/new', methods=['GET', 'POST'])
@admin_required
def blog_new():
    """Create a new blog post."""
    if request.method == 'POST':
        posts = cast(Posts, read_json('blog.json', []))
        post_id = f"post-{len(posts)+1}"
        
        # Extract form data
        post = extract_blog_form_data(
            request.form,
            request.files,
            post_id=post_id
        )
        
        # Save post
        posts.append(post)
        write_json('blog.json', posts)
        flash('Post created successfully', 'success')
        return redirect(url_for('admin.blog'))
        
    return render_template('admin/edit_blog.html')


@bp.route('/blog/edit/<post_id>', methods=['GET', 'POST'])
@admin_required
def blog_edit(post_id: str):
    """Edit an existing blog post.
    
    Args:
        post_id: The ID of the post to edit
    """
    posts = cast(Posts, read_json('blog.json', []))
    post = next((p for p in posts if p['id'] == post_id), None)
    
    if not post:
        flash('Post not found', 'error')
        return redirect(url_for('admin.blog'))
        
    if request.method == 'POST':
        # Get updated post data
        updated_post = extract_blog_form_data(
            request.form,
            request.files,
            post_id=post_id
        )
        
        # Keep original created_at
        updated_post['created_at'] = post.get(
            'created_at', current_utc_iso()
        )
        
        # Update post
        post.update(updated_post)
        
        # Save changes
        write_json('blog.json', posts)
        flash('Post updated successfully', 'success')
        return redirect(url_for('admin.blog'))
        
    return render_template('admin/edit_blog.html', post=post)


class OrderItem(TypedDict):
    """Type definition for an order item."""
    product_id: str
    quantity: int
    price: float
    title: str


class Order(TypedDict):
    """Type definition for standard order data."""
    id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str]
    items: List[OrderItem]
    total: float
    status: str
    payment_status: str
    created_at: str
    updated_at: Optional[str]
    notes: Optional[str]


class CustomOrderDetails(TypedDict):
    """Type definition for custom order details."""
    size: str
    flavor: str
    filling: Optional[str]
    frosting: str
    message: Optional[str]
    design_details: str
    reference_image: Optional[str]
    pickup_date: str
    allergies: Optional[str]
    special_instructions: Optional[str]


class CustomOrder(TypedDict):
    """Type definition for custom cake/pastry order."""
    id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str]
    details: CustomOrderDetails
    status: str
    payment_status: str
    created_at: str
    updated_at: Optional[str]
    notes: Optional[str]


class PaymentSettings(TypedDict):
    """Type definition for payment settings."""
    gateway: str
    api_key: str
    api_secret: str
    webhook: Optional[str]


@bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    """Update payment gateway settings in .env file."""
    env_path = Path('.') / '.env'
    load_dotenv(env_path)
    
    if request.method == 'POST':
        # Extract settings from form
        settings = PaymentSettings(
            gateway=str(request.form.get('gateway', '')),
            api_key=str(request.form.get('api_key', '')),
            api_secret=str(request.form.get('api_secret', '')),
            webhook=str(request.form.get('webhook', '')) or None
        )
        
        # Write to .env
        try:
            str_path = str(env_path)
            for key, env_key in {
                'gateway': 'PAYMENT_GATEWAY',
                'api_key': 'PAYMENT_API_KEY',
                'api_secret': 'PAYMENT_API_SECRET',
                'webhook': 'PAYMENT_WEBHOOK'
            }.items():
                if settings[key] is not None:
                    set_key(str_path, env_key, settings[key])
            flash('Settings saved successfully', 'success')
            
        except Exception as e:
            flash(f'Unable to save settings: {e}', 'error')
            
        return redirect(url_for('admin.settings'))

    # Load current settings
    current = PaymentSettings(
        gateway=str(os.getenv('PAYMENT_GATEWAY', '')),
        api_key=str(os.getenv('PAYMENT_API_KEY', '')),
        api_secret=str(os.getenv('PAYMENT_API_SECRET', '')),
        webhook=str(os.getenv('PAYMENT_WEBHOOK', '')) or None
    )
    
    return render_template('admin/settings.html', current=current)


@bp.route('/blog/delete/<post_id>', methods=['POST'])
@admin_required
def blog_delete(post_id: str):
    """Delete a blog post by ID.
    
    Args:
        post_id: The ID of the post to delete
    """
    posts = cast(Posts, read_json('blog.json', []))
    posts = [p for p in posts if p['id'] != post_id]
    write_json('blog.json', posts)
    flash('Post deleted successfully', 'success')
    return redirect(url_for('admin.blog'))


def generate_csv(orders: List[Dict[str, Any]], custom: bool = False) -> str:
    """Generate CSV data for orders.
    
    Args:
        orders: List of orders to include
        custom: Whether these are custom orders
        
    Returns:
        CSV formatted string
    """
    from io import StringIO
    import csv
    
    output = StringIO()
    writer = csv.writer(output)
    
    if custom:
        # Headers for custom orders
        writer.writerow([
            'Order ID',
            'Customer Name',
            'Email',
            'Phone',
            'Status',
            'Payment',
            'Size',
            'Flavor',
            'Filling',
            'Frosting',
            'Message',
            'Pickup Date',
            'Allergies',
            'Special Instructions',
            'Created',
            'Updated',
            'Notes'
        ])
        # Data rows
        for order in orders:
            writer.writerow([
                order['id'],
                order['customer_name'],
                order['customer_email'],
                order.get('customer_phone', ''),
                order['status'],
                order['payment_status'],
                order['details']['size'],
                order['details']['flavor'],
                order['details'].get('filling', ''),
                order['details']['frosting'],
                order['details'].get('message', ''),
                order['details']['pickup_date'],
                order['details'].get('allergies', ''),
                order['details'].get('special_instructions', ''),
                order['created_at'],
                order.get('updated_at', ''),
                order.get('notes', '')
            ])
    else:
        # Headers for standard orders
        writer.writerow([
            'Order ID',
            'Customer Name',
            'Email',
            'Phone',
            'Status',
            'Payment',
            'Items',
            'Total',
            'Created',
            'Updated',
            'Notes'
        ])
        # Data rows
        for order in orders:
            items = '; '.join(
                f"{item['title']} ({item['quantity']}x @ {item['price']})"
                for item in order['items']
            )
            writer.writerow([
                order['id'],
                order['customer_name'],
                order['customer_email'],
                order.get('customer_phone', ''),
                order['status'],
                order['payment_status'],
                items,
                order['total'],
                order['created_at'],
                order.get('updated_at', ''),
                order.get('notes', '')
            ])
    
    return output.getvalue()


@bp.route('/orders', methods=['GET', 'POST'])
@admin_required
def orders():
    """List all orders with filtering and sorting."""
    # Get filter parameters
    status = request.args.get('status')
    payment = request.args.get('payment')
    search = request.args.get('q', '').lower()
    order_type = request.args.get('type', 'all')
    
    # Handle batch actions
    is_batch = (
        request.method == 'POST' 
        and request.form.get('action') == 'batch_update'
    )
    if is_batch:
        order_ids = request.form.getlist('order_ids[]')
        new_status = request.form.get('new_status')
        new_payment_status = request.form.get('new_payment_status')
        
        if order_ids and (new_status or new_payment_status):
            standard = cast(Orders, read_json('orders.json', []))
            custom = cast(CustomOrders, read_json('custom_orders.json', []))
            
            # Update matching orders
            updated_count = 0
            current_time = current_utc_iso()
            
            for orders_list in [standard, custom]:
                for order in orders_list:
                    if order['id'] in order_ids:
                        if new_status:
                            order['status'] = new_status
                        if new_payment_status:
                            order['payment_status'] = new_payment_status
                        order['updated_at'] = current_time
                        updated_count += 1
            
            # Save changes
            write_json('orders.json', standard)
            write_json('custom_orders.json', custom)
            
            flash(f'Updated {updated_count} orders successfully', 'success')
            return redirect(url_for('admin.orders'))
    
    # Load orders and properly validate structure
    raw_standard = read_json('orders.json', [])
    raw_custom = read_json('custom_orders.json', [])
    
    # Convert standard orders to properly structured Order objects
    standard = []
    for o in raw_standard:
        # Ensure items is a list that can be iterated
        items = o.get('items', []) if isinstance(o.get('items'), list) else []
        order = {
            'id': str(o.get('id', '')),
            'customer_name': str(o.get('customer_name', '')),
            'customer_email': str(o.get('customer_email', '')),
            'customer_phone': o.get('customer_phone'),
            'items': items,  # Now guaranteed to be a list
            'total': float(o.get('total', 0.0)),
            'status': str(o.get('status', 'pending')),
            'payment_status': str(o.get('payment_status', 'pending')),
            'created_at': str(o.get('created_at', current_utc_iso())),
            'updated_at': o.get('updated_at'),
            'notes': o.get('notes')
        }
        standard.append(order)
    
    # Convert custom orders while preserving their flat structure
    custom = [{
        'id': str(o.get('id', '')),
        'name': str(o.get('name', '')),
        'email': str(o.get('email', '')),
        'phone': o.get('phone'),
        'size': str(o.get('size', '')),
        'flavor': str(o.get('flavor', '')),
        'notes': o.get('notes'),
        'status': str(o.get('status', 'pending')),
        'payment_status': str(o.get('payment_status', 'pending')),
        'created_at': str(o.get('created_at', current_utc_iso())),
        'updated_at': o.get('updated_at')
    } for o in raw_custom]
    
    # Apply filters
    if status:
        standard = [o for o in standard if o['status'] == status]
        custom = [o for o in custom if o['status'] == status]
    
    if payment:
        standard = [o for o in standard if o['payment_status'] == payment]
        custom = [o for o in custom if o['payment_status'] == payment]
    
    if search:
        standard = [
            o for o in standard
            if search in o['customer_name'].lower()
            or search in o['customer_email'].lower()
            or search in o['id'].lower()
        ]
        custom = [
            o for o in custom
            if search in o['customer_name'].lower()
            or search in o['customer_email'].lower()
            or search in o['id'].lower()
        ]
    
    if order_type == 'standard':
        custom = []
    elif order_type == 'custom':
        standard = []
    
    # Sort by created_at desc (default to empty string if not present)
    standard.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    custom.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Handle CSV export
    if request.args.get('format') == 'csv':
        from flask import Response
        if order_type == 'custom':
            csv_data = generate_csv(custom, custom=True)
            filename = 'custom_orders.csv'
        elif order_type == 'standard':
            csv_data = generate_csv(standard)
            filename = 'orders.csv'
        else:
            # Export both
            csv_data = (
                generate_csv(standard)
                + '\n\nCustom Orders:\n'
                + generate_csv(custom, custom=True)
            )
            filename = 'all_orders.csv'
            
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment;filename={filename}'}
        )
    
    return render_template(
        'admin/orders.html',
        standard_orders=standard,
        custom_orders=custom,
        statuses=ORDER_STATUSES,
        payment_statuses=PAYMENT_STATUSES,
        current_status=status,
        current_payment=payment,
        current_search=search,
        current_type=order_type
    )


@bp.route('/orders/<order_id>', methods=['GET', 'POST'])
@admin_required
def order_detail(order_id: str):
    """Show and update order details."""
    print(f"\nAccessing order details for order ID: {order_id}")
    
    # Load raw data
    standard_orders = read_json('orders.json', [])
    custom_orders = read_json('custom_orders.json', [])
    
    print("Loaded orders:")
    print(f"Standard orders: {len(standard_orders)}")
    print(f"Custom orders: {len(custom_orders)}")
    print("Standard order IDs:", [o.get('id') for o in standard_orders])
    print("Custom order IDs:", [o.get('id') for o in custom_orders])

    # First check custom orders
    custom_order = next((o for o in custom_orders if str(o.get('id', '')) == order_id), None)
    if custom_order:
        raw_order = custom_order
        is_custom = True
    else:
        # Then check standard orders
        standard_order = next((o for o in standard_orders if str(o.get('id', '')) == order_id), None)
        if standard_order:
            raw_order = standard_order
            is_custom = False
        else:
            raw_order = None
            is_custom = False
    
    if not raw_order:
        flash('Order not found', 'error')
        return redirect(url_for('admin.orders'))    # Convert order to proper structure
    if is_custom:
        order = {
            'id': str(raw_order.get('id', '')),
            'name': str(raw_order.get('name', '')),
            'email': str(raw_order.get('email', '')),
            'phone': raw_order.get('phone'),
            'size': str(raw_order.get('size', '')),
            'flavor': str(raw_order.get('flavor', '')),
            'filling': raw_order.get('filling'),
            'frosting': str(raw_order.get('frosting', '')),
            'message': raw_order.get('message'),
            'pickup_date': str(raw_order.get('pickup_date', '')),
            'design_details': str(raw_order.get('design_details', '')),
            'reference_image': raw_order.get('reference_image'),
            'allergies': raw_order.get('allergies'),
            'special_instructions': raw_order.get('special_instructions'),
            'notes': raw_order.get('notes'),
            'status': str(raw_order.get('status', 'pending')),
            'payment_status': str(raw_order.get('payment_status', 'pending')),
            'created_at': str(raw_order.get('created_at', '')),
            'updated_at': raw_order.get('updated_at')
        }
    else:
        # Convert items to proper structure
        items_list = raw_order.get('items', []) if isinstance(raw_order.get('items'), list) else []
        processed_items = []
        for item in items_list:
            processed_items.append({
                'product_id': str(item.get('id', '')),
                'title': str(item.get('title', '')),
                'quantity': int(item.get('quantity', 0)),
                'price': float(item.get('price', 0.0))
            })
            
        order = {
            'id': str(raw_order.get('id', '')),
            'customer_name': str(raw_order.get('customer_name', '')),
            'customer_email': str(raw_order.get('customer_email', '')),
            'customer_phone': raw_order.get('customer_phone'),
            'items': processed_items,
            'total': float(raw_order.get('total', 0.0)),
            'status': str(raw_order.get('status', 'pending')),
            'payment_status': str(raw_order.get('payment_status', 'pending')),
            'created_at': str(raw_order.get('created_at', '')),
            'updated_at': raw_order.get('updated_at'),
            'notes': raw_order.get('notes')
        }
    
    if request.method == 'POST':
        try:
            print(f"Received POST request for order {order_id}")
            # Get the submitted form data
            new_status = request.form.get('status')
            new_payment_status = request.form.get('payment_status')
            notes = request.form.get('notes')
            current_time = current_utc_iso()
            
            print(f"New status: {new_status}")
            print(f"New payment status: {new_payment_status}")
            print(f"Is custom order: {is_custom}")

            # Update the order in the correct file
            if is_custom:
                # Update custom order
                custom_orders = read_json('custom_orders.json', [])
                print("Updating custom order")
                
                for order in custom_orders:
                    if str(order.get('id', '')) == str(order_id):
                        print(f"Found custom order {order_id}")
                        print("Before update:", order)
                        order['status'] = new_status
                        order['payment_status'] = new_payment_status
                        order['updated_at'] = current_time
                        if notes:
                            order['notes'] = notes
                        print("After update:", order)
                        write_json('custom_orders.json', custom_orders)
                        flash('Order updated successfully', 'success')
                        break
            else:
                # Update standard order
                standard_orders = read_json('orders.json', [])
                print("Updating standard order")
                
                for order in standard_orders:
                    if str(order.get('id', '')) == str(order_id):
                        print(f"Found standard order {order_id}")
                        print("Before update:", order)
                        order['status'] = new_status
                        order['payment_status'] = new_payment_status
                        order['updated_at'] = current_time
                        if notes:
                            order['notes'] = notes
                        print("After update:", order)
                        write_json('orders.json', standard_orders)
                        flash('Order updated successfully', 'success')
                        break

            if updated:
                print(f"Successfully updated order {order_id}")
                flash('Order updated successfully', 'success')
            else:
                print(f"Order {order_id} not found in {'custom' if is_custom else 'standard'} orders")
                flash('Order not found', 'error')

            try:
                if hasattr(current_app, 'cache'):
                    current_app.cache.delete('orders')
                    current_app.cache.delete('custom_orders')
            except Exception as cache_error:
                print(f"Cache clear error (non-critical): {str(cache_error)}")

            return redirect(url_for('admin.order_detail', order_id=order_id))
            
        except Exception as e:
            print(f"Error updating order: {str(e)}")
            flash(f'Error updating order: {str(e)}', 'error')
            return redirect(url_for('admin.order_detail', order_id=order_id))
            
        flash('Order updated successfully', 'success')
        return redirect(url_for('admin.order_detail', order_id=order_id))
    
    # Load related product info for standard orders
    products = {}
    if not is_custom:
        all_products = cast(Products, read_json('products.json', []))
        products = {p['id']: p for p in all_products}
    
    return render_template(
        'admin/order_detail.html',
        order=order,
        is_custom=is_custom,
        products=products,
        statuses=ORDER_STATUSES,
        payment_statuses=PAYMENT_STATUSES
    )
