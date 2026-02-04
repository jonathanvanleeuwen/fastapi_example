from datetime import timedelta

import pytest
from fastapi import HTTPException

from fastapi_example.auth.oauth_auth import (
    create_access_token,
    create_oauth_provider,
    verify_access_token,
)


def test_create_oauth_provider_google():
    provider = create_oauth_provider("google")
    assert provider.provider_name == "google"
    assert "accounts.google.com" in provider.authorization_url
    assert "oauth2.googleapis.com" in provider.token_url


def test_create_oauth_provider_azure():
    provider = create_oauth_provider("azure")
    assert provider.provider_name == "azure"
    assert "login.microsoftonline.com" in provider.authorization_url


def test_create_oauth_provider_github():
    provider = create_oauth_provider("github")
    assert provider.provider_name == "github"
    assert "github.com" in provider.authorization_url


def test_create_oauth_provider_invalid():
    with pytest.raises(ValueError, match="Unsupported OAuth provider"):
        create_oauth_provider("invalid_provider")


def test_create_access_token():
    data = {"sub": "test@example.com", "provider": "google"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_access_token_success():
    data = {"sub": "test@example.com", "provider": "google"}
    token = create_access_token(data)
    payload = verify_access_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["provider"] == "google"


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
