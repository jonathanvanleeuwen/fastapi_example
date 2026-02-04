import pytest

from fastapi_example.auth.oauth_auth import create_access_token


@pytest.fixture
def oauth_token():
    """Create a valid OAuth JWT token for testing."""
    token_data = {"sub": "test@example.com", "provider": "google"}
    return create_access_token(token_data)


@pytest.fixture
def oauth_headers(oauth_token):
    """Headers with valid OAuth JWT token."""
    return {"Authorization": f"Bearer {oauth_token}"}


def test_oauth_add_endpoint(client, oauth_headers, sample_input_data):
    response = client.post(
        "/oauth_protected/add", json=sample_input_data, headers=oauth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "add"
    assert data["result"] == 15.0
    assert data["user"] == "test@example.com"


def test_oauth_subtract_endpoint(client, oauth_headers, sample_input_data):
    response = client.post(
        "/oauth_protected/subtract", json=sample_input_data, headers=oauth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "subtract"
    assert data["result"] == 5.0
    assert data["user"] == "test@example.com"


def test_oauth_multiply_endpoint(client, oauth_headers, sample_input_data):
    response = client.post(
        "/oauth_protected/multiply", json=sample_input_data, headers=oauth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "multiply"
    assert data["result"] == 50.0
    assert data["user"] == "test@example.com"


def test_oauth_divide_endpoint(client, oauth_headers, sample_input_data):
    response = client.post(
        "/oauth_protected/divide", json=sample_input_data, headers=oauth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "divide"
    assert data["result"] == 2.0
    assert data["user"] == "test@example.com"


def test_oauth_endpoint_without_token(client, sample_input_data):
    response = client.post("/oauth_protected/add", json=sample_input_data)
    assert response.status_code == 401


def test_oauth_endpoint_with_invalid_token(client, sample_input_data):
    invalid_headers = {"Authorization": "Bearer invalid_token"}
    response = client.post(
        "/oauth_protected/add", json=sample_input_data, headers=invalid_headers
    )
    assert response.status_code == 401


def test_oauth_endpoint_with_expired_token(client, sample_input_data):
    from datetime import timedelta

    expired_token = create_access_token(
        {"sub": "test@example.com"}, expires_delta=timedelta(seconds=-1)
    )
    expired_headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.post(
        "/oauth_protected/add", json=sample_input_data, headers=expired_headers
    )
    assert response.status_code == 401
