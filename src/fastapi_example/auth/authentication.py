import logging
from collections.abc import Callable

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
    api_keys should be a dict with the following structure:
    {
        "api_key_string": {
            "username": str,
            "roles": list[str]
        }
    }

    The function checks:
      - If the API key exists
      - If allowed_roles is given, user must have at least one matching role
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

        # If roles are required, enforce them
        if allowed_roles and not any(role in roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have required role",
            )

        logger.info(f"Authenticated user: {username} with roles {roles}")
        request.state.user = username
        request.state.roles = roles

    return bearer_auth


def get_current_user(request: Request) -> str:
    return request.state.user


auth_admin = get_bearer_dependency(get_settings().api_keys, allowed_roles=["admin"])
auth_user = get_bearer_dependency(
    get_settings().api_keys, allowed_roles=["admin", "user"]
)
auth_any = get_bearer_dependency(get_settings().api_keys)  # any valid key
