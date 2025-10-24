"""Payment gateway integration supporting Stripe, Paystack, and Yoco"""
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any, List, TypedDict

try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

@dataclass
class PaymentConfig:
    """Payment gateway configuration."""
    provider: str
    api_key: str
    webhook_secret: Optional[str] = None


@dataclass
class PaymentResult:
    """Result of a payment operation."""
    success: bool
    reference: str
    client_secret: Optional[str] = None  # For Stripe client-side confirmation
    error_message: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    
class PaymentGateway(ABC):
    """Abstract base class for payment gateways."""
    
    @abstractmethod
    def create_payment(
        self,
        amount: float,
        currency: str = 'ZAR',
        metadata: Optional[Dict[str, str]] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> PaymentResult:
        """Create a payment intent/transaction."""
        pass
        
    @abstractmethod
    def verify_webhook(
        self,
        payload: Dict[str, Any],
        signature: str
    ) -> bool:
        """Verify webhook signature."""
        pass


class StripeGateway(PaymentGateway):
    """Stripe payment gateway implementation."""
    
    def __init__(self, config: PaymentConfig):
        """Initialize Stripe gateway."""
        self.api_key = config.api_key
        self.webhook_secret = config.webhook_secret
        stripe.api_key = self.api_key
    
    def create_payment(
        self,
        amount: float,
        currency: str = 'ZAR',
        metadata: Optional[Dict[str, str]] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> PaymentResult:
        """Create a Stripe payment session or intent."""
        try:
            if items and success_url and cancel_url:
                # Create checkout session
                line_items = [{
                    'price_data': {
                        'currency': currency.lower(),
                        'unit_amount': int(item['price'] * 100),
                        'product_data': {
                            'name': item['title'],
                            'images': [item.get('image')] if item.get('image') else []
                        }
                    },
                    'quantity': item['quantity']
                } for item in items]

                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=success_url,
                    cancel_url=cancel_url,
                    customer_email=customer_email,
                    metadata=metadata or {}
                )

                return PaymentResult(
                    success=True,
                    reference=session.id,
                    gateway_response={
                        'provider': 'stripe',
                        'type': 'checkout',
                        'url': session.url,
                        'session_id': session.id
                    }
                )
            else:
                # Create payment intent
                amount_cents = int(amount * 100)
                intent = stripe.PaymentIntent.create(
                    amount=amount_cents,
                    currency=currency.lower(),
                    metadata=metadata or {}
                )
                
                return PaymentResult(
                    success=True,
                    reference=intent.id,
                    client_secret=intent.client_secret,
                    gateway_response={
                        'provider': 'stripe',
                        'type': 'intent',
                        'amount': amount,
                        'currency': currency,
                        'status': intent.status
                    }
                )
        except stripe.error.StripeError as e:
            return PaymentResult(
                success=False,
                reference='',
                error_message=str(e)
            )
    
    def verify_webhook(
        self,
        payload: Dict[str, Any],
        signature: str
    ) -> bool:
        """Verify Stripe webhook signature."""
        if not self.webhook_secret:
            return False
            
        try:
            # Verify webhook signature
            stripe.Webhook.construct_event(
                payload,
                signature,
                self.webhook_secret
            )
            return True
        except (stripe.error.SignatureVerificationError, ValueError):
            return False


class PaystackGateway(PaymentGateway):
    """Paystack payment gateway implementation."""
    
    def __init__(self, config: PaymentConfig):
        """Initialize Paystack gateway."""
        self.api_key = config.api_key
    
    def create_payment(
        self,
        amount: float,
        currency: str = 'ZAR',
        metadata: Optional[Dict[str, str]] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> PaymentResult:
        """Create a Paystack payment."""
        # TODO: Implement Paystack integration
        return PaymentResult(
            success=False,
            reference='',
            error_message='Paystack integration not implemented'
        )
    
    def verify_webhook(
        self,
        payload: Dict[str, Any],
        signature: str
    ) -> bool:
        """Verify Paystack webhook signature."""
        return False  # TODO: Implement verification


class YocoGateway(PaymentGateway):
    """Yoco payment gateway implementation."""
    
    def __init__(self, config: PaymentConfig):
        """Initialize Yoco gateway."""
        self.api_key = config.api_key
    
    def create_payment(
        self,
        amount: float,
        currency: str = 'ZAR',
        metadata: Optional[Dict[str, str]] = None,
        items: Optional[List[Dict[str, Any]]] = None,
        success_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        customer_email: Optional[str] = None
    ) -> PaymentResult:
        """Create a Yoco payment."""
        # TODO: Implement Yoco integration
        return PaymentResult(
            success=False,
            reference='',
            error_message='Yoco integration not implemented'
        )
    
    def verify_webhook(
        self,
        payload: Dict[str, Any],
        signature: str
    ) -> bool:
        """Verify Yoco webhook signature."""
        return False  # TODO: Implement verification


def get_payment_gateway() -> Optional[PaymentGateway]:
    """Factory function to get configured payment gateway."""
    provider = os.getenv('PAYMENT_PROVIDER', '').lower()
    
    if provider == 'stripe':
        if not STRIPE_AVAILABLE:
            raise PaymentError("Stripe package is not installed. Please install it with 'pip install stripe'")
        return StripeGateway(PaymentConfig(
            provider='stripe',
            api_key=os.getenv('STRIPE_API_KEY', ''),
            webhook_secret=os.getenv('STRIPE_WEBHOOK_SECRET')
        ))
    elif provider == 'paystack':
        return PaystackGateway(PaymentConfig(
            provider='paystack',
            api_key=os.getenv('PAYSTACK_SECRET_KEY', '')
        ))
    elif provider == 'yoco':
        return YocoGateway(PaymentConfig(
            provider='yoco',
            api_key=os.getenv('YOCO_PRIVATE_KEY', '')
        ))
    return None


class PaymentError(Exception):
    """Custom exception for payment errors."""
    pass


def create_payment_session(
    order_id: str,
    items: List[Dict[str, Any]],
    total: float,
    success_url: str,
    cancel_url: str,
    customer_email: Optional[str] = None
) -> Any:
    """Create a payment session for checkout.
    
    Args:
        order_id: Order ID for reference
        items: List of items with title, price, quantity
        total: Total amount
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect after cancelled payment
        customer_email: Optional customer email
        
    Returns:
        Payment session object
        
    Raises:
        PaymentError: If payment gateway is not configured or creation fails
    """
    gateway = get_payment_gateway()
    if not gateway:
        raise PaymentError('Payment gateway not configured')
        
    result = gateway.create_payment(
        amount=total,
        items=items,
        success_url=success_url,
        cancel_url=cancel_url,
        customer_email=customer_email,
        metadata={'order_id': order_id}
    )
    
    if not result.success:
        error_msg = result.error_message or 'Could not create payment session'
        raise PaymentError(error_msg)
        
    return result.gateway_response
