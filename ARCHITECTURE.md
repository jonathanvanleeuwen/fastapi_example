# Architecture Overview

This document explains how the FastAPI example application is structured.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client                               │
│  (Browser, curl, Python requests, JavaScript fetch, etc.)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ HTTP Request
                       │ (with Authorization header)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    main.py                            │  │
│  │  - Creates FastAPI app                                │  │
│  │  - Registers routers                                  │  │
│  │  - Configures middleware (CORS)                       │  │
│  └──────────────┬────────────────────────────────────────┘  │
│                 │                                            │
│                 ▼                                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Authentication Layer                     │  │
│  │  ┌─────────────────┐  ┌──────────────────┐           │  │
│  │  │  api_key_auth   │  │   oauth_auth     │           │  │
│  │  │  - Validates    │  │  - JWT tokens    │           │  │
│  │  │    API keys     │  │  - OAuth flow    │           │  │
│  │  │  - Checks roles │  │  - Providers     │           │  │
│  │  └─────────────────┘  └──────────────────┘           │  │
│  └──────────────┬────────────────────────────────────────┘  │
│                 │                                            │
│                 ▼                                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Routers                            │  │
│  │  ┌──────────────┐  ┌──────────┐  ┌───────────────┐   │  │
│  │  │ production   │  │  oauth   │  │   testing     │   │  │
│  │  │  - /add      │  │ /authorize│ │  /test        │   │  │
│  │  │  - /subtract │  │ /token   │  │  (dev only)   │   │  │
│  │  │  - /multiply │  │          │  │               │   │  │
│  │  │  - /divide   │  │          │  │               │   │  │
│  │  └──────┬───────┘  └──────────┘  └───────────────┘   │  │
│  └─────────┼──────────────────────────────────────────────┘  │
│            │                                                 │
│            ▼                                                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                Workers (Business Logic)               │  │
│  │  ┌────────────────────────────────────────────────┐   │  │
│  │  │        math_operations.py                      │   │  │
│  │  │  - add_numbers(a, b) → float                   │   │  │
│  │  │  - subtract_numbers(a, b) → float              │   │  │
│  │  │  - multiply_numbers(a, b) → float              │   │  │
│  │  │  - divide_numbers(a, b) → float                │   │  │
│  │  └────────────────────────────────────────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │             Models (Data Validation)                  │  │
│  │  - InputData: {A: float, B: float}                    │  │
│  │  - Pydantic validates all requests/responses          │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │            Settings (Configuration)                   │  │
│  │  - Environment variables                              │  │
│  │  - API keys (base64 encoded)                          │  │
│  │  - OAuth credentials                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow

### Example: Adding Two Numbers

```
1. Client sends request:
   POST /fastapi_example/add
   Headers: Authorization: Bearer test
   Body: {"A": 10, "B": 5}

2. FastAPI receives request
   ↓
3. Authentication layer validates API key
   - Checks if "test" exists in api_keys
   - Verifies user has "admin" role
   - Sets request.state.user = "Jonathan"
   ↓
4. Router endpoint receives request
   - Validates InputData model
   - Calls worker function: add_numbers(10, 5)
   ↓
5. Worker executes business logic
   - result = 10 + 5 = 15
   - Returns 15
   ↓
6. Router formats response
   - {"operation": "add", "a": 10, "b": 5, "result": 15}
   ↓
7. FastAPI sends response to client
   - Status: 200 OK
   - Content-Type: application/json
```

## Layer Responsibilities

### 1. **Routers** (`routers/`)
**What:** Handle HTTP requests and responses
**Responsibility:**
- Define API endpoints
- Extract data from requests
- Call worker functions
- Format responses
- Handle HTTP-specific concerns

**Don't:** Contain business logic, do calculations, make decisions

### 2. **Workers** (`workers/`)
**What:** Pure business logic
**Responsibility:**
- Perform calculations
- Process data
- Make business decisions
- Reusable functions

**Don't:** Know about HTTP, requests, responses, or authentication

### 3. **Models** (`models/`)
**What:** Data structures
**Responsibility:**
- Define request/response formats
- Validate data
- Type checking
- Documentation

### 4. **Authentication** (`auth/`)
**What:** Security layer
**Responsibility:**
- Verify API keys
- Handle OAuth flow
- Check permissions
- Manage JWT tokens

### 5. **Settings** (`settings.py`)
**What:** Configuration
**Responsibility:**
- Environment variables
- Application settings
- Secrets management

## Why This Structure?

### Separation of Concerns
Each layer has ONE job:
- **Routers** = HTTP
- **Workers** = Logic
- **Models** = Data
- **Auth** = Security

