## Description
Brief description of changes and why they were made.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (change that alters existing functionality)
- [ ] Documentation update
- [ ] Infrastructure change (Bicep/IaC)

## Related Issues
Closes #(issue number) or Relates to #(issue number)

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] Unit tests added/updated
- [ ] Tests pass locally: `pytest tests/ -v`
- [ ] Coverage maintained or improved: `pytest --cov=foundry_agents`

## Code Quality
- [ ] Code follows PEP 8 style guide
- [ ] No flake8 violations: `flake8 . --max-line-length=100`
- [ ] No unused imports or variables
- [ ] Docstrings added for public functions

## For Infrastructure Changes
- [ ] Bicep syntax validated: `az bicep build --file infra/main.bicep`
- [ ] No hardcoded values (parameters used)
- [ ] RBAC permissions reviewed
- [ ] Network security considered

## Documentation
- [ ] README updated (if needed)
- [ ] Docstrings added
- [ ] Comments added for complex logic

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots/Logs (if applicable)
Add screenshots or test output if relevant.

---
**Note**: This PR must pass automated checks before review:
- ✅ Flake8 code style check
- ✅ Unit tests
- ✅ Import validation

See [TESTING_DOCUMENTATION_INDEX.md](../../TESTING_DOCUMENTATION_INDEX.md) for details.
