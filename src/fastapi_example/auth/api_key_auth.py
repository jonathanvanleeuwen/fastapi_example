import logging
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_example.settings import get_settings

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


def get_bearer_dependency(
    api_keys: dict[str, dict[str, str | list[str]]],
    allowed_roles: list[str] | None = None,
) -> Callable:
    """
    Creates a dependency that validates API key authentication.

    Args:
        api_keys: Dictionary mapping API keys to user info with structure:
            {
                "api_key_string": {
                    "username": str,
                    "roles": list[str]
                }
            }
        allowed_roles: Optional list of roles. User must have at least one matching role.

    Returns:
        Dependency function that validates the API key and checks roles.
    """

    async def bearer_auth(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),  # noqa: B008
    ) -> None:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing Authorization header",
            )

        token = credentials.credentials
        user_info = api_keys.get(token)

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

    return bearer_auth


def get_current_user(request: Request) -> dict[str, Any] | None:
    """Get current user info (works for both API key and OAuth)."""
    return getattr(request.state, "user_info", None)


auth_admin = get_bearer_dependency(get_settings().api_keys, allowed_roles=["admin"])
auth_user = get_bearer_dependency(
    get_settings().api_keys, allowed_roles=["admin", "user"]
)
auth_any = get_bearer_dependency(get_settings().api_keys)
