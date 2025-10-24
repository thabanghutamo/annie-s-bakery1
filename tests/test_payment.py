"""Tests for payment processing."""
import pytest
from unittest.mock import patch, MagicMock
from utils.payment import (
    PaymentGateway,
    StripeGateway,
    PaystackGateway,
    YocoGateway,
    PaymentConfig,
    PaymentResult,
    get_payment_gateway
)


@pytest.fixture
def stripe_gateway():
    """Create Stripe gateway for testing."""
    return StripeGateway(PaymentConfig(
        provider='stripe',
        api_key='test_key',
        webhook_secret='test_secret'
    ))


@pytest.fixture
def paystack_gateway():
    """Create Paystack gateway for testing."""
    return PaystackGateway(PaymentConfig(
        provider='paystack',
        api_key='test_key'
    ))


@pytest.fixture
def yoco_gateway():
    """Create Yoco gateway for testing."""
    return YocoGateway(PaymentConfig(
        provider='yoco',
        api_key='test_key'
    ))


def test_stripe_payment_intent():
    """Test creating Stripe payment intent."""
    with patch('stripe.PaymentIntent.create') as mock_create:
        mock_create.return_value = MagicMock(
            id='pi_test',
            client_secret='test_secret',
            status='requires_payment_method'
        )
        
        gateway = StripeGateway(PaymentConfig(
            provider='stripe',
            api_key='test_key'
        ))
        
        result = gateway.create_payment(
            amount=99.99,
            currency='ZAR',
            metadata={'order_id': 'test-1'}
        )
        
        assert result.success
        assert result.reference == 'pi_test'
        assert result.client_secret == 'test_secret'
        assert result.gateway_response['provider'] == 'stripe'
        assert result.gateway_response['type'] == 'intent'
        
        mock_create.assert_called_once_with(
            amount=9999,  # In cents
            currency='zar',
            metadata={'order_id': 'test-1'}
        )


def test_stripe_checkout_session():
    """Test creating Stripe checkout session."""
    with patch('stripe.checkout.Session.create') as mock_create:
        mock_create.return_value = MagicMock(
            id='cs_test',
            url='https://checkout.stripe.com/test'
        )
        
        gateway = StripeGateway(PaymentConfig(
            provider='stripe',
            api_key='test_key'
        ))
        
        result = gateway.create_payment(
            amount=99.99,
            currency='ZAR',
            metadata={'order_id': 'test-1'},
            items=[{
                'title': 'Test Product',
                'price': 99.99,
                'quantity': 1,
                'image': '/test.jpg'
            }],
            success_url='http://example.com/success',
            cancel_url='http://example.com/cancel',
            customer_email='test@example.com'
        )
        
        assert result.success
        assert result.reference == 'cs_test'
        assert result.gateway_response['provider'] == 'stripe'
        assert result.gateway_response['type'] == 'checkout'
        assert result.gateway_response['url'] == 'https://checkout.stripe.com/test'
        
        mock_create.assert_called_once_with(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'zar',
                    'unit_amount': 9999,
                    'product_data': {
                        'name': 'Test Product',
                        'images': ['/test.jpg']
                    }
                },
                'quantity': 1
            }],
            mode='payment',
            success_url='http://example.com/success',
            cancel_url='http://example.com/cancel',
            customer_email='test@example.com',
            metadata={'order_id': 'test-1'}
        )


def test_stripe_webhook_verification():
    """Test Stripe webhook signature verification."""
    with patch('stripe.Webhook.construct_event') as mock_verify:
        gateway = StripeGateway(PaymentConfig(
            provider='stripe',
            api_key='test_key',
            webhook_secret='test_secret'
        ))
        
        # Test valid signature
        mock_verify.return_value = {'type': 'payment_intent.succeeded'}
        assert gateway.verify_webhook({'data': 'test'}, 'test_sig')
        
        # Test invalid signature
        mock_verify.side_effect = ValueError()
        assert not gateway.verify_webhook({'data': 'test'}, 'bad_sig')


def test_payment_gateway_factory():
    """Test payment gateway factory function."""
    with patch.dict('os.environ', {
        'PAYMENT_PROVIDER': 'stripe',
        'STRIPE_API_KEY': 'test_key'
    }):
        gateway = get_payment_gateway()
        assert isinstance(gateway, StripeGateway)
    
    with patch.dict('os.environ', {
        'PAYMENT_PROVIDER': 'paystack',
        'PAYSTACK_SECRET_KEY': 'test_key'
    }):
        gateway = get_payment_gateway()
        assert isinstance(gateway, PaystackGateway)
    
    with patch.dict('os.environ', {
        'PAYMENT_PROVIDER': 'yoco',
        'YOCO_PRIVATE_KEY': 'test_key'
    }):
        gateway = get_payment_gateway()
        assert isinstance(gateway, YocoGateway)
    
    with patch.dict('os.environ', {'PAYMENT_PROVIDER': 'invalid'}):
        gateway = get_payment_gateway()
        assert gateway is None