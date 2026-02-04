import base64
import json
from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    app_name: str = "fastapi_example"
    description: str = "fastapi_example api"
    stage: Literal["test", "development", "production"] = "development"

    # CORS
    cors_allow_origins: tuple = ("*",)

    # API Key Authentication settings
    api_keys: dict[str, str] | str = (
        "eyJ0ZXN0IjogeyJ1c2VybmFtZSI6ICJKb25hdGhhbiIsICJyb2xlcyI6IFsiYWRtaW4iLCAidXNlciJdfSwgInRlc3QyIjogeyJ1c2VybmFtZSI6ICJib2IiLCAicm9sZXMiOiBbInVzZXIiXX19"
    )

    # OAuth settings
    oauth_secret_key: str = "your-secret-key-min-32-chars-change-in-production"
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_tenant_id: str = ""
    oauth_access_token_expire_minutes: int = 30

    @model_validator(mode="after")
    def ensure_unique_values(self) -> "Settings":
        if isinstance(self.api_keys, str):
            decoded = base64.b64decode(self.api_keys).decode()
            self.api_keys = json.loads(decoded)
        secrets = list(self.api_keys.keys())
        if len(secrets) != len(set(secrets)):
            raise ValueError("All Keys in 'api_keys' must be unique")
        return self

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache
def get_settings() -> Settings:
    return Settings()
