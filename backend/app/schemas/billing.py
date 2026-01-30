from pydantic import BaseModel
from typing import Optional


class CheckoutSessionCreate(BaseModel):
    success_url: Optional[str] = None
    cancel_url: Optional[str] = None


class SubscriptionStatus(BaseModel):
    is_paid: bool
    stripe_customer_id: Optional[str] = None
