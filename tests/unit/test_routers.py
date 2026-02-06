def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/static/index.html"


def test_add_endpoint_success(client, admin_headers, sample_input_data):
    response = client.post("/math/add", json=sample_input_data, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "add"
    assert data["result"] == 15.0


def test_subtract_endpoint_success(client, admin_headers, sample_input_data):
    response = client.post(
        "/math/subtract", json=sample_input_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "subtract"
    assert data["result"] == 5.0


def test_multiply_endpoint_success(client, admin_headers, sample_input_data):
    response = client.post(
        "/math/multiply", json=sample_input_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "multiply"
    assert data["result"] == 50.0


def test_divide_endpoint_success(client, admin_headers, sample_input_data):
    response = client.post(
        "/math/divide", json=sample_input_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "divide"
    assert data["result"] == 2.0


def test_divide_by_zero_endpoint(client, admin_headers):
    input_data = {"A": 10.0, "B": 0.0}
    response = client.post("/math/divide", json=input_data, headers=admin_headers)
    assert response.status_code == 500


def test_endpoint_without_auth(client, sample_input_data):
    response = client.post("/math/add", json=sample_input_data)
    assert response.status_code == 401


def test_endpoint_with_invalid_auth(client, invalid_headers, sample_input_data):
    response = client.post(
        "/math/add",
        json=sample_input_data,
        headers=invalid_headers,
        follow_redirects=False,
    )
    assert response.status_code == 307
    assert response.headers["Location"] == "/auth/oauth/authorize"


def test_user_can_access_endpoint(client, user_headers, sample_input_data):
    """Test that users with 'user' role can access endpoints."""
    response = client.post("/math/add", json=sample_input_data, headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "add"
    assert data["result"] == 15.0
