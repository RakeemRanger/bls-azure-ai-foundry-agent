# 🤖 Scalable AI Agent Platform on Azure

![Validate Infrastructure](https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions/workflows/validate-infra.yml/badge.svg)
![Validate Functions](https://github.com/RakeemRanger/bls-azure-ai-foundry-agent/actions/workflows/validate-functions.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Production-ready infrastructure for scaling AI agents using Azure AI Services, Semantic Kernel, and Azure Functions.**

This repository demonstrates enterprise-grade patterns for:
- **Automated Agent Provisioning** - Dynamic AI agent creation via Azure AI Foundry SDK
- **Semantic Kernel Agent Integration** - Scalable agent orchestration with plugins
- **Event-Driven Architecture** - Async queue-based processing for high-throughput agent requests
- **Infrastructure as Code** - Complete Bicep templates for reproducible deployments
- **Enterprise Security** - Private endpoints, managed identities, zero public access

## 🏗️ Architecture

```
External Services              Queue-Driven Processing
        │                            │
        ├────→ agent-creation-queue  │
        └────→  Function App (Python)
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
  AI Foundry              Semantic Kernel
  (Agents, Models)        (Agent Executor, Plugins)
        │                         │
        └─────────Response Queues─┘

Security: VNet Private Endpoints, Managed Identity, Zero Public Access
Monitoring: Application Insights, Structured Logging
```

### Core Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **AI Foundry** | Agent hosting & model management | Azure AI Services |
| **Semantic Kernel** | Agent orchestration & plugins | Microsoft SK framework |
| **Function App** | Agent processing engine | Azure Functions (Python 3.11) |
| **Queue Processing** | Scalable async requests | Azure Storage Queues |
| **Managed Identity** | Secure authentication | Azure Entra ID |
| **Private Endpoints** | Network isolation | Azure Virtual Network |
| **Monitoring** | Observability | Application Insights |

## 🎯 Key Features

✅ **Scalability** - Create and manage multiple agents dynamically
✅ **Semantic Kernel** - Native SK agent executor with plugins
✅ **Security** - Zero public access, managed identity, RBAC
✅ **Testing** - 500+ lines of tests, 80%+ coverage
✅ **CI/CD** - GitHub Actions with automated validation
✅ **IaC** - Complete Bicep templates, repeatable deployments
✅ **Monitoring** - Application Insights, structured logging

## 💡 Technical Showcase

This repository demonstrates expertise in:

### Azure AI Services
- Azure AI Foundry API integration (agents, models, projects)
- Azure AI Search with embeddings
- Azure OpenAI Service for LLM inference
- Multi-model orchestration

### Semantic Kernel Framework
- Agent executor implementation
- Plugin architecture for tool integration
- Memory management and context handling
- Kernel configuration and initialization

### Scalable Architecture Patterns
- Event-driven queue-based processing
- Async/await patterns in Python
- Managed Identity authentication (no secrets)
- VNet private endpoint isolation

### Infrastructure as Code
- Bicep templating with modules
- Resource parameterization
- RBAC configuration
- Network isolation by default

### DevOps & Automation
- GitHub Actions CI/CD pipelines
- Code quality checks (flake8, PEP8)
- Infrastructure validation
- 80%+ test coverage

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md) | **Start here** - Guide to finding everything in the repo |
| [docs/TESTING_DOCUMENTATION_INDEX.md](docs/TESTING_DOCUMENTATION_INDEX.md) | Unit tests, integration tests, pytest |
| [docs/PR_WORKFLOW.md](docs/PR_WORKFLOW.md) | PR process, automated checks, review workflow |
| [docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md) | CI/CD workflows, validation pipelines |
| [docs/PRIVATE_ENDPOINT_DEPLOYMENT.md](docs/PRIVATE_ENDPOINT_DEPLOYMENT.md) | Deployment guide, security, private endpoints |
| [docs/QUEUE_ARCHITECTURE.md](docs/QUEUE_ARCHITECTURE.md) | Queue patterns, agent creation details |

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/RakeemRanger/bls-azure-ai-foundry-agent.git
cd bls-azure-ai-foundry-agent
```

### 2. Setup Environment
```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Tests
```bash
# Run all tests with coverage
pytest tests/ -v --cov=foundry_agents --cov-report=html

# Check code quality
flake8 function_app.py foundry_agents/ --max-line-length=100
```

### 4. Deploy Infrastructure
```bash
# Login to Azure
az login
az account set --subscription <subscription-id>

# See deployment guide for complete steps
cat docs/PRIVATE_ENDPOINT_DEPLOYMENT.md

# Deploy
python3 scripts/deploy.py --environment sweden --location swedencentral
```

## 🔄 Queue Patterns

### Pattern 1: Agent Creation
```
External → agent-creation-queue → Function → AI Projects SDK → Agent Created
```
- Dynamic agent provisioning
- Model deployment
- Reference: [function_app.py](function_app.py)

