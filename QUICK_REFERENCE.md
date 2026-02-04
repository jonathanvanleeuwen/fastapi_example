# FastAPI Example - Quick Reference

## Common Commands

```bash
# Install dependencies
pip install -e ".[dev]"

# Run development server
python dev_server.py

# Run tests
pytest

# Run tests with coverage
pytest --cov=fastapi_example --cov-report=html

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Project Structure at a Glance

```
src/fastapi_example/
├── auth/              # Authentication logic
│   ├── api_key_auth.py     # API key auth
│   └── oauth_auth.py       # OAuth 2.0 auth
├── routers/           # API endpoints
│   ├── production.py       # Main endpoints
│   ├── testing.py          # Test endpoints
│   └── oauth.py            # OAuth flow
├── workers/           # Business logic
│   └── math_operations.py  # Math functions
├── models/            # Data models
│   └── input.py           # Request/response models
├── custom_logger/     # Logging setup
├── main.py            # Application entry
└── settings.py        # Configuration
```

## API Endpoints

### Math Operations (Requires Admin)
- `POST /fastapi_example/add` - Add numbers
- `POST /fastapi_example/subtract` - Subtract numbers
- `POST /fastapi_example/multiply` - Multiply numbers
- `POST /fastapi_example/divide` - Divide numbers

### OAuth Flow (Public)
- `POST /auth/oauth/authorize` - Get authorization URL
- `POST /auth/oauth/token` - Exchange code for token

### Other
- `GET /` - Redirects to `/docs`
- `GET /docs` - Interactive API documentation

## Authentication

### API Key (Header)
```
Authorization: Bearer YOUR_API_KEY
```

### OAuth Token (Header)
```
Authorization: Bearer JWT_TOKEN
```

## Request Examples

### API Key Auth
```bash
curl -X POST "http://localhost:8000/fastapi_example/add" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
```

### OAuth Flow
```bash
# 1. Get authorization URL
curl -X POST "http://localhost:8000/auth/oauth/authorize" \
  -d '{"provider": "google", "redirect_uri": "http://localhost/callback"}'

# 2. User authorizes (browser)

# 3. Exchange code
curl -X POST "http://localhost:8000/auth/oauth/token" \
  -d '{"provider": "google", "code": "CODE", "redirect_uri": "http://localhost/callback"}'
```

## Environment Variables

### Required
```bash
FASTAPI_EXAMPLE_API_KEYS  # Base64 encoded API keys
```

### Optional (OAuth)
```bash
FASTAPI_EXAMPLE_OAUTH_CLIENT_ID
FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET
FASTAPI_EXAMPLE_OAUTH_SECRET_KEY
FASTAPI_EXAMPLE_OAUTH_TENANT_ID  # Azure only
```

## Roles

- **admin** - Full access to all endpoints
- **user** - Access to test endpoints only

## Response Format

### Success
```json
{
  "operation": "add",
  "a": 10,
  "b": 5,
  "result": 15
}
```

### Error
```json
{
  "detail": "Invalid API Key"
}
```

## HTTP Status Codes

- `200` - Success
- `401` - Unauthorized (invalid/missing auth)
- `403` - Forbidden (insufficient permissions)
- `400` - Bad Request (invalid input)
- `500` - Internal Server Error

## Testing

### Run Specific Tests
```bash
pytest tests/unit/test_workers.py
pytest tests/unit/test_routers.py
pytest tests/unit/test_oauth.py
pytest tests/unit/test_auth.py
```

### Test Coverage
```bash
pytest --cov=fastapi_example
pytest --cov=fastapi_example --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Adding New Features

### 1. Add Worker Function
```python
# src/fastapi_example/workers/math_operations.py
def new_operation(a: float, b: float) -> float:
    return a + b  # Your logic
```

### 2. Export from Worker Module
```python
# src/fastapi_example/workers/__init__.py
from fastapi_example.workers.math_operations import new_operation
__all__ = [..., "new_operation"]
```

### 3. Create Endpoint
```python
# src/fastapi_example/routers/production.py
@fastapi_router.post("/new")
def new_endpoint(input_data: InputData, user: str = Depends(get_current_user)):
    result = new_operation(input_data.A, input_data.B)
    return {"result": result}
```

### 4. Add Tests
```python
# tests/unit/test_workers.py
def test_new_operation():
    assert new_operation(1, 2) == 3

# tests/unit/test_routers.py
def test_new_endpoint(client, admin_headers):
    response = client.post("/fastapi_example/new",
                          json={"A": 1, "B": 2},
                          headers=admin_headers)
    assert response.status_code == 200
```

## Troubleshooting

### Import Errors
```bash
# Reinstall dependencies
pip install -e ".[dev]"
```

### Test Failures
```bash
# Run with verbose output
pytest -v

# Run single test
pytest tests/unit/test_workers.py::test_add_numbers
```

### Authentication Issues
```bash
# Check API key format
python -c "import base64; print(base64.b64decode('YOUR_KEY').decode())"

# Verify secrets structure
cat src/fastapi_example/auth/secrets_example.json
```

## Links

- Interactive API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## File Reference

- `README.md` - Main documentation
- `USAGE_EXAMPLES.md` - Practical examples
- `EXTENDING.md` - Guide for adding features
- `CHANGES.md` - Summary of changes
- `.env.example` - Environment variable template
