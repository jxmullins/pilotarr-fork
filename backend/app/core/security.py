import hashlib
import hmac
from collections import defaultdict, deque
from collections.abc import Mapping
from time import time

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

_webhook_rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)


def clear_webhook_rate_limit_state():
    """Test helper: clear in-memory webhook rate-limit buckets."""
    _webhook_rate_limit_buckets.clear()


def validate_webhook_secret(headers: Mapping[str, str], body: bytes):
    """Validate webhook secret using plain secret header or HMAC SHA-256 signature."""
    webhook_secret = settings.WEBHOOK_SECRET
    if not webhook_secret:
        return

    request_secret = headers.get("X-Webhook-Secret", "")
    if request_secret and hmac.compare_digest(request_secret, webhook_secret):
        return

    request_signature = headers.get("X-Webhook-Signature", "")
    expected_signature = "sha256=" + hmac.new(
        webhook_secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()
    if request_signature and hmac.compare_digest(request_signature, expected_signature):
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Secret webhook invalide")


# ---------------------------------------------------------------------------
# Webhook: ?apiKey=xxx query parameter (machine-to-machine, Jellyfin webhook)
# ---------------------------------------------------------------------------


async def verify_webhook_api_key(api_key: str = Query(..., alias="apiKey")):
    """Check that ?apiKey= query parameter matches the configured key."""
    if not hmac.compare_digest(api_key, settings.API_KEY):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API Key")
    return api_key


async def enforce_webhook_rate_limit(request: Request):
    """Simple in-memory rate limit to reduce webhook abuse."""
    client_host = request.client.host if request.client else "unknown"
    now = time()
    window = settings.WEBHOOK_RATE_LIMIT_WINDOW_SECONDS
    limit = settings.WEBHOOK_RATE_LIMIT_MAX_REQUESTS
    bucket = _webhook_rate_limit_buckets[client_host]

    while bucket and now - bucket[0] > window:
        bucket.popleft()

    if len(bucket) >= limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many webhook requests")

    bucket.append(now)


# ---------------------------------------------------------------------------
# Bearer JWT for all user-facing routes
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
):
    """
    Validate a Bearer JWT and return the corresponding User ORM object.

    Import is deferred to avoid circular dependency between security ↔ auth_service ↔ models.
    """
    from app.db import SessionLocal
    from app.services.auth_service import decode_access_token, get_user_by_username

    token = credentials.credentials
    username = decode_access_token(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = SessionLocal()
    try:
        user = get_user_by_username(db, username)
    finally:
        db.close()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
