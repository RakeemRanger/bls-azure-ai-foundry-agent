# Pull Request & Approval Workflow

## Overview

This document explains the pull request process, automated checks, and approval workflow.

## Pull Request Process

### 1. Create Pull Request

When creating a PR:
```bash
git checkout -b feature/my-feature
# Make changes
git add .
git commit -m "feat: description of changes"
git push origin feature/my-feature
# Open PR on GitHub
```

### 2. PR Template Auto-fills

The PR template at [.github/pull_request_template.md](./.pull_request_template.md) automatically fills with:
- Description placeholder
- Type of change checkboxes
- Testing checklist
- Code quality checklist
- Documentation checklist

**Fill out ALL sections before submitting.**

### 3. Automated Checks Run

**Triggers**: Creation of PR to `main` branch

#### Code Quality Check (PEP8 & Flake8)
```
✓ Syntax validation
✓ PEP 8 style check (max 100 char lines)
✓ No unused imports or variables
```

**Command run**:
```bash
flake8 function_app.py foundry_agents/ --max-line-length=100
```

**Common issues & fixes**:
| Error | Fix |
|-------|-----|
| E501: Line too long | Break line at 100 characters |
| F401: Unused import | Remove the import |
| E302: Need blank lines | Add blank lines between functions |
| W291: Trailing whitespace | Remove spaces at end of line |

#### Unit Tests
```
✓ Python syntax validation
✓ Import validation
✓ Unit tests execution
✓ Code coverage measurement
```

**Command run**:
```bash
python -m py_compile *.py
pytest tests/ -v --cov=foundry_agents --cov-report=xml
```

**Coverage Requirements**:
- Overall: 80%+ coverage
- foundry_agents: 85%+ coverage

### 4. Fix Issues

If checks fail, the workflow shows details:
1. Go to **Checks** tab in PR
2. Click **PR Checks - Code Quality & Tests**
3. Expand failed step to see error details
4. Fix issues locally:
   ```bash
   # Fix code style
   flake8 function_app.py foundry_agents/
   # Fix any issues shown
   
   # Run tests
   pytest tests/ -v
   # Make sure all pass
   ```
5. Commit and push fix:
   ```bash
   git add .
   git commit -m "fix: resolve PR check failures"
   git push origin feature/my-feature
   ```
6. Checks re-run automatically

### 5. Request Review

Once all checks pass (✅):
1. Click **Request review** in PR
2. Specify reviewer (@RakeemRanger)
3. Add comment explaining changes if needed

### 6. Owner Review & Approval

**Only owner (@RakeemRanger) can approve PRs to main.**

This is enforced by:
- [CODEOWNERS](./CODEOWNERS) file
- GitHub branch protection rules
- Approval requirement on main branch

Reviewer will:
1. Check automated test results
2. Review code changes
3. Check PR template is complete
4. Approve or request changes

### 7. Merge to Main

Once approved:
1. All checks must pass ✅
2. Minimum 1 approval required
3. Click **Merge pull request**
4. Delete feature branch

---

## Workflow Summary

### On Pull Request (PR)
```
┌─────────────────────────────────────┐
│  PR created to main                 │
└────────────┬────────────────────────┘
             │
             ├──→ Code Quality (flake8)
             │    - PEP 8 style check
             │    - Line length (100 char max)
             │    - No unused imports
             │
             └──→ Unit Tests (pytest)
                  - Syntax validation
                  - Import check
                  - Unit test execution
                  - Coverage measurement
                  
              ✅ All pass → Ready for review
              ❌ Fails → Fix and re-push
```

### On Push to Main
```
┌─────────────────────────────────────┐
│  Code merged to main                │
└────────────┬────────────────────────┘
             │
             ├──→ Validate Infrastructure
             │    - Bicep validation
             │    - Deployment dry-run
             │
             └──→ Validate Functions
                  - Function tests
                  - Startup check
                  - Coverage report
                  
              ✅ All pass → Code validated
              ❌ Fails → Investigate logs
```

---

## Code Owners

[CODEOWNERS](./.CODEOWNERS) specifies who must approve changes:

```
* @RakeemRanger
```

**Meaning**: All files require approval from @RakeemRanger before merging.

**Specific rules**:
- Workflow files: @RakeemRanger
- Infrastructure (Bicep): @RakeemRanger
- Tests: @RakeemRanger
- Application code: @RakeemRanger
- Config files: @RakeemRanger

---

## Branch Protection Rules

Main branch has protection:

1. **Require status checks to pass**
   - ✅ PR Checks - Code Quality & Tests
   - ✅ Validate Infrastructure (after merge)
   - ✅ Validate Functions (after merge)

2. **Require code review before merging**
   - Minimum 1 approval required
   - Must be from code owner (@RakeemRanger)
   - Dismiss stale pull request approvals

3. **Require branches to be up to date**
   - Must be rebased on latest main
   - No merge old branches

---

## Common Scenarios

### Scenario 1: Flake8 Fails on Line Length

**Error**: `E501: line too long (120 > 100 characters)`

