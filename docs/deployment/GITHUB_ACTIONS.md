# GitHub Actions Validation Workflows

## Overview

Two automated workflows validate code quality before deployment:

1. **validate-infra.yml** - Validates infrastructure as code (Bicep)
2. **validate-functions.yml** - Validates Python code and functions

Both workflows run automatically on relevant changes and prevent deployment of broken code.

## Validate Infrastructure Workflow

### Trigger Events

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'infra/**'
  pull_request:
    branches:
      - main
    paths:
      - 'infra/**'
  workflow_dispatch:
```

Runs automatically when:
- ✅ Changes to `infra/` are pushed to main
- ✅ Pull request modifies any `.bicep` files
- ✅ Manually triggered from Actions tab

### Validation Steps

#### 1. Bicep Syntax Check
```bash
az bicep build --file infra/main.bicep
```
- Validates Bicep syntax
- Checks for parameter mismatches
- Detects schema errors

#### 2. Parameter Validation
```bash
bicep_output=$(az bicep build --file infra/main.bicep 2>&1)
```
- Ensures all parameters are used
- Checks for unused variables
- Validates expressions

#### 3. Template Expansion Check
```bash
az bicep build --file infra/main.bicep | python3 -m json.tool
```
- Expands all variables and references
- Validates JSON structure
- Checks for circular dependencies

#### 4. Deployment Validation (Dry-Run)
```bash
az deployment sub validate \
  --template-file infra/main.bicep \
  --parameters "@infra/parameters.bicepparams"
```
- Simulates deployment without creating resources
- Validates RBAC permissions
- Checks resource constraints
- Verifies all dependencies

**Note**: This step requires Azure credentials via OIDC

#### 5. Code Quality Checks
```bash
grep -E "TODO|FIXME" infra/**/*.bicep || true
```
- Identifies unfinished code
- Warns about technical debt

#### 6. Resource Summary
```bash
echo "### Bicep Template Summary"
echo "- Template: $(basename infra/main.bicep)"
echo "- Input Parameters: $(grep -c '@param' infra/main.bicep)"
echo "- Modules: $(find infra -name '*.bicep' | wc -l)"
```

### Workflow Output

Check workflow results:
1. Navigate to [GitHub Actions](https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions)
2. Click **Validate Infrastructure**
3. View latest run
4. Expand each step to see details

Example output:
```
✅ Bicep compilation successful
✅ Parameters valid
✅ Template expansion passed
✅ Deployment validation (dry-run) passed
⚠️  Found 2 TODOs in templates
✅ Resource summary: 12 modules found
```

### Troubleshooting

**Error: "Template validation failed"**

1. Check the error message in workflow logs
2. Typically indicates syntax errors or missing parameters
3. Fix locally: `az bicep build --file infra/main.bicep`
4. Push again to re-trigger workflow

**Error: "Deployment validation failed"**

1. Usually means RBAC permissions or schema error
2. Check the specific error in logs
3. Validate locally with credentials:
   ```bash
   az login
   az deployment sub validate \
     --template-file infra/main.bicep \
     --parameters "@infra/parameters.bicepparams"
   ```

**Error: "Could not authenticate with Azure"**

1. OIDC token generation may have failed
2. Check that GitHub Actions secrets are set correctly
3. Verify OIDC trust relationship in Azure
See [PRIVATE_ENDPOINT_DEPLOYMENT.md](./PRIVATE_ENDPOINT_DEPLOYMENT.md#github-actions-setup) for setup

## Validate Functions Workflow

### Trigger Events

```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'function_app.py'
      - 'foundry_agents/**'
      - 'tests/**'
      - '.github/workflows/validate-functions.yml'
  pull_request:
    branches:
      - main
    paths:
      - 'function_app.py'
      - 'foundry_agents/**'
      - 'tests/**'
  workflow_dispatch:
