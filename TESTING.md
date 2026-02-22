# Testing Guide for Azure AI Foundry Function App

## Overview

This project includes comprehensive testing for both infrastructure and function code:

- **Infrastructure Validation**: Bicep template validation and dry-run deployment checks
- **Function Validation**: Python syntax, imports, and startup checks
- **Unit Tests**: Tests for foundry_agents module and Azure Functions
- **Integration Tests**: End-to-end testing (requires Azure credentials)

## Test Structure

```
tests/
├── __init__.py                 # Test package marker
├── conftest.py                 # Pytest configuration and fixtures
├── test_foundry_agents.py      # Unit tests for foundry_agents module
└── test_function_app.py        # Tests for Azure Functions

.github/workflows/
├── validate-infra.yml          # Infrastructure validation workflow
└── validate-functions.yml      # Function validation workflow
```

## Running Tests Locally

### Prerequisites

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=foundry_agents --cov-report=html

# Run specific test file
pytest tests/test_foundry_agents.py -v

# Run specific test class
pytest tests/test_foundry_agents.py::TestSettings -v

# Run specific test function
pytest tests/test_foundry_agents.py::TestSettings::test_settings_initialization -v
```

### Run by Category

```bash
# Run only unit tests
pytest tests/ -v -m "unit"

# Run only integration tests
pytest tests/ -v -m "integration"

# Skip slow tests
pytest tests/ -v -m "not slow"

