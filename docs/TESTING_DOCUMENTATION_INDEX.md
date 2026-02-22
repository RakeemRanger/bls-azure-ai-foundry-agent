# Testing & Validation Documentation Index

This directory contains complete documentation for testing and validation of the Azure AI Foundry Function App.

## 📚 Documentation Files

### 1. [TESTING.md](./TESTING.md) - Complete Testing Guide
**For**: Understanding the full testing architecture and best practices

**Covers**:
- Test structure and organization
- Running tests locally (all categories)
- Writing new tests (naming conventions, fixtures, mocking)
- Best practices (do's and don'ts)
- Troubleshooting common issues
- Coverage goals and monitoring

**Key Sections**:
- Running tests: `pytest tests/ -v --cov=foundry_agents`
- By category: `pytest -m unit`, `pytest -m integration`
- Coverage report: `pytest --cov-report=html && open htmlcov/index.html`
- Test anatomy with examples

### 2. [GITHUB_ACTIONS.md](./GITHUB_ACTIONS.md) - Workflow Documentation
**For**: Understanding automated validation pipelines

**Covers**:
- **validate-infra.yml** workflow
  - Bicep template validation
  - Parameter checking
  - Deployment dry-run (no actual resources created)
  - Code quality checks
  
- **validate-functions.yml** workflow
  - Python syntax and import validation
  - Unit tests with coverage
  - Code linting (flake8)
  - Function startup validation
  - JSON schema validation

- Troubleshooting broken workflows
- Integration with GitHub (branch protection, PR checks, status badges)
- Performance optimization
- Security & OIDC authentication

### 3. [TESTING_QUICK_REFERENCE.md](./TESTING_QUICK_REFERENCE.md) - Command Cheat Sheet
**For**: Quick command lookups and common scenarios

**Contains**:
- Essential commands (setup, run, filter, lint, coverage)
- Test categories table
- Common issues & fixes
- Debugging techniques
- File structure reference
- Test markers quick lookup
- Mock object examples
- Fixture patterns
- GitHub Actions commands

## 🗺️ Quick Navigation

### I want to...

