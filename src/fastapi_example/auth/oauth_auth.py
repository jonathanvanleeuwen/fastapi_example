import logging
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2AuthorizationCodeBearer

from fastapi_example.settings import get_settings

logger = logging.getLogger(__name__)


OAUTH_PROVIDERS = {
    "github": {
        "authorization_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scope": "user:email",
    },
    "google": {
        "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile",
    },
}


def get_oauth_config() -> dict[str, str]:
    settings = get_settings()
    provider = settings.oauth_provider

    if provider not in OAUTH_PROVIDERS:
        raise ValueError(f"Unsupported OAuth provider: {provider}")

    return OAUTH_PROVIDERS[provider]


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/auth/oauth/authorize",
    tokenUrl="/auth/oauth/token",
    auto_error=False,
)

# Module-level singleton to satisfy B008 linter rule
_depends_oauth2_scheme = Depends(oauth2_scheme)


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None,
    roles: list[str] | None = None,
) -> str:
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.oauth_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})

    if roles:
        to_encode["roles"] = roles

    return jwt.encode(to_encode, settings.oauth_secret_key, algorithm="HS256")


def verify_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.oauth_secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc


async def get_current_oauth_user(
    request: Request,
    token: str | None = _depends_oauth2_scheme,
) -> dict[str, Any]:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = verify_access_token(token)
    user_email = payload.get("sub")

    if user_email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user_data = {
        "sub": user_email,
        "auth_type": "oauth",
        "provider": payload.get("provider", "unknown"),
        "roles": payload.get("roles", []),
    }

    logger.info(f"Authenticated OAuth user: {user_email}")
    request.state.user_info = user_data
    return user_data


def get_current_user(request: Request) -> dict[str, Any] | None:
    """Get current user info (works for both API key and OAuth)."""
    return getattr(request.state, "user_info", None)
