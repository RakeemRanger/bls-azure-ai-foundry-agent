# Azure AI Foundry Function App - Private Endpoint Deployment Guide

## Architecture Overview

This project uses Azure AI Foundry with a private Function App protected by:
- **Virtual Network (VNet)**: Private network isolation (10.0.0.0/16)
- **Private Endpoints**: Direct private connections from VNet to Function App
- **Managed Identity**: Passwordless authentication for all services
- **Network Security**: `publicNetworkAccess: Disabled` on all resources

## Deployment Strategies

### Option 1: GitHub Actions with Temporary Public Access (Current)
Best for: Standard CI/CD with GitHub

**How It Works:**
1. GitHub Actions triggers on code push
2. Workflow temporarily enables `publicNetworkAccess: Enabled`
3. Waits for settings to propagate (15 seconds)
4. Deploys function code via REST API
5. Immediately disables `publicNetworkAccess`
6. Function App remains private

**Pros:**
- Simple GitHub Actions workflow
- No infrastructure changes needed
- Works with existing VNet/Private Endpoints
- Automatic restore if deployment fails

**Cons:**
- Briefly exposed to public internet during deployment
- Requires `publicNetworkAccess` toggle

**Implementation:**
```bash
python3 deploy.py --environment sweden --location swedencentral --infra-only
# Then GitHub Actions deployment is automatic on git push
```

### Option 2: Self-Hosted GitHub Runner (Recommended for Production)
Best for: High-security environments

**Setup:**
1. Create Azure VM in the VNet
2. Install GitHub Actions self-hosted runner
3. Runner can access private endpoints directly
4. No public access needed

**Steps:**
```bash
# Create a VM in the VNet (add to main.bicep)
# SSH into VM and install runner:
mkdir ~/runner
cd ~/runner
curl -o actions-runner-linux-x64-2.x.x.tar.gz \
  https://github.com/actions/runner/releases/download/v2.x.x/actions-runner-linux-x64-2.x.x.tar.gz
tar xzf ./actions-runner-linux-x64-2.x.x.tar.gz
# Configure with GitHub repo token
./config.sh --url https://github.com/RakeemRanger/bls-azure-ai-foundry-agent --token <TOKEN>
./run.sh
```

### Option 3: Azure Container Registry (ACR) + Webhook
Best for: Complex deployments with multiple environments

**How It Works:**
1. Push function code to GitHub
2. GitHub Actions builds Docker image
3. Push image to ACR
4. ACR webhook triggers Function App update
5. Function App fetches container from ACR (no public access needed)

**Requires:**
- Docker container for Python functions
- ACR instance
- Function App configured for container deployment

### Option 4: Azure DevOps Pipelines
Best for: Complex enterprise scenarios

**How It Works:**
1. Function App deployment via Azure DevOps
2. Run agent on Azure VM in VNet
3. Direct access to private endpoints
4. No public exposure needed

---

## Current Production Setup

This project uses **Option 1** because:
- Minimal infrastructure overhead
- Works with GitHub Actions without agents
- Secure: Public access is temporary and monitored
- Scalable to larger deployments

### Deployment Flow

```
┌─────────────────┐
│  Git Push (main)│
└────────┬────────┘
         │
         ▼
┌──────────────────────────────┐
│  GitHub Actions Workflow     │
│  1. Checkout code            │
│  2. Setup Python 3.11        │
│  3. Install dependencies     │
│  4. Create ZIP package       │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Enable Public Access (15 seconds)       │
│  az functionapp update --set \           │
│  publicNetworkAccess=Enabled             │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Deploy Code via ZIP API                 │
│  curl -X POST with publishing creds      │
│  Upload 140MB package                    │
└────────┬─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Disable Public Access (Immediate)       │
│  az functionapp update --set \           │
│  publicNetworkAccess=Disabled            │
└──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────┐
│  Function App Operational                │
│  - Private only via VNet                 │
│  - Queue triggers working                │
│  - Managed identity authentication       │
└──────────────────────────────────────────┘
```

---

