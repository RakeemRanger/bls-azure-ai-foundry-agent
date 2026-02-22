# Queue Architecture: Two Patterns

## Overview

The infrastructure supports **two distinct queue-based patterns** for different use cases:

1. **Agent Creation Queue** - Uses Azure AI Projects SDK to create Foundry agents
2. **Semantic Kernel Agent Queue** - Request/Response pattern for agent queries

## Pattern 1: Agent Creation (AI Projects SDK)

### Flow

```
External Caller → agent-creation-queue → Function App → AI Projects SDK → Foundry Agent Created
```

### Components

- **Queue**: `agent-creation-queue`
- **Trigger**: Function App listens to queue
- **Processing**: Uses `azure-ai-projects>=2.0.0b3` SDK
- **Action**: Creates agents in Foundry account/project
- **Implementation**: See [src/function_app.py](../src/function_app.py) for reference

### Message Format

```json
{
  "agentName": "doc-bot",
  "mcpEndpoint": "https://mcp-endpoint.azurewebsites.net/runtime/webhooks/mcp",
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

### Usage

```python
# Send agent creation request
queue_client.send_message(json.dumps({
    "agentName": "my-agent",
    "mcpEndpoint": "https://...",
    "models": [...]
}))

# Function App automatically processes and creates the agent
```

### Who Uses This?

- **DevOps/Admins**: Programmatically create agents
- **CI/CD Pipelines**: Automated agent deployment
- **Management Tools**: Agent lifecycle management

---

## Pattern 2: Semantic Kernel Agent (Request/Response)

### Flow

```
Foundry Agent → sk-agent-request-queue → Function App (SK Agent) → sk-agent-response-queue → Foundry Agent
         ↓                                        ↓                          ↑
    Send Query                            Process with SK                Get Answer
                                      (Time, Weather, etc.)
```

### Components

- **Request Queue**: `sk-agent-request-queue`
- **Response Queue**: `sk-agent-response-queue`  
- **Trigger**: Function App listens to request queue (internal only)
- **Processing**: Uses Semantic Kernel with plugins
- **Action**: Sends response to response queue
- **Foundry Agent**: Reads response from response queue

### Request Message Format

```json
{
  "requestId": "uuid-v4-unique-id",
  "query": "What is the current time in Tokyo?",
  "requester": "foundry-agent-name"
}
```

### Response Message Format

```json
{
  "requestId": "uuid-v4-unique-id",
  "query": "What is the current time in Tokyo?",
  "answer": "The current time in Tokyo is 3:45 PM JST",
  "metadata": {
    "processingTime": 1.2,
    "pluginsUsed": ["time", "timezone"],
    "requester": "foundry-agent-name"
  }
}
```

### Usage

**From Foundry Agent:**

```python
from examples.sk_agent_request_response import SemanticKernelAgentClient

# Initialize client
sk_client = SemanticKernelAgentClient(
    storage_account_name="rangerblsdevagent",
    request_queue_name="sk-agent-request-queue",
    response_queue_name="sk-agent-response-queue"
)

# Send query and get response
response = sk_client.send_query(
    query="What is the weather in Seattle?",
    requester="my-foundry-agent",
    timeout=30
)

