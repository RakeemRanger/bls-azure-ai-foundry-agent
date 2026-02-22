#!/usr/bin/env python3
"""
Smart Function App Deployment
Handles temporary storage configuration for deployment, then restores to MSI-only
"""

import subprocess
import sys
from typing import Optional

def run_command(cmd: list, description: str = "", check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command"""
    if description:
        print(f"[INFO] {description}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and check:
        print(f"[ERROR] Command failed: {' '.join(cmd)}")
        if result.stderr:
            print(f"Error output:\n{result.stderr}")
        sys.exit(1)
    return result

def get_storage_connection_string(storage_account_name: str, resource_group: str) -> str:
    """Get storage account connection string"""
    result = run_command(
        ["az", "storage", "account", "show-connection-string",
         "--name", storage_account_name,
         "--resource-group", resource_group,
         "--output", "tsv"],
        description=f"Getting connection string for {storage_account_name}..."
    )
    return result.stdout.strip()

def set_app_setting(function_app: str, resource_group: str, key: str, value: str):
    """Set function app application setting"""
    run_command(
        ["az", "functionapp", "config", "appsettings", "set",
         "--name", function_app,
         "--resource-group", resource_group,
         "--settings", f"{key}={value}"],
        description=f"Setting {key}..."
    )

def delete_app_setting(function_app: str, resource_group: str, key: str):
    """Delete function app application setting"""
    run_command(
        ["az", "functionapp", "config", "appsettings", "delete",
         "--name", function_app,
         "--resource-group", resource_group,
         "--setting-names", key],
        description=f"Removing {key}..."
    )

def deploy_function_app(function_app: str, build_option: str = "native-deps") -> bool:
    """Deploy function app using func CLI"""
    if build_option == "remote":
        cmd = ["func", "azure", "functionapp", "publish", function_app,
               "--python", "--build", "remote"]
    else:
        cmd = ["func", "azure", "functionapp", "publish", function_app,
               "--python", f"--build-{build_option}"]
    
    print(f"\n[INFO] Deploying function app with build option: {build_option}...")
    # Wait a bit for storage settings to propagate
    import time
    time.sleep(5)
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 deploy-function.py <function-app-name> [resource-group-name] [--build-remote|--build-native-deps]")
        print("Example: python3 deploy-function.py ranger-bls-sweden-func ranger-bls-sweden-rg --build-remote")
        sys.exit(1)
    
    function_app = sys.argv[1]
    resource_group = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    build_option = "remote"  # Default to remote build
    
    # Parse build option
    for arg in sys.argv:
        if arg == "--build-remote":
            build_option = "remote"
        elif arg == "--build-native-deps":
            build_option = "native-deps"
    
    if not resource_group:
        # Try to infer resource group from app
        print("[INFO] Inferring resource group from function app...")
        result = run_command(
            ["az", "functionapp", "show", "--name", function_app,
             "--query", "resourceGroup", "-o", "tsv"],
            check=False
        )
        if result.returncode == 0:
            resource_group = result.stdout.strip()
        else:
            print("[ERROR] Could not find function app. Please provide resource group name.")
            sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Deploying Function App: {function_app}")
    print(f"Resource Group: {resource_group}")
    print(f"{'='*60}\n")
    
    # Get storage account name from function app settings
    print("[INFO] Getting function app storage account...")
    result = run_command(
        ["az", "functionapp", "config", "appsettings", "list",
         "--name", function_app,
         "--resource-group", resource_group,
         "--query", "[?name=='AzureWebJobsStorage__accountName'].value | [0]",
         "-o", "tsv"]
    )
    storage_account = result.stdout.strip()
    
    if not storage_account:
        print("[ERROR] Could not find storage account name in function app settings.")
        sys.exit(1)
    
    print(f"[INFO] Storage account: {storage_account}\n")
    
    # Step 1: Temporarily enable storage account public access
    print("[INFO] Temporarily enabling storage account public access...")
    run_command(
        ["az", "storage", "account", "update",
         "--name", storage_account,
         "--resource-group", resource_group,
         "--public-network-access", "Enabled",
         "--default-action", "Allow"],
        description="Enabling storage network access..."
    )
    
    # Step 1b: Temporarily enable function app public access
    print("[INFO] Temporarily enabling function app public access...")
    run_command(
        ["az", "functionapp", "update",
         "--name", function_app,
         "--resource-group", resource_group,
         "--set", "publicNetworkAccess=Enabled"],
        description="Enabling function app network access..."
    )
    
    # Step 2: Get connection string
    conn_string = get_storage_connection_string(storage_account, resource_group)
    
    # Step 3: Set connection string for deployment
    print("\n[INFO] Configuring storage for deployment...")
    set_app_setting(function_app, resource_group, "AzureWebJobsStorage", conn_string)
    
    # Wait for settings to propagate
    print("[INFO] Waiting for settings to propagate...")
    import time
    time.sleep(10)
    
    # Step 4: Deploy
    print()
    success = deploy_function_app(function_app, build_option)
    
    # Step 5: Clean up - restore restrictions
    print("\n[INFO] Cleaning up deployment configuration...")
    try:
        # Remove connection string
        delete_app_setting(function_app, resource_group, "AzureWebJobsStorage")
        print("[INFO] Removed connection string.")
        
        # Re-disable storage account public access
        print("[INFO] Restoring storage account to private access...")
        run_command(
            ["az", "storage", "account", "update",
             "--name", storage_account,
             "--resource-group", resource_group,
             "--public-network-access", "Disabled",
             "--default-action", "Deny"],
            description="Disabling storage network access..."
        )
        print("[INFO] Restored storage to managed identity-only access.")
        
        # Re-disable function app public access
        print("[INFO] Restoring function app to private access...")
        run_command(
            ["az", "functionapp", "update",
             "--name", function_app,
             "--resource-group", resource_group,
             "--set", "publicNetworkAccess=Disabled"],
            description="Disabling function app network access..."
        )
        print("[INFO] Restored function app to private access.")
    except Exception as e:
        print(f"[WARNING] Cleanup incomplete. Please restore manually:")
        print(f"  az functionapp config appsettings delete --name {function_app} --resource-group {resource_group} --setting-names AzureWebJobsStorage")
        print(f"  az storage account update --name {storage_account} --resource-group {resource_group} --public-network-access Disabled --default-action Deny")
        print(f"  az functionapp update --name {function_app} --resource-group {resource_group} --set publicNetworkAccess=Disabled")
    
    print(f"\n{'='*60}")
    if success:
        print(f"✅ Deployment successful!")
        print(f"Function App: {function_app}")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"❌ Deployment failed!")
        print(f"{'='*60}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
