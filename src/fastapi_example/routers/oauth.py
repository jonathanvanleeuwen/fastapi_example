import logging
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from fastapi_example.auth.oauth_auth import create_access_token, get_oauth_config
from fastapi_example.models.oauth import (
    AuthorizationRequest,
    TokenRequest,
    TokenResponse,
)
from fastapi_example.settings import Settings, get_settings

logger = logging.getLogger(__name__)

# Module-level singleton to satisfy B008 linter rule
_depends_settings = Depends(get_settings)

oauth_router = APIRouter(tags=["oauth"], prefix="/auth/oauth")


@oauth_router.get("/provider", status_code=200)
def get_provider_info(
    settings: Settings = _depends_settings,
) -> dict[str, str]:
    """Get the configured OAuth provider name."""
    return {"provider": settings.oauth_provider}


@oauth_router.post("/authorize", status_code=200)
def get_authorization_url(
    request: AuthorizationRequest,
    settings: Settings = _depends_settings,
) -> dict[str, str]:
    oauth_config = get_oauth_config()

    auth_url = (
        f"{oauth_config['authorization_url']}"
        f"?client_id={settings.oauth_client_id}"
        f"&redirect_uri={request.redirect_uri}"
        f"&response_type=code"
        f"&scope={oauth_config['scope']}"
    )

    logger.info(f"Generated authorization URL for provider: {settings.oauth_provider}")
    return {"authorization_url": auth_url}


@oauth_router.post("/token", status_code=200)
async def exchange_code_for_token(
    request: TokenRequest,
    settings: Settings = _depends_settings,
) -> TokenResponse:
    oauth_config = get_oauth_config()

    token_data = {
        "client_id": settings.oauth_client_id,
        "client_secret": settings.oauth_client_secret,
        "code": request.code,
        "redirect_uri": request.redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                oauth_config["token_url"],
                data=token_data,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            oauth_tokens = response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to exchange code for token: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code",
            ) from e

        provider_access_token = oauth_tokens.get("access_token")
        if not provider_access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token in response",
            )

        try:
            user_response = await client.get(
                oauth_config["userinfo_url"],
                headers={"Authorization": f"Bearer {provider_access_token}"},
            )
            user_response.raise_for_status()
            user_info = user_response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user information",
            ) from e

    user_email = user_info.get("email") or user_info.get("mail")

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in user info",
        )

    token_data_to_encode: dict[str, Any] = {
        "sub": user_email,
        "provider": settings.oauth_provider,
    }
    access_token = create_access_token(token_data_to_encode, roles=["admin"])

    logger.info(
        f"Successfully authenticated user: {user_email} via {settings.oauth_provider}"
    )

    return TokenResponse(access_token=access_token)
