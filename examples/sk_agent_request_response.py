#!/usr/bin/env python3
"""
Example: Foundry Agent using Semantic Kernel Agent via Request/Response Queues

This demonstrates how a Foundry agent can:
1. Send a query to sk-agent-request-queue
2. Wait for and receive response from sk-agent-response-queue
3. Use the response in its workflow

The SK agent in the Function App processes these requests internally
and returns results (time, weather, calculations, etc.)
"""

import json
import uuid
import time
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient
from typing import Optional, Dict, Any


class SemanticKernelAgentClient:
    """
    Client for Foundry agents to interact with the SK Agent via queues.
    """
    
    def __init__(
        self,
        storage_account_name: str,
        request_queue_name: str = "sk-agent-request-queue",
        response_queue_name: str = "sk-agent-response-queue"
    ):
        self.storage_account_name = storage_account_name
        self.request_queue_name = request_queue_name
        self.response_queue_name = response_queue_name
        
        # Use managed identity (same as Foundry agent)
        self.credential = DefaultAzureCredential()
        
        # Create queue clients
        account_url = f"https://{storage_account_name}.queue.core.windows.net"
        
        self.request_queue = QueueClient(
            account_url=account_url,
            queue_name=request_queue_name,
            credential=self.credential
        )
        
        self.response_queue = QueueClient(
            account_url=account_url,
            queue_name=response_queue_name,
            credential=self.credential
        )
    
    def send_query(
        self,
        query: str,
        requester: str = "foundry-agent",
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Send a query to the SK agent and wait for response.
        
        Args:
            query: The question/query to send
            requester: Identifier for the requesting agent
            timeout: Maximum seconds to wait for response
            
        Returns:
            Dictionary with answer and metadata
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Create request message
        request_message = {
            "requestId": request_id,
            "query": query,
            "requester": requester
        }
        
        print(f"📤 Sending query to SK Agent:")
        print(f"   Request ID: {request_id}")
        print(f"   Query: {query}")
        print()
        
        # Send to request queue
        self.request_queue.send_message(json.dumps(request_message))
        
        # Poll response queue for answer
        print("⏳ Waiting for response...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check for messages in response queue
            messages = self.response_queue.receive_messages(
                max_messages=32,
                visibility_timeout=5
            )
            
            for message in messages:
                try:
                    response_data = json.loads(message.content)
                    
                    # Check if this is our response
                    if response_data.get("requestId") == request_id:
                        # Found our response! Delete the message
                        self.response_queue.delete_message(message)
                        
                        print(f"✅ Received response!")
                        print(f"   Answer: {response_data.get('answer')}")
                        print(f"   Processing time: {response_data.get('metadata', {}).get('processingTime')} seconds")
                        print(f"   Plugins used: {response_data.get('metadata', {}).get('pluginsUsed')}")
                        print()
                        
                        return response_data
                    else:
                        # Not our message, make it visible again
                        # (it will timeout automatically)
                        pass
                        
                except json.JSONDecodeError:
                    # Invalid message, skip
                    pass
            
            # Wait a bit before checking again
            time.sleep(0.5)
        
        # Timeout
        raise TimeoutError(f"No response received within {timeout} seconds for request {request_id}")


def main():
    """
    Example usage from a Foundry agent's perspective.
    """
    print("🤖 Foundry Agent - SK Agent Integration Example")
    print("=" * 60)
    print()
    
    # Initialize the client (in a real Foundry agent, these would come from the connection)
    storage_account_name = "rangerblsdevagent"  # From deployment outputs
    
    client = SemanticKernelAgentClient(
        storage_account_name=storage_account_name,
        request_queue_name="sk-agent-request-queue",
        response_queue_name="sk-agent-response-queue"
    )
    
    # Example 1: Ask for current time
    print("Example 1: Getting current time")
    print("-" * 60)
    
    try:
        response = client.send_query(
            query="What is the current time?",
            requester="foundry-time-agent"
        )
        
        print(f"Agent can now use this answer: {response['answer']}")
        print()
        
    except TimeoutError as e:
        print(f"⚠️  {e}")
        print()
    
    # Example 2: Ask for weather
    print("Example 2: Getting weather information")
    print("-" * 60)
    
    try:
        response = client.send_query(
            query="What is the weather in Seattle?",
            requester="foundry-weather-agent"
        )
        
        print(f"Agent can now use this answer: {response['answer']}")
        print()
        
    except TimeoutError as e:
        print(f"⚠️  {e}")
        print()
    
    # Example 3: Complex query
    print("Example 3: Complex calculation")
    print("-" * 60)
    
    try:
        response = client.send_query(
            query="Calculate the time difference between New York (EST) and Tokyo (JST)",
            requester="foundry-calculation-agent"
        )
        
        print(f"Agent can now use this answer: {response['answer']}")
        print()
        
    except TimeoutError as e:
        print(f"⚠️  {e}")
        print()


def example_foundry_agent_integration():
    """
    Example of how to integrate this into a Foundry agent's code.
    """
    print()
    print("=" * 60)
    print("Example: Integration into Foundry Agent")
    print("=" * 60)
    print()
    
    print("""
In your Foundry agent code, you can use the SK Agent like this:

```python
# Initialize the client
sk_client = SemanticKernelAgentClient(
    storage_account_name=os.environ.get("AGENT_STORAGE_ACCOUNT_NAME"),
    request_queue_name="sk-agent-request-queue",
    response_queue_name="sk-agent-response-queue"
)

# In your agent's message handler
def handle_user_message(user_message):
    # Check if we need external information
    if "time" in user_message.lower():
        # Ask SK agent for time
        response = sk_client.send_query(
            query="What is the current time?",
            requester="my-foundry-agent",
            timeout=10
        )
        
        # Use the answer in your response
        return f"Based on SK Agent: {response['answer']}"
    
    elif "weather" in user_message.lower():
        # Ask SK agent for weather
        response = sk_client.send_query(
            query=f"Weather information for: {user_message}",
            requester="my-foundry-agent",
            timeout=15
        )
        
        return response['answer']
    
    else:
        # Handle with your agent's normal logic
        return process_with_foundry_agent(user_message)
```

This pattern keeps the Function App internal-only while allowing
Foundry agents to leverage the SK agent's capabilities.
    """)


if __name__ == "__main__":
    try:
        main()
        example_foundry_agent_integration()
        
        print()
        print("✅ Examples completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
