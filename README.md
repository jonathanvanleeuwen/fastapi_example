# fastapi_example

A minimal FastAPI template demonstrating authentication, logging, workers, and data models.

## Table of Contents
- [Features](#features)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
  - [API Key Authentication](#api-key-authentication)
  - [OAuth Authentication](#oauth-authentication)
  - [Setting Up OAuth](#setting-up-oauth)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Development](#development)
  - [Running Tests](#running-tests)
  - [Adding New Features](#adding-new-features)
  - [Environment Variables](#environment-variables)
- [Installation](#installation)
- [CI/CD](#cicd)
- [Examples](#examples)
- [Coverage Report](#coverage-report)

## Features

### Core Features
* **Worker/Service Layer Pattern**: Clean separation between API routes and business logic
* **Dual Authentication System**:
  - API Key authentication with role-based access control (RBAC)
  - OAuth 2.0 with support for Google, Azure AD, and GitHub (with RBAC)
* **Sample Math Operations API**: Demonstrates the worker pattern
* **Structured Logging**: JSON logging with request tracking
* **Modern Python Packaging**: Using pyproject.toml

### Development & CI/CD
* Automated testing on PR using GitHub Actions
* Pre-commit hooks for code quality
* Semantic release automation
* Automatic code coverage reporting
* Automatic wheel build and GitHub Release publishing

## Quick Start

### Prerequisites
- Python 3.12 or higher
- Git

### Installation

```bash
git clone https://github.com/jonathanvanleeuwen/fastapi_example.git
cd fastapi_example

python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

### Running the Application

```bash
python dev_server.py
```

Visit the interactive API docs at http://localhost:8000/docs

## Authentication

This application supports two authentication methods that work seamlessly together.

### API Key Authentication

API keys are stored in a base64-encoded JSON structure with usernames and roles. **API keys are hashed using SHA256** before storage for security.

#### How It Works

The `FASTAPI_EXAMPLE_API_KEYS` environment variable contains a base64-encoded JSON:
```json
{
    "your_secret_key_here": {
        "username": "John Doe",
        "roles": ["admin", "user"]
    },
    "another_secret_key": {
        "username": "Jane Smith",
        "roles": ["user"]
    }
}
```

When the application starts:
1. API keys are decoded from base64
2. Each key is hashed with SHA256 using the `hash_api_key()` utility function
3. Hashed keys are stored in memory
4. During authentication, incoming tokens are hashed and compared against stored hashes

**Usage:**
```bash
curl -X POST "http://localhost:8000/math/add" \
  -H "Authorization: Bearer your_secret_key_here" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
```

#### Setting Up API Keys

**Option 1: Environment Variable (Recommended)**
```bash
python -c "import base64, json; print(base64.b64encode(json.dumps({'my_key': {'username': 'admin_user', 'roles': ['admin']}}).encode()).decode())"

export FASTAPI_EXAMPLE_API_KEYS="<base64_encoded_string>"
```

**Option 2: Direct JSON (Development)**
See `src/fastapi_example/auth/secrets_example.json` for the structure.

### OAuth Authentication

OAuth allows users to log in with GitHub (default) or Google accounts. OAuth tokens include roles for RBAC.

**Default Provider:** GitHub (configurable via `FASTAPI_EXAMPLE_OAUTH_PROVIDER` environment variable)

**OAuth Failure Handling:** If OAuth authentication fails, users are automatically redirected to the OAuth login page.

#### OAuth Flow

1. **Get auredirect_uri": "http://localhost:3000/callback"}'
   ```

2. **User authorizes** your app via the returned URL

3. **Exchange code for token**:
   ```bash
   curl -X POST "http://localhost:8000/auth/oauth/token" \
     -H "Content-Type: application/json" \
     -d '{
       "code": "authorization_code_from_step_2",
       "redirect_uri": "http://localhost:3000 \
     -d '{
       "provider": "google",
       "code": "authorization_code_from_step_2",
       "redirect_uri": "http://localhost/callback"
     }'
   ```

4. **Use the access token**:
   ```bash
   curl -X POST "http://localhost:8000/math/add" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"A": 10, "B": 5}'
   ```

### Setting Up OAuth

#### Prerequisites
- An OAuth application registered with your provider
- Client ID and Client Secret
- Redirect URI configured in your OAuth application

#### Step 1: Register Your Application

**For Google:**
1. Go titHub (Default):**
1. Go to [GitHub Settings](https://github.com/settings/developers)
2. Click "OAuth Apps" > "New OAuth App"
3. Fill in application details
4. Set Authorization callback URL: `http://localhost:8000/static/callback.html`
5. Copy the Client ID and generate a Client Secret

**For Google:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth 2.0 Client ID"
5. Configure OAuth consent screen
6. Set application type to "Web application"
7. Add authorized redirect URIs: `http://localhost:8000/static/callback.html`
8. Copy the Client ID and Client Secret
#### Step 2: Configure Environment Variables

```bash
export FASTAPI_EXAMPLE_OAUTH_CLIENT_ID="your_client_id"
export FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET="your_client_secret"
export FASTAPI_EXAMPLE_OAUTH_SECRET_KEY="your-random-32-char-secret-key-here"
export FASTAPI_EXAMPLE_OAUTH_TENANT_ID="your_tenant_id"  # Azure AD only
```

**Generating a Secret Key:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
# Required
export FASTAPI_EXAMPLE_OAUTH_CLIENT_ID="your_client_id"
export FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET="your_client_secret"
export FASTAPI_EXAMPLE_OAUTH_SECRET_KEY="your-random-32-char-secret-key-here"

# Optional - defaults to "github"
export FASTAPI_EXAMPLE_OAUTH_PROVIDER="github"  # or "google" creating a token, you can specify roles:

**In your OAuth flow** (example in `routers/oauth.py`):
```python
from fastapi_example.auth.oauth_auth import create_access_token

token = create_access_token(
    data={"sub": user_email, "provider": "google"},
    roles=["admin", "user"]  # Assign roles to the user
)
```

**Role Requirements:**
- `admin` role: Required for `/math/*` endpoints
- No role requirement: OAuth flow endpoints (`/auth/oauth/*`)

**How It Works:**
1. When a user authenticates via OAuth, your backend determines their roles
2. Roles are embedded in the JWT token
3. The `create_aFull access to all `/math/*` endpoints
- `user` role: Also has access todency validates the token and checks roles
4. Access is granted if the user has at least one required role

#### Step 4: Test OAuth Flow

**Using the Frontend (Easiest):**
1. Start the FastAPI server: `python dev_server.py`
2. Open your browser to: `http://localhost:8000` (automatically redirects to OAuth test page)
3. Click "Login with [Provider]" (button text updates based on configured provider)
4. Authorize the application
5. View the access token and test protected endpoints

**Using cURL:**
1. Start the server: `python dev_server.py`
2. Get authorization URL: `POST http://localhost:8000/auth/oauth/authorize`
3. Visit the URL in a browser
4. After authorizing, exchange the code for a token
5. Use the token to access protected endpoints

## Project Structure

```
fastapi_example/
├── src/fastapi_example/
│   ├── auth/
│   │   ├── dependencies.py       # Unified auth (API key + OAuth with roles)
│   │   ├── oauth_auth.py         # OAuth implementation
│   │   └── secrets_example.json  # Example API keys structure
│   ├── routers/
│   │   ├── math.py               # Math operations (admin/user roles)
│   │   └── oauth.py              # OAuth flow endpoints
│   ├── workers/
│   │   └── math_operations.py    # Business logic
│   ├── models/
│   │   ├── input.py              # Request/response models
│   │   └── oauth.py              # OAuth models
│   ├── utils/
│   │   └── auth_utils.py         # Authentication utilities
│   ├── static/                   # OAuth testing frontend (illustrative only)
│   │   ├── index.html            # Main OAuth test page
│   │   └── callback.html         # OAuth callback handler
│   ├── custom_logger/            # Logging setup
│   ├── main.py                   # Application entry
│   └── settings.py               # Configuration
├── tests/
│   ├── conftest.py               # Test fixtures
│   └── unit/                     # Unit tests
└── pyproject.toml                # Dependencies
```

### Key Concepts

**Utilities:** The `utils/auth_utils.py` module provides:
- `hash_api_key()`: SHA256 hashing for API key security
- `get_user_roles()`: Mock database function for user role lookup (returns `["user"]` by default)

**Worker Pattern:** Business logic is separated from HTTP routes for better testability and reusability.

**Unified Auth:** Single authentication system that checks API keys first, then OAuth tokens. Both support RBAC. Failed OAuth authentication automatically redirects to login.

**Models:** Pydantic models validateor User  all inputs and outputs automatically.

## API Endpoints

### Math Operations (Requires Admin Role)

All endpoints accept JSON with `A` and `B` numbers:

- `POST /math/add` - Add two numbers
- `POST /math/subtract` - Subtract B from A
- `POST /math/multiply` - Multiply two numbers
- `POST /math/divide` - Divide A by B

**Example:**
```bash
curl -X POST "http://localhost:8000/math/multiply" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"A": 7, "B": 6}'

# Response: {"operation": "multiply", "a": 7, "b": 6, "result": 42}
```

### OAuth Endpoints (No Auth Required)

- `POST /auth/oauth/authorize` - Get authorization URL
- `POST /auth/oauth/token` - Exchange code for token

## Development

### Running Tests

```bash
pytest

pytest --cov=fastapi_example --cov-report=html

pytest tests/unit/test_workers.py
```

### Adding New Features

#### 1. Add business logic to a worker

```python
# src/fastapi_example/workers/math_operations.py
def power_numbers(a: float, b: float) -> float:
    return a ** b
```

#### 2. Export from worker module

```python
# src/fastapi_example/workers/__init__.py
from fastapi_example.workers.math_operations import power_numbers

__all__ = ["power_numbers", ...]
```

#### 3. Create the route

```python
# src/fastapi_example/routers/math.py
from fastapi_example.workers import power_numbers

@math_router.post("/power")
def power(input_data: InputData, request: Request) -> dict:
    user_info = request.state.user_info
    result = power_numbers(input_data.A, input_data.B)
    return {"operation": "power", "result": result}
```

#### 4. Add tests

```python
# tests/unit/test_workers.py
def test_power_numbers():
    assert power_numbers(2, 3) == 8
```

### Environment Variables

Create a `.env` file:

```bash
FASTAPI_EXAMPLE_API_KEYS="eyJ0ZXN0Ijp7InVzZXJuYW1lIjoiSm9uYXRoYW4iLCJyb2xlcyI6WyJhZG1pbiIsInVzZXIiXX19"

FASTAPI_EXAMPLE_OAUTH_CLIENT_ID=your_client_id
FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET=your_client_secret
FASTAPI_EXAMPLE_OAUTH_SECRET_KEY=your-secret-key-min-32-chars
FASTAPI_EXAMPLE_OAUTH_TENANT_ID=your_tenant_id
```

## Installation

### From GitHub (Private Repository)

#### Option 1: Using Personal Access Token

```bash
pip install "git+https://YOUR_TOKEN@github.com/jonathanvanleeuwen/fastapi_example.git@VERSION"
```

#### Option 2: Using Git Credentials

```bash
git config --global credential.helper store
pip install "git+https://github.com/jonathanvanleeuwen/fastapi_example.git@VERSION"
```

### From Source

```bash
git clone https://github.com/jonathanvanleeuwen/fastapi_example.git
cd fastapi_example
pip install -e ".[dev]"
```

### In requirements.txt

```txt
fastapi_example @ git+https://github.com/jonathanvanleeuwen/fastapi_example.git@v1.0.0
```

## CI/CD

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

Checks: code formatting (ruff), import sorting (isort), trailing whitespace, YAML/JSON syntax

### Semantic Release

Triggered on merge to main:

**Patch release** (1.0.0 → 1.0.1):
```
fix: your commit message
```

**Minor release** (1.0.0 → 1.1.0):
```
feat: your commit message
```

**Major release** (1.0.0 → 2.0.0):
```
feat: your commit message

BREAKING CHANGE: description
```

## Examples

### Using Python requests

```python
import requests

url = "http://localhost:8000/math/add"
headers = {"Authorization": "Bearer test"}
data = {"A": 10, "B": 5}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### Using JavaScript fetch

```javascript
const response = await fetch('http://localhost:8000/math/add', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer test',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ A: 10, B: 5 })
});

const data = await response.json();
console.log(data);
```

### Error Handling

**Invalid Credentials:**
```bash
curl -X POST "http://localhost:8000/math/add" \
  -H "Authorization: Bearer invalid_key" \
  -d '{"A": 10, "B": 5}'

# Response: {"detail": "Invalid authentication credentials"}
# Status: 401
```

**Insufficient Permissions:**
```bash
curl -X POST "http://localhost:8000/math/add" \
  -H "Authorization: Bearer user_key" \
  -d '{"A": 10, "B": 5}'

# Response: {"detail": "User does not have required role"}
# Status: 403
```

## Coverage Report
<!-- Pytest Coverage Comment:Begin -->
<!-- Pytest Coverage Comment:End -->
