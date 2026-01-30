import redis
from ..config import settings
from typing import Optional

# Try to connect to Redis, fall back to mock if not available
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_connect_timeout=2)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except (redis.ConnectionError, redis.TimeoutError, Exception):
    REDIS_AVAILABLE = False
    
    # Mock Redis for local development without running server
    class MockRedis:
        """Simple in-memory mock Redis for development"""
        def __init__(self):
            self.data = {}
            self.expiry = {}
        
        def get(self, key: str) -> Optional[str]:
            """Get value by key"""
            import time
            if key in self.expiry:
                if time.time() > self.expiry[key]:
                    del self.data[key]
                    del self.expiry[key]
                    return None
            return self.data.get(key)
        
        def set(self, key: str, value: str) -> None:
            """Set value"""
            self.data[key] = value
        
        def setex(self, key: str, ex: int, value: str) -> None:
            """Set value with expiry"""
            import time
            self.data[key] = value
            self.expiry[key] = time.time() + ex
        
        def incr(self, key: str) -> int:
            """Increment counter"""
            import time
            # Remove if expired
            if key in self.expiry and time.time() > self.expiry[key]:
                del self.data[key]
                del self.expiry[key]
            
            if key not in self.data:
                self.data[key] = 1
            else:
                self.data[key] = int(self.data[key]) + 1
            return self.data[key]
        
        def expire(self, key: str, ex: int) -> None:
            """Set expiry for key"""
            import time
            if key in self.data:
                self.expiry[key] = time.time() + ex
        
        def delete(self, key: str) -> None:
            """Delete key"""
            self.data.pop(key, None)
            self.expiry.pop(key, None)
        
        def ping(self) -> str:
            """Health check"""
            return "PONG"
    
    redis_client = MockRedis()


def get_redis():
    """Get Redis client (real or mock)"""
    return redis_client
