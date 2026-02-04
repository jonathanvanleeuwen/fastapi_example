# fastapi_example

A FastAPI template application with modern authentication, worker pattern, and CI/CD setup.

## 📚 Documentation

- **[Setup Checklist](SETUP_CHECKLIST.md)** - Step-by-step setup guide for beginners
- **[Architecture Overview](ARCHITECTURE.md)** - Understanding how the app is structured
- **[Quick Reference](QUICK_REFERENCE.md)** - Commands, endpoints, and common tasks at a glance
- **[Usage Examples](USAGE_EXAMPLES.md)** - Practical code examples for API requests
- **[Extending Guide](EXTENDING.md)** - Step-by-step guide for adding new features
- **[Changes Summary](CHANGES.md)** - Overview of recent enhancements

---

## Features

### Core Features
* **Worker/Service Layer Pattern**: Clean separation between API routes and business logic
* **Dual Authentication System**:
  - API Key authentication for simple service-to-service auth
  - OAuth 2.0 support for Google, Azure AD, and GitHub
* **Sample Math Operations API**: Template endpoints demonstrating the worker pattern
* **Modern Python Packaging**: Using pyproject.toml with proper dependency management

### Development & CI/CD
* Automated testing on PR using GitHub Actions
* Pre-commit hooks for code quality (ruff, isort, trailing whitespace, etc.)
* Semantic release using GitHub Actions
* Automatic code coverage report in README
* Automatic wheel build and GitHub Release publishing

*Notes*:
- Workflows trigger when a branch is merged into main
- This template is designed for juniors to understand and extend
- Code is intentionally simple and well-structured

---

## Quick Start

### Running the Application

1. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Run the development server:
   ```bash
   python dev_server.py
   ```

3. Visit the interactive API docs at http://localhost:8000/docs

---

## Authentication

This application supports two authentication methods:

### 1. API Key Authentication (Recommended for service-to-service)

API keys are stored in a base64-encoded JSON structure. This keeps secrets out of your code!

#### How API Keys Work

The `secrets.json` file (or `FASTAPI_EXAMPLE_API_KEYS` environment variable) contains:
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

**How to use:**
1. The keys (like `"your_secret_key_here"`) are the actual API keys users send
2. Each key has a username and list of roles
3. Endpoints can require specific roles (e.g., only "admin" can access certain routes)

#### Setting Up API Keys

**Option 1: Environment Variable (Production)**
```bash
# Encode your secrets.json to base64
python -c "import base64, json; print(base64.b64encode(json.dumps({'key1': {'username': 'user1', 'roles': ['admin']}}).encode()).decode())"

# Set as environment variable
export FASTAPI_EXAMPLE_API_KEYS="<base64_encoded_string>"
```

**Option 2: Direct JSON (Development)**
See `src/fastapi_example/auth/secrets_example.json` for the structure.

#### Using API Keys in Requests

```bash
curl -X POST "http://localhost:8000/fastapi_example/add" \
  -H "Authorization: Bearer your_secret_key_here" \
  -H "Content-Type: application/json" \
  -d '{"A": 10, "B": 5}'
```

### 2. OAuth Authentication (For user login flows)

OAuth allows users to log in with their Google, Azure AD, or GitHub accounts.

#### OAuth Setup

