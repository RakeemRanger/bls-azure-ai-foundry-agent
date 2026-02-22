# Deployment Guide

This guide covers deploying Azure AI Foundry infrastructure and function code using Python scripts and GitHub Actions.

## Overview

- **Python Deployment Script** (`deploy.py`): Local deployment using Azure CLI via subprocess
- **GitHub Actions**: Automated CI/CD pipeline for function app and infrastructure deployment
- **Everything Internal**: Function App and storage accounts have `publicNetworkAccess: Disabled` for security

## Local Deployment with Python Script

### Prerequisites

- Azure CLI installed and authenticated: `az login`
- Python 3.8+
- Azure Functions Core Tools: `brew install azure-functions-core-tools` (macOS) or `apt-get install azure-functions-core-tools-4` (Linux)

### Usage

#### Deploy Infrastructure Only

```bash
python3 deploy.py --environment sweden --location swedencentral --infra-only
```

#### Deploy Infrastructure + Function Code

```bash
python3 deploy.py --environment sweden --location swedencentral
```

When prompted, confirm both the infrastructure deployment and function code deployment.

#### Deploy Function Code Only (after infrastructure exists)

```bash
python3 deploy.py --func-only --name foundry-deployment-<timestamp>
```

### Options

- `-e, --environment`: Environment type (dev, prod, sweden) - default: dev
- `-l, --location`: Azure region - default: eastus
- `-n, --name`: Deployment name (auto-generated if not provided)
- `--allowed-ips`: Comma-separated IPs to whitelist (e.g., `75.180.19.164,10.0.0.0/24`)
- `--infra-only`: Deploy infrastructure only, skip function code
- `--func-only`: Deploy function code only (requires previous deployment name)

### Example Workflows

**Deploy everything manually:**
```bash
python3 deploy.py --environment sweden --location swedencentral
```

**Deploy infrastructure, then function code separately:**
```bash
python3 deploy.py --environment sweden --location swedencentral --infra-only
# ... later ...
python3 deploy.py --func-only --name foundry-deployment-1708614955
```

**Deploy with IP whitelisting (for temporary local access during development):**
```bash
python3 deploy.py --environment sweden --location swedencentral --allowed-ips 75.180.19.164
```

---

## GitHub Actions CI/CD

### Setup

#### 1. Create Azure Entra ID App Registration

For OIDC authentication (recommended, no secrets needed):

```bash
# Create app registration
az ad app create --display-name "foundry-ci-cd"

# Register service principal
az ad sp create --id <app-id>

# Note the Application ID (client-id) and Directory ID (tenant-id)
```

#### 2. Configure Federated Credentials

Allow GitHub to authenticate as the Azure app:

```bash
az ad app federated-credential create \
  --id <app-id> \
  --parameters '{
    "name": "foundry-github-actions",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:RakeemRanger/bls-azure-ai-foundry-agent:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

#### 3. Assign Azure Roles

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
OBJECT_ID=$(az ad sp show --id <app-id> --query id -o tsv)

# Contribute role for infrastructure deployment
az role assignment create \
  --role Contributor \
  --assignee-object-id $OBJECT_ID \
  --scope /subscriptions/$SUBSCRIPTION_ID

# Additional role for function app deployment
az role assignment create \
  --role "Website Contributor" \
  --assignee-object-id $OBJECT_ID \
  --scope /subscriptions/$SUBSCRIPTION_ID
```

#### 4. Add GitHub Secrets

In your GitHub repository settings, add these secrets:

- `AZURE_CLIENT_ID`: App registration Application ID
- `AZURE_TENANT_ID`: Azure AD Tenant ID  
- `AZURE_SUBSCRIPTION_ID`: Azure Subscription ID

### Workflows

#### Deploy Infrastructure

Triggered on:
- Push to `main` with changes to `infra/**`
- Manual workflow dispatch

```bash
# Manual trigger with custom parameters
gh workflow run deploy-infra.yml \
  -f environment=sweden \
  -f location=swedencentral
```

#### Deploy Function App

Triggered on:
- Push to `main` with changes to `function_app.py`, `requirements.txt`, `foundry_agents/**`
- Manual workflow dispatch

```bash
# Manual trigger
gh workflow run deploy-function.yml
```

### Security Features

- **OIDC Authentication**: No long-lived secrets stored in GitHub
- **Federated Credentials**: GitHub Actions tokens are exchanged for Azure tokens
- **Least Privilege**: Service principal has minimal required roles
- **Internal-Only Resources**: Function App and storage don't have public access

---

## Architecture Decision: Internal-Only Deployment

All resources are configured as `publicNetworkAccess: Disabled`:

```bicep
// Storage Account
publicNetworkAccess: 'Disabled'
networkAcls: {
  defaultAction: 'Deny'
  bypass: 'AzureServices'
}

// Function App
publicNetworkAccess: 'Disabled'
```

**Why?**
- Maximum security - only Azure services can access
- CI/CD pipeline can authenticate with Azure credentials (no public endpoints needed)
- Managed identity provides runtime authentication
- Complies with zero-trust networking principles

**Deployment Flow:**
1. GitHub Actions or local Azure CLI authenticates to Azure
2. Infrastructure deploys with full MSI-based access
3. Function code deploys without needing public access
4. Runtime uses managed identity to access storage and Foundry services

---

## Troubleshooting

### Python Script Issues

**"Azure CLI is not installed"**
```bash
# macOS
brew install azure-cli

# Ubuntu/Debian
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

**"Not logged in to Azure"**
```bash
az login
# or for sovereign clouds
az login --cloud AzureUSGovernment
```

**"Deployment parameters validation failed"**
- Check Bicep template syntax: `az bicep build --file infra/main.bicep`
- Verify location is valid for your region
- Ensure environment type is one of: dev, prod, sweden

### GitHub Actions Issues

**"OIDC token exchange failed"**
- Verify federated credential subject matches your repo and branch
- Check that app registration exists and is properly created
- Ensure roles are assigned to the service principal

**"Insufficient permissions"**
- Add `Contributor` role to the service principal
- For Function App deployment, also add `Website Contributor` role

### Deployment Timeouts

Infrastructure deployment typically takes 10-15 minutes. Function deployment takes 3-5 minutes.

If a deployment times out:
1. Check Azure Portal for resource status
2. Review operation logs in Resource Group
3. Re-run the same deployment command (deployments are idempotent)

---

## Next Steps

1. **Set up GitHub Actions**: Follow the setup section above
2. **Test infrastructure deployment**: `python3 deploy.py --environment sweden --location swedencentral --infra-only`
3. **Monitor deployment**: Watch the outputs and verify resources in Azure Portal
4. **Deploy function code**: Run again without `--infra-only` or use GitHub Actions
5. **Configure monitoring**: Set up Application Insights alerts in Azure Portal

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review GitHub Actions logs in the Actions tab
3. Examine Azure CLI output for detailed error messages
4. Check Azure Portal for resource health status