**Run tests locally**
→ [TESTING.md - Running Tests](./TESTING.md#running-tests-locally)

**Add new tests**
→ [TESTING.md - Writing Tests](./TESTING.md#writing-tests)

**Understand workflows**
→ [GITHUB_ACTIONS.md - Overview](./GITHUB_ACTIONS.md#overview)

**Debug failing tests**
→ [TESTING_QUICK_REFERENCE.md - Debugging](./TESTING_QUICK_REFERENCE.md#debugging-tests)

**Fix flake8 errors**
→ [GITHUB_ACTIONS.md - Troubleshooting](./GITHUB_ACTIONS.md#troubleshooting)

**Check test coverage**
→ [TESTING.md - Generate Coverage Report](./TESTING.md#generate-coverage-report)

**Setup CI/CD**
→ [GITHUB_ACTIONS.md - Integration with GitHub](./GITHUB_ACTIONS.md#integration-with-github)

## 🎯 Test Categories

### Unit Tests
- **File**: `tests/test_foundry_agents.py`
- **Purpose**: Test individual components without Azure dependencies
- **Run**: `pytest -m unit`
- **Time**: < 1 second
- **Examples**:
  - Settings initialization
  - ToolsRegistry structure
  - FoundryClient factory
  - Prompts templates

### Integration Tests
- **File**: `tests/test_function_app.py`
- **Purpose**: Test Azure Functions and queue processing
- **Run**: `pytest -m integration`
- **Time**: 2-5 seconds (Azure API calls)
- **Examples**:
  - Queue trigger validation
  - Agent creation processor
  - Error handling
  - Environment variables

### Validation (GitHub Actions)
- **Purpose**: Automated checks before deployment
- **Files**:
  - `.github/workflows/validate-infra.yml` (Bicep validation)
  - `.github/workflows/validate-functions.yml` (Function validation)
- **Triggers**: Push to main, pull requests
- **Time**: 2-3 minutes total

## 🏃 Quick Start

### 1. Setup (First Time)
```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock flake8
```

### 2. Run All Tests
```bash
pytest tests/ -v --cov=foundry_agents --cov-report=html
open htmlcov/index.html
```

### 3. Run Unit Tests Only (Fast)
```bash
pytest tests/ -m unit -v
```

### 4. Check Code Style
```bash
flake8 function_app.py foundry_agents/ --max-line-length=100
```

### 5. Before Committing
```bash
# Run validations
flake8 foundry_agents/ function_app.py
pytest tests/ -v --cov=foundry_agents

# Check results
echo "If all pass, commit and push!"
git push origin main
```

## 📊 Test Coverage

### Target Coverage
- **Overall**: 80%+
- **foundry_agents**: 85%+
- **function_app**: 80%+

### Current Coverage
```bash
# Generate report
pytest tests/ --cov=foundry_agents --cov-report=term-missing
```

### View HTML Report
```bash
pytest tests/ --cov=foundry_agents --cov-report=html
open htmlcov/index.html
```

## 🔧 Common Tasks

### Add a New Test
1. Create function in `tests/test_*.py`
2. Follow naming convention: `test_descriptive_name()`
3. Use existing fixtures from `conftest.py`
4. Add pytest marker if applicable: `@pytest.mark.unit`
5. Run locally: `pytest tests/test_file.py::test_name -v`

### Fix Failing Test
```bash
# Run test with details
pytest tests/test_file.py::TestClass::test_name -v -s

# Use debugger
pytest tests/test_file.py::TestClass::test_name --pdb

# Check test setup
pytest tests/test_file.py::TestClass::test_name --setup-show
```

### Improve Coverage
```bash
# Find untested lines
pytest tests/ --cov=foundry_agents --cov-report=term-missing

# Add tests for missing coverage
# Edit test files to cover uncovered lines
```

### Debug GitHub Actions Failure
1. Go to [Actions tab](https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions)
2. Click failed workflow
3. Expand failed step to see logs
4. Look for error message and stack trace
5. Reproduce locally or fix code
6. Push fix to re-trigger workflow

## 📈 Workflow Status

### Monitor Workflows
```
https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions
```

### Available Workflows
1. **validate-infra** - Bicep template validation
2. **validate-functions** - Python code validation
3. **CI** - Combined validation and testing

### Require Passing Checks
In GitHub Settings > Branches > main:
- ✅ Require status checks to pass
- ✅ Select validate-infra
- ✅ Select validate-functions
- ✅ Require branches to be up to date

## 🐛 Troubleshooting Guide

### ModuleNotFoundError
```bash
# Ensure virtual environment activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Tests Timeout
```bash
# Skip slow tests
pytest -m "not slow"

# Increase timeout
pytest --timeout=60

# See which tests are slow
pytest --durations=10
```

### Azure Credential Errors
```bash
# Integration tests skip without credentials
pytest -m "not azure"

# Login to Azure if needed
az login
export AZURE_SUBSCRIPTION_ID=$(az account show -q --query id -o tsv)
```

### Coverage Below Target
```bash
# Find missing coverage
pytest --cov=foundry_agents --cov-report=term-missing

# Write tests for uncovered lines
# Run again to verify coverage improved
```

### Workflow Failing
See [GITHUB_ACTIONS.md - Troubleshooting](./GITHUB_ACTIONS.md#troubleshooting)

## 🔐 Security

### No Secrets Stored
- Uses OIDC federation for GitHub Actions authentication
- No Azure credentials in repository
- No passwords or API keys in code
- Credentials provided at runtime from environment

### Safe Mocking
- Tests use mock objects, not real Azure services
- `conftest.py` handles credential mocking
- Unit tests don't require Azure access
- Integration tests skip when not authenticated

## 📚 Resource Links

### Documentation
- [TESTING.md](./TESTING.md) - Full testing guide
- [GITHUB_ACTIONS.md](./GITHUB_ACTIONS.md) - Workflow documentation
- [TESTING_QUICK_REFERENCE.md](./TESTING_QUICK_REFERENCE.md) - Command reference
- [PRIVATE_ENDPOINT_DEPLOYMENT.md](./PRIVATE_ENDPOINT_DEPLOYMENT.md) - Deployment guide

### External References
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [unittest.mock Reference](https://docs.python.org/3/library/unittest.mock.html)
- [Flake8 Rules](https://flake8.pycqa.org/en/latest/user/error-codes.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure SDK Testing Guide](https://github.com/Azure/azure-sdk-for-python/wiki/Testing)

## ✅ Implementation Checklist

### Repository Setup ✅
- [x] Test files created (test_*.py)
- [x] Fixtures configured (conftest.py)
- [x] pytest.ini configured
- [x] GitHub Actions workflows created
- [x] Requirements.txt includes test dependencies

### Testing ✅
- [x] Unit tests for foundry_agents
- [x] Integration tests for function_app
- [x] Mocking for Azure services
- [x] Coverage configured and measured
- [x] Local test execution works

### Validation ✅
- [x] Bicep template validation workflow
- [x] Python validation workflow
- [x] Automated on push and PR
- [x] Coverage reporting
- [x] Code quality checks

### Documentation ✅
- [x] TESTING.md (full guide)
- [x] GITHUB_ACTIONS.md (workflow guide)
- [x] TESTING_QUICK_REFERENCE.md (command reference)
- [x] This index document

## 🚀 Next Steps

After reviewing this documentation:

1. **Run tests locally**
   ```bash
   pytest tests/ -v --cov=foundry_agents
   ```

2. **Review workflow runs**
   ```
   GitHub Actions > Validate Infrastructure/Functions
   ```

3. **Check coverage**
   ```bash
   pytest --cov-report=html && open htmlcov/index.html
   ```

4. **Deploy infrastructure**
   See [PRIVATE_ENDPOINT_DEPLOYMENT.md](./PRIVATE_ENDPOINT_DEPLOYMENT.md)

5. **Monitor in production**
   Application Insights metrics and logs

## 📝 Notes

- Tests run in **parallel** within test files
- **Fixtures** in conftest.py are shared across all tests
- **Mocking** prevents real Azure API calls in unit tests
- **Coverage** reports which lines were executed during tests
- **Linting** checks code style before commits
- **Workflows** validate automatically before deployment

## 🤝 Contributing

When adding code:
1. Write tests first (TDD approach)
2. Run tests locally before pushing
3. Ensure coverage doesn't decrease
4. Check linting pass: `flake8 your_file.py`
5. Wait for GitHub Actions to pass
6. Get code review before merging

---

**Last Updated**: Implementation complete with comprehensive testing infrastructure

**Status**: ✅ All documentation current and complete
