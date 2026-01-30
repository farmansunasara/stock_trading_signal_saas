import pytest
import json
import hmac
import hashlib
import time
from unittest.mock import patch, MagicMock
from app.config import settings


def test_create_checkout_session(client, auth_token, test_user):
    """Test creating Stripe checkout session"""
    
    # Mock Stripe Customer and Checkout Session creation
    with patch('app.routers.billing.stripe.Customer.create') as mock_customer, \
         patch('app.routers.billing.stripe.checkout.Session.create') as mock_session:
        
        # Setup mock responses
        mock_customer.return_value = MagicMock(id="cus_test123")
        mock_session.return_value = MagicMock(
            id="cs_test_session123",
            url="https://checkout.stripe.com/test-session"
        )
        
        # Make request
        response = client.post(
            "/billing/create-checkout",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "success_url": "http://localhost:3000/dashboard?success=true",
                "cancel_url": "http://localhost:3000/dashboard?canceled=true"
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "checkout_url" in data
        assert "session_id" in data
        assert data["checkout_url"] == "https://checkout.stripe.com/test-session"
        assert data["session_id"] == "cs_test_session123"
        
        # Verify Stripe calls
        mock_customer.assert_called_once()
        mock_session.assert_called_once()


def test_create_checkout_session_existing_customer(client, auth_token, test_user, db_session):
    """Test checkout session creation with existing Stripe customer"""
    
    # Set existing Stripe customer ID
    test_user.stripe_customer_id = "cus_existing123"
    db_session.commit()
    
    with patch('app.routers.billing.stripe.checkout.Session.create') as mock_session:
        mock_session.return_value = MagicMock(
            id="cs_test_session456",
            url="https://checkout.stripe.com/test-session-456"
        )
        
        response = client.post(
            "/billing/create-checkout",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "checkout_url" in data


def test_create_checkout_session_without_auth(client):
    """Test checkout session creation without authentication"""
    response = client.post("/billing/create-checkout", json={})
    assert response.status_code == 403  # No authorization header


def test_get_billing_status_free_user(client, auth_token, test_user):
    """Test billing status endpoint for free user"""
    response = client.get(
        "/billing/status",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_paid"] == False
    assert "stripe_customer_id" in data


def test_get_billing_status_paid_user(client, paid_auth_token, test_paid_user):
    """Test billing status endpoint for paid user"""
    response = client.get(
        "/billing/status",
        headers={"Authorization": f"Bearer {paid_auth_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_paid"] == True


def test_webhook_checkout_completed(client, test_user, db_session):
    """Test webhook handling for checkout.session.completed event"""
    
    # Set Stripe customer ID for test user
    test_user.stripe_customer_id = "cus_webhook_test123"
    db_session.commit()
    
    # Create mock webhook event
    event_data = {
        "id": "evt_test_checkout_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "customer": "cus_webhook_test123",
                "payment_status": "paid"
            }
        }
    }
    
    # Mock Stripe webhook signature verification
    with patch('app.routers.billing.stripe.Webhook.construct_event') as mock_construct:
        mock_construct.return_value = event_data
        
        # Send webhook
        response = client.post(
            "/billing/webhook",
            json=event_data,
            headers={"stripe-signature": "mock_signature"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["event_type"] == "checkout.session.completed"
        
        # Verify user is now paid
        db_session.refresh(test_user)
        assert test_user.is_paid == True


def test_webhook_invoice_payment_succeeded(client, test_user, db_session):
    """Test webhook handling for invoice.payment_succeeded event"""
    
    test_user.stripe_customer_id = "cus_invoice_test456"
    test_user.is_paid = False
    db_session.commit()
    
    event_data = {
        "id": "evt_test_invoice_456",
        "type": "invoice.payment_succeeded",
        "data": {
            "object": {
                "id": "in_test_456",
                "customer": "cus_invoice_test456"
            }
        }
    }
    
    with patch('app.routers.billing.stripe.Webhook.construct_event') as mock_construct:
        mock_construct.return_value = event_data
        
        response = client.post(
            "/billing/webhook",
            json=event_data,
            headers={"stripe-signature": "mock_signature"}
        )
        
        assert response.status_code == 200
        
        # Verify subscription extended
        db_session.refresh(test_user)
        assert test_user.is_paid == True


def test_webhook_subscription_deleted(client, test_user, db_session):
    """Test webhook handling for customer.subscription.deleted event"""
    
    test_user.stripe_customer_id = "cus_cancel_test789"
    test_user.is_paid = True
    db_session.commit()
    
    event_data = {
        "id": "evt_test_cancel_789",
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_test_789",
                "customer": "cus_cancel_test789"
            }
        }
    }
    
    with patch('app.routers.billing.stripe.Webhook.construct_event') as mock_construct:
        mock_construct.return_value = event_data
        
        response = client.post(
            "/billing/webhook",
            json=event_data,
            headers={"stripe-signature": "mock_signature"}
        )
        
        assert response.status_code == 200
        
        # Verify user downgraded to free
        db_session.refresh(test_user)
        assert test_user.is_paid == False


def test_webhook_idempotency(client, test_user, db_session):
    """Test webhook idempotency - prevent duplicate event processing"""
    
    test_user.stripe_customer_id = "cus_idempotency_test"
    test_user.is_paid = False
    db_session.commit()
    
    event_data = {
        "id": "evt_idempotency_unique_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_idempotency",
                "customer": "cus_idempotency_test"
            }
        }
    }
    
    with patch('app.routers.billing.stripe.Webhook.construct_event') as mock_construct:
        mock_construct.return_value = event_data
        
        # First webhook call - should process
        response1 = client.post(
            "/billing/webhook",
            json=event_data,
            headers={"stripe-signature": "mock_signature"}
        )
        
        assert response1.status_code == 200
        assert response1.json()["status"] == "success"
        
        # Verify user became paid
        db_session.refresh(test_user)
        assert test_user.is_paid == True
        
        # Second webhook call with SAME event_id - should skip
        test_user.is_paid = False  # Reset to verify no change
        db_session.commit()
        
        response2 = client.post(
            "/billing/webhook",
            json=event_data,
            headers={"stripe-signature": "mock_signature"}
        )
        
        assert response2.status_code == 200
        assert response2.json()["status"] == "already_processed"
        
        # Verify user status NOT changed (idempotency worked)
        db_session.refresh(test_user)
        assert test_user.is_paid == False


