import base64
import json
import logging
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

    # LLM API
    model_name: str = "gemini-2.5-flash"
    openai_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    openai_api_key: str

    # Prompt templates
    extraction_system_prompt: str = ""  # Set in load_system_prompt

    # Authentication settings
    api_keys: dict[str, str] | str = ""

    # logging
    app_log_level: int = logging.INFO  # 20: info, 10: debug

    # Validate that all api key values are unique
    @model_validator(mode="after")
    def ensure_unique_values(self) -> "Settings":
        # base64 decode if string
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