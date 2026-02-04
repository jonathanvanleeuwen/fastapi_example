import logging
from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_example.settings import Settings, get_settings

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(request: Request) -> dict[str, Any] | None:
    """Get current user info (works for both API key and OAuth)."""
    return getattr(request.state, "user_info", None)


def create_auth_dependency(allowed_roles: list[str] | None = None) -> Callable:
    """
    Creates an API key authentication dependency with optional role checking.

    Args:
        allowed_roles: Optional list of roles. User must have at least one matching role.

    Returns:
        FastAPI dependency that validates API key and checks roles.
    """

    async def check_api_key(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),  # noqa: B008
        settings: Settings = Depends(get_settings),  # noqa: B008
    ) -> None:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing Authorization header",
            )

        token = credentials.credentials
        user_info = settings.api_keys.get(token)

        if user_info is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API Key",
            )

        username = user_info.get("username")
        roles = user_info.get("roles", [])

        if allowed_roles and not any(role in roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have required role",
            )

        # Standardized user info structure (compatible with OAuth)
        user_data = {
            "sub": username,
            "auth_type": "api_key",
            "roles": roles,
        }

        logger.info(f"Authenticated user: {username} with roles {roles}")
        request.state.user_info = user_data

    return check_api_key


# Authentication dependencies
auth_admin = create_auth_dependency(allowed_roles=["admin"])
auth_user = create_auth_dependency(allowed_roles=["admin", "user"])
auth_any = create_auth_dependency()