1. **Get OAuth credentials** from your provider:
   - Google: [Google Cloud Console](https://console.cloud.google.com/)
   - Azure: [Azure Portal](https://portal.azure.com/)
   - GitHub: [GitHub OAuth Apps](https://github.com/settings/developers)

2. **Set environment variables**:
   ```bash
   export FASTAPI_EXAMPLE_OAUTH_CLIENT_ID="your_client_id"
   export FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET="your_client_secret"
   export FASTAPI_EXAMPLE_OAUTH_SECRET_KEY="your-secret-key-min-32-chars"

   # For Azure only:
   export FASTAPI_EXAMPLE_OAUTH_TENANT_ID="your_tenant_id"
   ```

#### OAuth Flow (How it works)

1. **Get authorization URL**:
   ```bash
   curl -X POST "http://localhost:8000/auth/oauth/authorize" \
     -H "Content-Type: application/json" \
     -d '{"provider": "google", "redirect_uri": "http://localhost/callback"}'
   ```

2. **User visits the URL** and authorizes your app

3. **Exchange code for token**:
   ```bash
   curl -X POST "http://localhost:8000/auth/oauth/token" \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "google",
       "code": "authorization_code_from_step_2",
       "redirect_uri": "http://localhost/callback"
     }'
   ```

4. **Use the access token** in subsequent requests:
   ```bash
   curl -X POST "http://localhost:8000/fastapi_example/add" \
     -H "Authorization: Bearer <access_token>" \
     -H "Content-Type: application/json" \
     -d '{"A": 10, "B": 5}'
   ```

---

## Project Structure

```
fastapi_example/
├── src/fastapi_example/
│   ├── auth/                      # Authentication modules
│   │   ├── api_key_auth.py       # API key authentication
│   │   ├── oauth_auth.py         # OAuth authentication
│   │   └── secrets_example.json  # Example API keys structure
│   ├── routers/                   # API route definitions
│   │   ├── production.py         # Production endpoints
│   │   ├── testing.py            # Test endpoints (dev only)
│   │   └── oauth.py              # OAuth flow endpoints
│   ├── workers/                   # Business logic layer
│   │   └── math_operations.py   # Example: Math operations
│   ├── models/                    # Pydantic models
│   │   └── input.py              # Request/response models
│   ├── custom_logger/            # Logging configuration
│   ├── main.py                    # Application entry point
│   └── settings.py               # Configuration management
├── tests/
│   ├── conftest.py               # Shared test fixtures
│   └── unit/                     # Unit tests
└── pyproject.toml                # Dependencies and metadata
```

### Understanding the Worker Pattern

The **worker** (or service layer) separates your business logic from your API routes:

```python
# ❌ BAD: Business logic in the route
@app.post("/add")
def add(data: InputData):
    result = data.A + data.B  # Logic mixed with routing
    return {"result": result}

# ✅ GOOD: Business logic in worker
@app.post("/add")
def add(data: InputData):
    result = add_numbers(data.A, data.B)  # Clean separation
    return {"result": result}
```

**Benefits:**
- Easy to test business logic independently
- Reuse logic across multiple endpoints
- Clear responsibility: routes handle HTTP, workers handle business logic

---

## API Endpoints

### Math Operations (Requires Admin Role)

All endpoints accept JSON with `A` and `B` numbers:

- `POST /fastapi_example/add` - Add two numbers
- `POST /fastapi_example/subtract` - Subtract B from A
- `POST /fastapi_example/multiply` - Multiply two numbers
- `POST /fastapi_example/divide` - Divide A by B

**Example:**
```bash
curl -X POST "http://localhost:8000/fastapi_example/multiply" \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"A": 7, "B": 6}'

# Response: {"operation": "multiply", "a": 7, "b": 6, "result": 42}
```

### OAuth Endpoints (No Auth Required)

- `POST /auth/oauth/authorize` - Get authorization URL
- `POST /auth/oauth/token` - Exchange code for token

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fastapi_example --cov-report=html

# Run specific test file
pytest tests/unit/test_workers.py
```

### Adding New Endpoints

1. **Add business logic** to a worker:
   ```python
   # src/fastapi_example/workers/my_worker.py
   def process_data(input: str) -> str:
       return input.upper()
   ```

2. **Create the route**:
   ```python
   # src/fastapi_example/routers/production.py
   from fastapi_example.workers.my_worker import process_data

   @router.post("/process")
   def process(data: str):
       result = process_data(data)
       return {"result": result}
   ```

3. **Add tests**:
   ```python
   # tests/unit/test_my_worker.py
   def test_process_data():
       assert process_data("hello") == "HELLO"
   ```

### Environment Variables

Create a `.env` file for local development:

```bash
# App settings
FASTAPI_EXAMPLE_STAGE=development

# API Keys (base64 encoded JSON)
FASTAPI_EXAMPLE_API_KEYS="eyJ0ZXN0Ijp7InVzZXJuYW1lIjoiSm9uYXRoYW4iLCJyb2xlcyI6WyJhZG1pbiIsInVzZXIiXX19"

# OAuth (optional - only if using OAuth)
FASTAPI_EXAMPLE_OAUTH_CLIENT_ID=your_client_id
FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET=your_client_secret
FASTAPI_EXAMPLE_OAUTH_SECRET_KEY=your-secret-key-min-32-chars
FASTAPI_EXAMPLE_OAUTH_TENANT_ID=your_tenant_id  # Azure only
```

---

---

## Installation (For Distribution)

### Option 1: Install from Private GitHub Release (Recommended)
Since this is a private repository, you need to authenticate with a GitHub Personal Access Token (PAT).

### Configure git credentials (more secure, recommended)
This method doesn't expose your token in command history:

```bash
# Store credentials in git (one-time setup)
git config --global credential.helper store

# Then install normally - git will prompt for credentials once
pip install "git+https://github.com/jonathanvanleeuwen/fastapi_example.git@VERSION"
# When prompted: username = your GitHub username, password = your PAT
```

### Step 1: Create a Personal Access Token (one-time setup)

1. Go to [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it a descriptive name (e.g., `fastapi_example-install`)
4. Select the **`repo`** scope (required for private repositories)
5. Click **"Generate token"**
6. **Copy the token immediately** - you won't be able to see it again!

### Step 2: Install the package

```bash
# Replace YOUR_TOKEN with your actual token and VERSION with the desired version (e.g., v1.0.0)
pip install "git+https://YOUR_TOKEN@github.com/jonathanvanleeuwen/fastapi_example.git@VERSION"

# Install the latest version (main branch):
pip install "git+https://YOUR_TOKEN@github.com/jonathanvanleeuwen/fastapi_example.git"
```

### Using uv (faster alternative to pip)

```bash
uv pip install "git+https://YOUR_TOKEN@github.com/jonathanvanleeuwen/fastapi_example.git@v1.0.0"
```

## Option 2: Install from Wheel File in Repository

The latest wheel files are also committed to the `dist/` directory in the repository. After cloning:

```bash
# Clone the repository first
git clone https://github.com/jonathanvanleeuwen/fastapi_example.git

# Install the wheel file directly
pip install fastapi_example/dist/fastapi_example-1.0.0-py3-none-any.whl
```

> **Note:** Replace the version number with the actual version in the `dist/` directory.

## Option 3: Install from Source (Clone Repository)

```bash
# Clone the repository
git clone https://github.com/jonathanvanleeuwen/fastapi_example.git
cd fastapi_example

# Install using pip
pip install .

# Or install in editable/development mode with dev dependencies
pip install -e ".[dev]"
```

## Option 4: Add to requirements.txt or pyproject.toml

**In requirements.txt:**

```txt
fastapi_example @ git+https://github.com/jonathanvanleeuwen/fastapi_example.git@v1.0.0
```

**In pyproject.toml (for projects using PEP 621):**

```toml
[project]
dependencies = [
    "fastapi_example @ git+https://github.com/jonathanvanleeuwen/fastapi_example.git@v1.0.0",
]
```

## Building a Wheel File Locally

```bash
pip install build
python -m build --wheel
# The wheel will be created in the dist/ directory
```


---

# Pre-commit Setup (For Contributors)

This project uses pre-commit hooks to ensure code quality.

1. Install pre-commit:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. Run on all files (first time):
   ```bash
   pre-commit run --all-files
   ```

Pre-commit will now run automatically on every commit, checking:
- Code formatting (ruff)
- Import sorting (isort)
- Trailing whitespace
- YAML/JSON syntax
- And more...

---

# Semantic Release (For Maintainers)

https://python-semantic-release.readthedocs.io/en/latest/

The workflows are triggered when you merge into main!

When committing, use the following format for your commit message:

**Patch release** (1.0.0 → 1.0.1):
```
fix: your commit message
```

**Minor release** (1.0.0 → 1.1.0):
```
feat: your commit message
```

**Major/breaking release** (1.0.0 → 2.0.0):
```
feat: your commit message

BREAKING CHANGE: description of breaking change
```


# Coverage Report
<!-- Pytest Coverage Comment:Begin -->
<!-- Pytest Coverage Comment:End -->
