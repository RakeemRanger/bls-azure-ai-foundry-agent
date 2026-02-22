#!/usr/bin/env python3
"""
Sample script to submit agent creation requests to the Azure Storage Queue.

Supports two message formats:
1. New format (recommended): Uses agent_name, model, instructions, tools
2. Legacy format: Uses agentName, mcpEndpoint, models
"""

import json
import argparse
from azure.storage.queue import QueueClient
from azure.identity import DefaultAzureCredential


def submit_agent_creation_request(
    storage_account_name: str,
    queue_name: str,
    agent_name: str,
    model: str = "gpt-4.1",
    instructions: str = None,
    tools: list = None,
    # Legacy format fields
    mcp_endpoint: str = None,
    models: list = None,
    use_legacy: bool = False
):
    """
    Submit an agent creation request to the Azure Storage Queue.
    
    Args:
        storage_account_name: Name of the storage account
        queue_name: Name of the queue
        agent_name: Name of the agent to create
        model: Model name (e.g., "gpt-4.1") - new format
        instructions: Custom instructions (optional) - new format
        tools: List of tool names (e.g., ["ai_search", "code_interpreter"]) - new format
        mcp_endpoint: MCP endpoint URL - legacy format
        models: List of model definitions - legacy format
        use_legacy: Use legacy message format
    """
    # Create queue client using managed identity
    credential = DefaultAzureCredential()
    queue_url = f"https://{storage_account_name}.queue.core.windows.net"
    
    queue_client = QueueClient(
        account_url=queue_url,
        queue_name=queue_name,
        credential=credential
    )
    
    # Create message based on format
    if use_legacy:
        # Legacy format
        message = {
            "agentName": agent_name,
            "mcpEndpoint": mcp_endpoint,
            "models": models or []
        }
    else:
        # New format
        message = {
            "agent_name": agent_name,
            "model": model,
        }
        if instructions:
            message["instructions"] = instructions
        if tools:
            message["tools"] = tools
    
    # Send message
    message_json = json.dumps(message)
    queue_client.send_message(message_json)
    
    print(f"✅ Successfully submitted agent creation request for: {agent_name}")
    print(f"📝 Message: {message_json}")


def main():
    parser = argparse.ArgumentParser(
        description="Submit agent creation requests to Azure Storage Queue"
    )
    parser.add_argument(
        "--storage-account",
        required=True,
        help="Name of the Azure Storage account"
    )
    parser.add_argument(
        "--queue-name",
        default="agent-creation-queue",
        help="Name of the queue (default: agent-creation-queue)"
    )
    parser.add_argument(
        "--agent-name",
        required=True,
        help="Name of the agent to create"
    )
    
    # New format arguments
    parser.add_argument(
        "--model",
        default="gpt-4.1",
        help="Model name (new format, default: gpt-4.1)"
    )
    parser.add_argument(
        "--instructions",
        help="Custom instructions for the agent (new format)"
    )
    parser.add_argument(
        "--tools",
        nargs="+",
        help="List of tools (new format, e.g., --tools ai_search code_interpreter)"
    )
    
    # Legacy format arguments
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy message format"
    )
    parser.add_argument(
        "--mcp-endpoint",
        help="MCP endpoint URL for the agent (legacy format)"
    )
    parser.add_argument(
        "--models-file",
        help="Path to JSON file with model definitions (legacy format)"
    )
    
    args = parser.parse_args()
    
    if args.legacy:
        # Legacy format
        if not args.mcp_endpoint:
            parser.error("--mcp-endpoint is required when using --legacy")
        
        # Load models from file or use default
        if args.models_file:
            with open(args.models_file, 'r') as f:
                models = json.load(f)
        else:
            # Default models
            models = [
                {
                    "name": "gpt-4.1",
                    "skuName": "GlobalStandard",
                    "capacity": 50,
                    "format": "OpenAI",
                    "modelName": "gpt-4.1",
                    "version": "2025-04-14"
                },
                {
                    "name": "text-embedding-3-small",
                    "skuName": "Standard",
                    "capacity": 120,
                    "format": "OpenAI",
                    "modelName": "text-embedding-3-small",
                    "version": "1"
                }
            ]
            print("ℹ️  Using default model configuration")
        
        submit_agent_creation_request(
            storage_account_name=args.storage_account,
            queue_name=args.queue_name,
            agent_name=args.agent_name,
            mcp_endpoint=args.mcp_endpoint,
            models=models,
            use_legacy=True
        )
    else:
        # New format (recommended)
        submit_agent_creation_request(
            storage_account_name=args.storage_account,
            queue_name=args.queue_name,
            agent_name=args.agent_name,
            model=args.model,
            instructions=args.instructions,
            tools=args.tools,
            use_legacy=False
        )


if __name__ == "__main__":
    main()
