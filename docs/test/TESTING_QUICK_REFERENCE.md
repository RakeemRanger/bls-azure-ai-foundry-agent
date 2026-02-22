# Testing Quick Reference

## Essential Commands

### Setup

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock flake8
```

### Run Tests

```bash
# All tests with verbose output
pytest tests/ -v

# All tests with coverage
pytest tests/ -v --cov=foundry_agents --cov-report=html

# Specific test file
pytest tests/test_foundry_agents.py -v

# Specific test class
pytest tests/test_foundry_agents.py::TestSettings -v

# Specific test
pytest tests/test_foundry_agents.py::TestSettings::test_settings_initialization -v
```

### Filter Tests

```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# Skip slow tests
pytest tests/ -m "not slow"

# Keyword filter
pytest tests/ -k "registry" -v

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s
```

### Linting

```bash
# Check code style
flake8 function_app.py foundry_agents/

# Check with specific rules
flake8 foundry_agents/ --max-line-length=100

# Show statistics
flake8 foundry_agents/ --statistics
```

### Coverage

```bash
# Generate HTML report
pytest tests/ --cov=foundry_agents --cov-report=html
open htmlcov/index.html

# Generate XML report (for CI)
pytest tests/ --cov=foundry_agents --cov-report=xml

# Show missing lines
pytest tests/ --cov=foundry_agents --cov-report=term-missing
```

## Test Categories

| Category | Run command | Use case |
|----------|------------|----------|
| All | `pytest tests/` | Before commit |
| Unit | `pytest -m unit` | Fast feedback |
| Integration | `pytest -m integration` | Azure integration |
| Skip slow | `pytest -m "not slow"` | Quick runs |
| Coverage | `pytest --cov` | Coverage analysis |

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| ModuleNotFoundError | Venv not activated | `source .venv/bin/activate` |
| Permission denied | .venv in path | Check venv activation |
| No module azure | Missing requirements | `pip install -r requirements.txt` |
| Tests timeout | Slow test running | `pytest -m "not slow"` or `--timeout=30` |
| Import errors | PYTHONPATH issue | Run from workspace root |
| JSON decode error | Invalid test data | Check fixtures in conftest.py |
| Credential errors | Azure not logged in | Skip with `pytest -m "not azure"` |

## Debugging Tests

### Verbose Output

```bash
# Show all prints
pytest tests/test_foundry_agents.py::TestSettings -v -s

# Show fixture usage
pytest tests/ -v --setup-show

# Show test duration
pytest tests/ -v --durations=10
```

### Debugging with pdb

```python
# Add to test
import pdb; pdb.set_trace()

# Or use pytest --pdb flag
pytest tests/test_foundry_agents.py -v --pdb
```

### Inspect Test Parameters

```bash
# Show parametrized test variations
pytest tests/test_function_app.py::TestEnvironmentVariables --collect-only

# Run only one parameter variation
pytest tests/test_function_app.py::TestEnvironmentVariables[test_param_1] -v
```

## File Structure

```
tests/
├── __init__.py                 # Package marker
├── conftest.py                 # Shared fixtures
├── test_foundry_agents.py      # Module tests
│   ├── TestSettings
│   ├── TestToolsRegistry
│   ├── TestFoundryClient
│   ├── TestPrompts
│   └── TestIntegration
└── test_function_app.py        # Function tests
    ├── TestFunctionApp
    ├── TestQueueTriggers
    ├── TestAgentProcessing
    ├── TestErrorHandling
    └── TestEnvironmentVariables
```

## Test Markers

```python
# Mark test as unit (fast, no dependencies)
@pytest.mark.unit

# Mark test as integration (requires Azure)
@pytest.mark.integration

# Mark test as slow (skip in CI)
@pytest.mark.slow

# Mark test as requiring Azure credentials
@pytest.mark.azure

# Skip in CI environments
@pytest.mark.skip_ci

# Skip test entirely
@pytest.mark.skip(reason="Not ready yet")

# Skip on specific condition
@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
```

## Mock Objects

### Mock Azure Credentials

```python
from unittest.mock import MagicMock, patch

