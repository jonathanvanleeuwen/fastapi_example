import base64
import json
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings

from fastapi_example.utils import hash_api_key


class Settings(BaseSettings):
    app_name: str = "fastapi_example"
    description: str = "fastapi_example api"

    cors_allow_origins: tuple = ("http://localhost:3000", "http://127.0.0.1:3000", "*")

    api_keys: dict[str, dict] | str = (
        "eyJ0ZXN0Ijp7InVzZXJuYW1lIjoiSm9uYXRoYW4iLCJyb2xlcyI6WyJhZG1pbiIsInVzZXIiXX0sInRlc3QyIjp7InVzZXJuYW1lIjoiYm9iIiwicm9sZXMiOlsidXNlciJdfX0="
    )

    oauth_provider: str = "github"
    oauth_secret_key: str = "your-secret-key-min-32-chars-change-in-production"
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_access_token_expire_minutes: int = 30

    @model_validator(mode="after")
    def process_api_keys(self) -> "Settings":
        if isinstance(self.api_keys, str):
            decoded = base64.b64decode(self.api_keys).decode()
            self.api_keys = json.loads(decoded)

        api_key_list = list(self.api_keys.keys())
        if len(api_key_list) != len(set(api_key_list)):
            raise ValueError("All Keys in 'api_keys' must be unique")

        hashed_keys = {}
        for key, value in self.api_keys.items():
            hashed_key = hash_api_key(key)
            hashed_keys[hashed_key] = value

        self.api_keys = hashed_keys
        return self

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache
def get_settings() -> Settings:
    return Settings()
