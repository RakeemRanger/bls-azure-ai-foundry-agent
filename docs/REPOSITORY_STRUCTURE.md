# Repository Structure Guide

**Quick reference for finding things in this repository.**

## 📍 Root Level (Essential Files Only)

```
README.md                           # Start here - project overview
function_app.py                     # Azure Functions entry point (Python)
requirements.txt                    # Python dependencies
pytest.ini                          # Test configuration
host.json                          # Azure Functions configuration
local.settings.json.template       # Local development template
.funcignore                        # Files to ignore in Functions
.gitignore                         # Git ignore rules
```

## 📚 Documentation (`docs/`)

**Everything you need to learn about the project:**

| File | Purpose |
|------|---------|
| [docs/README.md](../README.md) | Main project README (in root) |
| [docs/TESTING_DOCUMENTATION_INDEX.md](TESTING_DOCUMENTATION_INDEX.md) | Complete testing guide index |
| [docs/TESTING.md](TESTING.md) | Unit & integration testing details |
| [docs/TESTING_QUICK_REFERENCE.md](TESTING_QUICK_REFERENCE.md) | Quick test commands cheat sheet |
| [docs/GITHUB_ACTIONS.md](GITHUB_ACTIONS.md) | CI/CD workflow documentation |
| [docs/PR_WORKFLOW.md](PR_WORKFLOW.md) | Pull request process & approval |
| [docs/PRIVATE_ENDPOINT_DEPLOYMENT.md](PRIVATE_ENDPOINT_DEPLOYMENT.md) | Deployment guide & security |
| [docs/DEPLOYMENT.md](DEPLOYMENT.md) | Alternative deployment docs |
| [docs/QUEUE_ARCHITECTURE.md](QUEUE_ARCHITECTURE.md) | Queue patterns & architecture |
| [docs/QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick commands reference |
| [docs/AGENT_CREATION_EXAMPLES.md](AGENT_CREATION_EXAMPLES.md) | Agent creation code examples |
| [docs/PRIVATE_QUEUE_ACCESS.md](PRIVATE_QUEUE_ACCESS.md) | Queue access patterns |

**How to use docs:**
- **New to the project?** Start with README.md, then [docs/QUEUE_ARCHITECTURE.md](QUEUE_ARCHITECTURE.md)
- **Want to write tests?** Read [docs/TESTING_DOCUMENTATION_INDEX.md](TESTING_DOCUMENTATION_INDEX.md)
- **Contributing code?** Follow [docs/PR_WORKFLOW.md](PR_WORKFLOW.md)
- **Deploying infrastructure?** See [docs/PRIVATE_ENDPOINT_DEPLOYMENT.md](PRIVATE_ENDPOINT_DEPLOYMENT.md)
- **Need quick commands?** Check [docs/TESTING_QUICK_REFERENCE.md](TESTING_QUICK_REFERENCE.md)

## 🛠️ Scripts (`scripts/`)

**Automation and deployment scripts:**

| Script | Purpose |
|--------|---------|
| [scripts/deploy.py](../scripts/deploy.py) | Deploy infrastructure (main entry point) |
| [scripts/deploy-function.py](../scripts/deploy-function.py) | Deploy function app code |
| [scripts/deploy.sh](../scripts/deploy.sh) | Bash wrapper for deployments |
| [scripts/setup-github-oidc.sh](../scripts/setup-github-oidc.sh) | GitHub OIDC federation setup |

**How to use scripts:**
```bash
# Deploy infrastructure
python scripts/deploy.py --environment sweden --location swedencentral

# Setup GitHub OIDC (one-time)
bash scripts/setup-github-oidc.sh

# Deploy function code
python scripts/deploy-function.py
```

## 💡 Examples (`examples/`)

**Reference implementations and configurations:**

| File | Purpose |
|------|---------|
| [examples/submit_agent_request.py](../examples/submit_agent_request.py) | Submit messages to agent creation queue |
| [examples/sample_models.json](../examples/sample_models.json) | Sample model configuration |
| [examples/agent_queue_example.py](../examples/agent_queue_example.py) | Agent queue processing example |
| [examples/sk_agent_request_response.py](../examples/sk_agent_request_response.py) | Semantic Kernel agent example |

**How to use examples:**
```bash
# Submit a queue message
python examples/submit_agent_request.py \
  --agent-name my-agent \
  --mcp-endpoint https://my-endpoint.com/mcp

# Reference for implementation patterns
cat examples/agent_queue_example.py
```

## 🏗️ Infrastructure (`infra/`)

**Bicep Infrastructure as Code:**

```
infra/
├── main.bicep                      # Main orchestration template
├── agent/                         # AI Foundry account
├── foundryAccount/                # Foundry project
├── foundryAgent/                  # Agent configuration
├── identity/                      # Managed Identity
├── rbac/                          # Role-based access control
└── network/                       # VNet & private endpoints
```

**How to use:**
```bash
# Validate templates
az bicep build --file infra/main.bicep

# Deploy (via scripts/deploy.py)
python scripts/deploy.py --environment sweden
```

## 💻 Source Code (`foundry_agents/`)

**Core Python module:**

```
foundry_agents/
├── configs/
│   ├── settings.py               # Configuration management
│   ├── tools_registry.py         # Semantic Kernel plugins
│   └── constants.py              # Application constants
├── utils/
│   ├── foundry_client.py         # AI Foundry SDK wrapper
│   └── akv.py                    # Azure Key Vault utility
└── prompts/
    └── agent_prompts.py          # Agent prompt templates
```

## 🧪 Tests (`tests/`)

**Test suite with pytest:**

```
tests/
├── test_foundry_agents.py         # Module tests
├── test_function_app.py           # Function app tests
└── conftest.py                    # Pytest fixtures
```

**How to run:**
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=foundry_agents

# Specific test file
pytest tests/test_foundry_agents.py -v
```

## 🔧 GitHub Configuration (`.github/`)

**CI/CD and community guidelines:**

```
.github/
├── workflows/
│   ├── validate-infra.yml         # Bicep validation
│   ├── validate-functions.yml     # Function validation
│   └── pr-checks.yml              # Pull request checks
├── ISSUE_TEMPLATE/
│   ├── 1-bug-report.yml           # Bug report template
│   ├── 2-feature-request.yml      # Feature request template
│   ├── 3-question.yml             # Question template
│   └── 4-documentation.yml        # Documentation template
├── CODEOWNERS                     # Approval requirements
└── pull_request_template.md       # PR template
```

## 📖 Quick Navigation

### I want to...

**Understand the architecture**
→ [docs/QUEUE_ARCHITECTURE.md](QUEUE_ARCHITECTURE.md)

**Write and run tests**
→ [docs/TESTING_DOCUMENTATION_INDEX.md](TESTING_DOCUMENTATION_INDEX.md)

**Deploy infrastructure**
→ [docs/PRIVATE_ENDPOINT_DEPLOYMENT.md](PRIVATE_ENDPOINT_DEPLOYMENT.md)

**Contribute code**
→ [docs/PR_WORKFLOW.md](PR_WORKFLOW.md)

**Check CI/CD setup**
→ [docs/GITHUB_ACTIONS.md](GITHUB_ACTIONS.md)

**Find quick commands**
→ [docs/TESTING_QUICK_REFERENCE.md](TESTING_QUICK_REFERENCE.md) or [docs/QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**See code examples**
→ [examples/](../examples/) or [docs/AGENT_CREATION_EXAMPLES.md](AGENT_CREATION_EXAMPLES.md)

## 🎯 Key Directories Summary

| Directory | What | When to use |
|-----------|------|------------|
| **root** | Essential project files | Starting point |
| **docs/** | Comprehensive documentation | Learning & reference |
| **scripts/** | Automation tools | Deployment & setup |
| **examples/** | Reference implementations | Code samples |
| **.github/** | CI/CD & community | Workflows & PRs |
| **infra/** | Infrastructure templates | Deployment |
| **foundry_agents/** | Source code | Reading code |
| **tests/** | Test suite | Running tests |

---

**Last Updated**: February 22, 2026
**Repository Structure**: Clean & organized for scalability
