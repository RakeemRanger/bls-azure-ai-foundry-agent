# Azure AI Foundry Agent Infrastructure

This repository contains Bicep infrastructure as code (IaC) for deploying Azure AI Foundry with **two queue-based patterns**:
1. **Agent Creation** - Automated agent provisioning using Azure AI Projects SDK
2. **Semantic Kernel Agent** - Request/Response pattern for agent queries (time, weather, etc.)

## Architecture

The infrastructure includes:

- **Azure AI Foundry Account & Project**: Hosts AI agents and model deployments
- **Managed Identity**: User-assigned identity for secure authentication
- **Storage Accounts with 3 Queues**:
  - `agent-creation-queue` - Create new Foundry agents
  - `sk-agent-request-queue` - Send queries to SK agent
  - `sk-agent-response-queue` - Receive SK agent responses
- **Azure Function App**: Internal-only, processes both queue patterns
- **Application Insights**: Monitoring and logging
- **RBAC**: Proper role assignments for storage and AI Services access

## Queue Patterns

### Pattern 1: Agent Creation (AI Projects SDK)
```
External → agent-creation-queue → Function → AI Projects SDK → Agent Created
```
- Creates agents in Foundry using `azure-ai-projects>=2.0.0b3`
- Reference implementation: [src/function_app.py](src/function_app.py)
- Used by: DevOps, CI/CD, Management Tools

### Pattern 2: Semantic Kernel Agent (Request/Response)
```
Foundry Agent → sk-request-queue → Function (SK) → sk-response-queue → Foundry Agent
```
- Foundry agents send queries to SK agent (internal Function App)
- SK agent processes with plugins (time, weather, etc.)
- Responses sent back via response queue
- Function App stays internal-only, never reached directly

See [docs/QUEUE_ARCHITECTURE.md](docs/QUEUE_ARCHITECTURE.md) for detailed architecture.

## Infrastructure Components

### Core Resources
- **AI Services Account**: Multi-service cognitive services account
- **Foundry Project**: AI Foundry project within the account
- **Managed Identity**: Used by AI services, Function App, and Foundry agents

### Function App Stack
- **App Service Plan**: Consumption plan (Y1 SKU) for cost optimization
- **Function App**: Python 3.11, internal-only with managed identity
- **Queue Triggers**: 
  - Agent creation (Pattern 1)
  - SK agent request/response (Pattern 2)

### Storage
- **Function Storage**: Backend storage for Azure Functions runtime
- **Agent Storage**: Contains 3 queues (all private, managed identity access)
- **Function Storage**: Backend storage for Azure Functions runtime
- **Agent Storage**: Contains the `agent-creation-queue` for external callers

### Monitoring
- **Application Insights**: Function App telemetry and logs
- **Log Analytics Workspace**: Centralized logging

## Deployment

### Prerequisites
- Azure CLI installed
- Azure subscription
- Appropriate permissions to create resources

### Deploy Infrastructure

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription <subscription-id>

# Deploy using Bicep
az deployment sub create \
  --name foundry-deployment \
  --location eastus \
  --template-file infra/main.bicep \
  --parameters environmentType=dev location=eastus
```

### Parameters

- `environmentType`: Environment type (`dev` or `prod`)
- `location`: Azure region (`canadaeast`, `eastus`, or `westeurope`)

## Queue Message Format

To create an agent, submit a JSON message to the `agent-creation-queue`:

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
    },
    {
      "name": "text-embedding-3-small",
      "skuName": "Standard",
      "capacity": 120,
      "format": "OpenAI",
      "modelName": "text-embedding-3-small",
      "version": "1"
    }
  ]
}
```

### Submitting Queue Messages

**Important:** The agent storage account has public access disabled for security. Messages must be submitted using Azure AD authentication (managed identity or user credentials).

You can submit messages using:

1. **Azure CLI** (uses your Azure login):
```bash
az storage message put \
  --queue-name agent-creation-queue \
  --account-name <agent-storage-account-name> \
  --content '<json-message>' \
  --auth-mode login
```

2. **Azure SDK (Python)** with Managed Identity:
```python
from azure.storage.queue import QueueClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
queue_client = QueueClient(
    account_url="https://<storage-account>.queue.core.windows.net",
    queue_name="agent-creation-queue",
    credential=credential
)

message = {
    "agentName": "my-agent",
    "mcpEndpoint": "https://...",
    "models": [...]
}

import json
queue_client.send_message(json.dumps(message))
```

3. **From Foundry Agents**:
   - Agents automatically have access via the `agent-queue-storage` connection
   - The connection uses the same managed identity as the Foundry account
   - See [examples/agent_queue_example.py](examples/agent_queue_example.py) for usage patterns

4. **Helper Script**:
```bash
python submit_agent_request.py \
  --storage-account <agent-storage-account-name> \
  --agent-name my-agent \
  --mcp-endpoint https://my-endpoint.com/mcp \
  --models-file sample_models.json
```

## Function App Development

### Local Development

1. Copy the template:
```bash
cp local.settings.json.template local.settings.json
```

2. Update `local.settings.json` with your Azure resource values

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run locally:
```bash
func start
```

### Implementing Agent Creation Logic

The queue trigger function is in [function_app.py](function_app.py). Add your agent creation logic in the `TODO` section:

```python
# TODO: Implement agent creation logic here
# 1. Deploy models to AI Services account
# 2. Create account-level and project-level connections
# 3. Configure the agent with MCP endpoint
```

### Deployment

```bash
# Deploy function code
func azure functionapp publish <function-app-name>
```

## Security

- **Function App**: Internal-only, public network access disabled
- **Managed Identity**: All authentication uses managed identity (no connection strings)
- **Storage**: Both storage accounts are private (public access disabled)
  - Function backend storage: Accessed by Function App managed identity
  - Agent queue storage: Accessed by both Function App and Foundry managed identity
- **RBAC**: Least privilege access configured
  - Foundry managed identity: Storage Queue Data Contributor on agent storage
  - Function App managed identity: Full storage access + AI Services access
- **Queue Access**: 
  - Foundry agents can send/receive messages via `agent-queue-storage` connection
  - External callers must authenticate using Azure AD credentials
  - No anonymous or shared key access permitted

## Monitoring

View logs and metrics in Application Insights:

```bash
# Get Application Insights name
az deployment sub show \
  --name foundry-deployment \
  --query properties.outputs.appInsightsName.value

# View in Azure Portal
az portal insights show --name <app-insights-name> --resource-group <rg-name>
```

## Static Agent Definitions

You can still define agents statically in [infra/main.bicep](infra/main.bicep) L28-58:

```bicep
var agents = [
  {
    name: 'dartinbot'
    mcpEndpoint: 'https://...'
    models: [...]
  }
  // Add more agents here
]
```

These will be deployed during infrastructure deployment.

## Outputs

After deployment, you'll get:

- `functionAppName`: Name of the Function App
- `agentStorageAccountName`: Storage account for queue submissions
- `agentQueueName`: Queue name for agent creation requests
- `appInsightsConnectionString`: Application Insights connection string

## Next Steps

1. ✅ Infrastructure deployed
2. ⏳ Implement agent creation logic in `function_app.py`
3. ⏳ Test queue trigger with sample messages
4. ⏳ Configure CI/CD for automatic function deployment

## Resources

- [Azure Functions Python Developer Guide](https://learn.microsoft.com/azure/azure-functions/functions-reference-python)
- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure Storage Queue Trigger](https://learn.microsoft.com/azure/azure-functions/functions-bindings-storage-queue-trigger)
