"""
Unified authentication that works with both API key and OAuth.
This module provides dependencies that can be applied at the router level.
"""

import logging
from typing import Any

from fastapi import HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_example.auth.api_key_auth import get_bearer_dependency
from fastapi_example.auth.oauth_auth import get_current_oauth_user
from fastapi_example.settings import get_settings

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


async def authenticate_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),  # noqa: B008
) -> dict[str, Any]:
    """
    Unified authentication that tries OAuth first, then falls back to API key.
    Sets request.state.user_info with standardized user data.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing Authorization header",
        )

    token = credentials.credentials
    settings = get_settings()

    # Try OAuth JWT token first
    try:
        from fastapi_example.auth.oauth_auth import verify_access_token

        payload = verify_access_token(token)
        user_email = payload.get("sub")

        if user_email:
            user_data = {
                "sub": user_email,
                "auth_type": "oauth",
                "provider": payload.get("provider", "unknown"),
            }
            request.state.user_info = user_data
            logger.info(f"Authenticated via OAuth: {user_email}")
            return user_data
    except HTTPException:
        # Not a valid OAuth token, try API key
        pass

    # Try API key
    api_keys = settings.api_keys
    user_info = api_keys.get(token)

    if user_info:
        username = user_info.get("username")
        roles = user_info.get("roles", [])

        user_data = {
            "sub": username,
            "auth_type": "api_key",
            "roles": roles,
        }
        request.state.user_info = user_data
        logger.info(f"Authenticated via API key: {username}")
        return user_data

    # Neither OAuth nor API key worked
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
    )


async def require_role(required_roles: list[str] | None = None):
    """
    Dependency factory that checks if user has required roles.
    Only applies to API key authentication (OAuth doesn't use roles).
    """

    async def check_role(request: Request) -> None:
        user_info = getattr(request.state, "user_info", None)

        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        # OAuth users pass through (no role checking)
        if user_info.get("auth_type") == "oauth":
            return

        # API key users need role checking
        if required_roles:
            user_roles = user_info.get("roles", [])
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

    return check_role


# Pre-configured dependencies for common use cases
api_key_admin = get_bearer_dependency(get_settings().api_keys, allowed_roles=["admin"])
api_key_user = get_bearer_dependency(
    get_settings().api_keys, allowed_roles=["admin", "user"]
)
oauth_required = get_current_oauth_user
