"""Tests for public routes."""
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app import create_app
from utils.json_store import write_json


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_products():
    """Create sample products data."""
    products = [
        {
            'id': 'prod-1',
            'title': 'Test Cake',
            'description': 'A test cake',
            'short_description': 'Test cake',
            'price': 29.99,
            'category': 'cakes',
            'visible': True,
            'featured': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 'prod-2',
            'title': 'Hidden Cake',
            'description': 'A hidden cake',
            'short_description': 'Hidden cake',
            'price': 39.99,
            'category': 'cakes',
            'visible': False,
            'featured': False,
            'created_at': datetime.now().isoformat()
        }
    ]
    write_json('products.json', products)
    return products


@pytest.fixture
def sample_posts():
    """Create sample blog posts data."""
    posts = [
        {
            'id': 'post-1',
            'title': 'Test Post',
            'short_description': 'A test post',
            'content': 'Test content',
            'published': True,
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 'post-2',
            'title': 'Draft Post',
            'short_description': 'A draft post',
            'content': 'Draft content',
            'published': False,
            'created_at': datetime.now().isoformat()
        }
    ]
    write_json('blog.json', posts)
    return posts


def test_home_page(client, sample_products):
    """Test home page shows featured products."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Test Cake' in response.data
    assert b'Hidden Cake' not in response.data


def test_products_page(client, sample_products):
    """Test products page shows visible products."""
    response = client.get('/products')
    assert response.status_code == 200
    assert b'Test Cake' in response.data
    assert b'Hidden Cake' not in response.data


def test_blog_page(client, sample_posts):
    """Test blog page shows published posts."""
    response = client.get('/blog')
    assert response.status_code == 200
    assert b'Test Post' in response.data
    assert b'Draft Post' not in response.data


def test_blog_pagination(client):
    """Test blog pagination."""
    # Create 15 posts
    posts = []
    for i in range(15):
        posts.append({
            'id': f'post-{i+1}',
            'title': f'Post {i+1}',
            'short_description': f'Description {i+1}',
            'content': f'Content {i+1}',
            'published': True,
            'created_at': datetime.now().isoformat()
        })
    write_json('blog.json', posts)
    
    # Test first page
    response = client.get('/blog')
    assert response.status_code == 200
    assert b'Post 1' in response.data
    assert b'Post 10' in response.data
    assert b'Post 11' not in response.data
    
    # Test second page
    response = client.get('/blog?page=2')
    assert response.status_code == 200
    assert b'Post 11' in response.data
    assert b'Post 15' in response.data
    assert b'Post 1' not in response.data


def test_blog_post_view(client, sample_posts):
    """Test individual blog post view."""
    # Test published post
    response = client.get('/blog/post/post-1')
    assert response.status_code == 200
    assert b'Test Post' in response.data
    assert b'Test content' in response.data
    
    # Test draft post
    response = client.get('/blog/post/post-2')
    assert response.status_code == 302  # Redirects


def test_contact_form(client):
    """Test contact form submission."""
    with patch('routes.public_routes.send_email') as mock_send:
        mock_send.return_value = True
        
        response = client.post('/contact', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Test message'
        })
        
        assert response.status_code == 302
        mock_send.assert_called_once()


def test_order_form(client):
    """Test custom order form."""
    # Get form
    response = client.get('/order')
    assert response.status_code == 200
    
    # Submit form
    with patch('routes.public_routes.send_email') as mock_send:
        mock_send.return_value = True
        
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'size': '6"',
            'flavor': 'Chocolate',
            'frosting': 'Vanilla',
            'message': 'Test cake',
            'design_details': 'Simple design',
            'pickup_date': (
                datetime.now() + timedelta(days=3)
            ).strftime('%Y-%m-%d')
        }
        
        response = client.post('/order', data=data)
        
        assert response.status_code == 302
        mock_send.assert_called_once()


def test_order_form_validation(client):
    """Test custom order form validation."""
    # Test required fields
    response = client.post('/order', data={})
    assert response.status_code == 400
    
    # Test future date validation
    response = client.post('/order', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'size': '6"',
        'flavor': 'Chocolate',
        'frosting': 'Vanilla',
        'design_details': 'Simple design',
        'pickup_date': datetime.now().strftime('%Y-%m-%d')  # Today
    })
    assert response.status_code == 400
    assert b'Pickup date must be at least 2 days from today' in response.data