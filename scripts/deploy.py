#!/usr/bin/env python3
"""
Azure AI Foundry Infrastructure and Function App Deployment Script
Handles infrastructure deployment and function code deployment
"""

import subprocess
import json
import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict
import time

# Colors for output
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color

def print_info(msg: str):
    print(f"{GREEN}[INFO]{NC} {msg}")

def print_warning(msg: str):
    print(f"{YELLOW}[WARNING]{NC} {msg}")

def print_error(msg: str):
    print(f"{RED}[ERROR]{NC} {msg}")

def run_command(cmd: List[str], description: str = "", check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and handle errors"""
    if description:
        print_info(description)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0 and check:
            print_error(f"Command failed: {' '.join(cmd)}")
            if result.stderr:
                print_error(f"Error: {result.stderr}")
            if result.stdout:
                print_error(f"Output: {result.stdout}")
            sys.exit(1)
        
        return result
    except Exception as e:
        print_error(f"Failed to run command: {e}")
        sys.exit(1)

def check_azure_cli():
    """Check if Azure CLI is installed and user is logged in"""
    result = run_command(["az", "--version"], check=False)
    if result.returncode != 0:
        print_error("Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        sys.exit(1)
    
    result = run_command(["az", "account", "show"], description="Checking Azure CLI login status...", check=False)
    if result.returncode != 0:
        print_warning("Not logged in to Azure. Logging in...")
        run_command(["az", "login"], description="Logging in to Azure...")

def get_subscription_info() -> tuple:
    """Get current Azure subscription info"""
    result = run_command(
        ["az", "account", "show", "--query", "name", "-o", "tsv"],
        check=True
    )
    subscription_name = result.stdout.strip()
    
    result = run_command(
        ["az", "account", "show", "--query", "id", "-o", "tsv"],
        check=True
    )
    subscription_id = result.stdout.strip()
    
    return subscription_name, subscription_id

def create_params_file(environment: str, location: str, github_repo: str = '', github_branch: str = 'main', enable_github: bool = False) -> str:
    """Create deployment parameters JSON file"""
    params = {
        "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {
            "environmentType": {"value": environment},
            "location": {"value": location},
            "githubRepoUrl": {"value": github_repo},
            "githubBranch": {"value": github_branch},
            "enableGitHubDeploy": {"value": enable_github}
        }
    }
    
    params_file = Path("/tmp") / f"deploy-params-{int(time.time())}.json"
    with open(params_file, 'w') as f:
        json.dump(params, f, indent=2)
    
    return str(params_file)

def deploy_infrastructure(environment: str, location: str, deployment_name: Optional[str] = None, 
                         github_repo: str = '', github_branch: str = 'main', enable_github: bool = False) -> Dict:
    """Deploy infrastructure using Bicep template"""
    if not deployment_name:
        timestamp = int(time.time())
        deployment_name = f"foundry-deployment-{timestamp}"
    
    params_file = create_params_file(environment, location, github_repo, github_branch, enable_github)
    
    print_info(f"Starting deployment with parameters:")
    print(f"  Environment: {environment}")
    print(f"  Location: {location}")
    print()
    
    # Confirm deployment (skip if --yes flag used)
    if not getattr(deploy_infrastructure, '_skip_confirm', False):
        try:
            response = input("Do you want to proceed with the deployment? (y/n) ")
            if response.lower() != 'y':
                print_warning("Deployment cancelled")
                sys.exit(0)
        except EOFError:
            # In non-interactive mode (e.g., GitHub Actions), assume yes
            print_warning("No terminal input available - proceeding with deployment")
    
    # Deploy
    cmd = [
        "az", "deployment", "sub", "create",
        "--name", deployment_name,
        "--location", location,
        "--template-file", "infra/main.bicep",
        "--parameters", params_file,
        "--output", "table"
    ]
    
    run_command(cmd, description="Deploying infrastructure...")
    
    print_info("Infrastructure deployment completed successfully!")
    print()
    
    # Get deployment outputs
    print_info("Retrieving deployment outputs...")
    outputs = {}
    
    output_queries = {
        "resourceGroupName": "properties.outputs.resourceGroupName.value",
        "functionAppName": "properties.outputs.functionAppName.value",
        "agentStorageAccountName": "properties.outputs.agentStorageAccountName.value",
        "agentCreationQueueName": "properties.outputs.agentCreationQueueName.value",
        "skAgentRequestQueueName": "properties.outputs.skAgentRequestQueueName.value",
        "skAgentResponseQueueName": "properties.outputs.skAgentResponseQueueName.value",
        "appInsightsName": "properties.outputs.appInsightsName.value",
    }
    
    for key, query in output_queries.items():
        result = run_command(
            ["az", "deployment", "sub", "show", "--name", deployment_name, "--query", query, "-o", "tsv"],
            check=True
        )
        outputs[key] = result.stdout.strip()
    
    print_info("Deployment outputs:")
    for key, value in outputs.items():
        print(f"  {key}: {value}")
    print()
    
    return outputs

def deploy_function_code(function_app_name: str, resource_group_name: str):
    """Deploy function code to Azure Function App"""
    print_info("Deploying function code to Azure...")
    print_warning("Note: Using managed identity for authentication, no connection string needed")
    print()
    
    cmd = [
        "func", "azure", "functionapp", "publish", function_app_name,
        "--python", "--build-native-deps"
    ]
    
    run_command(cmd, description="Publishing function code...")
    print_info("Function code deployment completed successfully!")

def main():
    parser = argparse.ArgumentParser(description="Deploy Azure AI Foundry Infrastructure and Functions")
    parser.add_argument("-e", "--environment", default="dev", choices=["dev", "prod", "sweden"],
                        help="Environment type (default: dev)")
    parser.add_argument("-l", "--location", default="eastus",
                        choices=["canadaeast", "eastus", "westeurope", "swedencentral"],
                        help="Azure region (default: eastus)")
    parser.add_argument("-n", "--name", help="Deployment name (optional)")
    parser.add_argument("--infra-only", action="store_true",
                        help="Deploy infrastructure only (skip function code deployment)")
    parser.add_argument("--func-only", action="store_true",
                        help="Deploy function code only (infrastructure must already exist)")
    parser.add_argument("--github-repo", default="",
                        help="GitHub repository URL (e.g., https://github.com/user/repo)")
    parser.add_argument("--github-branch", default="main",
                        help="GitHub branch to deploy from (default: main)")
    parser.add_argument("--enable-github-deploy", action="store_true",
                        help="Enable automatic deployment from GitHub")
    parser.add_argument("-y", "--yes", action="store_true",
                        help="Skip confirmation prompts (for automation/CI-CD)")
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)
    
    # Check Azure CLI
    check_azure_cli()
    sub_name, sub_id = get_subscription_info()
    print_info(f"Using subscription: {sub_name} ({sub_id})")
    print()
    
    if args.func_only:
        # Function code deployment only
        if not args.name:
            print_error("--func-only requires --name parameter with deployment name")
            sys.exit(1)
        
        # Get outputs from previous deployment
        print_info("Retrieving previous deployment outputs...")
        result = run_command(
            ["az", "deployment", "sub", "show", "--name", args.name, "--query", 
             "properties.outputs.functionAppName.value", "-o", "tsv"],
            check=True
        )
        function_app_name = result.stdout.strip()
        
        result = run_command(
            ["az", "deployment", "sub", "show", "--name", args.name, "--query", 
             "properties.outputs.resourceGroupName.value", "-o", "tsv"],
            check=True
        )
        resource_group_name = result.stdout.strip()
        
        deploy_function_code(function_app_name, resource_group_name)
    else:
        # Infrastructure deployment (and optionally function code)
        outputs = deploy_infrastructure(args.environment, args.location, args.name,
                                       args.github_repo, args.github_branch, args.enable_github_deploy)
        
        if not args.infra_only:
            print()
            if args.yes:
                # Non-interactive mode - auto-deploy function code
                print_info("Auto-deploying function code (--yes flag)")
                deploy_function_code(outputs["functionAppName"], outputs["resourceGroupName"])
            else:
                try:
                    response = input("Deploy function code to Function App? (y/n) ")
                    if response.lower() == 'y':
                        deploy_function_code(outputs["functionAppName"], outputs["resourceGroupName"])
                except EOFError:
                    # In non-interactive mode, skip function deployment
                    print_warning("No terminal input available - skipping function code deployment")
    
    print()
    print_info("Deployment complete!")

if __name__ == "__main__":
    main()
