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


def test_exchange_code_for_token_success(client, monkeypatch):
    from unittest.mock import MagicMock

    import httpx

    # Mock the AsyncClient
    mock_token_response = MagicMock()
    mock_token_response.json.return_value = {"access_token": "mock_provider_token"}
    mock_token_response.raise_for_status = MagicMock()

    mock_user_response = MagicMock()
    mock_user_response.json.return_value = {"email": "test@example.com"}
    mock_user_response.raise_for_status = MagicMock()

    async def mock_post(*args, **kwargs):
        return mock_token_response

    async def mock_get(*args, **kwargs):
        return mock_user_response

    class MockAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        post = mock_post
        get = mock_get

    monkeypatch.setattr(httpx, "AsyncClient", lambda: MockAsyncClient())

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
