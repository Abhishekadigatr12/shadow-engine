import hashlib
import secrets
from typing import Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

from .config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_api_key() -> str:
    """Generate a random API key"""
    return secrets.token_urlsafe(32)


def hash_string(text: str) -> str:
    """Hash a string using SHA256"""
    return hashlib.sha256(text.encode()).hexdigest()


def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove null bytes and other dangerous characters
    sanitized = text.replace('\x00', '')
    return sanitized[:10000]  # Limit to 10k chars