print(response['answer'])  # Use the SK agent's answer
```

**In Function App:**

```python
# Function automatically triggers on request queue messages
# Processes with Semantic Kernel
# Sends response to response queue
# (Already implemented in function_app.py)
```

### Who Uses This?

- **Foundry Agents**: Get real-time info (time, weather, calculations)
- **Chatbots**: Augment responses with external data
- **Workflows**: Integrate SK capabilities without exposing Function App

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Azure Subscription                              │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Foundry Account & Project                                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │ │
│  │  │ Agent 1      │  │ Agent 2      │  │ Agent 3      │        │ │
│  │  │ (created)    │  │ (created)    │  │ (created)    │        │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │ │
│  │         ↑                                     │                 │ │
│  │         │                                     │ Uses SK         │ │
│  │         │ Created by                          ↓                 │ │
│  │         │ Pattern 1                    Request/Response        │ │
│  │         │                                Pattern 2              │ │
│  └────────────────────────────────────────────────────────────────┘ │
│           ↑                                       ↕                  │
│           │                                       │                  │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Agent Storage Account (Private)                               │ │
│  │  ┌──────────────────────┐  ┌──────────────────────┐           │ │
│  │  │ agent-creation-queue │  │ sk-agent-request-q   │           │ │
│  │  │ (Pattern 1)          │  │ (Pattern 2 In)       │           │ │
│  │  └──────────────────────┘  └──────────────────────┘           │ │
│  │                             ┌──────────────────────┐           │ │
│  │                             │ sk-agent-response-q  │           │ │
│  │                             │ (Pattern 2 Out)      │           │ │
│  │                             └──────────────────────┘           │ │
│  └────────────────────────────────────────────────────────────────┘ │
│           ↑                               ↑         │               │
│           │ Trigger #1                    │ Trigger │ Send          │
│           │ (Agent Creation)              │ #2 (SK) │ Response      │
│           │                               │         ↓               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Function App (Internal Only)                                  │ │
│  │  ┌──────────────────────┐  ┌──────────────────────┐           │ │
│  │  │ Queue Trigger 1      │  │ Queue Trigger 2      │           │ │
│  │  │ - AI Projects SDK    │  │ - Semantic Kernel    │           │ │
│  │  │ - Create agents      │  │ - Time plugin        │           │ │
│  │  │                      │  │ - Weather plugin     │           │ │
│  │  │                      │  │ - Other plugins      │           │ │
│  │  └──────────────────────┘  └──────────────────────┘           │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Differences

| Aspect | Pattern 1 (Agent Creation) | Pattern 2 (SK Agent) |
|--------|---------------------------|----------------------|
| **Purpose** | Create new Foundry agents | Answer queries for existing agents |
| **Queues** | 1 queue (one-way) | 2 queues (request/response) |
| **SDK** | azure-ai-projects | semantic-kernel |
| **Caller** | External (DevOps, CI/CD) | Foundry Agents |
| **Response** | No response needed | Response sent to response queue |
| **Frequency** | Infrequent (agent lifecycle) | Frequent (per-query) |
| **Processing** | Create Azure resources | In-memory processing |

## Security

Both patterns use:
- **Private storage** (no public access)
- **Managed identity** authentication
- **RBAC** for queue access
- **Internal-only Function App**

Foundry agents use the `agent-queue-storage` connection (managed identity) to access queues.

## Implementation Status

### ✅ Completed
- Infrastructure (3 queues created)
- Function App structure (both triggers)
- Queue connection to Foundry project
- RBAC permissions

### ⏳ TODO - Pattern 1 (Agent Creation)
See [src/function_app.py](../src/function_app.py) for reference implementation:
- Use `azure-ai-projects` SDK
- Create agents with proper configuration
- Handle model deployments
- Configure MCP endpoints

### ⏳ TODO - Pattern 2 (SK Agent)
In [function_app.py](../function_app.py):
- Add Semantic Kernel initialization
- Implement time plugin
- Implement weather plugin
- Add other plugins as needed
- Handle async processing

## Testing

### Test Pattern 1
```bash
python submit_agent_request.py \
  --storage-account rangerblsdevagent \
  --agent-name test-agent \
  --mcp-endpoint https://test.com/mcp
```

### Test Pattern 2
```bash
python examples/sk_agent_request_response.py
```

## Next Steps

1. Implement AI Projects SDK logic in Pattern 1 trigger
2. Implement Semantic Kernel logic in Pattern 2 trigger
3. Add plugins to SK agent (time, weather, etc.)
4. Test end-to-end flows
5. Monitor in Application Insights
