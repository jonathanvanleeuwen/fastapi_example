# 🚀 FastAPI Example

> A production-ready FastAPI template with dual authentication (API Keys + OAuth), role-based access control, and comprehensive testing.

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [⚡ Quick Start](#-quick-start)
- [🔐 Authentication](#-authentication)
- [🏗️ Project Structure](#️-project-structure)
- [🌐 API Endpoints](#-api-endpoints)
- [🛠️ Development](#️-development)
- [📦 Installation](#-installation)
- [🔄 CI/CD](#-cicd)

---

## ✨ Features

### Core Capabilities

- 🔑 **Dual Authentication**: API Keys (SHA256 hashed) + OAuth 2.0 (GitHub/Google)
- 👥 **Role-Based Access Control**: Fine-grained permissions with `admin` and `user` roles
- 🎯 **Worker Pattern**: Clean separation between routes and business logic
- 📝 **Structured Logging**: JSON logs with request tracking
- 🧪 **100% Test Coverage**: Comprehensive unit and integration tests
- 📱 **OAuth Test Frontend**: Built-in web UI for testing authentication flows

### Developer Experience

- ⚙️ **Modern Python**: Using `pyproject.toml` and Pydantic Settings
- 🔄 **Automated CI/CD**: GitHub Actions with semantic versioning
- 🎨 **Code Quality**: Pre-commit hooks with ruff, isort, and more
- 📊 **Coverage Reports**: Automatic HTML coverage generation

---

## ⚡ Quick Start

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

### 🎯 Access Points

- **🌐 OAuth Frontend**: http://localhost:8000 (main page)
- **📚 API Documentation**: http://localhost:8000/docs
- **🔍 Alternative Docs**: http://localhost:8000/redoc

---

## 🔐 Authentication

### 🔑 API Key Authentication

API keys are hashed with **SHA256** for security and stored with user metadata.

#### Configuration

**Base64-encoded JSON format:**
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

**Setup via Environment Variable:**
```bash
# Generate base64-encoded keys
python -c "import base64, json; print(base64.b64encode(json.dumps({'my_key': {'username': 'admin', 'roles': ['admin', 'user']}}).encode()).decode())"

# Set environment variable
export FASTAPI_EXAMPLE_API_KEYS="<base64_output>"
```

#### Usage Example

```bash
curl -X POST "http://localhost:8000/math/add" \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
```

**Security Flow:**
1. Incoming API key is hashed with SHA256
2. Hash is compared against stored hashes
3. User roles are validated against endpoint requirements
4. Access granted if roles match

---

### 🌐 OAuth 2.0 Authentication

Supports **GitHub** (default) and **Google** OAuth providers with JWT tokens.

#### Provider Setup

<details>
<summary><b>GitHub OAuth (Default)</b></summary>

1. Go to [GitHub Settings → Developer Settings](https://github.com/settings/developers)
2. Click **OAuth Apps** → **New OAuth App**
3. Fill in application details
4. Set **Authorization callback URL**: `http://localhost:8000/static/callback.html`
5. Copy **Client ID** and generate **Client Secret**

</details>

<details>
<summary><b>Google OAuth</b></summary>

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Navigate to **APIs & Services** → **Credentials**
4. Create **OAuth 2.0 Client ID**
5. Configure OAuth consent screen
6. Set authorized redirect URI: `http://localhost:8000/static/callback.html`
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

**🎨 Web Interface (Recommended):**
1. Start server: `python dev_server.py`
2. Visit: http://localhost:8000
3. Click **"Login with [Provider]"** (button updates based on configured provider)
4. Authorize the application
5. Test protected endpoints with your token

**🔧 Manual cURL Flow:**
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
curl -X POST "http://localhost:8000/math/add" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
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

**Access Control:**
- 🔴 **`admin`**: Full access to all math endpoints
- 🟢 **`user`**: Access to all math endpoints
- ⚪ **No auth**: OAuth flow endpoints only

---

## 🏗️ Project Structure

```
fastapi_example/
├── src/fastapi_example/
│   ├── auth/
│   │   ├── dependencies.py          # Unified auth dependency factory
│   │   └── oauth_auth.py            # OAuth token management
│   ├── routers/
│   │   ├── math.py                  # Math operations (protected)
│   │   └── oauth.py                 # OAuth flow endpoints
│   ├── workers/
│   │   └── math_operations.py       # Business logic layer
│   ├── models/
│   │   ├── input.py                 # Request/response models
│   │   └── oauth.py                 # OAuth models
│   ├── utils/
│   │   └── auth_utils.py            # Hashing & user utilities
│   ├── static/                      # OAuth test frontend
│   │   ├── index.html               # Main test page
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
| **Worker Pattern** | Business logic separated from HTTP layer for testability |
| **Unified Auth** | Single dependency factory supporting multiple auth methods |
| **Security Utilities** | `hash_api_key()` for SHA256 hashing of API keys |
| **Pydantic Models** | Automatic validation for all inputs and outputs |

---

## 🌐 API Endpoints

### Math Operations (Requires `admin` or `user` role)

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/math/add` | POST | Add two numbers | `{"A": 10, "B": 5}` → `{"result": 15}` |
| `/math/subtract` | POST | Subtract B from A | `{"A": 10, "B": 5}` → `{"result": 5}` |
| `/math/multiply` | POST | Multiply two numbers | `{"A": 7, "B": 6}` → `{"result": 42}` |
| `/math/divide` | POST | Divide A by B | `{"A": 10, "B": 2}` → `{"result": 5}` |

**Example Request:**
```bash
curl -X POST "http://localhost:8000/math/multiply" \
  -H "Authorization: Bearer your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"A": 7, "B": 6}'
```

**Response:**
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

---

## 🛠️ Development

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

#### 1️⃣ Add Business Logic

```python
# src/fastapi_example/workers/math_operations.py
def power_numbers(a: float, b: float) -> float:
    """Raise a to the power of b."""
    return a ** b
```

#### 2️⃣ Export from Worker Module

```python
# src/fastapi_example/workers/__init__.py
from fastapi_example.workers.math_operations import power_numbers

__all__ = ["power_numbers", ...]
```

#### 3️⃣ Create Route

```python
# src/fastapi_example/routers/math.py
from fastapi_example.workers import power_numbers
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

#### 4️⃣ Add Tests

```python
# tests/unit/test_workers.py
from fastapi_example.workers import power_numbers

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

---

## 📦 Installation

### From GitHub (Private Repository)

#### Using Personal Access Token

```bash
pip install "git+https://YOUR_TOKEN@github.com/jonathanvanleeuwen/fastapi_example.git@v1.0.0"
```

#### Using Git Credentials

```bash
git config --global credential.helper store
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

---

## 🔄 CI/CD

### Pre-commit Hooks

Automated code quality checks before each commit:

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

**Configured Checks:**
- ✅ Code formatting (ruff)
- ✅ Import sorting (isort)
- ✅ Trailing whitespace
- ✅ YAML/JSON syntax
- ✅ Large file detection

### Semantic Versioning

Automated releases based on commit messages:

| Commit Type | Version Change | Example |
|-------------|----------------|---------|
| `fix:` | Patch (1.0.0 → 1.0.1) | `fix: correct calculation error` |
| `feat:` | Minor (1.0.0 → 1.1.0) | `feat: add power operation` |
| `BREAKING CHANGE:` | Major (1.0.0 → 2.0.0) | `feat: redesign API`<br>`BREAKING CHANGE: removed old endpoints` |

---

## 📚 Usage Examples

### Python requests

```python
import requests

url = "http://localhost:8000/math/add"
headers = {"Authorization": "Bearer your_api_key"}
data = {"A": 10, "B": 5}

response = requests.post(url, json=data, headers=headers)
print(response.json())
# Output: {"operation": "add", "a": 10, "b": 5, "result": 15}
```

### JavaScript fetch

```javascript
const response = await fetch('http://localhost:8000/math/add', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your_api_key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ A: 10, B: 5 })
});

const data = await response.json();
console.log(data);
// Output: {operation: "add", a: 10, b: 5, result: 15}
```

### Error Handling

**Invalid Authentication:**
```bash
curl -X POST "http://localhost:8000/math/add" \
  -H "Authorization: Bearer invalid_key" \
  -d '{"A": 10, "B": 5}'

# Response: 307 Redirect to /auth/oauth/authorize
```

**Insufficient Permissions:**
```bash
# If user lacks required role
curl -X POST "http://localhost:8000/math/add" \
  -H "Authorization: Bearer user_without_role" \
  -d '{"A": 10, "B": 5}'

# Response: {"detail": "User does not have required role"}
# Status: 403 Forbidden
```

**Invalid Input:**
```bash
curl -X POST "http://localhost:8000/math/add" \
  -H "Authorization: Bearer your_api_key" \
  -d '{"A": "not_a_number", "B": 5}'

# Response: {"detail": [{"type": "float_parsing", "loc": ["body", "A"], ...}]}
# Status: 422 Unprocessable Entity
```

---

## 📊 Coverage Report

<!-- Pytest Coverage Comment:Begin -->
<!-- Pytest Coverage Comment:End -->

---

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

Made with ❤️ using FastAPI
