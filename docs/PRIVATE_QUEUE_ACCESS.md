# Private Queue Access Configuration

## Overview

The infrastructure has been updated to provide **secure, private access** to the agent queue storage while enabling:
- Foundry agents to send and receive messages
- Function App to process queue triggers
- No public/anonymous access

## Architecture Changes

### 1. Storage Access Model

**Before:**
- Agent storage had public access enabled
- Anyone could submit queue messages anonymously

**After:**
- Agent storage has public access **disabled**
- All access requires Azure AD authentication (managed identity or user credentials)
- RBAC controls who can access the queue

### 2. Components Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Azure Subscription                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  User-Assigned Managed Identity                        │ │
│  │  • Used by: Foundry Account & Function App             │ │
│  │  • Permissions: Storage Queue + AI Services            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────┐    ┌────────────────────────┐  │
│  │  Foundry Account       │    │  Function App          │  │
│  │  ┌──────────────────┐  │    │  (Internal Only)       │  │
│  │  │ Project          │  │    │                        │  │
│  │  │  ├─ Agents       │  │    │  Queue Trigger         │  │
│  │  │  ├─ Models       │  │    │                        │  │
│  │  │  └─ Connections  │  │    │  Creates agents when   │  │
│  │  │     └─ agent-    │  │    │  queue messages arrive │  │
│  │  │        queue-     │  │    │                        │  │
│  │  │        storage    │  │    │                        │  │
│  │  └──────────────────┘  │    └────────────────────────┘  │
│  └────────────────────────┘                │                │
│              │                              │                │
│              │ Managed Identity             │ Managed       │
│              │ Auth                         │ Identity      │
│              ▼                              ▼                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Agent Storage Account (Private)                       │ │
│  │  • Public Access: Disabled                             │ │
│  │  • Network: Allow Azure Services                       │ │
│  │                                                         │ │
│  │  ┌─────────────────────────────────────────────────┐  │ │
│  │  │  agent-creation-queue                            │  │ │
│  │  │  • Send/Receive: Foundry agents (via managed ID) │  │ │
│  │  │  • Trigger: Function App (via managed ID)        │  │ │
│  │  └─────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## RBAC Configuration

### Foundry Managed Identity Permissions

| Resource | Role | Purpose |
|----------|------|---------|
| AI Services Account | Cognitive Services Contributor | Manage AI resources |
| AI Services Account | Cognitive Services User | Use AI services |
| AI Services Account | Cognitive Services OpenAI Contributor | Manage OpenAI deployments |
| Agent Storage Account | Storage Queue Data Contributor | Send/receive queue messages |

### Function App Managed Identity Permissions

| Resource | Role | Purpose |
|----------|------|---------|
| Function Storage | Storage Blob/Queue/Table Data Contributor | Function runtime operations |
| Agent Storage | Storage Queue Data Contributor | Process queue triggers |
| AI Services Account | Cognitive Services Contributor | Create agents |

## Foundry Project Connection

A storage connection is automatically created in the Foundry project:

**Connection Name:** `agent-queue-storage`
- **Type:** Azure Storage Queue
- **Authentication:** Managed Identity (same as Foundry account)
- **Queue:** `agent-creation-queue`
- **Shared:** Yes (available to all project users)

### Using the Connection in Agents

Agents can reference this connection to interact with the queue:

```python
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient

# The connection provides these details:
storage_account = "rangerblsdevagent"  # From connection
queue_name = "agent-creation-queue"     # From connection

# Use the same managed identity as Foundry
credential = DefaultAzureCredential()

queue_client = QueueClient(
    account_url=f"https://{storage_account}.queue.core.windows.net",
    queue_name=queue_name,
    credential=credential
)

# Send a message
queue_client.send_message('{"task": "create-agent"}')

# Receive messages
for message in queue_client.receive_messages():
    print(message.content)
    queue_client.delete_message(message)
```

## Access Patterns

### 1. External Caller → Queue (CLI)

Users with Azure AD permissions can submit messages:

```bash
az login

az storage message put \
  --queue-name agent-creation-queue \
  --account-name rangerblsdevagent \
  --content '{"agentName": "bot", "mcpEndpoint": "https://..."}' \
  --auth-mode login
```

