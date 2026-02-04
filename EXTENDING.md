# Extending the FastAPI Example Application

This guide helps you add new features to the application using the established patterns.

## Adding a New Worker Function

Workers contain your business logic. They're pure functions that don't know about HTTP.

**Example: Add a power function**

1. Add the function to `src/fastapi_example/workers/math_operations.py`:

```python
def power_numbers(a: float, b: float) -> float:
    result = a ** b
    logger.debug(f"Calculating {a} ^ {b} = {result}")
    return result
```

2. Export it from `src/fastapi_example/workers/__init__.py`:

```python
from fastapi_example.workers.math_operations import (
    add_numbers,
    divide_numbers,
    multiply_numbers,
    power_numbers,  # Add this
    subtract_numbers,
)

__all__ = [
    "add_numbers",
    "subtract_numbers",
    "multiply_numbers",
    "divide_numbers",
    "power_numbers",  # Add this
]
```

3. Add tests in `tests/unit/test_workers.py`:

```python
def test_power_numbers():
    assert power_numbers(2, 3) == 8
    assert power_numbers(5, 2) == 25
    assert power_numbers(10, 0) == 1
```

## Adding a New API Endpoint

Endpoints connect HTTP requests to your workers.

1. Add endpoint to `src/fastapi_example/routers/production.py`:

```python
from fastapi_example.workers import power_numbers  # Add to imports

@fastapi_router.post("/power", operation_id="power_numbers", status_code=200)
def power(input_data: InputData, user: str = Depends(get_current_user)) -> dict:
    logger.debug(f"User {user} requesting power operation")
    result = power_numbers(input_data.A, input_data.B)
    return {"operation": "power", "a": input_data.A, "b": input_data.B, "result": result}
```

2. Add tests in `tests/unit/test_routers.py`:

```python
def test_power_endpoint_success(client, admin_headers, sample_input_data):
    response = client.post(
        "/fastapi_example/power", json=sample_input_data, headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["operation"] == "power"
    assert data["result"] == 100000.0  # 10 ^ 5
```

## Creating a New Worker Module

For larger features, create a new worker module.

1. Create `src/fastapi_example/workers/string_operations.py`:

```python
import logging

logger = logging.getLogger(__name__)


def reverse_string(text: str) -> str:
    result = text[::-1]
    logger.debug(f"Reversing '{text}' to '{result}'")
    return result


def uppercase_string(text: str) -> str:
    result = text.upper()
    logger.debug(f"Uppercasing '{text}' to '{result}'")
    return result
```

2. Update `src/fastapi_example/workers/__init__.py`:

```python
from fastapi_example.workers.string_operations import (
    reverse_string,
    uppercase_string,
)

__all__ = [
    # ... existing exports
    "reverse_string",
    "uppercase_string",
]
```

3. Create a new router `src/fastapi_example/routers/strings.py`:

```python
import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from fastapi_example.auth.api_key_auth import get_current_user
from fastapi_example.workers import reverse_string, uppercase_string

logger = logging.getLogger(__name__)

string_router = APIRouter(tags=["strings"], prefix="/strings")


class StringInput(BaseModel):
    text: str


@string_router.post("/reverse", status_code=200)
def reverse(input_data: StringInput, user: str = Depends(get_current_user)) -> dict:
    result = reverse_string(input_data.text)
    return {"operation": "reverse", "input": input_data.text, "result": result}


@string_router.post("/uppercase", status_code=200)
def uppercase(input_data: StringInput, user: str = Depends(get_current_user)) -> dict:
    result = uppercase_string(input_data.text)
    return {"operation": "uppercase", "input": input_data.text, "result": result}
```

4. Register the router in `src/fastapi_example/main.py`:

```python
from fastapi_example.routers.strings import string_router  # Add import

# Add to app
app.include_router(string_router, dependencies=[Depends(auth_user)])
```

## Adding New Pydantic Models

Models define your API's data structures.

1. Create `src/fastapi_example/models/complex_input.py`:

