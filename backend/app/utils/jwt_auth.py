from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from app.utils.redis_cache import cache

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenBlacklist:
    """Token blacklist using Redis"""
    
    @staticmethod
    def add_to_blacklist(token: str, exp: datetime):
        """Add token to blacklist"""
        ttl = int((exp - datetime.utcnow()).total_seconds())
        if ttl > 0:
            cache.set(f"blacklist:{token}", "1", ttl=ttl)
    
    @staticmethod
    def is_blacklisted(token: str) -> bool:
        """Check if token is blacklisted"""
        return cache.exists(f"blacklist:{token}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a new access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a new refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT token"""
    try:
        # Check if token is blacklisted
        if TokenBlacklist.is_blacklisted(token):
            raise JWTError("Token has been revoked")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise


def refresh_access_token(refresh_token: str) -> Dict[str, str]:
    """Generate new access token from refresh token"""
    try:
        payload = decode_token(refresh_token)
        
        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")
        
        # Create new access token
        access_token_data = {
            "sub": payload.get("sub"),
            "role": payload.get("role"),
            "email": payload.get("email"),
        }
        
        new_access_token = create_access_token(access_token_data)
        
        # Optional: Token rotation - create new refresh token
        new_refresh_token = create_refresh_token(access_token_data)
        
        # Blacklist old refresh token
        exp = datetime.fromtimestamp(payload.get("exp"))
        TokenBlacklist.add_to_blacklist(refresh_token, exp)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise


def revoke_token(token: str):
    """Revoke a token by adding it to blacklist"""
    try:
        payload = decode_token(token)
        exp = datetime.fromtimestamp(payload.get("exp"))
        TokenBlacklist.add_to_blacklist(token, exp)
    except JWTError:
        pass  # Token is already invalid


def get_token_expiry(token: str) -> Optional[datetime]:
    """Get token expiration time"""
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        if exp:
            return datetime.fromtimestamp(exp)
        return None
    except JWTError:
        return None
