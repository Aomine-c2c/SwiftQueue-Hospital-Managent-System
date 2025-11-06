import redis
import json
from typing import Any, Optional
from functools import wraps
import os

class RedisCache:
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=2)
            # Test connection
            self.client.ping()
            self.enabled = True
            print("Redis connection successful")
        except Exception as e:
            print(f"Redis connection failed: {e}. Caching disabled.")
            self.client = None
            self.enabled = False
        self.default_ttl = 300  # 5 minutes

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not self.enabled:
            return False
        try:
            serialized = json.dumps(value, default=str)
            if ttl is None:
                ttl = self.default_ttl
            return self.client.setex(key, ttl, serialized)
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled:
            return False
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled:
            return 0
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis delete pattern error: {e}")
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.enabled:
            return False
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            print(f"Redis incr error: {e}")
            return 0

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on existing key"""
        try:
            return bool(self.client.expire(key, ttl))
        except Exception as e:
            print(f"Redis expire error: {e}")
            return False


# Global cache instance
cache = RedisCache()


def cache_response(key_prefix: str, ttl: int = 300):
    """Decorator to cache function responses"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached = cache.get(cache_key)
            if cached is not None:
                return cached
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache by pattern"""
    return cache.delete_pattern(pattern)