def test_webhook_invalid_signature(client):
    """Test webhook with invalid signature"""
    
    event_data = {
        "id": "evt_invalid_sig",
        "type": "checkout.session.completed",
        "data": {"object": {}}
    }
    
    with patch('app.routers.billing.stripe.Webhook.construct_event') as mock_construct:
        # Mock signature verification failure
        from stripe.error import SignatureVerificationError
        mock_construct.side_effect = SignatureVerificationError("Invalid signature", "sig_header")
        
        response = client.post(
            "/billing/webhook",
            json=event_data,
            headers={"stripe-signature": "invalid_signature"}
        )
        
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]


def test_webhook_invalid_payload(client):
    """Test webhook with invalid payload"""
    
    with patch('app.routers.billing.stripe.Webhook.construct_event') as mock_construct:
        # Mock payload parsing error
        mock_construct.side_effect = ValueError("Invalid payload")
        
        response = client.post(
            "/billing/webhook",
            json={"invalid": "data"},
            headers={"stripe-signature": "mock_sig"}
        )
        
        assert response.status_code == 400
        assert "Invalid payload" in response.json()["detail"]


def test_webhook_unknown_event_type(client):
    """Test webhook with unknown event type (should not error)"""
    
    event_data = {
        "id": "evt_unknown_type",
        "type": "customer.updated",  # Event type we don't handle
        "data": {"object": {}}
    }
    
    with patch('app.routers.billing.stripe.Webhook.construct_event') as mock_construct:
        mock_construct.return_value = event_data
        
        response = client.post(
            "/billing/webhook",
            json=event_data,
            headers={"stripe-signature": "mock_signature"}
        )
        
        # Should succeed but not take any action
        assert response.status_code == 200
        assert response.json()["event_type"] == "customer.updated"


def test_stripe_error_handling(client, auth_token):
    """Test Stripe API error handling during checkout creation"""
    
    with patch('app.routers.billing.stripe.Customer.create') as mock_customer:
        # Mock Stripe error
        from stripe.error import StripeError
        mock_customer.side_effect = StripeError("Card declined")
        
        response = client.post(
            "/billing/create-checkout",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={}
        )
        
        assert response.status_code == 400
        assert "Stripe error" in response.json()["detail"]
