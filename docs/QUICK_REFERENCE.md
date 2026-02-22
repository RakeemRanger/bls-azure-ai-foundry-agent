# Quick Reference: Queue Patterns

## 🚀 Quick Start

### For DevOps: Create Agents (Pattern 1)

```bash
# Submit agent creation request
python submit_agent_request.py \
  --storage-account rangerblsdevagent \
  --agent-name my-bot \
  --mcp-endpoint https://my-mcp.azurewebsites.net/runtime/webhooks/mcp \
  --models-file sample_models.json
```

### For Foundry Agents: Use SK Agent (Pattern 2)

```python
from examples.sk_agent_request_response import SemanticKernelAgentClient

# Initialize
sk_client = SemanticKernelAgentClient(
    storage_account_name="rangerblsdevagent"
)

# Get real-time info
response = sk_client.send_query(
    query="What is the current time?",
    requester="my-agent"
)

print(response['answer'])
```

## 📋 Queue Names

| Queue | Purpose | Who Sends | Who Receives |
|-------|---------|-----------|--------------|
| `agent-creation-queue` | Create new agents | External callers | Function App |
| `sk-agent-request-queue` | Query SK agent | Foundry agents | Function App |
| `sk-agent-response-queue` | SK agent answers | Function App | Foundry agents |

## 🔐 Authentication

All queues use **managed identity** authentication:

```python
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient

credential = DefaultAzureCredential()
queue_client = QueueClient(
    account_url="https://rangerblsdevagent.queue.core.windows.net",
    queue_name="queue-name",
    credential=credential
)
```

## 📝 Message Formats

### Agent Creation Request
```json
{
  "agentName": "doc-bot",
  "mcpEndpoint": "https://endpoint.com/mcp",
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

### SK Agent Request
```json
{
  "requestId": "uuid-v4",
  "query": "What is the weather?",
  "requester": "agent-name"
}
```

### SK Agent Response
```json
{
  "requestId": "uuid-v4",
  "query": "What is the weather?",
  "answer": "Sunny, 72°F",
  "metadata": {
    "processingTime": 1.2,
    "pluginsUsed": ["weather"]
  }
}
```

## 🛠️ Local Development

1. Copy settings:
```bash
cp local.settings.json.template local.settings.json
# Edit with your values
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run locally:
```bash
func start
```

## 🔍 Monitoring

View Function App logs:
```bash
# Stream live logs
func azure functionapp logstream <function-app-name>

# View in Application Insights
az portal application-insights show --name <app-insights-name>
```

## 🏗️ Deployment

```bash
# Deploy infrastructure
./deploy.sh --environment dev --location eastus

# Deploy function code
func azure functionapp publish <function-app-name>
```

## 📖 Documentation

- **Full Architecture**: [docs/QUEUE_ARCHITECTURE.md](docs/QUEUE_ARCHITECTURE.md)
- **Private Access**: [docs/PRIVATE_QUEUE_ACCESS.md](docs/PRIVATE_QUEUE_ACCESS.md)
- **Main README**: [README.md](../README.md)

## 🔗 Storage Account Connection

In Foundry project, use the `agent-queue-storage` connection:
- Automatically configured
- Managed identity authentication
- Access to all 3 queues

## ⚡ Common Tasks

### Submit Test Message
```bash
az storage message put \
  --queue-name agent-creation-queue \
  --account-name rangerblsdevagent \
  --content '{"agentName":"test","mcpEndpoint":"https://test.com/mcp","models":[]}' \
  --auth-mode login
```

### Check Queue Length
```bash
az storage queue stats show \
  --name agent-creation-queue \
  --account-name rangerblsdevagent \
  --auth-mode login
```

### Grant User Access
```bash
az role assignment create \
  --assignee user@example.com \
  --role "Storage Queue Data Contributor" \
  --scope "/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/rangerblsdevagent"
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't send to queue | Check RBAC permissions (Storage Queue Data Contributor) |
| Function not triggering | Verify managed identity has queue access |
| Timeout waiting for response | Check Function App logs in Application Insights |
| Authentication error | Ensure `DefaultAzureCredential()` is configured |

## 📞 Support

- **Errors**: Check Application Insights logs
- **Architecture Questions**: See [QUEUE_ARCHITECTURE.md](docs/QUEUE_ARCHITECTURE.md)
- **Security**: See [PRIVATE_QUEUE_ACCESS.md](docs/PRIVATE_QUEUE_ACCESS.md)