```

Runs automatically when:
- ✅ Changes to function code are pushed
- ✅ Changes to foundry_agents/ are pushed
- ✅ Test files are modified
- ✅ Pull request modifies function code
- ✅ Manually triggered

### Validation Steps

#### 1. Python Version Check
```bash
python3 --version
```
- Ensures Python 3.11+ is available
- Matches runtime version

#### 2. Dependency Installation
```bash
pip install -r requirements.txt
pip install pytest pytest-cov flake8
```
- Installs application dependencies
- Installs test tools

#### 3. Python Syntax Check
```bash
python3 -m py_compile function_app.py
python3 -m py_compile foundry_agents/*.py
```
- Validates Python syntax
- Detects compilation errors
- Quick validation pass

#### 4. Import Validation
```bash
python3 -c "from foundry_agents import *; from function_app import *"
```
- Verifies all imports work
- Detects missing dependencies
- Checks for circular imports

#### 5. Code Linting (flake8)
```bash
flake8 function_app.py foundry_agents/ --max-line-length=100 --extend-ignore=E203,W503
```
- Checks code style (PEP 8)
- Detects unused imports
- Identifies potential bugs

**Common findings**:
- `E501`: Line too long
- `F401`: Unused import
- `E302`: Need 2 blank lines
- `W291`: Trailing whitespace

#### 6. Unit Tests (pytest)
```bash
pytest tests/ -v --cov=foundry_agents --cov-report=xml --cov-report=term
```
- Runs all test suites
- Generates coverage report
- Produces XML for GitHub integration

**Output example**:
```
tests/test_foundry_agents.py::TestSettings::test_settings_initialization PASSED
tests/test_foundry_agents.py::TestToolsRegistry::test_registry_structure PASSED
tests/test_function_app.py::TestFunctionApp::test_queue_trigger_structure PASSED
===================== 15 passed in 1.23s =====================
coverage: 87% (92/106 lines covered)
```

#### 7. Function Metadata Validation
```bash
python3 -c "
import json
with open('function_app.py') as f:
    content = f.read()
    assert 'def agent_creation_processor' in content
    print('✅ Queue trigger function found')
"
```
- Verifies required functions exist
- Checks function decorators
- Validates function signatures

#### 8. JSON Schema Validation
```bash
python3 -m json.tool < function_app.py > /dev/null
python3 -c "import json; json.load(open('host.json'))"
```
- Validates `host.json` format
- Checks configuration syntax

#### 9. Function Startup Check
```bash
timeout 10 func start --verbose 2>&1 | head -50
```
- Attempts to start the function
- Validates runtime environment
- Detects missing dependencies

**Expected output**:
```
Worker process started and initialized.
Listening on 'http://0.0.0.0:7071'
```

**Note**: Timeout of 10 seconds prevents hanging; function doesn't process requests in this check.

### Workflow Output

Check workflow results:
1. Navigate to [GitHub Actions](https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions)
2. Click **Validate Functions**
3. View latest run
4. Expand each step to see details

Example output:
```
✅ Python 3.11+ found
✅ Dependencies installed
✅ Syntax check passed
✅ Imports validated
✅ Linting check: 0 issues
✅ Unit tests: 15 passed (87% coverage)
✅ Function metadata valid
✅ JSON schemas valid
✅ Function startup successful
```

### Troubleshooting

**Error: "Import error module not found"**

1. Check that module is in `requirements.txt`
2. Verify module name spelling
3. Install locally: `pip install -r requirements.txt`
4. Test import: `python3 -c "from module import *"`

**Error: "Flake8 found issues"**

Common issues and fixes:

```python
# E501: Line too long
# Fix: Break into multiple lines or use backslash
def function_with_very_long_name(param1, param2, param3, param4,
                                  param5, param6):
    pass

# F401: Unused imports
# Fix: Remove unused imports
import unused_module  # Remove this

# W291: Trailing whitespace
# Fix: Remove whitespace at end of line
x = 5  # -> x = 5
```

**Error: "Unit tests failed"**

1. Run tests locally: `pytest tests/ -v`
2. Check test output for specific failures
3. Fix test or code accordingly
4. Verify coverage hasn't decreased
5. Push fix to re-trigger workflow

**Error: "Function startup timeout"**

1. Check for missing dependencies in `requirements.txt`
2. Verify `host.json` configuration
3. Check for syntax errors in `function_app.py`
4. Run locally: `func start`

**Error: "Coverage dropped below threshold"**

1. Add tests for new code
2. Run coverage locally: `pytest --cov=foundry_agents`
3. Check coverage report: `htmlcov/index.html`
4. Target 80%+ coverage

## Workflow Status Badges

Display workflow status in README:

```markdown
![Validate Infrastructure](https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions/workflows/validate-infra.yml/badge.svg)
![Validate Functions](https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions/workflows/validate-functions.yml/badge.svg)
```

## Best Practices

### ✅ Do's

✅ **Run workflows before merging**
- All checks must pass (green ✅)
- Don't merge red workflow runs

✅ **Review workflow logs**
- Detailed output helps debug issues
- Learn from warnings

✅ **Keep dependencies updated**
- Periodically update `requirements.txt`
- Re-run validation workflows

✅ **Test locally before pushing**
- Faster feedback loop
- Fewer workflow runs needed

### ❌ Don'ts

❌ **Don't disable workflows**
- They catch issues early
- Better to fix issues than skip checks

❌ **Don't ignore warnings**
- Code quality warnings indicate problems
- Address them proactively

❌ **Don't push without testing**
- Wastes workflow minutes
- Delays feedback

❌ **Don't commit from web editor**
- No local validation
- Harder to debug

## Performance Considerations

### Workflow Execution Time

Typical workflow times:

| Workflow | Time | Notes |
|----------|------|-------|
| Validate Infrastructure | 2-3 min | Depends on Azure API latency |
| Validate Functions | 1-2 min | Depends on dependency installation |
| Both running parallel | 2-3 min | Total time is max(infra, functions) |

### Reducing Workflow Time

1. **Cache dependencies**
   - Already configured in workflows
   - Speeds up pip install

2. **Use workflow_dispatch for big changes**
   - Normal on-push workflows don't run
   - Manually trigger validation

3. **Batch related changes**
   - Make multiple changes before pushing
   - Reduces total workflow runs

## Secrets and Security

### OIDC Authentication

Workflows authenticate with Azure using OIDC. No secrets stored!

**Configured in**:
- `.github/workflows/*.yml` (federated credential)
- Azure Entra ID (trust relationship)
- `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` (GitHub settings)

See [PRIVATE_ENDPOINT_DEPLOYMENT.md](./PRIVATE_ENDPOINT_DEPLOYMENT.md#github-actions-setup) for configuration.

### GitHub Secrets Used

None! OIDC eliminates the need for storing Azure credentials.

### Credential Scope

OIDC tokens have minimal scope:
- Read infrastructure as code
- Validate templates (dry-run only)
- No actual resource creation
- No data access

## Integration with GitHub

### Require Status Checks

To enforce workflow passing before merge:

1. Go to **Settings** → **Branches**
2. Click **Add rule** → main
3. Check **Require status checks to pass**
4. Select:
   - ✅ Validate Infrastructure
   - ✅ Validate Functions
5. Check **Require branches to be up to date**

### Pull Request Checks

Workflows automatically:
1. Run on PR creation
2. Show status as green/red
3. Block merge if red ✅
4. Update automatically on push

### Deployment Gates

Use workflow results to gate deployments:

```yaml
- name: Deploy (only if validation passed)
  if: success()  # Or if: failure() to notify
  run: echo "Deploying..."
```

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure CLI Bicep Commands](https://docs.microsoft.com/en-us/cli/azure/bicep)
- [Pytest Workflows](https://docs.pytest.org/)
- [Flake8 Configuration](https://flake8.pycqa.org/)
- [Azure Functions Core Tools](https://github.com/Azure/azure-functions-core-tools)
