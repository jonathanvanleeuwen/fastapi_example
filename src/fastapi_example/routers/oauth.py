import logging

from fastapi import APIRouter, Depends

from fastapi_example.auth.oauth_auth import create_access_token
from fastapi_example.models.oauth import (
    AuthorizationRequest,
    TokenRequest,
    TokenResponse,
)
from fastapi_example.settings import Settings, get_settings
from fastapi_example.workers.oauth_service import (
    build_authorization_url,
    exchange_code_for_provider_token,
    extract_user_email,
    get_user_info_from_provider,
)

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
    """Generate OAuth authorization URL."""
    auth_url = build_authorization_url(
        provider=settings.oauth_provider,
        client_id=settings.oauth_client_id,
        redirect_uri=request.redirect_uri,
    )

    logger.info("Generated authorization URL for provider: %s", settings.oauth_provider)
    return {"authorization_url": auth_url}


@oauth_router.post("/token", status_code=200)
async def exchange_code_for_token(
    request: TokenRequest,
    settings: Settings = _depends_settings,
) -> TokenResponse:
    """Exchange authorization code for access token."""
    # Exchange code for provider access token
    provider_access_token = await exchange_code_for_provider_token(
        provider=settings.oauth_provider,
        code=request.code,
        client_id=settings.oauth_client_id,
        client_secret=settings.oauth_client_secret,
        redirect_uri=request.redirect_uri,
    )

    # Get user info from provider
    user_info = await get_user_info_from_provider(
        provider=settings.oauth_provider,
        provider_access_token=provider_access_token,
    )

    # Extract user email
    user_email = extract_user_email(user_info)

    # Create our internal access token
    access_token = create_access_token(
        data={"sub": user_email, "provider": settings.oauth_provider},
        roles=["admin"],
    )

    logger.info(
        "Successfully authenticated user: %s via %s",
        user_email,
        settings.oauth_provider,
    )

    return TokenResponse(access_token=access_token)
