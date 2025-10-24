"""Unit tests for utility modules."""
import os
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from werkzeug.datastructures import FileStorage

from utils.json_store import read_json, write_json
from utils.payment import (
    get_payment_gateway, PaymentConfig, StripeGateway,
    PaymentGateway, PaymentResult
)
from utils.email_utils import send_email
from utils.scheduler import check_scheduled_posts
from utils.files import (
    init_upload_dirs, secure_upload_path,
    save_uploaded_file, UPLOAD_DIRS, ALLOWED_EXTENSIONS
)

from typing import Generator


@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary data directory for tests.
    
    Returns:
        Generator[Path, None, None]: Temporary directory path
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        old_data_dir = os.getenv('DATA_DIR')
        os.environ['DATA_DIR'] = tmpdir
        yield Path(tmpdir)
        if old_data_dir:
            os.environ['DATA_DIR'] = old_data_dir


@pytest.fixture
def mock_file() -> Generator[FileStorage, None, None]:
    """Create a mock file for upload tests.
    
    Returns:
        Generator[FileStorage, None, None]: Mock file for testing
    """
    with tempfile.NamedTemporaryFile(suffix='.jpg') as f:
        f.write(b'test image content')
        f.seek(0)
        file = FileStorage(
            stream=f,
            filename='test.jpg',
            content_type='image/jpeg'
        )
        yield file


def test_json_store(temp_data_dir: Path) -> None:
    """Test JSON read/write operations."""
    test_data: dict[str, object] = {
        'test': True,
        'items': [1, 2, 3]
    }
    
    # Write JSON
    write_json('test.json', test_data)
    assert (temp_data_dir / 'test.json').exists()
    
    # Read JSON
    loaded = read_json('test.json')
    assert loaded == test_data
    
    # Test default for missing file
    assert read_json('missing.json', default=[]) == []


def test_file_uploads(temp_data_dir: Path) -> None:
    """Test file upload utilities."""
    init_upload_dirs()
    
    # Verify upload directories were created
    for dir_path in UPLOAD_DIRS.values():
        assert Path(dir_path).exists()
        assert os.access(Path(dir_path), os.W_OK)


def test_secure_upload_path(mock_file: FileStorage) -> None:
    """Test secure file upload path generation."""
    # Test valid file
    url_path, file_path = secure_upload_path(mock_file, 'products')
    assert url_path and file_path
    assert url_path.startswith('/static/uploads/products/')
    assert str(file_path).endswith('.jpg')
    assert 'products-test' in str(file_path)
    
    # Test invalid category
    url_path, file_path = secure_upload_path(mock_file, 'invalid')
    assert not url_path and not file_path
    
    # Test invalid extension
    with tempfile.NamedTemporaryFile(suffix='.exe') as f:
        bad_file = FileStorage(
            stream=f,
            filename='test.exe',
            content_type='application/octet-stream'
        )
        url_path, file_path = secure_upload_path(bad_file, 'products')
        assert not url_path and not file_path


@patch('stripe.PaymentIntent')
def test_stripe_gateway(mock_intent: MagicMock) -> None:
    """Test Stripe payment gateway."""
    # Mock successful payment
    mock_intent.create.return_value = MagicMock(
        id='pi_123',
        client_secret='secret_123',
        status='requires_payment_method'
    )
    
    gateway = StripeGateway(PaymentConfig(
        provider='stripe',
        api_key='test_key',
        webhook_secret='whsec_test'
    ))
    
    # Test successful payment
    result = gateway.create_payment(100.00, 'ZAR')
    assert result.success
    assert result.reference == 'pi_123'
    assert result.client_secret == 'secret_123'
    
    # Verify Stripe was called correctly
    mock_intent.create.assert_called_once_with(
        amount=10000,  # 100.00 converted to cents
        currency='zar',
        metadata={}
    )


def test_payment_gateway_factory() -> None:
    """Test payment gateway factory."""
    # Test no gateway when not configured
    assert get_payment_gateway() is None
    
    # Test Stripe gateway
    os.environ['PAYMENT_PROVIDER'] = 'stripe'
    os.environ['STRIPE_API_KEY'] = 'test_key'
    gateway = get_payment_gateway()
    assert isinstance(gateway, StripeGateway)
    
    # Test unsupported gateway
    os.environ['PAYMENT_PROVIDER'] = 'unsupported'
    gateway = get_payment_gateway()
    assert gateway is None


def test_email_utils() -> None:
    """Test email utility (just validation, no actual sending)."""
    # Test without SMTP config
    assert not send_email('test', 'body', 'test@example.com')


def test_scheduler() -> None:
    """Test blog post scheduler."""
    from datetime import datetime, timedelta
    
    # Create a test post scheduled for yesterday
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    posts = [{
        'id': 'test-1',
        'title': 'Test Post',
        'published': False,
        'publish_date': yesterday
    }]
    
    write_json('blog.json', posts)
    check_scheduled_posts()  # Run one scheduler iteration
    
    # Verify post was published
    updated = read_json('blog.json')
    assert updated[0]['published'] is True
