from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Signal(BaseModel):
    symbol: str
    type: str  # "BUY", "SELL", "HOLD"
    price: float
    confidence: float
    timestamp: datetime


class SignalsResponse(BaseModel):
    signals: List[Signal]
    user_limit: Optional[str] = None
    is_paid: bool
