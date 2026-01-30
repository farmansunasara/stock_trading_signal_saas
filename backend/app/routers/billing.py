from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import stripe
from ..database import get_db
from ..models.user import User
from ..schemas.billing import CheckoutSessionCreate, SubscriptionStatus
from ..utils.jwt import get_current_user
from ..utils.redis_client import get_redis
from ..utils.stripe_client import stripe
from ..config import settings

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.post("/create-checkout")
async def create_checkout_session(
    checkout_data: CheckoutSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe Checkout session for ₹499 subscription"""
    try:
        # Create or retrieve Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                metadata={"user_id": str(current_user.id)}
            )
            current_user.stripe_customer_id = customer.id
            db.commit()
        else:
            customer_id = current_user.stripe_customer_id
        
        # Create checkout session
        success_url = checkout_data.success_url or f"{settings.FRONTEND_URL}/dashboard?success=true"
        cancel_url = checkout_data.cancel_url or f"{settings.FRONTEND_URL}/dashboard?canceled=true"
        
        checkout_session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": settings.STRIPE_PRICE_ID,
                    "quantity": 1,
                }
            ],
            mode="subscription",  # or "payment" for one-time
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(current_user.id),
                "user_email": current_user.email
            }
        )
        
        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id
        }
    
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


@router.get("/status", response_model=SubscriptionStatus)
async def get_billing_status(current_user: User = Depends(get_current_user)):
    """Get current user's subscription status"""
    return {
        "is_paid": current_user.is_paid,
        "stripe_customer_id": current_user.stripe_customer_id
    }


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events with Redis idempotency"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    redis_client = get_redis()
    event_id = event["id"]
    
    # Redis idempotency check (24h TTL)
    redis_key = f"stripe_event:{event_id}"
    if redis_client.get(redis_key):
        return {"status": "already_processed"}
    
    # Mark event as processed
    redis_client.setex(redis_key, 86400, "1")
    
    # Handle different event types
    event_type = event["type"]
    
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session.get("customer")
        
        # Find user by Stripe customer ID
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.is_paid = True
            db.commit()
    
    elif event_type == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        
        # Extend subscription
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.is_paid = True
            db.commit()
    
    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        
        # Downgrade to free
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.is_paid = False
            db.commit()
    
    return {"status": "success", "event_type": event_type}
