import jwt
import datetime
from typing import Dict, Any, Optional
from app.services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)

class JWTService:
    def __init__(self, secret_key: str, algorithm: str = 'HS256', access_token_expire_minutes: int = 30, refresh_token_expire_days: int = 7):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.datetime.utcnow() + datetime.timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_token_pair(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Create both access and refresh tokens"""
        access_token = self.create_access_token(data)
        refresh_token = self.create_refresh_token(data)

        # Store refresh token in Redis for validation
        user_id = data.get("sub")
        if user_id:
            redis_service.set(f"refresh_token:{user_id}", refresh_token, self.refresh_token_expire_days * 24 * 60 * 60)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != token_type:
                logger.warning(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
                return None

            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def verify_refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Verify refresh token and check if it's stored in Redis"""
        payload = self.verify_token(refresh_token, "refresh")
        if not payload:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Check if refresh token exists in Redis
        stored_token = redis_service.get(f"refresh_token:{user_id}")
        if not stored_token or stored_token != refresh_token:
            logger.warning(f"Refresh token not found or mismatched for user {user_id}")
            return None

        return payload

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Generate new access token using refresh token"""
        payload = self.verify_refresh_token(refresh_token)
        if not payload:
            return None

        # Remove 'exp', 'iat', 'type' from payload for new token
        token_data = {k: v for k, v in payload.items() if k not in ['exp', 'iat', 'type']}

        new_access_token = self.create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    def revoke_refresh_token(self, user_id: str) -> bool:
        """Revoke refresh token by removing it from Redis"""
        return redis_service.delete(f"refresh_token:{user_id}")

    def revoke_all_user_tokens(self, user_id: str) -> bool:
        """Revoke all refresh tokens for a user"""
        return self.revoke_refresh_token(user_id)

    def get_token_expiry(self, token: str) -> Optional[datetime.datetime]:
        """Get token expiry datetime without full verification"""
        try:
            # Decode without verification to get payload
            header = jwt.get_unverified_header(token)
            payload = jwt.decode(token, options={"verify_signature": False, "verify_exp": False})

            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.datetime.fromtimestamp(exp_timestamp, tz=datetime.timezone.utc)

        except Exception as e:
            logger.error(f"Error getting token expiry: {e}")

        return None

    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired"""
        expiry = self.get_token_expiry(token)
        if expiry:
            return datetime.datetime.now(datetime.timezone.utc) > expiry
        return True

    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token payload without verification (for debugging)"""
        try:
            return jwt.decode(token, options={"verify_signature": False, "verify_exp": False})
        except Exception as e:
            logger.error(f"Error getting token payload: {e}")
            return None

    def blacklist_token(self, token: str, ttl: int = None) -> bool:
        """Add token to blacklist (for logout)"""
        try:
            # Use token as key, store minimal data
            if ttl is None:
                # Default to token expiry time
                expiry = self.get_token_expiry(token)
                if expiry:
                    ttl = int((expiry - datetime.datetime.now(datetime.timezone.utc)).total_seconds())
                else:
                    ttl = 3600  # 1 hour default

            return redis_service.set(f"blacklist:{token}", "blacklisted", ttl)
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return False

    def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return redis_service.exists(f"blacklist:{token}")

    def validate_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Complete token validation including blacklist check"""
        # First verify the token
        payload = self.verify_token(token, token_type)
        if not payload:
            return None

        # Check if token is blacklisted
        if self.is_token_blacklisted(token):
            logger.warning("Token is blacklisted")
            return None

        return payload

    def get_user_sessions(self, user_id: str) -> Dict[str, Any]:
        """Get all active sessions for a user"""
        # This is a simplified version - in production you might want to track all user sessions
        refresh_token = redis_service.get(f"refresh_token:{user_id}")
        return {
            "has_active_session": refresh_token is not None,
            "refresh_token_exists": refresh_token is not None
        }

# Global instance - will be initialized with proper config
jwt_service = None

def init_jwt_service(secret_key: str, **kwargs):
    """Initialize global JWT service instance"""
    global jwt_service
    jwt_service = JWTService(secret_key, **kwargs)
    return jwt_service

# Export for use in other modules
__all__ = ['JWTService', 'jwt_service', 'init_jwt_service']