from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.api.config import get_settings, get_bool_env
from src.db.models import User
from src.db.session import get_db

# Use a stable, pure-Python KDF by default to avoid environment-specific bcrypt backend issues.
# pbkdf2_sha256 is widely supported and avoids native extension pitfalls seen with bcrypt in CI.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

settings = get_settings()


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a stored hash.

    Uses the configured Passlib CryptContext (pbkdf2_sha256).
    """
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hash a password using the configured KDF (pbkdf2_sha256)."""
    return pwd_context.hash(password)


def _token_exp_seconds() -> int:
    try:
        return int(os.getenv("JWT_EXPIRES_IN", "3600"))
    except ValueError:
        return 3600


# PUBLIC_INTERFACE
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token for the given subject (user id or email)."""
    expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(seconds=_token_exp_seconds()))
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


# PUBLIC_INTERFACE
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT or allow dev bypass if enabled."""
    # Support dev bypass
    if get_bool_env("DEV_AUTH_BYPASS", False):
        dev_user_email = os.getenv("DEV_AUTH_USER_EMAIL", "dev@example.com")
        user = db.query(User).filter(User.email == dev_user_email).first()
        if user is None:
            # Auto-provision lightweight dev user if not existing
            user = User(email=dev_user_email, full_name="Dev User", hashed_password=get_password_hash("devpassword"))
            db.add(user)
            db.commit()
            db.refresh(user)
        return user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        subject: Optional[str] = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Treat subject as email (simpler for this basic CRM)
    user = db.query(User).filter(User.email == subject).first()
    if user is None:
        raise credentials_exception
    return user
