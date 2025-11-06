import redis
import json
import pickle
from typing import Any, Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self._connection = None

    @property
    def connection(self):
        if self._connection is None:
            try:
                self._connection = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                # Test connection
                self._connection.ping()
                logger.info("Redis connection established")
            except redis.ConnectionError as e:
                logger.error(f"Redis connection failed: {e}")
                self._connection = None
        return self._connection

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        try:
            return self.connection is not None and self.connection.ping()
        except:
            return False

    # Basic key-value operations
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a key-value pair with optional TTL in seconds"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, str):
                value = str(value)

            if ttl:
                return self.connection.setex(key, ttl, value)
            else:
                return self.connection.set(key, value)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        try:
            return self.connection.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            return bool(self.connection.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.connection.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key"""
        try:
            return bool(self.connection.expire(key, ttl))
        except Exception as e:
            logger.error(f"Redis expire error: {e}")
            return False

    # JSON operations
    def set_json(self, key: str, data: Dict[str, Any], ttl: int = None) -> bool:
        """Store JSON data"""
        try:
            json_data = json.dumps(data)
            return self.set(key, json_data, ttl)
        except Exception as e:
            logger.error(f"Redis set_json error: {e}")
            return False

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve JSON data"""
        try:
            data = self.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get_json error: {e}")
            return None

    # Session management
    def set_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600) -> bool:
        """Store session data with 1 hour default TTL"""
        return self.set_json(f"session:{session_id}", data, ttl)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        return self.get_json(f"session:{session_id}")

    def delete_session(self, session_id: str) -> bool:
        """Delete session data"""
        return self.delete(f"session:{session_id}")

    # Cache operations
    def set_cache(self, key: str, data: Any, ttl: int = 300) -> bool:
        """Cache data with 5 minute default TTL"""
        try:
            if isinstance(data, (dict, list, int, float, bool)):
                return self.set_json(f"cache:{key}", {"data": data, "type": type(data).__name__}, ttl)
            else:
                # For complex objects, use pickle
                pickled_data = pickle.dumps(data)
                return self.connection.setex(f"cache:{key}", ttl, pickled_data)
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """Retrieve cached data"""
        try:
            cache_key = f"cache:{key}"
            data = self.connection.get(cache_key)
            if not data:
                return None

            # Try to decode as JSON first
            try:
                parsed = json.loads(data)
                if isinstance(parsed, dict) and "data" in parsed:
                    return parsed["data"]
            except:
                # If JSON fails, try pickle
                try:
                    return pickle.loads(data)
                except:
                    return data.decode('utf-8') if isinstance(data, bytes) else data
        except Exception as e:
            logger.error(f"Redis cache get error: {e}")
            return None

    def clear_cache(self, pattern: str = "*") -> int:
        """Clear cache keys matching pattern"""
        try:
            keys = self.connection.keys(f"cache:{pattern}")
            if keys:
                return self.connection.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis clear cache error: {e}")
            return 0

    # Queue operations
    def enqueue(self, queue_name: str, item: Any) -> bool:
        """Add item to queue"""
        try:
            if isinstance(item, (dict, list)):
                item = json.dumps(item)
            return bool(self.connection.rpush(f"queue:{queue_name}", item))
        except Exception as e:
            logger.error(f"Redis enqueue error: {e}")
            return False

    def dequeue(self, queue_name: str) -> Optional[str]:
        """Remove and return item from queue"""
        try:
            return self.connection.lpop(f"queue:{queue_name}")
        except Exception as e:
            logger.error(f"Redis dequeue error: {e}")
            return None

    def queue_length(self, queue_name: str) -> int:
        """Get queue length"""
        try:
            return self.connection.llen(f"queue:{queue_name}")
        except Exception as e:
            logger.error(f"Redis queue length error: {e}")
            return 0

    # Rate limiting
    def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check if rate limit is exceeded"""
        try:
            # Use sliding window rate limiting
            now = int(self.connection.time()[0])
            window_start = now - window

            # Remove old entries
            self.connection.zremrangebyscore(f"ratelimit:{key}", 0, window_start)

            # Count current requests
            count = self.connection.zcard(f"ratelimit:{key}")

            if count >= limit:
                return False

            # Add current request
            self.connection.zadd(f"ratelimit:{key}", {str(now): now})

            # Set expiration for the key
            self.connection.expire(f"ratelimit:{key}", window)

            return True
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            return True  # Allow request if Redis fails

    # Analytics and metrics
    def increment_counter(self, key: str, amount: int = 1) -> int:
        """Increment a counter"""
        try:
            return self.connection.incrby(f"counter:{key}", amount)
        except Exception as e:
            logger.error(f"Redis increment counter error: {e}")
            return 0

    def get_counter(self, key: str) -> int:
        """Get counter value"""
        try:
            value = self.connection.get(f"counter:{key}")
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Redis get counter error: {e}")
            return 0

    # Pub/Sub operations
    def publish(self, channel: str, message: str) -> int:
        """Publish message to channel"""
        try:
            return self.connection.publish(channel, message)
        except Exception as e:
            logger.error(f"Redis publish error: {e}")
            return 0

    # Bulk operations
    def set_multiple(self, data: Dict[str, Any], ttl: int = None) -> bool:
        """Set multiple key-value pairs"""
        try:
            pipeline = self.connection.pipeline()
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                elif not isinstance(value, str):
                    value = str(value)

                if ttl:
                    pipeline.setex(key, ttl, value)
                else:
                    pipeline.set(key, value)

            pipeline.execute()
            return True
        except Exception as e:
            logger.error(f"Redis set multiple error: {e}")
            return False

    def get_multiple(self, keys: List[str]) -> Dict[str, Optional[str]]:
        """Get multiple values by keys"""
        try:
            values = self.connection.mget(keys)
            return dict(zip(keys, values))
        except Exception as e:
            logger.error(f"Redis get multiple error: {e}")
            return {}

    # Health check
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            "connected": self.is_connected(),
            "host": self.host,
            "port": self.port,
            "db": self.db
        }

# Global instance
redis_service = RedisService()

# Export for use in other modules
__all__ = ['RedisService', 'redis_service']