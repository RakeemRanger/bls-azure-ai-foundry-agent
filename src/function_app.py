import azure.functions as func
import json
import logging

from foundry_agents.configs import get_settings, resolve_tools
from foundry_agents.utils import get_project_client
from foundry_agents.prompts import get_prompt

app = func.FunctionApp()

# ──────────────────────────────────────────────
# Queue Trigger: Create Agent from queue message
# ──────────────────────────────────────────────
# Queue message format:
# {
#   "agent_name": "doc-bot",
#   "model": "gpt-4.1",
#   "instructions": "...(optional, overrides prompt registry)...",
#   "tools": ["ai_search", "microsoft_learn_mcp"]
# }
@app.queue_trigger(arg_name="msg", queue_name="agent-jobs", connection="AzureWebJobsStorage")
def create_agent(msg: func.QueueMessage):
    logging.info("Agent creation job received from queue.")

    try:
        config = json.loads(msg.get_body().decode("utf-8"))
    except (json.JSONDecodeError, ValueError) as e:
        logging.error(f"Invalid message format: {e}")
        return

    agent_name = config.get("agent_name", "default-agent")
    model = config.get("model", "gpt-4.1")
    # Use explicit instructions from the message, or fall back to the prompt registry
    instructions = config.get("instructions") or get_prompt(agent_name)
    tool_names = config.get("tools", [])

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

    logging.info(f"Agent created: {agent.id} ({agent_name})")


# ──────────────────────────────────────────────
# Timer Trigger: Update AI Search index hourly
# ──────────────────────────────────────────────
@app.timer_trigger(schedule="0 0 * * * *", arg_name="timer", run_on_startup=False)
def update_search_index(timer: func.TimerRequest):
    if timer.past_due:
        logging.warning("Timer is past due, running now.")

    logging.info("Starting AI Search index update.")

    # TODO: Add your indexing logic here
    # Examples:
    # - Pull new documents from Blob Storage
    # - Push data to AI Search index via REST API or SDK
    # - Run an AI Search indexer via the Search Management SDK

    logging.info("AI Search index update completed.")