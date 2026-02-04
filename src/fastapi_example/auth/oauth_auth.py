import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2AuthorizationCodeBearer

from fastapi_example.settings import get_settings

logger = logging.getLogger(__name__)


class OAuthProvider:
    """Base class for OAuth providers with minimal configuration."""

    def __init__(
        self,
        provider_name: str,
        client_id: str,
        client_secret: str,
        authorization_url: str,
        token_url: str,
        userinfo_url: str,
    ):
        self.provider_name = provider_name
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorization_url = authorization_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url


def create_oauth_provider(provider_type: str) -> OAuthProvider:
    """
    Factory function to create OAuth provider based on type.

    Supported providers:
    - google: Google OAuth
    - azure: Microsoft Azure AD
    - github: GitHub OAuth
    """
    settings = get_settings()

    providers_config = {
        "google": {
            "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        },
        "azure": {
            "authorization_url": f"https://login.microsoftonline.com/{settings.oauth_tenant_id}/oauth2/v2.0/authorize",
            "token_url": f"https://login.microsoftonline.com/{settings.oauth_tenant_id}/oauth2/v2.0/token",
            "userinfo_url": "https://graph.microsoft.com/v1.0/me",
        },
        "github": {
            "authorization_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "userinfo_url": "https://api.github.com/user",
        },
    }

    if provider_type not in providers_config:
        raise ValueError(f"Unsupported OAuth provider: {provider_type}")

    config = providers_config[provider_type]

    return OAuthProvider(
        provider_name=provider_type,
        client_id=settings.oauth_client_id,
        client_secret=settings.oauth_client_secret,
        authorization_url=config["authorization_url"],
        token_url=config["token_url"],
        userinfo_url=config["userinfo_url"],
    )


oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/auth/oauth/authorize",
    tokenUrl="/auth/oauth/token",
    auto_error=False,
)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token."""
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.now(timezone.UTC) + (
        expires_delta or timedelta(minutes=settings.oauth_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.oauth_secret_key, algorithm="HS256")


def verify_access_token(token: str) -> dict[str, Any]:
    """Verify and decode a JWT access token."""
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
    token: str | None = Depends(oauth2_scheme),
) -> dict[str, Any]:
    """Dependency to get current user from OAuth token."""
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

    # Standardized user info structure (compatible with API key)
    user_data = {
        "sub": user_email,
        "auth_type": "oauth",
        "provider": payload.get("provider", "unknown"),
    }

    logger.info(f"Authenticated OAuth user: {user_email}")
    request.state.user_info = user_data
    return user_data


def get_current_user(request: Request) -> dict[str, Any] | None:
    """Get current user info (works for both API key and OAuth)."""
    return getattr(request.state, "user_info", None)
