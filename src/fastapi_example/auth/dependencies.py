import logging
from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_example.auth.oauth_auth import verify_access_token
from fastapi_example.settings import Settings, get_settings
from fastapi_example.utils.auth_utils import hash_api_key

logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)

# Module-level singletons to satisfy B008 linter rule
_security_bearer = Security(bearer_scheme)
_depends_settings = Depends(get_settings)


def _check_roles(user_roles: list[str], allowed_roles: list[str] | None) -> None:
    if allowed_roles and not any(role in user_roles for role in allowed_roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have required role",
        )


def _try_api_key_auth(
    token: str, settings: Settings, allowed_roles: list[str] | None
) -> dict[str, Any] | None:
    hashed_token = hash_api_key(token)
    user_info = settings.api_keys.get(hashed_token)

    if not user_info:
        return None

    username = user_info.get("username")
    roles = user_info.get("roles", [])

    _check_roles(roles, allowed_roles)

    user_data = {
        "sub": username,
        "auth_type": "api_key",
        "roles": roles,
    }
    logger.info(
        "Authenticated via API key, user: %s, roles: %s",
        username,
        roles,
        extra={"user": username},
    )
    return user_data


def _try_oauth_auth(
    token: str, allowed_roles: list[str] | None
) -> dict[str, Any] | None:
    try:
        payload = verify_access_token(token)
        user_email = payload.get("sub")

        if not user_email:
            return None

        oauth_roles = payload.get("roles", [])
        _check_roles(oauth_roles, allowed_roles)

        user_data = {
            "sub": user_email,
            "auth_type": "oauth",
            "provider": payload.get("provider", "unknown"),
            "roles": oauth_roles,
        }
        logger.info(
            "Authenticated via OAuth: %s, roles: %s",
            user_email,
            oauth_roles,
            extra={"user": user_email},
        )
        return user_data
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            detail="OAuth authentication failed",
            headers={"Location": "/auth/oauth/authorize"},
        ) from None


def create_auth(allowed_roles: list[str] | None = None) -> Callable:
    async def auth_dependency(
        request: Request,
        credentials: HTTPAuthorizationCredentials = _security_bearer,
        settings: Settings = _depends_settings,
    ) -> dict[str, Any]:
        if not credentials or credentials.scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing Authorization header",
            )

        token = credentials.credentials

        user_data = _try_api_key_auth(token, settings, allowed_roles)
        if user_data:
            request.state.user_info = user_data
            return user_data

        user_data = _try_oauth_auth(token, allowed_roles)
        if user_data:
            request.state.user_info = user_data
            return user_data

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return auth_dependency
