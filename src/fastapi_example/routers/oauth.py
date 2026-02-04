import logging
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from fastapi_example.auth.oauth_auth import create_access_token, create_oauth_provider
from fastapi_example.settings import get_settings

logger = logging.getLogger(__name__)

oauth_router = APIRouter(tags=["oauth"], prefix="/auth/oauth")


class AuthorizationRequest(BaseModel):
    provider: str
    redirect_uri: str


class TokenRequest(BaseModel):
    provider: str
    code: str
    redirect_uri: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@oauth_router.post("/authorize", operation_id="get_authorization_url", status_code=200)
def get_authorization_url(request: AuthorizationRequest) -> dict[str, str]:
    """
    Get the OAuth authorization URL for a specific provider.

    This is the first step in the OAuth flow.
    Redirect the user to this URL so they can authorize your app.
    """
    try:
        provider = create_oauth_provider(request.provider)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    settings = get_settings()
    scopes = {
        "google": "openid email profile",
        "azure": "openid email profile",
        "github": "user:email",
    }

    scope = scopes.get(request.provider, "email")

    auth_url = (
        f"{provider.authorization_url}"
        f"?client_id={provider.client_id}"
        f"&redirect_uri={request.redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
    )

    if request.provider == "azure":
        auth_url += f"&tenant={settings.oauth_tenant_id}"

    logger.info(f"Generated authorization URL for provider: {request.provider}")
    return {"authorization_url": auth_url}


@oauth_router.post("/token", operation_id="exchange_code_for_token", status_code=200)
async def exchange_code_for_token(request: TokenRequest) -> TokenResponse:
    """
    Exchange the authorization code for an access token.

    This is the second step in the OAuth flow.
    After the user authorizes, they'll be redirected back with a code.
    Exchange that code here for an access token.
    """
    try:
        provider = create_oauth_provider(request.provider)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    token_data = {
        "client_id": provider.client_id,
        "client_secret": provider.client_secret,
        "code": request.code,
        "redirect_uri": request.redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                provider.token_url,
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
                provider.userinfo_url,
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
        "provider": request.provider,
    }
    access_token = create_access_token(token_data_to_encode)

    logger.info(f"Successfully authenticated user: {user_email} via {request.provider}")

    return TokenResponse(access_token=access_token)
