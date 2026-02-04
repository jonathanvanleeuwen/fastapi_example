def test_root_redirect(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/docs"


def test_add_endpoint_success(client, admin_headers, sample_input_data):
    response = client.post(
        "/fastapi_example/add", json=sample_input_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "add"
    assert data["result"] == 15.0


def test_subtract_endpoint_success(client, admin_headers, sample_input_data):
    response = client.post(
        "/fastapi_example/subtract", json=sample_input_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "subtract"
    assert data["result"] == 5.0


def test_multiply_endpoint_success(client, admin_headers, sample_input_data):
    response = client.post(
        "/fastapi_example/multiply", json=sample_input_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "multiply"
    assert data["result"] == 50.0


def test_divide_endpoint_success(client, admin_headers, sample_input_data):
    response = client.post(
        "/fastapi_example/divide", json=sample_input_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "divide"
    assert data["result"] == 2.0


def test_divide_by_zero_endpoint(client, admin_headers):
    input_data = {"A": 10.0, "B": 0.0}
    response = client.post(
        "/fastapi_example/divide", json=input_data, headers=admin_headers
    )
    assert response.status_code == 500


def test_endpoint_without_auth(client, sample_input_data):
    response = client.post("/fastapi_example/add", json=sample_input_data)
    assert response.status_code == 401


def test_endpoint_with_invalid_auth(client, invalid_headers, sample_input_data):
    response = client.post(
        "/fastapi_example/add", json=sample_input_data, headers=invalid_headers
    )
    assert response.status_code == 401


def test_user_cannot_access_admin_endpoint(client, user_headers, sample_input_data):
    response = client.post(
        "/fastapi_example/add", json=sample_input_data, headers=user_headers
    )
    assert response.status_code == 403


def test_test_endpoint_access(client, user_headers, sample_input_data, test_settings):
    test_settings.stage = "development"
    response = client.post(
        "/fastapi_example_test/test", json=sample_input_data, headers=user_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["test_mode"] is True
    assert data["result"] == 15.0
