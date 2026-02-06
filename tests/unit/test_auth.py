from datetime import timedelta

import pytest
from fastapi import HTTPException

from fastapi_example.auth.oauth_auth import (
    create_access_token,
    get_oauth_config,
    verify_access_token,
)


def test_get_oauth_config():
    config = get_oauth_config()
    assert "authorization_url" in config
    assert "token_url" in config
    assert "userinfo_url" in config
    assert "scope" in config
    assert "github.com" in config["authorization_url"]


def test_create_access_token():
    data = {"sub": "test@example.com", "provider": "github"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_access_token_success():
    data = {"sub": "test@example.com", "provider": "github"}
    token = create_access_token(data)
    payload = verify_access_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["provider"] == "github"


def test_verify_access_token_expired():
    data = {"sub": "test@example.com"}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))

    with pytest.raises(HTTPException) as exc_info:
        verify_access_token(token)
    assert exc_info.value.status_code == 401
    assert "expired" in exc_info.value.detail.lower()


def test_verify_access_token_invalid():
    with pytest.raises(HTTPException) as exc_info:
        verify_access_token("invalid_token")
    assert exc_info.value.status_code == 401
    assert "Invalid token" in exc_info.value.detail
