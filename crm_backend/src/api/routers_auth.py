from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.api.schemas import LoginRequest, Token, UserCreate, UserOut
from src.api.security import create_access_token, verify_password, get_password_hash
from src.db.models import User
from src.db.session import get_db

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


# PUBLIC_INTERFACE
@router.post(
    "/login",
    response_model=Token,
    summary="Login",
    description="Authenticate with email and password to obtain a JWT bearer token.",
    responses={401: {"description": "Invalid credentials"}, 422: {"description": "Validation Error"}},
)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> Token:
    """Authenticate a user and issue JWT token.

    Parameters:
        data: LoginRequest containing email and password.
    Returns:
        Token: Bearer token and TTL.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(subject=user.email, expires_delta=timedelta(seconds=3600))
    return Token(access_token=access_token, expires_in=3600)


# PUBLIC_INTERFACE
@router.post(
    "/signup",
    response_model=UserOut,
    status_code=201,
    summary="Signup",
    description="Create a user account. In production, restrict this endpoint appropriately.",
    responses={
        201: {"description": "User created"},
        400: {"description": "Invalid request"},
        409: {"description": "User already exists"},
        422: {"description": "Validation Error"},
    },
)
def signup(data: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    """Create a new user for bootstrapping.

    Parameters:
        data: UserCreate
    Returns:
        UserOut
    """
    # Check explicit existence to provide a friendly error; still handle race with IntegrityError.
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user = User(email=data.email, full_name=data.full_name, hashed_password=get_password_hash(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        # Likely unique constraint violation (duplicate email) or other integrity issue.
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    except Exception:
        db.rollback()
        # Avoid leaking internal errors to clients; instruct client to try again.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create user")
    db.refresh(user)
    return UserOut.model_validate(user)