### Easy Testing
```python
# Test business logic without HTTP
def test_add_numbers():
    assert add_numbers(10, 5) == 15  # Simple!

# Test HTTP separately
def test_add_endpoint(client, admin_headers):
    response = client.post("/add", json={"A": 10, "B": 5}, headers=admin_headers)
    assert response.status_code == 200
```

### Reusable Code
Workers can be used anywhere:
```python
# In a router
result = add_numbers(a, b)

# In another worker
def complex_calculation():
    x = add_numbers(1, 2)
    y = multiply_numbers(x, 3)
    return y

# In a background job
def batch_process():
    for item in items:
        result = add_numbers(item.a, item.b)
```

## Authentication Flow

### API Key Authentication

```
Client Request
    ↓
Bearer Token in Header: "Authorization: Bearer test"
    ↓
api_key_auth.py validates:
    1. Token exists? ✓
    2. User exists? ✓ (Jonathan)
    3. Has required role? ✓ (admin)
    ↓
Request proceeds to router
    ↓
Router can access: request.state.user = "Jonathan"
```

### OAuth Authentication

```
Step 1: Get Authorization URL
    Client → POST /auth/oauth/authorize
    Server → Returns URL to Google/Azure/GitHub

Step 2: User Authorizes
    User clicks URL → Authorizes app
    Provider redirects → Back to client with code

Step 3: Exchange Code
    Client → POST /auth/oauth/token with code
    Server → Calls provider with code
    Provider → Returns access token
    Server → Creates JWT token
    Server → Returns JWT to client

Step 4: Use Token
    Client → Sends JWT in Authorization header
    Server → Validates JWT
    Server → Allows access
```

## Data Flow

### Request → Response

```
HTTP Request (JSON)
    ↓
Pydantic Model (validates)
    ↓
Python Objects (type-safe)
    ↓
Worker Function (processes)
    ↓
Python Result
    ↓
Pydantic Model (validates)
    ↓
HTTP Response (JSON)
```

### Example

```python
# 1. Request comes in as JSON
{"A": 10, "B": 5}

# 2. Pydantic converts to Python object
input_data = InputData(A=10.0, B=5.0)

# 3. Router calls worker
result = add_numbers(input_data.A, input_data.B)

# 4. Worker returns Python value
15.0

# 5. Router creates response dict
{"operation": "add", "a": 10.0, "b": 5.0, "result": 15.0}

# 6. FastAPI converts to JSON and sends
```

## File Organization

```
src/fastapi_example/
├── main.py              # 🚪 Entry point - creates app
├── settings.py          # ⚙️  Configuration
├── auth/                # 🔒 Security
│   ├── api_key_auth.py
│   └── oauth_auth.py
├── routers/             # 🛣️  HTTP endpoints
│   ├── production.py
│   ├── testing.py
│   └── oauth.py
├── workers/             # ⚙️  Business logic
│   └── math_operations.py
└── models/              # 📋 Data structures
    └── input.py

tests/
├── conftest.py          # 🧪 Test fixtures
└── unit/                # 🧪 Unit tests
    ├── test_workers.py
    ├── test_routers.py
    ├── test_oauth.py
    └── test_auth.py
```

## Key Concepts for Juniors

### 1. Dependency Injection
```python
def endpoint(user: str = Depends(get_current_user)):
    # FastAPI automatically calls get_current_user()
    # and passes the result as 'user'
    print(f"User is: {user}")
```

### 2. Pydantic Models
```python
class InputData(BaseModel):
    A: float  # Automatic validation!
    B: float

# FastAPI ensures A and B are floats
# Rejects requests with wrong types
```

### 3. Router Organization
```python
router = APIRouter(prefix="/math", tags=["math"])

@router.post("/add")
def add(...):
    # Actual URL: /math/add
    pass
```

## Common Patterns

### Pattern: Router → Worker
```python
# Router (handles HTTP)
@router.post("/add")
def add_endpoint(input_data: InputData, user: str = Depends(get_current_user)):
    result = add_numbers(input_data.A, input_data.B)  # Call worker
    return {"result": result}

# Worker (pure logic)
def add_numbers(a: float, b: float) -> float:
    return a + b
```

### Pattern: Fixture in Tests
```python
# conftest.py
@pytest.fixture
def admin_headers():
    return {"Authorization": "Bearer test"}

# test_*.py
def test_endpoint(client, admin_headers):
    response = client.post("/add", headers=admin_headers, ...)
```

## Summary

The architecture is simple:
1. **Client** sends HTTP request
2. **Auth** validates credentials
3. **Router** handles HTTP and calls worker
4. **Worker** does the actual work
5. **Router** sends HTTP response

Each layer is independent and testable. This makes the code:
- Easy to understand
- Easy to test
- Easy to extend
- Easy to maintain