**Fix**:
```python
# Bad - too long
result = some_function(param1, param2, param3, param4, param5, param6)

# Good - broken into multiple lines
result = some_function(
    param1, param2, param3,
    param4, param5, param6
)
```

### Scenario 2: Unit Test Fails

**Error**: `AssertionError: expected True but got False`

**Debug**:
```bash
# Run just this test with verbose output
pytest tests/test_file.py::TestClass::test_name -v -s

# Use pdb debugger
pytest tests/test_file.py::TestClass::test_name --pdb

# See missing coverage
pytest tests/ --cov-report=term-missing | grep -A5 "test_module"
```

### Scenario 3: Coverage Below Target

**Error**: `Coverage dropped from 85% to 78%`

**Fix**:
1. Find untested code:
   ```bash
   pytest tests/ --cov=foundry_agents --cov-report=html
   open htmlcov/index.html  # View which lines aren't covered
   ```

2. Write tests for missing coverage:
   ```python
   # In tests/test_file.py
   def test_uncovered_function():
       result = uncovered_function()
       assert result is not None
   ```

3. Run tests again:
   ```bash
   pytest tests/ --cov=foundry_agents
   ```

### Scenario 4: Unused Import Import

**Error**: `F401: 'sys' imported but unused`

**Fix**:
```python
# Bad
import sys
import os
print(os.getcwd())

# Good
import os
print(os.getcwd())
```

### Scenario 5: Waiting for Approval

**What to do while PR is waiting for review**:
- Work on another feature branch
- Don't delete your branch until merged
- Keep an eye on PR for feedback
- Answer any reviewer questions

```bash
# Create new feature while waiting
git checkout main
git pull origin main
git checkout -b feature/another-feature
```

---

## Tips & Best Practices

### Before Creating PR

✅ **Do**:
```bash
# Run all checks locally first
flake8 function_app.py foundry_agents/
pytest tests/ -v --cov=foundry_agents

# Only push if all pass
git push origin feature/my-feature
```

❌ **Don't**:
- Push without testing
- Ignore flake8 warnings
- Have declining coverage
- Skip test coverage

### During PR Review

✅ **Do**:
- Be responsive to feedback
- Explain complex changes with comments
- Reference related issues
- Ask clarifying questions

❌ **Don't**:
- Force push (can cause confusion)
- Ignore automated check failures
- Mark as ready before passing checks
- Argue about style (flake8 is the source of truth)

### After Approval

✅ **Do**:
- Merge and delete branch
- Verify deployment succeeded
- Monitor Application Insights

❌ **Don't**:
- Keep the branch around
- Push more changes to merged PR
- Ignore deployment failures

---

## FAQ

**Q: Why does the PR template show up?**
A: `pull_request_template.md` is GitHub-standard. It appears automatically for all PRs.

**Q: Can I skip the PR checks?**
A: No. Branch protection requires all checks to pass before merging.

**Q: Who can approve PRs?**
A: Only @RakeemRanger (enforced by CODEOWNERS).

**Q: What if I disagree with flake8?**
A: Flake8 is configured in `.github/workflows/pr-checks.yml`. Reconfigure there if needed.

**Q: How long do checks take?**
A: Usually 1-2 minutes total (parallel execution).

**Q: Can I merge if checks fail?**
A: No. The merge button is disabled until ✅ all checks pass.

**Q: What if I need to push more commits while waiting for review?**
A: Push to the same branch. Checks re-run automatically. Previous commits stay in history.

---

## Troubleshooting

### "Checks still running" in PR

This is normal. Checks take 1-2 minutes. Wait for completion.

```
No status checks yet - Running...
⏳ 1 minute | 2 minutes elapsed
```

### "Merge button is disabled" (grayed out)

Reasons:
1. Checks still running → Wait
2. Checks failed → Fix issues locally
3. Missing approval → Request review
4. Branch is out of date → Click "Update branch"

### "Request changes pending"

The reviewer requested changes. In the PR:
1. Read the **Files changed** comments
2. Fix the code locally
3. Commit and push: `git push origin feature/my-feature`
4. Checks re-run
5. Respond to review comments: "Fixed in latest commit"

### "Approval has been dismissed"

Another commit was pushed after approval. Dismiss stale approvals is enabled. You need new approval.

---

## Automation Summary

| Event | Check | Time | Required? |
|-------|-------|------|-----------|
| PR created | flake8 | 30s | ✅ Yes |
| PR created | unit tests | 60s | ✅ Yes |
| Code pushed to PR | Both re-run | 60s | ✅ Yes |
| Merge to main | infra validation | 2-3m | ✅ Yes |
| Merge to main | function validation | 1-2m | ✅ Yes |

---

## References

- [PR Template](./pull_request_template.md)
- [CODEOWNERS](./CODEOWNERS)
- [PR Checks Workflow](./workflows/pr-checks.yml)
- [Validate Infra Workflow](./workflows/validate-infra.yml)
- [Validate Functions Workflow](./workflows/validate-functions.yml)
- [Testing Guide](../TESTING.md)
