import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login/form"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
    subject: Any = None,
    expires_delta: Optional[timedelta] = None,
    data: Optional[dict] = None,
) -> str:
    """Creates a signed JWT access token. Accepts subject or a dict payload."""
    to_encode = {}
    if data:
        to_encode.update(data)
    if subject is not None:
        to_encode["sub"] = str(subject)

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Validates the JWT token and returns the current authenticated User model."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        sub: str = payload.get("sub")
        if not sub:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Try resolving 'sub' as a UUID object first
    user = None
    try:
        user_uuid = uuid.UUID(sub)
        user = db.scalar(select(User).where(User.id == user_uuid))
    except ValueError:
        # Fallback if 'sub' was populated with user email
        user = db.scalar(select(User).where(User.email == sub))

    if user is None or not user.is_active:
        raise credentials_exception

    return user