```python
from pydantic import BaseModel, Field


class ComplexInput(BaseModel):
    real: float = Field(description="Real part of complex number")
    imaginary: float = Field(description="Imaginary part of complex number")


class ComplexOutput(BaseModel):
    magnitude: float
    phase: float
```

2. Use in your router:

```python
from fastapi_example.models.complex_input import ComplexInput, ComplexOutput

@router.post("/complex/magnitude", response_model=ComplexOutput)
def calculate_magnitude(data: ComplexInput) -> ComplexOutput:
    magnitude = (data.real**2 + data.imaginary**2) ** 0.5
    phase = ...
    return ComplexOutput(magnitude=magnitude, phase=phase)
```

## Adding Configuration Options

Add new settings to `src/fastapi_example/settings.py`:

```python
class Settings(BaseSettings):
    # ... existing settings

    # Your new setting
    max_calculation_size: int = 1000000
    enable_caching: bool = False
    cache_ttl_seconds: int = 300
```

Access in your code:

```python
from fastapi_example.settings import get_settings

def some_function():
    settings = get_settings()
    if settings.enable_caching:
        # Use cache
        pass
```

## Adding Test Fixtures

Reusable test data goes in `tests/conftest.py`:

```python
@pytest.fixture
def complex_input_data():
    """Sample complex number input."""
    return {"real": 3.0, "imaginary": 4.0}


@pytest.fixture
def mock_external_api():
    """Mock external API responses."""
    with patch("requests.get") as mock:
        mock.return_value.json.return_value = {"status": "success"}
        yield mock
```

Use in tests:

```python
def test_with_fixture(client, admin_headers, complex_input_data):
    response = client.post(
        "/endpoint", json=complex_input_data, headers=admin_headers
    )
    assert response.status_code == 200
```

## Best Practices Checklist

When adding new features:

- [ ] Business logic is in workers, not routers
- [ ] Functions are small and do one thing
- [ ] Variable names are descriptive
- [ ] Added unit tests for workers
- [ ] Added integration tests for endpoints
- [ ] Updated docstrings if needed (but prefer self-documenting code)
- [ ] Ran pytest to verify all tests pass
- [ ] Ran pre-commit hooks
- [ ] Code is simple enough for a junior to understand

## Common Patterns

### Pattern: Validation in Pydantic

```python
from pydantic import BaseModel, field_validator

class PositiveNumbers(BaseModel):
    value: float

    @field_validator('value')
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('must be positive')
        return v
```

### Pattern: Async Workers

```python
import asyncio

async def fetch_data_async(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

### Pattern: Error Handling

```python
from fastapi import HTTPException, status

def divide_safely(a: float, b: float) -> float:
    if b == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Division by zero is not allowed"
        )
    return a / b
```

### Pattern: Dependency Injection

```python
from fastapi import Depends

def get_db_session():
    # Create session
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@router.get("/items")
def get_items(db: Session = Depends(get_db_session)):
    return db.query(Item).all()
```

## Testing Strategies

### Testing Workers (Pure Functions)

```python
def test_worker_function():
    # Arrange
    input_a = 10
    input_b = 5

    # Act
    result = add_numbers(input_a, input_b)

    # Assert
    assert result == 15
```

### Testing Endpoints (Integration)

```python
def test_endpoint(client, admin_headers):
    # Arrange
    data = {"A": 10, "B": 5}

    # Act
    response = client.post("/endpoint", json=data, headers=admin_headers)

    # Assert
    assert response.status_code == 200
    assert response.json()["result"] == 15
```

### Testing with Mocks

```python
from unittest.mock import patch

def test_external_api_call(client, admin_headers):
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value.json.return_value = {"data": "mocked"}

        response = client.get("/fetch-data", headers=admin_headers)

        assert response.status_code == 200
        mock_get.assert_called_once()
```

## Need Help?

- Check existing code for similar patterns
- Read the FastAPI docs: https://fastapi.tiangolo.com/
- Look at the tests to understand how things work
- Keep it simple - if it's getting complex, break it down
