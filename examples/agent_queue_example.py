#!/usr/bin/env python3
"""
Example: How Foundry agents can send and receive messages from the queue
using the managed identity.

This demonstrates the interaction pattern for agents to:
1. Send messages to the agent-creation-queue
2. Read messages from the queue
3. Process messages and delete them when done
"""

import json
import os
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient


def main():
    # These values would come from your Foundry agent's environment/configuration
    storage_account_name = os.environ.get("AGENT_STORAGE_ACCOUNT_NAME", "rangerblsdevagent")
    queue_name = os.environ.get("AGENT_QUEUE_NAME", "agent-creation-queue")
    
    # Use managed identity authentication (same identity used by Foundry)
    credential = DefaultAzureCredential()
    
    # Create queue client
    queue_url = f"https://{storage_account_name}.queue.core.windows.net"
    queue_client = QueueClient(
        account_url=queue_url,
        queue_name=queue_name,
        credential=credential
    )
    
    print(f"📍 Connected to queue: {queue_name}")
    print(f"🔐 Using managed identity authentication")
    print()
    
    # Example 1: Send a message to the queue
    print("=" * 60)
    print("Example 1: Sending a message to the queue")
    print("=" * 60)
    
    agent_request = {
        "agentName": "example-agent",
        "mcpEndpoint": "https://example-mcp.azurewebsites.net/runtime/webhooks/mcp",
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
    
    message_json = json.dumps(agent_request)
    send_result = queue_client.send_message(message_json)
    
    print(f"✅ Message sent successfully!")
    print(f"   Message ID: {send_result.id}")
    print(f"   Pop Receipt: {send_result.pop_receipt}")
    print()
    
    # Example 2: Read messages from the queue (peek without removing)
    print("=" * 60)
    print("Example 2: Peeking at messages (read without removing)")
    print("=" * 60)
    
    peeked_messages = queue_client.peek_messages(max_messages=5)
    for i, message in enumerate(peeked_messages, 1):
        print(f"📬 Peeked Message {i}:")
        print(f"   Content: {message.content[:100]}...")
        print()
    
    # Example 3: Receive and process messages (with visibility timeout)
    print("=" * 60)
    print("Example 3: Receiving messages for processing")
    print("=" * 60)
    
    # Receive messages (makes them invisible to other consumers for 30 seconds)
    received_messages = queue_client.receive_messages(
        max_messages=1,
        visibility_timeout=30  # Hide from other consumers for 30 seconds
    )
    
    for message in received_messages:
        print(f"📨 Received Message:")
        print(f"   ID: {message.id}")
        print(f"   Insertion Time: {message.inserted_on}")
        print(f"   Dequeue Count: {message.dequeue_count}")
        print()
        
        try:
            # Parse and process the message
            content = json.loads(message.content)
            print(f"📋 Parsed Content:")
            print(f"   Agent Name: {content.get('agentName')}")
            print(f"   MCP Endpoint: {content.get('mcpEndpoint')}")
            print(f"   Models: {len(content.get('models', []))} models")
            print()
            
            # After successful processing, delete the message
            queue_client.delete_message(message)
            print(f"✅ Message processed and deleted successfully!")
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing message: {e}")
            # In a real scenario, you might want to move this to a poison queue
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            # Message will become visible again after visibility timeout
    
    print()
    
    # Example 4: Get queue properties
    print("=" * 60)
    print("Example 4: Queue statistics")
    print("=" * 60)
    
    properties = queue_client.get_queue_properties()
    print(f"📊 Queue Properties:")
    print(f"   Approximate Message Count: {properties.approximate_message_count}")
    print(f"   Metadata: {properties.metadata}")
    print()


if __name__ == "__main__":
    print("🚀 Foundry Agent Queue Integration Example")
    print()
    
    try:
        main()
        print("✅ All examples completed successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