**Required Permission:** Storage Queue Data Contributor role on the storage account

### 2. Foundry Agent → Queue (Send)

Agents use the connection to send messages:

```python
# Using the agent-queue-storage connection
queue_client = get_queue_client_from_connection("agent-queue-storage")
queue_client.send_message(json.dumps({
    "agentName": "new-agent",
    "mcpEndpoint": "https://endpoint.com/mcp",
    "models": [...]
}))
```

### 3. Foundry Agent → Queue (Receive)

Agents can also read from the queue:

```python
# Receive and process messages
for message in queue_client.receive_messages(max_messages=10):
    data = json.loads(message.content)
    
    # Process the message
    process_agent_request(data)
    
    # Delete after successful processing
    queue_client.delete_message(message)
```

### 4. Function App → Queue (Trigger)

The Function App automatically triggers on new messages:

```python
@app.queue_trigger(
    arg_name="msg",
    queue_name="agent-creation-queue",
    connection="AGENT_STORAGE_ACCOUNT"
)
def agent_creation_processor(msg: func.QueueMessage):
    # Automatically invoked when messages arrive
    agent_request = json.loads(msg.get_body().decode('utf-8'))
    create_agent(agent_request)
```

## Granting External Access

To allow external users/apps to submit queue messages:

### Option 1: Grant User Permission

```bash
az role assignment create \
  --assignee user@example.com \
  --role "Storage Queue Data Contributor" \
  --scope "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/rangerblsdevagent"
```

### Option 2: Grant Service Principal Permission

```bash
az role assignment create \
  --assignee <app-id> \
  --role "Storage Queue Data Contributor" \
  --scope "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/rangerblsdevagent"
```

### Option 3: Grant Managed Identity Permission

```bash
az role assignment create \
  --assignee-object-id <managed-identity-object-id> \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Queue Data Contributor" \
  --scope "/subscriptions/<sub-id>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/rangerblsdevagent"
```

## Benefits

✅ **Security:**
- No anonymous access to queues
- All access is audited via Azure AD
- Fine-grained RBAC control

✅ **Integration:**
- Foundry agents have seamless queue access
- Function App processes messages reliably
- External callers use standard Azure authentication

✅ **Compliance:**
- No shared access keys
- Network isolation (private endpoints optional)
- Identity-based access only

## Migration from Public Access

If you previously had public access enabled:

1. **Update Infrastructure:**
   - Deploy the updated Bicep templates
   - RBAC permissions are automatically configured

2. **Update External Callers:**
   - Change from shared key auth → managed identity auth
   - Update code to use `DefaultAzureCredential()`
   - Grant necessary RBAC permissions

3. **Update Documentation:**
   - Inform users about authentication requirements
   - Provide examples using managed identity

4. **Test Access:**
   - Verify Foundry agents can send/receive
   - Verify Function App triggers correctly
   - Verify external callers can authenticate

## Troubleshooting

### "AuthorizationPermissionMismatch" Error

**Cause:** Managed identity lacks queue permissions

**Solution:**
```bash
# Verify RBAC assignment exists
az role assignment list \
  --assignee <managed-identity-object-id> \
  --scope /subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.Storage/storageAccounts/<storage>

# If missing, re-deploy infrastructure or manually assign
```

### Function App Not Triggering

**Cause:** Function App can't read from queue

**Solution:**
- Check that `AGENT_STORAGE_ACCOUNT__queueServiceUri` is set correctly
- Verify managed identity has Storage Queue Data Contributor role
- Check Application Insights logs for authentication errors

### Foundry Agent Can't Access Queue

**Cause:** Connection not configured or permissions missing

**Solution:**
- Verify `agent-queue-storage` connection exists in project
- Confirm connection uses correct storage account
- Verify managed identity RBAC permissions

## Next Steps

1. ✅ Private queue access configured
2. ✅ RBAC permissions assigned
3. ✅ Storage connection created
4. ⏳ Update agent logic to use queue connection
5. ⏳ Test end-to-end flow
6. ⏳ Grant permissions to external callers as needed
