import stripe
from ..config import settings
import os

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Mock Stripe for local development if running without real Stripe account
class MockStripe:
    """Mock Stripe client for local development"""
    
    class Customer:
        @staticmethod
        def create(email, metadata=None):
            return {
                "id": f"cus_mock_{email.split('@')[0]}",
                "email": email,
                "metadata": metadata or {}
            }
    
    class Checkout:
        class Session:
            @staticmethod
            def create(**kwargs):
                return {
                    "id": "cs_test_mock_session",
                    "url": "https://checkout.stripe.com/pay/cs_test_mock_session",
                    "client_secret": "cs_test_mock_secret",
                    "payment_status": "unpaid"
                }
    
    class Event:
        @staticmethod
        def construct_from(data, key):
            return data

# Use real Stripe if key looks valid, otherwise use mock for local development
def get_stripe_client():
    """Return Stripe client (real or mock based on environment)"""
    if settings.STRIPE_SECRET_KEY.startswith("sk_test_") and len(settings.STRIPE_SECRET_KEY) > 20:
        # Real or valid test key - use actual Stripe
        return stripe
    else:
        # Invalid/placeholder key - use mock
        return MockStripe()

# Export for use in routers
stripe = get_stripe_client()