### Pattern 2: Semantic Kernel Agent
```
Foundry Agent → sk-request-queue → Function (SK) → sk-response-queue → Foundry Agent
```
- Agent queries to SK agent
- Plugin-based processing
- Internal routing (no public access)
- Based on [Semantic Kernel SDK](https://github.com/microsoft/semantic-kernel)

See [docs/QUEUE_ARCHITECTURE.md](docs/QUEUE_ARCHITECTURE.md) for details.

## 💬 Queue Message Format

Submit JSON to `agent-creation-queue`:

```json
{
  "agentName": "my-agent",
  "mcpEndpoint": "https://my-mcp-endpoint.azurewebsites.net/runtime/webhooks/mcp",
  "models": [
    {
      "name": "gpt-4.1",
      "skuName": "GlobalStandard",
      "capacity": 50,
      "format": "OpenAI",
      "modelName": "gpt-4.1",
      "version": "2025-04-14"
    }
  ]
}
```

**See [docs/PRIVATE_ENDPOINT_DEPLOYMENT.md](docs/PRIVATE_ENDPOINT_DEPLOYMENT.md) for message submission methods.**

## 🔐 Security by Default

- ✅ **Private Endpoints** - Function App isolated in VNet
- ✅ **Managed Identity** - No connection strings or secrets stored
- ✅ **Zero Public Access** - Storage and AI services not publicly accessible
- ✅ **RBAC** - Least privilege role assignments
- ✅ **Network Isolation** - Queue messages routed through private endpoints
- ✅ **Audit Logging** - Application Insights for compliance

## 🧪 Testing & Quality

```bash
# Unit tests (fast, no Azure required)
pytest tests/ -m unit -v

# All tests with coverage
pytest tests/ -v --cov=foundry_agents --cov-report=html

# Code style
flake8 function_app.py foundry_agents/

# Validate Bicep
az bicep build --file infra/main.bicep

# Test function locally
func start --verbose
```

**Coverage Targets: 80%+ overall, 85%+ for foundry_agents**

See [docs/TESTING_DOCUMENTATION_INDEX.md](docs/TESTING_DOCUMENTATION_INDEX.md) for full guide.

## 🔄 Automated CI/CD

All workflows run automatically (must pass to merge):

1. **validate-infra.yml** - Bicep syntax, schema, dry-run deployment
2. **validate-functions.yml** - Python syntax, imports, unit tests, coverage
3. **pr-checks.yml** - Flake8, unit tests on all PRs

See [docs/GITHUB_ACTIONS.md](docs/GITHUB_ACTIONS.md) for details.

## 📊 Repository Stats

- **Infrastructure**: 2,000+ lines of Bicep
- **Code**: 500+ lines of Python
- **Tests**: 500+ lines of unit/integration tests
- **Documentation**: 3,000+ lines of guides
- **Workflows**: 3 GitHub Actions pipelines
- **Coverage**: 80%+ requirement

## 📁 Project Structure

```
├── infra/                           # Bicep IaC templates
│   ├── main.bicep                  # Orchestration
│   ├── agent/                      # AI Foundry account
│   ├── foundryAccount/             # Foundry project
│   ├── identity/                   # Managed Identity
│   └── rbac/                       # Role assignments
│
├── foundry_agents/                 # Core agent module
│   ├── configs/
│   │   ├── tools_registry.py      # SK plugin registry
│   │   └── settings.py            # Configuration
│   └── utils/
│       └── foundry_client.py      # AI Foundry SDK wrapper
│
├── tests/                          # Test suite (500+ lines)
├── examples/                       # Example scripts & config
│   ├── submit_agent_request.py    # Queue message submission
│   └── sample_models.json         # Sample model config
│
├── scripts/                        # Deployment & setup scripts
│   ├── deploy.py                  # Infrastructure deployment
│   ├── deploy-function.py         # Function app deployment
│   ├── deploy.sh                  # Bash deployment wrapper
│   └── setup-github-oidc.sh       # GitHub OIDC setup
│
├── docs/                           # Documentation
│   ├── TESTING_DOCUMENTATION_INDEX.md
│   ├── GITHUB_ACTIONS.md
│   ├── PR_WORKFLOW.md
│   ├── PRIVATE_ENDPOINT_DEPLOYMENT.md
│   ├── QUEUE_ARCHITECTURE.md
│   ├── QUICK_REFERENCE.md
│   └── ...
│
├── .github/
│   ├── workflows/                  # GitHub Actions CI/CD
│   ├── ISSUE_TEMPLATE/             # Issue templates
│   ├── CODEOWNERS                  # Approval requirements
│   └── pull_request_template.md    # PR template
│
├── function_app.py                 # Azure Functions (Python)
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
├── host.json                       # Functions configuration
├── README.md                       # This file
└── LICENSE                         # MIT License
```

## 🤝 Contributing

1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Test locally**: `pytest tests/ -v && flake8 .`
3. **Push and create PR**: GitHub Actions runs checks
4. **Wait for approval**: Owner-only approval required
5. **Merge when ready**: All checks must pass

See [docs/PR_WORKFLOW.md](docs/PR_WORKFLOW.md) for detailed guide.

## 📖 Resources

- [Azure AI Foundry Docs](https://learn.microsoft.com/en-us/azure/ai-services/)
- [Semantic Kernel GitHub](https://github.com/microsoft/semantic-kernel)
- [Azure Functions Python](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Bicep Docs](https://learn.microsoft.com/en-us/azure/azure-resource-manager/bicep/overview)
- [Azure Functions Triggers & Bindings](https://learn.microsoft.com/en-us/azure/azure-functions/functions-triggers-bindings)

## 📄 License

MIT License - See LICENSE file for details

---

**Built to showcase expertise in Azure AI Services, Semantic Kernel, Enterprise Architecture, and Production-Grade Python/Infrastructure Development.**
