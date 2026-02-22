"""
agent_prompts — Central registry of LLM system prompts for each agent type.

Add a new key to AGENT_PROMPTS whenever you define a new agent.
The queue message can reference the key by name so the Function App
looks up the full prompt text automatically.
"""

from __future__ import annotations

# ────────────────────────────────────────────────────
# Prompt registry:  agent_name  →  system instructions
# ────────────────────────────────────────────────────
AGENT_PROMPTS: dict[str, str] = {
    "doc-bot": (
        "You are a documentation assistant. "
        "Use the connected AI Search index to find relevant documentation, "
        "then provide clear, concise answers with source references. "
        "If the answer is not in the index, say so honestly."
    ),
    "code-helper": (
        "You are a coding assistant specialised in Azure services. "
        "Answer questions about Azure SDKs, Bicep, ARM templates, "
        "and cloud architecture. Provide code samples when helpful."
    ),
    "default": (
        "You are a helpful AI assistant powered by Azure AI Foundry."
    ),
}


def get_prompt(agent_name: str) -> str:
    """
    Return the system prompt for *agent_name*.

    Falls back to the ``"default"`` prompt when the name is not found.
    """
    return AGENT_PROMPTS.get(agent_name, AGENT_PROMPTS["default"])
