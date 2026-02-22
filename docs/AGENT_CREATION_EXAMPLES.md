# Agent Creation Examples

This document provides examples of how to create agents using the queue trigger.

## New Format (Recommended)

The new format uses the `foundry_agents` module which provides:
- Centralized project client management
- Tool registry for easy tool configuration
- Agent prompt registry
- Key Vault integration for secrets

### Example 1: Create a Documentation Bot with AI Search

```python
import json
from azure.storage.queue import QueueClient
from azure.identity import DefaultAzureCredential

# Create queue client
queue_client = QueueClient(
    account_url="https://your-storage.queue.core.windows.net",
    queue_name="agent-creation-queue",
    credential=DefaultAzureCredential()
)

# Submit agent creation request
message = {
    "agent_name": "doc-bot",
    "model": "gpt-4.1",
    "tools": ["ai_search"]
    # instructions are optional - will use prompt from agent_prompts.py
}

queue_client.send_message(json.dumps(message))
```

### Example 2: Create an Agent with Custom Instructions

```python
message = {
    "agent_name": "custom-agent",
    "model": "gpt-4.1",
    "instructions": "You are a helpful assistant that specializes in Python programming.",
    "tools": ["code_interpreter"]
}

queue_client.send_message(json.dumps(message))
```

### Example 3: Create an Agent with Multiple Tools

```python
message = {
    "agent_name": "multi-tool-agent",
    "model": "gpt-4.1",
    "tools": ["ai_search", "microsoft_learn_mcp", "code_interpreter"]
}

queue_client.send_message(json.dumps(message))
```

## Using the Command Line Script

### New Format

```bash
# Basic agent with default settings
python submit_agent_request.py \
    --storage-account your-storage \
    --agent-name my-agent

# Agent with specific tools
python submit_agent_request.py \
    --storage-account your-storage \
    --agent-name doc-bot \
    --model gpt-4.1 \
    --tools ai_search code_interpreter

# Agent with custom instructions
python submit_agent_request.py \
    --storage-account your-storage \
    --agent-name custom-agent \
    --model gpt-4.1 \
    --instructions "You are a helpful coding assistant" \
    --tools code_interpreter
```

### Legacy Format

```bash
python submit_agent_request.py \
    --storage-account your-storage \
    --agent-name my-agent \
    --mcp-endpoint https://mcp.example.com \
    --models-file sample_models.json \
    --legacy
```

## Available Tools

The following tools are registered in the `foundry_agents` module:

1. **ai_search** - Azure AI Search for grounded retrieval
   - Requires: AI Search connection ID and index name in Key Vault
   
2. **microsoft_learn_mcp** - Microsoft Learn MCP remote tool
   - Requires: MCP connection ID in Key Vault
   
3. **code_interpreter** - Sandboxed code execution
   - No additional configuration required

## Prompt Registry

Pre-defined prompts are available in `foundry_agents/prompts/agent_prompts.py`:

- **doc-bot** - Documentation assistant with AI Search
- **code-helper** - Azure coding assistant
- **default** - Generic helpful assistant

To use a registered prompt, simply set the `agent_name` to match the prompt key. You can override it by providing custom `instructions` in the message.

## How It Works

1. Message is sent to the `agent-creation-queue`
2. Function App triggers `agent_creation_processor`
3. Function imports `foundry_agents` module:
   - Gets project client via `get_project_client()` (handles auth)
   - Resolves tools via `resolve_tools()` (pulls config from Key Vault)
   - Gets instructions via `get_prompt()` (from prompt registry)
4. Agent is created using Azure AI Projects SDK
5. Agent ID is logged

## Environment Configuration

The Function App needs these environment variables:

```bash
# Managed Identity
AZURE_CLIENT_ID=<user-assigned-managed-identity-client-id>

# Key Vault
KEY_VAULT_URI=https://your-vault.vault.azure.net/

# Queue Storage
AGENT_STORAGE_ACCOUNT__queueServiceUri=https://your-storage.queue.core.windows.net
```

Secrets are stored in Key Vault:
- `foundry-project-endpoint` - Azure AI Foundry project endpoint
- `ai-search-connection-id` - AI Search connection ID (if using ai_search tool)
- `ai-search-index-name` - AI Search index name (if using ai_search tool)
- `mcp-connection-id` - MCP connection ID (if using microsoft_learn_mcp tool)
