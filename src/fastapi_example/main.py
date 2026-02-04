import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from fastapi_example.auth.authentication import auth_admin, auth_user
from fastapi_example.custom_logger.setup.setup_logger import setup_logging
from fastapi_example.routers.production import fastapi_router
from fastapi_example.routers.testing import fastapi_test_router
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


# Add redirect from root to docs
@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


# Add routers
app.include_router(fastapi_router, dependencies=[Depends(auth_admin)])
if settings.stage != "production":
    app.include_router(fastapi_test_router, dependencies=[Depends(auth_user)])