@patch('module.DefaultAzureCredential')
def test_with_mocked_credential(mock_cred_class):
    mock_cred = MagicMock()
    mock_cred_class.return_value = mock_cred
    # Test code
```

### Mock Azure SDK

```python
@patch('foundry_agents.ProjectClient')
def test_with_mock_project_client(mock_client_class):
    mock_client = MagicMock()
    mock_client.agents.create_agent.return_value = {
        'id': 'agent-123',
        'name': 'test-agent'
    }
    mock_client_class.return_value = mock_client
    # Test code
```

### Mock Environment

```python
import os

@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv('FOUNDRY_PROJECT_ENDPOINT', 'https://test.foundry.ai')
    monkeypatch.setenv('AI_SEARCH_CONNECTION_ID', 'test-id')
    return os.environ
```

## Fixtures

### Environment Setup

```python
# In conftest.py
@pytest.fixture
def setup_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv('FOUNDRY_PROJECT_ENDPOINT', 'https://test.url')
    yield
    # Teardown happens automatically
```

### Mock Objects

```python
@pytest.fixture
def mock_credential():
    """Mock Azure credentials"""
    with patch('module.DefaultAzureCredential') as mock:
        yield mock.return_value

@pytest.fixture
def mock_project_client():
    """Mock AI Foundry client"""
    with patch('foundry_agents.ProjectClient') as mock:
        yield mock.return_value
```

### Parametrized Fixtures

```python
@pytest.fixture(params=['param1', 'param2'])
def parametrized_fixture(request):
    """Return different values in sequence"""
    return request.param
```

## Coverage Goals

| Target | Goal |
|--------|------|
| Overall | 80%+ |
| foundry_agents | 85%+ |
| function_app | 80%+ |

### Check Coverage

```bash
# Show which lines aren't covered
pytest tests/ --cov=foundry_agents --cov-report=term-missing

# Find untested functions
coverage report -m

# Generate HTML report
coverage html && open htmlcov/index.html
```

## GitHub Actions

### Trigger Workflows

```bash
# Push changes (auto-triggers)
git push origin main

# Manual trigger
# Use GitHub Actions tab > Select workflow > Run workflow

# Or with GitHub CLI
gh workflow run validate-infra.yml
gh workflow run validate-functions.yml
```

### View Results

```bash
# CLI
gh run list
gh run view <run-id>

# Web
https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions
```

## Best Practices

### Before Committing

```bash
# Run all validations
flake8 foundry_agents/ function_app.py
pytest tests/ -v --cov=foundry_agents

# Check coverage didn't drop
coverage report | grep -E "^(TOTAL|foundry_agents)"
```

### Before Pushing

```bash
# Ensure tests pass
pytest tests/ -v

# Check no uncommitted changes
git status

# Verify branch is up to date
git pull origin main

# Push with confidence
git push origin feature-branch
```

### During Code Review

```bash
# Run specific area being reviewed
pytest tests/test_foundry_agents.py -v -k "agents"

# Check coverage for modified files
pytest tests/ --cov=foundry_agents --cov-report=term-missing | grep -A5 "function_name"
```

## Performance Tips

| Tip | Benefit | How |
|-----|---------|-----|
| Use `-m unit` | 10x faster | Skip integration tests |
| Use `-k keyword` | Faster iteration | Run related tests only |
| Cache deps | Faster installs | Already configured in workflows |
| Use fixtures | Reusable setup | Create in conftest.py |
| Mock Azure | No API latency | Use mock objects |
| Parallel tests | N cores faster | `pytest -n auto` with pytest-xdist |

## Useful Pytest Plugins

```bash
# Parallel test execution
pip install pytest-xdist
pytest tests/ -n auto

# Test coverage
pip install pytest-cov
pytest tests/ --cov=foundry_agents

# Mock utilities
pip install pytest-mock

# Timeout protection
pip install pytest-timeout
pytest tests/ --timeout=10

# Test reports
pip install pytest-html
pytest tests/ --html=report.html
```

## References

- [Pytest Docs](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Flake8](https://flake8.pycqa.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
