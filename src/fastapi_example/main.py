import logging
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from fastapi_example.auth.dependencies import create_auth
from fastapi_example.custom_logger.setup.setup_logger import setup_logging
from fastapi_example.routers.math import math_router
from fastapi_example.routers.oauth import oauth_router
from fastapi_example.settings import get_settings

settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="1.0",
    description=settings.description,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for OAuth testing frontend (illustrative purposes only)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount(
        "/static", StaticFiles(directory=str(static_dir), html=True), name="static"
    )


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")


app.include_router(oauth_router)
app.include_router(math_router, dependencies=[Depends(create_auth(["admin", "user"]))])
