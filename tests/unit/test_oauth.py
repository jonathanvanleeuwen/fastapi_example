from unittest.mock import AsyncMock, patch

import pytest


def test_get_authorization_url_google(client):
    request_data = {"provider": "google", "redirect_uri": "http://localhost/callback"}
    response = client.post("/auth/oauth/authorize", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "accounts.google.com" in data["authorization_url"]
    assert "test_client_id" in data["authorization_url"]


def test_get_authorization_url_azure(client):
    request_data = {"provider": "azure", "redirect_uri": "http://localhost/callback"}
    response = client.post("/auth/oauth/authorize", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "login.microsoftonline.com" in data["authorization_url"]


def test_get_authorization_url_github(client):
    request_data = {"provider": "github", "redirect_uri": "http://localhost/callback"}
    response = client.post("/auth/oauth/authorize", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "authorization_url" in data
    assert "github.com" in data["authorization_url"]


def test_get_authorization_url_invalid_provider(client):
    request_data = {
        "provider": "invalid_provider",
        "redirect_uri": "http://localhost/callback",
    }
    response = client.post("/auth/oauth/authorize", json=request_data)

    assert response.status_code == 400
    assert "Unsupported OAuth provider" in response.json()["detail"]


@pytest.mark.asyncio
async def test_exchange_code_for_token_success(client):
    mock_token_response = AsyncMock()
    mock_token_response.json.return_value = {"access_token": "mock_provider_token"}
    mock_token_response.raise_for_status = AsyncMock()

    mock_user_response = AsyncMock()
    mock_user_response.json.return_value = {"email": "test@example.com"}
    mock_user_response.raise_for_status = AsyncMock()

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_token_response
        )
        mock_client.return_value.__aenter__.return_value.get.return_value = (
            mock_user_response
        )

        request_data = {
            "provider": "google",
            "code": "test_code",
            "redirect_uri": "http://localhost/callback",
        }
        response = client.post("/auth/oauth/token", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
