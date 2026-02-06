# FastAPI Example

A FastAPI template with dual authentication (API Keys + OAuth), role-based access control, and comprehensive testing.

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Authentication](#authentication)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Development](#development)
- [Installation](#installation)
- [CI/CD](#cicd)

## Features

**Core Capabilities**

- Dual authentication system: API Keys (SHA256 hashed) and OAuth 2.0 (GitHub/Google)
- Role-based access control with granular permissions
- Worker pattern for clean separation between routes and business logic
- Structured JSON logging with request tracking
- Comprehensive unit test suite with coverage reporting
- Built-in authentication test frontend supporting both OAuth and API key flows

**Developer Experience**

- Modern Python development with `pyproject.toml` and Pydantic Settings
- Automated CI/CD using GitHub Actions with semantic versioning
- Code quality enforcement via pre-commit hooks (ruff, isort)
- Automatic HTML coverage reports

## Quick Start

### Prerequisites

- Python 3.12+
- Git

### Installation & Run

```bash
# Clone repository
git clone https://github.com/jonathanvanleeuwen/fastapi_example.git
cd fastapi_example

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run the server
python dev_server.py
```

### Access Points

- **Authentication Frontend**: http://localhost:8000/static/ (test both OAuth and API key methods)
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Authentication

### API Key Authentication

API keys are hashed with SHA256 for security and stored with user metadata.

#### Configuration

Base64-encoded JSON format:
```json
{
  "your_api_key_here": {
    "username": "John Doe",
    "roles": ["admin", "user"]
  },
  "another_key": {
    "username": "Jane Smith",
    "roles": ["user"]
  }
}
```

**Option 1: Using the secrets_b64.py helper script**

1. Create a `secrets.json` file in `src/fastapi_example/auth/`:
```json
{
  "my_secret_key_123": {
    "username": "John Doe",
    "roles": ["admin", "user"]
  },
  "another_key_456": {
    "username": "Jane Smith",
    "roles": ["user"]
  }
}
```

2. Encode the file to base64:
```bash
python src/fastapi_example/auth/secrets_b64.py encode
```

3. Set the environment variable:
```bash
# Copy the output from step 2
export FASTAPI_EXAMPLE_API_KEYS="<base64_output_from_encode>"
```

4. To verify/decode:
```bash
python src/fastapi_example/auth/secrets_b64.py decode "<base64_string>"
```

**Option 2: Manual one-liner**

```bash
# Generate base64-encoded keys
python -c "import base64, json; print(base64.b64encode(json.dumps({'my_key': {'username': 'admin', 'roles': ['admin', 'user']}}).encode()).decode())"

# Set environment variable
export FASTAPI_EXAMPLE_API_KEYS="<base64_output>"
```

#### Usage Example

```bash
curl "http://localhost:8000/math/add?A=10&B=5" \
  -H "Authorization: Bearer your_api_key_here"
```

Security flow:
1. Incoming API key is hashed with SHA256
2. Hash is compared against stored hashes
3. User roles are validated against endpoint requirements
4. Access granted if roles match

### OAuth 2.0 Authentication

Supports GitHub (default) and Google OAuth providers with JWT tokens.

#### Provider Setup

<details>
<summary><b>GitHub OAuth (Default)</b></summary>

1. Go to [GitHub Settings → Developer Settings](https://github.com/settings/developers)
2. Click **OAuth Apps** → **New OAuth App**
3. Fill in application details:
   - **Application name**: Your app name (e.g., "FastAPI Example")
   - **Homepage URL**: `http://localhost:8000`
   - **Authorization callback URL**: `http://localhost:8000/static/callback.html`
4. Click **Register application**
5. Copy **Client ID** and generate **Client Secret**

</details>

<details>
<summary><b>Google OAuth</b></summary>

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Navigate to **APIs & Services** → **Credentials**
4. Create **OAuth 2.0 Client ID**
5. Configure OAuth consent screen
6. Set application details:
   - **Application type**: Web application
   - **Authorized JavaScript origins**: `http://localhost:8000`
   - **Authorized redirect URIs**: `http://localhost:8000/static/callback.html`
7. Copy **Client ID** and **Client Secret**

</details>

#### Environment Configuration

```bash
# Required
export FASTAPI_EXAMPLE_OAUTH_CLIENT_ID="your_client_id"
export FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET="your_client_secret"
export FASTAPI_EXAMPLE_OAUTH_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"

# Optional - defaults to "github"
export FASTAPI_EXAMPLE_OAUTH_PROVIDER="github"  # or "google"
```

#### Testing OAuth Flow

Web interface (recommended):
1. Start server: `python dev_server.py`
2. Visit: http://localhost:8000/static/
3. Choose authentication method:
   - **OAuth Login**: Click "Login with [Provider]" → authorize → automatic token handling
   - **API Key**: Click "API Key" tab → enter your key → click "Set API Key"
4. Test protected endpoints using the math operation form

Both authentication methods provide access to the same endpoints. Your choice is persisted in the browser.

Manual cURL flow:
```bash
# 1. Get authorization URL
curl -X POST "http://localhost:8000/auth/oauth/authorize" \
  -H "Content-Type: application/json" \
  -d '{"redirect_uri": "http://localhost:8000/static/callback.html"}'

# 2. Visit the returned URL in browser and authorize

# 3. Exchange code for token
curl -X POST "http://localhost:8000/auth/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "<authorization_code>",
    "redirect_uri": "http://localhost:8000/static/callback.html"
  }'

# 4. Use the access token
curl "http://localhost:8000/math/add?A=10&B=5" \
  -H "Authorization: Bearer <access_token>"
```

#### Role Assignment

Roles are embedded in JWT tokens during OAuth flow:

```python
from fastapi_example.auth.oauth_auth import create_access_token

token = create_access_token(
    data={"sub": user_email, "provider": "github"},
    roles=["admin", "user"]  # Assign roles
)
```

Access control:
- `admin` role: Full access to all math endpoints
- `user` role: Access to all math endpoints
- No auth: OAuth flow endpoints only

#### Custom Roles and User Management

To implement custom role logic or save users to a database:

1. **Modify role assignment** in [utils/auth_utils.py](src/fastapi_example/utils/auth_utils.py):
   ```python
   def get_user_roles(email: str, provider: str) -> list[str]:
       # Add your custom logic here
       # Check database, external API, etc.
       if email in your_admin_list:
           return ["admin", "user"]
       return ["user"]
   ```

2. **User info is logged** when authenticated - check your logs to see all available user data:
   ```
   User authenticated: email=user@example.com, provider=github, name=John Doe
   ```

3. **Save users to database** in [workers/oauth_service.py](src/fastapi_example/workers/oauth_service.py) after `get_user_info_from_provider()`:
   ```python
   # Add after extracting user info and roles
   roles = get_user_roles(email, provider)
   save_user_to_database(email, name, provider, roles)
   ```

   Saving roles in the database allows you to:
   - Track who has authenticated and when
   - Update roles through database admin tools instead of code changes
   - Query users by role for management purposes

The user info dict contains all data returned by the OAuth provider (email, name, avatar, etc.) which you can use for role checks or persistence.

## Project Structure

```
fastapi_example/
├── src/fastapi_example/
│   ├── auth/
│   │   ├── dependencies.py          # Unified auth dependency factory
│   │   ├── oauth_auth.py            # OAuth token management
│   │   └── oauth_providers.py       # OAuth provider configurations
│   ├── routers/
│   │   ├── math.py                  # Math operations (protected)
│   │   └── oauth.py                 # OAuth flow endpoints
│   ├── workers/
│   │   ├── math_operations.py       # Business logic layer
│   │   └── oauth_service.py         # OAuth service layer
│   ├── models/
│   │   ├── input.py                 # Request/response models
│   │   └── oauth.py                 # OAuth models
│   ├── utils/
│   │   └── auth_utils.py            # Hashing utilities
│   ├── static/                      # Authentication test frontend
│   │   ├── index.html               # Main test page (OAuth + API Key)
│   │   └── callback.html            # OAuth callback handler
│   ├── custom_logger/               # Logging configuration
│   ├── main.py                      # FastAPI app entry point
│   └── settings.py                  # Pydantic settings
├── tests/
│   ├── conftest.py                  # Pytest fixtures
│   └── unit/                        # Unit tests
└── pyproject.toml                   # Project metadata
```

### Key Architectural Patterns

| Pattern | Description |
|---------|-------------|
| Worker Pattern | Business logic separated from HTTP layer for testability |
| Unified Auth | Single dependency factory supporting multiple auth methods |
| Security Utilities | `hash_api_key()` for SHA256 hashing of API keys |
| Pydantic Models | Automatic validation for all inputs and outputs |

## API Endpoints

### Math Operations (Requires `admin` or `user` role)

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/math/add` | GET | Add two numbers | `?A=10&B=5` → `{"result": 15}` |
| `/math/subtract` | GET | Subtract B from A | `?A=10&B=5` → `{"result": 5}` |
| `/math/multiply` | GET | Multiply two numbers | `?A=7&B=6` → `{"result": 42}` |
| `/math/divide` | GET | Divide A by B | `?A=10&B=2` → `{"result": 5}` |

Example request:
```bash
curl "http://localhost:8000/math/multiply?A=7&B=6" \
  -H "Authorization: Bearer your_api_key"
```

Response:
```json
{
  "operation": "multiply",
  "a": 7,
  "b": 6,
  "result": 42
}
```

### OAuth Endpoints (No auth required)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/oauth/provider` | GET | Get configured OAuth provider name |
| `/auth/oauth/authorize` | POST | Get authorization URL for OAuth flow |
| `/auth/oauth/token` | POST | Exchange authorization code for JWT token |

## Development

### Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=fastapi_example --cov-report=html

# Specific test file
pytest tests/unit/test_workers.py

# Verbose output
pytest -v
```

### Adding New Features

#### Step 1: Add Business Logic

```python
# src/fastapi_example/workers/math_operations.py
def power_numbers(a: float, b: float) -> float:
    """Raise a to the power of b."""
    return a ** b
```

#### Step 2: Create Route

```python
# src/fastapi_example/routers/math.py
from fastapi_example.workers.math_operations import power_numbers
from fastapi_example.models.input import InputData

@math_router.post("/power")
def power(input_data: InputData) -> dict:
    result = power_numbers(input_data.A, input_data.B)
    return {
        "operation": "power",
        "a": input_data.A,
        "b": input_data.B,
        "result": result
    }
```

#### Step 3: Add Tests

```python
# tests/unit/test_workers.py
from fastapi_example.workers.math_operations import power_numbers

def test_power_numbers():
    assert power_numbers(2, 3) == 8
    assert power_numbers(10, 2) == 100
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Keys (base64-encoded JSON)
FASTAPI_EXAMPLE_API_KEYS="eyJ0ZXN0Ijp7InVzZXJuYW1lIjoiSm9uYXRoYW4iLCJyb2xlcyI6WyJhZG1pbiIsInVzZXIiXX19"

# OAuth Configuration
FASTAPI_EXAMPLE_OAUTH_PROVIDER="github"
FASTAPI_EXAMPLE_OAUTH_CLIENT_ID="your_client_id"
FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET="your_client_secret"
FASTAPI_EXAMPLE_OAUTH_SECRET_KEY="your-32-char-secret-key"

# Application Settings
FASTAPI_EXAMPLE_APP_NAME="My FastAPI App"
```

## Installation

### From GitHub

```bash
pip install "git+https://github.com/jonathanvanleeuwen/fastapi_example.git@v1.0.0"
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

Automated code quality checks before each commit:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

Configured checks:
- Code formatting (ruff)
- Import sorting (isort)
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON syntax validation
- Case conflict detection
- Merge conflict detection
- Private key detection
- Prevent commits to main branch

### Semantic Versioning

Automated releases based on commit messages:

| Commit Type | Version Change | Example |
|-------------|----------------|---------|
| `fix:` | Patch (1.0.0 → 1.0.1) | `fix: correct calculation error` |
| `feat:` | Minor (1.0.0 → 1.1.0) | `feat: add power operation` |
| `BREAKING CHANGE:` | Major (1.0.0 → 2.0.0) | `feat: redesign API`<br>`BREAKING CHANGE: removed old endpoints` |

## Usage Examples

### Python requests

```python
import requests

url = "http://localhost:8000/math/add"
headers = {"Authorization": "Bearer your_api_key"}
params = {"A": 10, "B": 5}

response = requests.get(url, params=params, headers=headers)
print(response.json())
# Output: {"operation": "add", "a": 10, "b": 5, "result": 15}
```

### JavaScript fetch

```javascript
const response = await fetch('http://localhost:8000/math/add?A=10&B=5', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer your_api_key'
  }
});

const data = await response.json();
console.log(data);
// Output: {operation: "add", a: 10, b: 5, result: 15}
```

### Error Handling

Invalid authentication:
```bash
curl "http://localhost:8000/math/add?A=10&B=5" \
  -H "Authorization: Bearer invalid_key"

# Response: 307 Redirect to /static/
```

Insufficient permissions:
```bash
# If user lacks required role
curl "http://localhost:8000/math/add?A=10&B=5" \
  -H "Authorization: Bearer user_without_role"

# Response: {"detail": "User does not have required role"}
# Status: 403 Forbidden
```

Invalid input:
```bash
curl "http://localhost:8000/math/add?A=not_a_number&B=5" \
  -H "Authorization: Bearer your_api_key"

# Response: {"detail": [{"type": "float_parsing", "loc": ["query", "A"], ...}]}
# Status: 422 Unprocessable Entity
```

## Coverage Report

<!-- Pytest Coverage Comment:Begin -->
<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/README.md"><img alt="Coverage" src="https://img.shields.io/badge/Coverage-79%25-yellow.svg" /></a><details><summary>Coverage Report </summary><table><tr><th>File</th><th>Stmts</th><th>Miss</th><th>Cover</th><th>Missing</th></tr><tbody><tr><td colspan="5"><b>src/fastapi_example</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/__init__.py">__init__.py</a></td><td>1</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/main.py">main.py</a></td><td>24</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/settings.py">settings.py</a></td><td>36</td><td>1</td><td>97%</td><td><a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/settings.py#L37">37</a></td></tr><tr><td colspan="5"><b>src/fastapi_example/auth</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/dependencies.py">dependencies.py</a></td><td>54</td><td>13</td><td>76%</td><td><a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/dependencies.py#L22">22</a>, <a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/dependencies.py#L61-L81">61&ndash;81</a>, <a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/dependencies.py#L111-L115">111&ndash;115</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/oauth_auth.py">oauth_auth.py</a></td><td>34</td><td>1</td><td>97%</td><td><a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/oauth_auth.py#L20">20</a></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/oauth_providers.py">oauth_providers.py</a></td><td>1</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/secrets_b64.py">secrets_b64.py</a></td><td>34</td><td>34</td><td>0%</td><td><a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/auth/secrets_b64.py#L1-L52">1&ndash;52</a></td></tr><tr><td colspan="5"><b>src/fastapi_example/custom_logger</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/custom_logger/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>src/fastapi_example/custom_logger/formatters</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/custom_logger/formatters/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/custom_logger/formatters/json.py">json.py</a></td><td>25</td><td>13</td><td>48%</td><td><a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/custom_logger/formatters/json.py#L44-L45">44&ndash;45</a>, <a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/custom_logger/formatters/json.py#L48-L72">48&ndash;72</a></td></tr><tr><td colspan="5"><b>src/fastapi_example/custom_logger/setup</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/custom_logger/setup/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/custom_logger/setup/setup_logger.py">setup_logger.py</a></td><td>28</td><td>4</td><td>86%</td><td><a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/custom_logger/setup/setup_logger.py#L34-L37">34&ndash;37</a></td></tr><tr><td colspan="5"><b>src/fastapi_example/models</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/models/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/models/input.py">input.py</a></td><td>4</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/models/oauth.py">oauth.py</a></td><td>12</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td colspan="5"><b>src/fastapi_example/routers</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/routers/math.py">math.py</a></td><td>41</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/routers/oauth.py">oauth.py</a></td><td>28</td><td>1</td><td>96%</td><td><a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/routers/oauth.py#L33">33</a></td></tr><tr><td colspan="5"><b>src/fastapi_example/utils</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/utils/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/utils/auth_utils.py">auth_utils.py</a></td><td>10</td><td>1</td><td>90%</td><td><a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/utils/auth_utils.py#L40">40</a></td></tr><tr><td colspan="5"><b>src/fastapi_example/workers</b></td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/workers/__init__.py">__init__.py</a></td><td>0</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/workers/math_operations.py">math_operations.py</a></td><td>20</td><td>0</td><td>100%</td><td>&nbsp;</td></tr><tr><td>&nbsp; &nbsp;<a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/workers/oauth_service.py">oauth_service.py</a></td><td>53</td><td>17</td><td>68%</td><td><a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/workers/oauth_service.py#L25">25</a>, <a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/workers/oauth_service.py#L97-L99">97&ndash;99</a>, <a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/workers/oauth_service.py#L106">106</a>, <a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/workers/oauth_service.py#L143-L165">143&ndash;165</a>, <a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/workers/oauth_service.py#L168-L170">168&ndash;170</a>, <a href="https://github.com/jonathanvanleeuwen/fastapi_example/blob/main/src/fastapi_example/workers/oauth_service.py#L191">191</a></td></tr><tr><td><b>TOTAL</b></td><td><b>405</b></td><td><b>85</b></td><td><b>79%</b></td><td>&nbsp;</td></tr></tbody></table></details>
<!-- Pytest Coverage Comment:End -->

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
