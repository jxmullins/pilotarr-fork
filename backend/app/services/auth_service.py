"""
Auth service — password hashing, JWT creation/verification, user management.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import TypedDict

import bcrypt
import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import User

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"


class AccessTokenClaims(TypedDict):
    username: str
    token_version: int


# ---------------------------------------------------------------------------
# Password helpers (bcrypt directly — no passlib)
# ---------------------------------------------------------------------------


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------


def create_access_token(username: str, token_version: int = 0) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": username, "exp": expire, "ver": int(token_version)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Decode a JWT and return the username, or None if invalid/expired."""
    claims = decode_access_token_claims(token)
    return claims["username"] if claims else None


def decode_access_token_claims(token: str) -> AccessTokenClaims | None:
    """Decode a JWT and return the validated username/version claims."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_version = payload.get("ver", 0)

        if not username or not isinstance(username, str):
            logger.warning("JWT missing subject")
            return None

        if isinstance(token_version, str):
            if not token_version.isdigit():
                logger.warning("JWT token version is not numeric")
                return None
            token_version = int(token_version)

        if not isinstance(token_version, int):
            logger.warning("JWT token version is invalid")
            return None

        return {"username": username, "token_version": token_version}
    except jwt.ExpiredSignatureError:
        logger.warning("JWT expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT")
        return None


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def init_default_user(db: Session) -> None:
    """Create a bootstrap admin user once when explicitly configured."""
    username = (settings.BOOTSTRAP_ADMIN_USERNAME or "").strip() or None
    password = settings.BOOTSTRAP_ADMIN_PASSWORD

    if not username and not password:
        logger.info("Bootstrap admin credentials not configured; skipping initial admin creation")
        return

    if not username or not password:
        logger.warning("Incomplete bootstrap admin credentials; skipping initial admin creation")
        return

    existing_user = db.query(User.id).first()
    if existing_user:
        return

    user = User(username=username, hashed_password=hash_password(password), is_active=True)
    db.add(user)
    db.commit()
    logger.info("✅ Bootstrap user '%s' created", username)
