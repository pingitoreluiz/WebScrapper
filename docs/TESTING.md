# Testing Guide

## Overview

This project has comprehensive test coverage across multiple levels:

- **Unit Tests:** 68 backend + 20 frontend = 88 tests
- **Integration Tests:** Database + API integration
- **E2E Tests:** Full user workflows with Playwright
- **Performance Tests:** Load testing and profiling
- **Security Tests:** Vulnerability scanning

---

## Running Tests

### All Tests

```bash
pytest
```

### By Type

```bash
# Unit tests only (fast)
pytest -m unit

# Integration tests
pytest -m integration

# E2E tests
pytest -m e2e

# Performance tests
pytest -m performance

# Security tests
pytest -m security
```

### By Directory

```bash
# Backend unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/
```

### Specific Test File

```bash
pytest tests/integration/test_api_integration.py
```

### Specific Test Function

```bash
pytest tests/integration/test_api_integration.py::TestProductEndpoints::test_list_products_with_data
```

---

## Test Coverage

### Generate Coverage Report

```bash
# Run tests with coverage
pytest --cov=src --cov-report=html

# Open HTML report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### Coverage Requirements

- **Minimum:** 80% overall coverage
- **Target:** 90%+ for critical modules
- **Unit Tests:** 100% (already achieved)

---

## Integration Tests

### Prerequisites

Integration tests use an in-memory SQLite database, so no setup required.

### Running

```bash
pytest tests/integration/ -v
```

### What's Tested

- Scraping workflow (scraper → database → validation)
- API endpoints with real database
- Data processors (cleaner, validator, enricher)
- Data integrity constraints

---

## E2E Tests

### Prerequisites

```bash
# Install Playwright
pip install playwright
playwright install chromium
```

### Running

```bash
# Run E2E tests
pytest tests/e2e/ -v

# Run with visible browser (debugging)
pytest tests/e2e/ -v --headed

# Run specific browser
pytest tests/e2e/ --browser=firefox
```

### What's Tested

- Dashboard loading and display
- Scraper controls
- Product search and filtering
- Navigation between pages
- Responsive design
- Error handling

---

## Performance Tests

### Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/performance/test_load.py --host=http://localhost:8000

# Open browser to http://localhost:8089
```

### Profiling

```bash
# Run profiling tests
pytest tests/performance/test_profiling.py -v
```

---

## Security Tests

### Dependency Scanning

```bash
# Install tools
pip install safety bandit

# Scan dependencies
safety check

# Scan code
bandit -r src/
```

### Security Tests

```bash
pytest tests/security/ -v
```

---

## Test Markers

Use markers to categorize and run specific test groups:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.e2e
def test_e2e():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

---

## Continuous Integration

Tests run automatically on:

- Push to `main` branch
- Pull requests
- Manual workflow dispatch

See `.github/workflows/ci.yml` for configuration.

---

## Troubleshooting

### Tests Failing Locally

1. **Database issues:**

   ```bash
   # Clear test database
   rm test.db
   ```

2. **Browser issues (E2E):**

   ```bash
   # Reinstall browsers
   playwright install --force
   ```

3. **Import errors:**

   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

### Slow Tests

```bash
# Run only fast tests
pytest -m "not slow"

# Show slowest tests
pytest --durations=10
```

### Coverage Not Updating

```bash
# Clear coverage data
coverage erase

# Run tests again
pytest --cov=src
```

---

## Writing New Tests

### Unit Test Template

```python
import pytest
from src.module import function

class TestFunction:
    def test_basic_case(self):
        result = function(input)
        assert result == expected
    
    def test_edge_case(self):
        with pytest.raises(ValueError):
            function(invalid_input)
```

### Integration Test Template

```python
import pytest

class TestIntegration:
    def test_with_database(self, db_session):
        # Use db_session fixture
        # Test database operations
        pass
```

### E2E Test Template

```python
from playwright.sync_api import Page, expect

def test_user_flow(page: Page, base_url: str):
    page.goto(base_url)
    expect(page.locator("h1")).to_be_visible()
```

---

## Best Practices

1. **Keep tests isolated** - Each test should be independent
2. **Use fixtures** - Reuse common setup code
3. **Test edge cases** - Not just happy paths
4. **Clear assertions** - Make failures easy to understand
5. **Fast tests** - Keep unit tests under 1 second
6. **Descriptive names** - Test names should explain what they test

---

**Last Updated:** 2026-01-26
