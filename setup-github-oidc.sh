#!/bin/bash
# Setup GitHub OIDC for Azure Function App deployment
# This creates Azure resources and outputs GitHub secrets to configure

set -e

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)
REPO_OWNER="RakeemRanger"
REPO_NAME="bls-azure-ai-foundry-agent"

echo "=================================================="
echo "GitHub OIDC Setup for Azure Deployment"
echo "=================================================="
echo ""
echo "Subscription: $SUBSCRIPTION_ID"
echo "Tenant: $TENANT_ID"
echo "Repository: $REPO_OWNER/$REPO_NAME"
echo ""

# Create or get existing app registration
APP_NAME="github-actions-${REPO_NAME}"
echo "Creating/Getting App Registration: $APP_NAME"

APP_ID=$(az ad app list --display-name "$APP_NAME" --query "[0].appId" -o tsv)

if [ -z "$APP_ID" ]; then
    echo "Creating new app registration..."
    APP_ID=$(az ad app create --display-name "$APP_NAME" --query appId -o tsv)
else
    echo "Using existing app: $APP_ID"
fi

# Create or get service principal
echo "Creating/Getting Service Principal..."
SP_ID=$(az ad sp list --filter "appId eq '$APP_ID'" --query "[0].id" -o tsv)

if [ -z "$SP_ID" ]; then
    echo "Creating new service principal..."
    SP_ID=$(az ad sp create --id "$APP_ID" --query id -o tsv)
    sleep 10  # Wait for propagation
else
    echo "Using existing service principal: $SP_ID"
fi

# Assign Contributor role to subscription
echo "Assigning Contributor role..."
az role assignment create \
    --role Contributor \
    --assignee "$APP_ID" \
    --scope "/subscriptions/$SUBSCRIPTION_ID" \
    --output none 2>/dev/null || echo "Role already assigned"

# Configure federated credentials
CREDENTIAL_NAME="github-main-branch"
SUBJECT="repo:${REPO_OWNER}/${REPO_NAME}:ref:refs/heads/main"

echo "Configuring federated credential for: $SUBJECT"

# Delete existing credential if it exists
az ad app federated-credential delete \
    --id "$APP_ID" \
    --federated-credential-id "$CREDENTIAL_NAME" \
    --output none 2>/dev/null || true

# Create federated credential
az ad app federated-credential create \
    --id "$APP_ID" \
    --parameters "{
        \"name\": \"$CREDENTIAL_NAME\",
        \"issuer\": \"https://token.actions.githubusercontent.com\",
        \"subject\": \"$SUBJECT\",
        \"audiences\": [\"api://AzureADTokenExchange\"]
    }" --output none

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "Add these secrets to your GitHub repository:"
echo "Repository: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
echo ""
echo "AZURE_CLIENT_ID: $APP_ID"
echo "AZURE_TENANT_ID: $TENANT_ID"
echo "AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
echo ""
echo "=================================================="
