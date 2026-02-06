import pytest
from fastapi.testclient import TestClient

from fastapi_example.main import app
from fastapi_example.settings import Settings, get_settings


@pytest.fixture
def test_api_keys():
    """Sample API keys for testing."""
    return {
        "test_admin_key": {"username": "test_admin", "roles": ["admin", "user"]},
        "test_user_key": {"username": "test_user", "roles": ["user"]},
    }


@pytest.fixture
def test_settings(test_api_keys):
    """Override settings for testing."""

    class TestSettings(Settings):
        api_keys: dict = test_api_keys
        oauth_secret_key: str = "test_secret_key_at_least_32_characters_long"
        oauth_client_id: str = "test_client_id"
        oauth_client_secret: str = "test_client_secret"
        oauth_tenant_id: str = "test_tenant_id"

    return TestSettings()


@pytest.fixture
def override_settings(test_settings):
    """Override the get_settings dependency."""
    # Clear the lru_cache to ensure fresh settings
    get_settings.cache_clear()
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def client(override_settings):
    """FastAPI test client with overridden settings."""
    return TestClient(app)


@pytest.fixture
def admin_headers():
    """Headers with admin API key."""
    return {"Authorization": "Bearer test_admin_key"}


@pytest.fixture
def user_headers():
    """Headers with user API key."""
    return {"Authorization": "Bearer test_user_key"}


@pytest.fixture
def invalid_headers():
    """Headers with invalid API key."""
    return {"Authorization": "Bearer invalid_key"}


@pytest.fixture
def sample_input_data():
    """Sample input data for math operations."""
    return {"A": 10.0, "B": 5.0}
