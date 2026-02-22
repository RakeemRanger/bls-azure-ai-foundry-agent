import azure.functions as func
import logging
import json
import os
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueClient
from typing import Dict, Any

from foundry_agents.configs import get_settings, resolve_tools
from foundry_agents.utils import get_project_client
from foundry_agents.prompts import get_prompt

app = func.FunctionApp()

# ══════════════════════════════════════════════
# QUEUE TRIGGER 1: Agent Creation (AI Projects)
# ══════════════════════════════════════════════

@app.queue_trigger(
    arg_name="msg",
    queue_name=os.environ.get("AGENT_CREATION_QUEUE_NAME", "agent-creation-queue"),
    connection="AGENT_STORAGE_ACCOUNT"
)
def agent_creation_processor(msg: func.QueueMessage) -> None:
    """
    Queue trigger function to create agents using Azure AI Projects SDK.
    
    Expected message format:
    {
        "agent_name": "doc-bot",
        "model": "gpt-4.1",
        "instructions": "...(optional, overrides prompt registry)...",
        "tools": ["ai_search", "microsoft_learn_mcp"]
    }
    
    Legacy format also supported:
    {
        "agentName": "string",
        "mcpEndpoint": "string",
        "models": [...]
    }
    """
    logging.info('Agent creation job received from queue')
    
    try:
        # Parse the queue message
        message_body = msg.get_body().decode('utf-8')
        logging.info(f'Queue message: {message_body}')
        
        config = json.loads(message_body)
        
        # Support both new format (agent_name) and legacy format (agentName)
        agent_name = config.get("agent_name") or config.get("agentName", "default-agent")
        model = config.get("model", "gpt-4.1")
        
        # Use explicit instructions from the message, or fall back to the prompt registry
        instructions = config.get("instructions") or get_prompt(agent_name)
        tool_names = config.get("tools", [])
        
        logging.info(f'Creating agent: {agent_name} with model: {model}')
        logging.info(f'Tools requested: {tool_names}')
        
        # Resolve tools via the registry (connection IDs pulled from Settings)
        tools, tool_resources = resolve_tools(tool_names)
        
        # Create the agent via the shared client
        project_client = get_project_client()
        
        agent = project_client.agents.create_agent(
            model=model,
            name=agent_name,
            instructions=instructions,
            tools=tools,
            tool_resources=tool_resources,
        )
        
        logging.info(f'Agent created successfully: {agent.id} ({agent_name})')
        
    except json.JSONDecodeError as e:
        logging.error(f'Invalid JSON in queue message: {e}')
        raise
    except ValueError as e:
        logging.error(f'Validation error: {e}')
        raise
    except Exception as e:
        logging.error(f'Error processing agent creation request: {e}')
        raise


# ══════════════════════════════════════════════
# QUEUE TRIGGER 2: Semantic Kernel Agent 
# Request/Response Pattern
# ══════════════════════════════════════════════

@app.queue_trigger(
    arg_name="msg",
    queue_name=os.environ.get("SK_AGENT_REQUEST_QUEUE_NAME", "sk-agent-request-queue"),
    connection="AGENT_STORAGE_ACCOUNT"
)
def sk_agent_processor(msg: func.QueueMessage) -> None:
    """
    Queue trigger that processes requests using a Semantic Kernel agent,
    then sends responses back to the response queue.
    
    Expected message format:
    {
        "requestId": "unique-id",
        "query": "What is the current time?",
        "requester": "foundry-agent-name"
    }
    
    Response format (sent to response queue):
    {
        "requestId": "unique-id",
        "query": "What is the current time?",
        "answer": "The current time is 2:30 PM EST",
        "metadata": {
            "processingTime": 1.5,
            "pluginsUsed": ["time", "weather"]
        }
    }
    """
    logging.info('SK Agent: Processing request from queue')
    
    try:
        # Parse the queue message
        message_body = msg.get_body().decode('utf-8')
        logging.info(f'Request message: {message_body}')
        
        request_data = json.loads(message_body)
        
        # Validate required fields
        if 'requestId' not in request_data or 'query' not in request_data:
            raise ValueError('Missing required fields: requestId and/or query')
        
        request_id = request_data['requestId']
        query = request_data['query']
        requester = request_data.get('requester', 'unknown')
        
        logging.info(f'Processing request {request_id} from {requester}: {query}')
        
        # TODO: Implement Semantic Kernel agent logic
        # This is where you'll:
        # 1. Initialize Semantic Kernel with plugins (time, weather, etc.)
        # 2. Process the query
        # 3. Get the response
        #
        # Example:
        # import semantic_kernel as sk
        # from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
        # from datetime import datetime
        # 
        # kernel = sk.Kernel()
        # 
        # # Add Azure OpenAI service
        # kernel.add_service(
        #     AzureChatCompletion(
        #         deployment_name="gpt-4",
        #         endpoint=os.environ.get("AI_SERVICES_ENDPOINT"),
        #         credential=DefaultAzureCredential()
        #     )
        # )
        # 
        # # Add plugins for time, weather, etc.
        # from semantic_kernel.core_plugins import TimePlugin
        # kernel.add_plugin(TimePlugin(), plugin_name="time")
        # 
        # # Process the query
        # result = await kernel.invoke_prompt(query)
        # answer = str(result)
        
        # For now, mock response
        import time
        start_time = time.time()
        
        # Mock answer (replace with actual SK processing)
        answer = f"[Mock Response] Processed query: '{query}'"
        plugins_used = ["time", "weather"]  # Will be actual plugins used
        
        processing_time = time.time() - start_time
        
        # Build response
        response_data = {
            "requestId": request_id,
            "query": query,
            "answer": answer,
            "metadata": {
                "processingTime": processing_time,
                "pluginsUsed": plugins_used,
                "requester": requester
            }
        }
        
        # Send response to response queue
        response_queue_name = os.environ.get("SK_AGENT_RESPONSE_QUEUE_NAME", "sk-agent-response-queue")
        send_response_to_queue(response_data, response_queue_name)
        
        logging.info(f'Successfully processed request {request_id} and sent response')
        
    except json.JSONDecodeError as e:
        logging.error(f'Invalid JSON in queue message: {e}')
        raise
    except ValueError as e:
        logging.error(f'Validation error: {e}')
        raise
    except Exception as e:
        logging.error(f'Error processing SK agent request: {e}')
        raise


def send_response_to_queue(response_data: Dict[str, Any], queue_name: str) -> None:
    """Send response message to the response queue."""
    try:
        storage_account_name = os.environ.get("AGENT_STORAGE_ACCOUNT__accountname")
        if not storage_account_name:
            # Extract from queueServiceUri
            queue_uri = os.environ.get("AGENT_STORAGE_ACCOUNT__queueServiceUri", "")
            # Format: https://<account>.queue.core.windows.net
            if queue_uri:
                storage_account_name = queue_uri.split('//')[1].split('.')[0]
        
        credential = DefaultAzureCredential()
        queue_client = QueueClient(
            account_url=f"https://{storage_account_name}.queue.core.windows.net",
            queue_name=queue_name,
            credential=credential
        )
        
        message_json = json.dumps(response_data)
        queue_client.send_message(message_json)
        
        logging.info(f'Response sent to queue {queue_name}: requestId={response_data.get("requestId")}')
        
    except Exception as e:
        logging.error(f'Error sending response to queue: {e}')
        raise

