#!/bin/bash

# Azure AI Foundry Infrastructure Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
ENVIRONMENT_TYPE="dev"
LOCATION="eastus"
DEPLOYMENT_NAME="foundry-deployment-$(date +%Y%m%d-%H%M%S)"
ALLOWED_IPS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT_TYPE="$2"
            shift 2
            ;;
        -l|--location)
            LOCATION="$2"
            shift 2
            ;;
        -n|--name)
            DEPLOYMENT_NAME="$2"
            shift 2
            ;;
        --allowed-ips)
            ALLOWED_IPS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: ./deploy.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -e, --environment   Environment type (dev|prod) [default: dev]"
            echo "  -l, --location      Azure region [default: eastus]"
            echo "  -n, --name          Deployment name [default: foundry-deployment-TIMESTAMP]"
            echo "  --allowed-ips       Comma-separated IPs in CIDR format (e.g., 75.180.19.164/32,10.0.0.0/24)"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Example:"
            echo "  ./deploy.sh --environment prod --location westeurope --allowed-ips 75.180.19.164/32"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

print_info "Starting deployment with the following parameters:"
echo "  Environment: $ENVIRONMENT_TYPE"
echo "  Location: $LOCATION"
echo "  Deployment Name: $DEPLOYMENT_NAME"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it from https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
print_info "Checking Azure CLI login status..."
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure. Please log in..."
    az login
fi

# Get current subscription
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
print_info "Using subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"
echo ""

# Confirm deployment
read -p "Do you want to proceed with the deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled"
    exit 0
fi

# Deploy infrastructure
print_info "Deploying infrastructure..."

# Create parameters JSON file
PARAMS_FILE="/tmp/deploy-params-$$.json"
cat > "$PARAMS_FILE" << EOF
{
  "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environmentType": {
      "value": "$ENVIRONMENT_TYPE"
    },
    "location": {
      "value": "$LOCATION"
    },
    "allowedIpAddresses": {
      "value": [
EOF

# Add IPs to the array
if [ -n "$ALLOWED_IPS" ]; then
    IFS=',' read -ra IP_ARRAY <<< "$ALLOWED_IPS"
    for i in "${!IP_ARRAY[@]}"; do
        if [ $i -gt 0 ]; then
            echo "," >> "$PARAMS_FILE"
        fi
        echo -n "        \"${IP_ARRAY[$i]}\"" >> "$PARAMS_FILE"
    done
    print_info "Whitelisting IPs: $ALLOWED_IPS"
fi

cat >> "$PARAMS_FILE" << EOF
      ]
    }
  }
}
EOF

az deployment sub create \
    --name "$DEPLOYMENT_NAME" \
    --location "$LOCATION" \
    --template-file infra/main.bicep \
    --parameters "$PARAMS_FILE" \
    --output table

# Clean up temp file
rm -f "$PARAMS_FILE"

if [ $? -eq 0 ]; then
    print_info "Infrastructure deployment completed successfully!"
    echo ""
    
    # Get deployment outputs
    print_info "Deployment outputs:"
    echo ""
    
    RESOURCE_GROUP=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.resourceGroupName.value -o tsv)
    FUNCTION_APP_NAME=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.functionAppName.value -o tsv)
    AGENT_STORAGE_ACCOUNT=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.agentStorageAccountName.value -o tsv)
    AGENT_CREATION_QUEUE=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.agentCreationQueueName.value -o tsv)
    SK_REQUEST_QUEUE=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.skAgentRequestQueueName.value -o tsv)
    SK_RESPONSE_QUEUE=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.skAgentResponseQueueName.value -o tsv)
    APP_INSIGHTS_NAME=$(az deployment sub show --name "$DEPLOYMENT_NAME" --query properties.outputs.appInsightsName.value -o tsv)
    
    echo "  Resource Group: $RESOURCE_GROUP"
    echo "  Function App: $FUNCTION_APP_NAME"
    echo "  Agent Storage Account: $AGENT_STORAGE_ACCOUNT"
    echo "  Agent Creation Queue: $AGENT_CREATION_QUEUE"
    echo "  SK Request Queue: $SK_REQUEST_QUEUE"
    echo "  SK Response Queue: $SK_RESPONSE_QUEUE"
    echo "  Application Insights: $APP_INSIGHTS_NAME"
    echo ""
    
    print_info "Next steps:"
    echo "  1. Deploy function code: func azure functionapp publish $FUNCTION_APP_NAME"
    echo "  2. Submit test message: python submit_agent_request.py --storage-account $AGENT_STORAGE_ACCOUNT --agent-name test-agent"
    echo "  3. Monitor logs in Application Insights: $APP_INSIGHTS_NAME"
    echo ""
else
    print_error "Infrastructure deployment failed!"
    exit 1
fi

print_info "Deployment complete!"
