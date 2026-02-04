# Setup Checklist for Juniors

Follow this checklist to verify your FastAPI example setup is working correctly.

## Prerequisites

- [ ] Python 3.12 or higher installed
  ```bash
  python --version  # Should show 3.12 or higher
  ```

- [ ] Git installed (for cloning the repository)
  ```bash
  git --version
  ```

## Initial Setup

- [ ] Clone the repository
  ```bash
  git clone https://github.com/jonathanvanleeuwen/fastapi_example.git
  cd fastapi_example
  ```

- [ ] Create a virtual environment
  ```bash
  python -m venv .venv
  ```

- [ ] Activate the virtual environment
  ```bash
  # Windows
  .venv\Scripts\activate

  # macOS/Linux
  source .venv/bin/activate
  ```

- [ ] Install dependencies
  ```bash
  pip install -e ".[dev]"
  ```

## Verify Installation

- [ ] Check that imports work
  ```bash
  python -c "from fastapi_example.main import app; print('✓ Imports work!')"
  ```

- [ ] Run tests
  ```bash
  pytest
  ```
  All tests should pass (green).

## Run the Application

- [ ] Start the development server
  ```bash
  python dev_server.py
  ```

- [ ] Visit the API docs
  Open http://localhost:8000/docs in your browser
  You should see the interactive API documentation (Swagger UI)

- [ ] Test the root endpoint
  Visit http://localhost:8000/
  Should redirect to /docs

## Test Authentication

- [ ] Test API Key authentication with curl
  ```bash
  curl -X POST "http://localhost:8000/fastapi_example/add" \
    -H "Authorization: Bearer test" \
    -H "Content-Type: application/json" \
    -d "{\"A\": 10, \"B\": 5}"
  ```
  Expected response: `{"operation":"add","a":10,"b":5,"result":15}`

- [ ] Test via the interactive docs
  1. Go to http://localhost:8000/docs
  2. Click on any endpoint (e.g., `/fastapi_example/add`)
  3. Click "Try it out"
  4. Click the lock icon 🔒 and enter API key: `test`
  5. Fill in the request body: `{"A": 10, "B": 5}`
  6. Click "Execute"
  7. Should see a successful response

## Understanding the Code

- [ ] Read the worker function
  Open `src/fastapi_example/workers/math_operations.py`
  Understand how `add_numbers()` works

- [ ] Read a router
  Open `src/fastapi_example/routers/production.py`
  See how the endpoint calls the worker function

- [ ] Read a test
  Open `tests/unit/test_workers.py`
  Understand how tests verify worker functions

## Optional: OAuth Setup

Only complete this if you need OAuth authentication.

- [ ] Get OAuth credentials from a provider (Google, Azure, or GitHub)

- [ ] Create a `.env` file (copy from `.env.example`)
  ```bash
  cp .env.example .env
  ```

- [ ] Edit `.env` and add your OAuth credentials
  ```bash
  FASTAPI_EXAMPLE_OAUTH_CLIENT_ID=your_client_id
  FASTAPI_EXAMPLE_OAUTH_CLIENT_SECRET=your_client_secret
  FASTAPI_EXAMPLE_OAUTH_SECRET_KEY=your-secret-key-min-32-chars
  ```

- [ ] Restart the server and test OAuth endpoints
  ```bash
  curl -X POST "http://localhost:8000/auth/oauth/authorize" \
    -H "Content-Type: application/json" \
    -d '{"provider": "google", "redirect_uri": "http://localhost/callback"}'
  ```

## Pre-commit Hooks (Recommended)

- [ ] Install pre-commit
  ```bash
  pip install pre-commit
  pre-commit install
  ```

- [ ] Run pre-commit on all files
  ```bash
  pre-commit run --all-files
  ```
  Fix any issues that come up

## Try Adding a Feature

- [ ] Read the [Extending Guide](EXTENDING.md)

- [ ] Add a simple worker function
  Example: Create a function that squares a number

- [ ] Create an endpoint for your function

- [ ] Write a test for your function

- [ ] Run tests to verify
  ```bash
  pytest
  ```

## Common Issues

### "Module not found" errors
**Solution:** Make sure you're in the virtual environment and dependencies are installed
```bash
pip install -e ".[dev]"
```

### "Port already in use" error
**Solution:** Stop other servers or use a different port
```bash
python dev_server.py  # or
uvicorn fastapi_example.main:app --port 8001
```

### Tests fail
**Solution:** Make sure you're in the project root directory
```bash
cd fastapi_example
pytest
```

### Pre-commit issues
**Solution:** Run manually and fix reported issues
```bash
pre-commit run --all-files
```

## Next Steps

Once everything is working:

1. **Explore the API**
   - Visit http://localhost:8000/docs
   - Try all the endpoints
   - Understand the request/response structure

2. **Read the Code**
   - Start with `main.py` to see how the app is structured
   - Look at the workers to understand business logic
   - Check out the tests to learn testing patterns

3. **Read Documentation**
   - [Quick Reference](QUICK_REFERENCE.md) for commands
   - [Usage Examples](USAGE_EXAMPLES.md) for API usage
   - [Extending Guide](EXTENDING.md) for adding features

4. **Try Modifying**
   - Add a new math operation
   - Create a new endpoint
   - Write tests for your code

5. **Ask for Help**
   - If stuck, check the documentation files
   - Look at existing code for patterns
   - Ask your team for guidance

## Success Criteria

You've successfully set up the project when:

✅ All tests pass
✅ The server runs without errors
✅ You can make API requests successfully
✅ You understand the basic project structure
✅ You can read and understand the code

**Congratulations! You're ready to start developing.** 🎉