## Infrastructure Deployment

### Step 1: Deploy with Private Endpoints
```bash
# First time setup
python3 deploy.py --environment sweden --location swedencentral --infra-only

# Or with direct Azure CLI
az deployment sub create \
  --name foundry-deployment \
  --location swedencentral \
  --template-file infra/main.bicep \
  --parameters environmentType=sweden location=swedencentral
```

### Step 2: Verify Private Endpoints
```bash
# Check Function App is private
az functionapp show \
  --name ranger-bls-sweden-func \
  --resource-group ranger-bls-sweden-rg \
  --query publicNetworkAccess

# Should output: "Disabled"

# Check VNet configuration
az network private-endpoint list \
  --resource-group ranger-bls-sweden-rg \
  --output table
```

### Step 3: Test with GitHub Actions
```bash
# Commit a change to trigger deployment
git add .
git commit -m "test: Deploy via GitHub Actions"
git push origin main

# Monitor in GitHub Actions
gh run list --repo RakeemRanger/bls-azure-ai-foundry-agent
```

---

## Security Considerations

### Network Isolation
- Function App: Only accessible via VNet private endpoint
- Storage: Managed by Function App's managed identity
- Queues: Private access via storage connection string

### Identity & Access
- All services use Azure Managed Identity
- No connection strings in app settings (except during deployment)
- RBAC roles assigned by deployment scripts

### Temporary Public Access
- Only enabled during GitHub Actions deployment
- Duration: ~2 minutes (build + upload + disable)
- All access is authenticated via Azure credentials
- Logged in Azure Activity Log

### Monitoring
```bash
# View temporary public access events
az monitor activity-log list \
  --resource-group ranger-bls-sweden-rg \
  --offset 1d \
  --query "[?operationName.value=='Microsoft.Web/sites/config/write'].[eventTimestamp,resourceId,status]" \
  --output table
```

---

## Troubleshooting

### Deployment Fails with "403 Forbidden"
Check if Function App is public:
```bash
az functionapp show --name ranger-bls-sweden-func \
  --resource-group ranger-bls-sweden-rg \
  --query publicNetworkAccess
```

If "Disabled", GitHub Actions should enable it. Check workflow logs.

### Functions Not Executing
1. Check Function App runtime is healthy
2. Verify managed identity has proper RBAC roles
3. Check queue trigger connections in app settings
4. Review Application Insights for errors

### Private Endpoint Not Working
```bash
# Test from VM in VNet
nslookup ranger-bls-sweden-func.azurewebsites.net
# Should resolve to 10.0.x.x (not public IP)

curl -v https://ranger-bls-sweden-func.azurewebsites.net/
# Should work when connected to VNet
```

---

## Migration to Self-Hosted Runner

To migrate from Option 1 to Option 2:

1. Create VM in VNet (add to network.bicep)
2. Install GitHub Actions runner on VM
3. Update workflow labels to run on self-hosted runner
4. Remove temporary public access logic from workflow

```yaml
# Before
runs-on: ubuntu-latest

# After
runs-on: [self-hosted, linux]
```

---

## Cost Optimization

### Current Setup Costs
- Virtual Network: ~$0 (free)
- Private Endpoints: $0.75/endpoint/month (2 endpoints = $1.50/month)
- VNet is minimal impact on Function App cost

### Recommendation
Private endpoints are cost-effective for security-critical workloads. Use them for:
- Production deployments
- Customer-facing applications
- PII/sensitive data processing

For development, consider:
- Keeping `publicNetworkAccess: Enabled` for faster iteration
- Using separate dev VNet without private endpoints
- CI/CD from public agents for dev envs

---

## References

- [Azure Function App - Network Security](https://docs.microsoft.com/en-us/azure/azure-functions/functions-networking-options)
- [Private Endpoints](https://docs.microsoft.com/en-us/azure/private-link/private-endpoints-overview)
- [GitHub Actions - Self-hosted Runners](https://docs.github.com/en/actions/hosting-your-own-runners)
- [Azure Managed Identity](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/)
