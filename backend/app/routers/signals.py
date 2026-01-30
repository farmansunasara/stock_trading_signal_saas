from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, date
import json
import random
from ..models.user import User
from ..schemas.signal import SignalsResponse, Signal
from ..utils.jwt import get_current_user
from ..utils.redis_client import get_redis

router = APIRouter(prefix="/signals", tags=["Signals"])


def generate_mock_signals() -> list:
    """Generate mock trading signals for NIFTY/BANKNIFTY"""
    symbols = ["NIFTY", "BANKNIFTY"]
    signal_types = ["BUY", "SELL", "HOLD"]
    
    signals = []
    for symbol in symbols:
        for i in range(5):  # Generate 5 signals per symbol
            signals.append({
                "symbol": symbol,
                "type": random.choice(signal_types),
                "price": round(21500 + random.uniform(-500, 500), 2) if symbol == "NIFTY" else round(45000 + random.uniform(-1000, 1000), 2),
                "confidence": round(random.uniform(0.6, 0.95), 2),
                "timestamp": datetime.utcnow().isoformat()
            })
    
    return signals


@router.get("", response_model=SignalsResponse)
async def get_signals(current_user: User = Depends(get_current_user)):
    """
    Get trading signals with Redis caching and rate limiting.
    - Free users: 3 signals/day
    - Paid users: Unlimited signals
    """
    redis_client = get_redis()
    today = date.today().isoformat()
    
    # Check rate limit for free users
    if not current_user.is_paid:
        rate_key = f"signal_limit:{current_user.id}:{today}"
        count = redis_client.get(rate_key)
        
        if count and int(count) >= 3:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Daily limit exceeded. Upgrade to paid plan for unlimited signals."
            )
        
        # Increment counter
        if count is None:
            redis_client.setex(rate_key, 86400, 1)  # 24h TTL
        else:
            redis_client.incr(rate_key)
    
    # Check Redis cache for signals (TTL 300 sec = 5 min)
    cache_key = f"signals:all:{today}"
    cached_signals = redis_client.get(cache_key)
    
    if cached_signals:
        signals_data = json.loads(cached_signals)
    else:
        # Generate mock signals (simulating expensive computation)
        signals_data = generate_mock_signals()
        # Cache in Redis
        redis_client.setex(cache_key, 300, json.dumps(signals_data))
    
    # Limit signals for free users
    if not current_user.is_paid:
        signals_data = signals_data[:3]  # Only first 3 signals
        user_limit = "3/day (upgrade for unlimited)"
    else:
        user_limit = None
    
    return {
        "signals": signals_data,
        "user_limit": user_limit,
        "is_paid": current_user.is_paid
    }
