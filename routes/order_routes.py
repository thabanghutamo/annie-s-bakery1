import csv
import uuid
from datetime import datetime
from io import StringIO
from typing import TypedDict, List, Optional

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, jsonify, make_response
)
from flask_login import login_required
from utils.json_store import JsonStore
from utils.payment import create_payment_session, PaymentError
from utils.email_utils import send_email


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
    notes: Optional[List[str]]
import csv
import uuid
from io import StringIO

orders_bp = Blueprint('orders', __name__)

# Initialize JSON stores
orders_store = JsonStore('data/orders.json')
custom_orders_store = JsonStore('data/custom_orders.json')

@orders_bp.route('/admin/orders')
@login_required
def admin_orders():
    """Display all orders in admin panel"""
    orders = orders_store.get_all()
    custom_orders = custom_orders_store.get_all()
    
    # Sort orders by date descending
    orders = sorted(orders, key=lambda x: x.get('date', ''), reverse=True)
    custom_orders = sorted(custom_orders, key=lambda x: x.get('date', ''), reverse=True)
    
    return render_template('admin/orders.html', orders=orders, custom_orders=custom_orders)

@orders_bp.route('/admin/orders/<order_id>/status', methods=['POST'])
@login_required
def update_order_status(order_id):
    """Update order status"""
    status = request.form.get('status')
    if not status:
        flash('Status is required', 'error')
        return redirect(url_for('orders.admin_orders'))
    
    # Try updating in regular orders first
    order = orders_store.get_by_id(order_id)
    store = orders_store
    
    # If not found, try custom orders
    if not order:
        order = custom_orders_store.get_by_id(order_id)
        store = custom_orders_store
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('orders.admin_orders'))
    
    # Update status
    order['status'] = status
    order['updated_at'] = datetime.now().isoformat()
    store.update(order_id, order)
    
    flash('Order status updated successfully', 'success')
    return redirect(url_for('orders.admin_orders'))

@orders_bp.route('/admin/orders/note', methods=['POST'])
@login_required
def add_order_note():
    """Add a note to an order"""
    order_id = request.form.get('order_id')
    note = request.form.get('note')
    
    if not all([order_id, note]):
        flash('Order ID and note are required', 'error')
        return redirect(url_for('orders.admin_orders'))
    
    # Try finding in regular orders first
    order = orders_store.get_by_id(order_id)
    store = orders_store
    
    # If not found, try custom orders
    if not order:
        order = custom_orders_store.get_by_id(order_id)
        store = custom_orders_store
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('orders.admin_orders'))
    
    # Initialize notes list if doesn't exist
    if 'notes' not in order:
        order['notes'] = []
    
    # Add new note
    order['notes'].append({
        'text': note,
        'date': datetime.now().isoformat(),
        'by': 'admin'  # You can update this to use actual admin user info
    })
    
    store.update(order_id, order)
    flash('Note added successfully', 'success')
    return redirect(url_for('orders.admin_orders'))

@orders_bp.route('/cart/checkout', methods=['POST'])
def checkout():
    """Create a checkout session for cart items."""
    try:
        # Get cart data
        data = request.get_json()
        if not data or 'items' not in data:
            return jsonify({'error': 'Invalid cart data'}), 400

        # Generate order ID
        order_id = f"ord-{uuid.uuid4().hex[:8]}"
        
        # Create payment session
        session = create_payment_session(
            order_id=order_id,
            items=data['items'],
            total=data['total'],
            success_url=url_for(
                'orders.success',
                order_id=order_id,
                _external=True
            ),
            cancel_url=url_for(
                'orders.cancel',
                order_id=order_id,
                _external=True
            )
        )
        
        # Create order
        order = {
            'id': order_id,
            'customer_name': data.get('customer', {}).get('name', ''),
            'customer_email': data.get('customer', {}).get('email', ''),
            'customer_phone': data.get('customer', {}).get('phone', ''),
            'items': data['items'],
            'total': data['total'],
            'status': 'pending',
            'payment_status': 'pending',
            'created_at': datetime.now().isoformat(),
            'session_id': session.id
        }
        
        # Save order
        orders = orders_store.get_all()
        orders.append(order)
        orders_store.save_all(orders)
        
        return jsonify({
            'success': True,
            'checkoutUrl': session.url
        })
        
    except PaymentError as e:
        return jsonify({
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"Checkout error: {e}")
        return jsonify({
            'error': 'Could not process checkout'
        }), 500


@orders_bp.route('/cart/success/<order_id>')
def success(order_id: str):
    """Handle successful payment."""
    order = orders_store.get_by_id(order_id)
    
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('public.home'))
    
    # Update order status
    order['status'] = 'confirmed'
    order['payment_status'] = 'paid'
    order['updated_at'] = datetime.now().isoformat()
    orders_store.update(order_id, order)
    
    # Send confirmation email
    items_text = '\n'.join(
        f"- {item['quantity']}x {item['title']} (R{item['price']})"
        for item in order['items']
    )
    
    subject = f"Order Confirmation - {order_id}"
    body = f"""Thank you for your order!

Order Details:
{items_text}

Total: R{order['total']:.2f}

You can view your order status here: {url_for(
    'orders.order_status',
    order_id=order_id,
    _external=True
)}

Thank you for choosing Annie's Bakery!"""

    try:
        send_email(
            subject,
            body,
            to=order.get('customer_email')
        )
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")
    
    return render_template(
        'public/order_success.html',
        order=order
    )


@orders_bp.route('/cart/cancel/<order_id>')
def cancel(order_id: str):
    """Handle cancelled/failed payment."""
    order = orders_store.get_by_id(order_id)
    
    if order:
        order['status'] = 'cancelled'
        order['payment_status'] = 'cancelled'
        order['updated_at'] = datetime.now().isoformat()
        orders_store.update(order_id, order)
    
    flash('Your order was cancelled. Please try again.', 'info')
    return redirect(url_for('public.products_page'))


@orders_bp.route('/order/status/<order_id>')
def order_status(order_id: str):
    """Check order status."""
    # Try standard orders first
    order = orders_store.get_by_id(order_id)
    
    if not order:
        # Check custom orders
        order = custom_orders_store.get_by_id(order_id)
        
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('public.home'))
        
    return render_template(
        'public/order_status.html',
        order=order,
        is_custom='custom-' in order_id
    )


@orders_bp.route('/admin/orders/export')
@login_required
def export_orders():
    """Export orders as CSV"""
    # Get all orders
    regular_orders = orders_store.get_all()
    custom_orders = custom_orders_store.get_all()
    
    # Create CSV file in memory
    si = StringIO()
    cw = csv.writer(si)
    
    # Write headers
    cw.writerow(['Order ID', 'Type', 'Date', 'Customer Name', 'Email', 'Status', 'Total/Details'])
    
    # Write regular orders
    for order in regular_orders:
        cw.writerow([
            order.get('id'),
            'Regular',
            order.get('date'),
            order.get('customer_name'),
            order.get('email'),
            order.get('status'),
            f"R{order.get('total', 0):.2f}"
        ])
    
    # Write custom orders
    for order in custom_orders:
        cw.writerow([
            order.get('id'),
            'Custom',
            order.get('date'),
            order.get('name'),
            order.get('email'),
            order.get('status'),
            f"{order.get('size')} - {order.get('flavor')}"
        ])
    
    # Create the response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=orders_export.csv"
    output.headers["Content-type"] = "text/csv"
    return output