# Run Azure-authenticated tests only (when logged in)
pytest tests/ -v -m "azure"
```

### Generate Coverage Report

```bash
# Generate and open HTML coverage report
pytest tests/ --cov=foundry_agents --cov-report=html
open htmlcov/index.html
```

## GitHub Actions Workflows

### Validate Infrastructure (automatic on PR/push)

Triggered by:
- Push to `main` with changes to `infra/*.bicep`
- Pull requests to `main` with infrastructure changes
- Manual workflow dispatch

Checks:
- ✅ Bicep template syntax validation
- ✅ Azure resource schema validation
- ✅ Deployment dry-run (no actual deployment)
- ✅ Code quality (description, TODO comments)

View results: GitHub > Actions > Validate Infrastructure

### Validate Functions (automatic on PR/push)

Triggered by:
- Push to `main` with changes to function code
- Pull requests with function changes
- Manual workflow dispatch

Checks:
- ✅ Python syntax validation
- ✅ Import validation
- ✅ Unit tests (pytest)
- ✅ Code linting (flake8)
- ✅ Function structure validation
- ✅ Metadata verification

View results: GitHub > Actions > Validate Functions

## Test Categories

### Unit Tests

**Location**: `tests/test_foundry_agents.py`

Tests for individual components without Azure dependencies:

```python
@pytest.mark.unit
def test_tool_registry_structure():
    """Test that TOOL_REGISTRY is properly structured"""
    from foundry_agents.configs.tools_registry import TOOL_REGISTRY
    assert isinstance(TOOL_REGISTRY, dict)
```

Run: `pytest tests/ -v -m "unit"`

### Integration Tests

**Location**: `tests/test_function_app.py`

Tests that require Azure resources and credentials:

```python
@pytest.mark.integration
@pytest.mark.azure
def test_with_azure_credentials():
    """Test that requires Azure login"""
    # Only runs when AZURE_SUBSCRIPTION_ID is set
```

Run: `pytest tests/ -v -m "integration"`

**Note**: Integration tests are skipped unless you have:
- Azure CLI logged in
- `AZURE_SUBSCRIPTION_ID` environment variable set

### Slow Tests

Long-running tests marked for CI/CD skip:

```python
@pytest.mark.slow
def test_deployment_takes_long():
    """This test is slow and skipped in CI"""
```

Run: `pytest tests/ -v --no-skip-slow`

## Writing Tests

### Test Naming Conventions

- Test files: `test_*.py` or `*_test.py`
- Test classes: `Test*` (e.g., `TestSettings`)
- Test functions: `test_*` (e.g., `test_initialization`)

### Example Test

```python
import pytest
from unittest.mock import patch, MagicMock

class TestMyFeature:
    """Test suite for my feature"""
    
    def test_basic_functionality(self):
        """Test that feature works"""
        # Arrange
        expected = 42
        
        # Act
        result = my_function()
        
        # Assert
        assert result == expected
    
    @pytest.mark.parametrize("input,expected", [
        ("a", 1),
        ("b", 2),
    ])
    def test_multiple_inputs(self, input, expected):
        """Test with multiple inputs"""
        assert my_function(input) == expected
    
    @patch('module.dependency')
    def test_with_mock(self, mock_dep):
        """Test with mocked dependencies"""
        mock_dep.return_value = MagicMock()
        result = my_function()
        assert result is not None
```

### Using Fixtures

```python
import pytest

@pytest.fixture
def sample_data():
    """Fixture that provides test data"""
    return {
        'name': 'test',
        'value': 42
    }

def test_with_fixture(sample_data):
    """Test using fixture"""
    assert sample_data['value'] == 42
```

### Mocking Azure Services

```python
from unittest.mock import patch, MagicMock

@patch('foundry_agents.utils.foundry_client.AIProjectClient')
def test_with_mock_client(mock_client_class):
    """Test without actual Azure connection"""
    mock_client = MagicMock()
    mock_client.agents.create_agent.return_value = {'id': 'test'}
    mock_client_class.return_value = mock_client
    
    # Your test code here
```

## Best Practices

### Do's

✅ **Do**: Test one thing per test function
```python
def test_settings_endpoint_is_valid():
    """Test just the endpoint validation"""
```

✅ **Do**: Use descriptive test names
```python
def test_agent_creation_returns_agent_id():
    """Clear what is being tested"""
```

✅ **Do**: Use fixtures for setup
```python
@pytest.fixture
def configured_client():
    return MagicMock()

def test_with_client(configured_client):
    """Reusable fixture"""
```

✅ **Do**: Mock external dependencies
```python
@patch('module.external_service')
def test_my_feature(mock_service):
    """Isolated from external systems"""
```

### Don'ts

❌ **Don't**: Create file actions in tests
```python
# Bad - creates files
def test_write_config():
    with open('config.json', 'w') as f:
        f.write('data')
```

❌ **Don't**: Test multiple things in one test
```python
# Bad - tests 3 things
def test_agent_creation():
    agent = create_agent()
    assert agent.name == 'test'
    tools = load_tools()
    assert len(tools) > 0
    config = load_config()
    assert config is not None
```

❌ **Don't**: Depend on test execution order
```python
# Bad - test 2 depends on test 1
def test_1():
    global_state = setup()

def test_2():
    # Should not depend on test 1 running first
    assert global_state is not None  # BAD!
```

❌ **Don't**: Skip Azure tests without reason
```python
# Bad - no reason to skip
@pytest.mark.skip
def test_real_feature():
    pass
```

## Continuous Integration

### On Push to Main

1. **Validate Infrastructure** workflow runs
   - Validates all `.bicep` files
   - Checks syntax and schemas
   - Simulates deployment (dry-run)

2. **Validate Functions** workflow runs
   - Validates Python syntax
   - Runs all unit tests
   - Checks function startup
   - Generates coverage reports

### Before Merging Pull Request

- All validation workflows must pass
- Code coverage should maintain or improve
- All checks should be green ✅

### Monitoring Test Health

Check test health by visiting:
```
https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions
```

## Troubleshooting

### "ModuleNotFoundError" in Tests

**Solution**: Ensure virtual environment is activated
```bash
source .venv/bin/activate
```

### "Azure credentials required"

**Solution**: Tests requiring Azure are automatically skipped without credentials
```bash
# To run with credentials
az login
export AZURE_SUBSCRIPTION_ID=$(az account show -q --query id -o tsv)
pytest tests/
```

### Coverage Not Generated

**Solution**: Ensure pytest-cov is installed
```bash
pip install pytest-cov
pytest --cov=foundry_agents --cov-report=html
```

### Tests Timeout

**Solution**: Increase timeout or skip slow tests
```bash
pytest --timeout=300 tests/  # 5 minute timeout
pytest -m "not slow" tests/   # Skip slow tests
```

## Coverage Goals

- **Target**: 80% code coverage
- **Minimum**: 70% code coverage
- **Critical**: 100% coverage for security-sensitive code

View coverage report after running tests:
```bash
open htmlcov/index.html
```

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Azure SDK Testing](https://github.com/Azure/azure-sdk-for-python/wiki/Testing)
