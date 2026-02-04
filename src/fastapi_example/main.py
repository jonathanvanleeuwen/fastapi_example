import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from fastapi_example.auth.api_key_auth import auth_admin, auth_user
from fastapi_example.auth.oauth_auth import get_current_oauth_user
from fastapi_example.auth.unified_auth import authenticate_request
from fastapi_example.custom_logger.setup.setup_logger import setup_logging
from fastapi_example.routers.oauth import oauth_router
from fastapi_example.routers.oauth_protected import oauth_protected_router
from fastapi_example.routers.production import fastapi_router
from fastapi_example.routers.testing import fastapi_test_router
from fastapi_example.routers.unified import unified_router
from fastapi_example.settings import get_settings

# Configure logger
settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(
    title=settings.app_name,
    version="1.0",
    description=settings.description,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


# OAuth flow endpoints (no auth required)
app.include_router(oauth_router)

# Unified endpoints (accepts BOTH OAuth JWT tokens AND API keys)
# Uses authenticate_request to try OAuth first, then API key
app.include_router(unified_router, dependencies=[Depends(authenticate_request)])

# OAuth-protected endpoints (requires OAuth JWT token ONLY)
# Dependencies applied at router level
app.include_router(
    oauth_protected_router, dependencies=[Depends(get_current_oauth_user)]
)

# API key protected endpoints (requires API key with admin role ONLY)
# Dependencies applied at router level
app.include_router(fastapi_router, dependencies=[Depends(auth_admin)])

# Test endpoints (requires API key with user or admin role)
# Dependencies applied at router level
if settings.stage != "production":
    app.include_router(fastapi_test_router, dependencies=[Depends(auth_user)])
