"""OAuth service layer for handling OAuth operations."""

import logging
from typing import Any

import httpx
from fastapi import HTTPException, status

from fastapi_example.auth.oauth_providers import OAUTH_PROVIDERS

logger = logging.getLogger(__name__)


def get_oauth_config(provider: str) -> dict[str, str]:
    """Get OAuth configuration for a provider.

    Args:
        provider: The OAuth provider name (e.g., 'github', 'google')

    Returns:
        Dictionary containing provider configuration

    Raises:
        ValueError: If provider is not supported
    """
    if provider not in OAUTH_PROVIDERS:
        raise ValueError(f"Unsupported OAuth provider: {provider}")

    return OAUTH_PROVIDERS[provider]


def build_authorization_url(
    provider: str,
    client_id: str,
    redirect_uri: str,
) -> str:
    """Build OAuth authorization URL.

    Args:
        provider: OAuth provider name
        client_id: OAuth client ID
        redirect_uri: Redirect URI after authorization

    Returns:
        Complete authorization URL
    """
    oauth_config = get_oauth_config(provider)

    return (
        f"{oauth_config['authorization_url']}"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={oauth_config['scope']}"
    )


async def exchange_code_for_provider_token(
    provider: str,
    code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> str:
    """Exchange authorization code for provider access token.

    Args:
        provider: OAuth provider name
        code: Authorization code
        client_id: OAuth client ID
        client_secret: OAuth client secret
        redirect_uri: Redirect URI used during authorization

    Returns:
        Provider access token

    Raises:
        HTTPException: If token exchange fails
    """
    oauth_config = get_oauth_config(provider)

    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
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
            logger.error("Failed to exchange code for token: %s", e)
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

    return provider_access_token


async def get_user_info_from_provider(
    provider: str,
    provider_access_token: str,
) -> dict[str, Any]:
    """Get user information from OAuth provider.

    Args:
        provider: OAuth provider name
        provider_access_token: Access token from provider

    Returns:
        User information dictionary

    Raises:
        HTTPException: If user info retrieval fails
    """
    oauth_config = get_oauth_config(provider)

    async with httpx.AsyncClient() as client:
        try:
            user_response = await client.get(
                oauth_config["userinfo_url"],
                headers={"Authorization": f"Bearer {provider_access_token}"},
            )
            user_response.raise_for_status()
            return user_response.json()
        except httpx.HTTPError as e:
            logger.error("Failed to get user info: %s", e)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user information",
            ) from e


def extract_user_email(user_info: dict[str, Any]) -> str:
    """Extract email from user info.

    Args:
        user_info: User information dictionary from provider

    Returns:
        User email address

    Raises:
        HTTPException: If email not found in user info
    """
    user_email = user_info.get("email") or user_info.get("mail")

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in user info",
        )

    return user_email
