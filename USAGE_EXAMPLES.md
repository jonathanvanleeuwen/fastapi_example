# FastAPI Example - Usage Examples

This file contains practical examples of using the FastAPI example application.

## Running the Server

```bash
# Development mode
python dev_server.py

# Production mode with uvicorn directly
uvicorn fastapi_example.main:app --host 0.0.0.0 --port 8000
```

## API Key Authentication Examples

### Using curl

```bash
# Add operation (requires admin role)
curl -X POST "http://localhost:8000/fastapi_example/add" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'

# Response: {"operation":"add","a":10,"b":5,"result":15}
```

### Using Python requests

```python
import requests

url = "http://localhost:8000/fastapi_example/add"
headers = {
    "Authorization": "Bearer test",
    "Content-Type": "application/json"
}
data = {"A": 10, "B": 5}

response = requests.post(url, json=data, headers=headers)
print(response.json())
# Output: {'operation': 'add', 'a': 10.0, 'b': 5.0, 'result': 15.0}
```

### Using JavaScript fetch

```javascript
const response = await fetch('http://localhost:8000/fastapi_example/add', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer test',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ A: 10, B: 5 })
});

const data = await response.json();
console.log(data);
// Output: {operation: 'add', a: 10, b: 5, result: 15}
```

## OAuth Authentication Examples

### Step 1: Get Authorization URL

```bash
curl -X POST "http://localhost:8000/auth/oauth/authorize" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "redirect_uri": "http://localhost:3000/callback"
  }'

# Response: {"authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=..."}
```

### Step 2: User Authorizes (Manual Step)

The user visits the authorization_url from step 1 and grants permission.
They'll be redirected to your redirect_uri with a code parameter.

### Step 3: Exchange Code for Token

```bash
curl -X POST "http://localhost:8000/auth/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "code": "4/0AY0e-g7...",
    "redirect_uri": "http://localhost:3000/callback"
  }'

# Response: {"access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer"}
```

### Step 4: Use the Access Token

```bash
curl -X POST "http://localhost:8000/fastapi_example/add" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
```

## All Math Operations

### Addition
```bash
curl -X POST "http://localhost:8000/fastapi_example/add" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
```

### Subtraction
```bash
curl -X POST "http://localhost:8000/fastapi_example/subtract" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
```

### Multiplication
```bash
curl -X POST "http://localhost:8000/fastapi_example/multiply" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
```

### Division
```bash
curl -X POST "http://localhost:8000/fastapi_example/divide" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
```

## Error Handling Examples

### Invalid API Key
```bash
curl -X POST "http://localhost:8000/fastapi_example/add" \
  -H "Authorization: Bearer invalid_key" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'

# Response: {"detail": "Invalid API Key"}
# Status: 401
```

### Missing Authorization
```bash
curl -X POST "http://localhost:8000/fastapi_example/add" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'

# Response: {"detail": "Invalid or missing Authorization header"}
# Status: 401
```

### Insufficient Permissions
```bash
# User with only "user" role trying to access admin endpoint
curl -X POST "http://localhost:8000/fastapi_example/add" \
  -H "Authorization: Bearer test2" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'

# Response: {"detail": "User does not have required role"}
# Status: 403
```

### Division by Zero
```bash
curl -X POST "http://localhost:8000/fastapi_example/divide" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 0}'

# Response: {"detail": "Internal Server Error"}
# Status: 500
```

## Testing with Pytest

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_workers.py

# Run with coverage
pytest --cov=fastapi_example --cov-report=html

# Run with verbose output
pytest -v

# Run specific test
pytest tests/unit/test_workers.py::test_add_numbers
```

## Environment Setup Examples

### Development Environment

```bash
# .env file
FASTAPI_EXAMPLE_STAGE=development
FASTAPI_EXAMPLE_API_KEYS=eyJ0ZXN0Ijp7InVzZXJuYW1lIjoiSm9uYXRoYW4iLCJyb2xlcyI6WyJhZG1pbiIsInVzZXIiXX19
```

### Production Environment

```bash
# Set environment variables
export FASTAPI_EXAMPLE_STAGE=production
export FASTAPI_EXAMPLE_API_KEYS="<base64_encoded_secrets>"
export FASTAPI_EXAMPLE_OAUTH_SECRET_KEY="<secure_random_key>"
export FASTAPI_EXAMPLE_OAUTH_CLIENT_ID="<oauth_client_id>"
export FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET="<oauth_client_secret>"

# Run with gunicorn (production server)
gunicorn fastapi_example.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## Creating Custom API Keys

```python
import base64
import json

# Create your secrets
secrets = {
    "my_secret_key_123": {
        "username": "Alice",
        "roles": ["admin", "user"]
    },
    "another_key_456": {
        "username": "Bob",
        "roles": ["user"]
    }
}

# Encode to base64
encoded = base64.b64encode(json.dumps(secrets).encode()).decode()
print(encoded)

# Use this in your environment variable
# export FASTAPI_EXAMPLE_API_KEYS="<encoded_string>"
```
