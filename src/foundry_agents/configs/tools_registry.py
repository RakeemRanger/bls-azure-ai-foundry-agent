"""
tools_registry — Central registry of agent tool definitions.

Agent configs reference tools by short name (e.g. "ai_search").
The registry resolves each name into the SDK-compatible ``tool`` dict
and ``tool_resources`` fragment, pulling connection IDs and config
from Settings so secrets never leak into queue messages.

Adding a new tool:
    1. Write a builder function:  ``_build_<name>(settings) -> ToolEntry``
    2. Register it:  ``TOOL_REGISTRY["<name>"] = _build_<name>``
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from foundry_agents.configs.settings import Settings, get_settings

logger = logging.getLogger(__name__)


# ─── Data structures ──────────────────────────────────────────

@dataclass(frozen=True)
class ToolEntry:
    """Resolved tool ready to be passed to the Agents SDK."""

    # Goes into the ``tools`` list  (e.g. {"type": "azure_ai_search"})
    tool_def: dict[str, Any]

    # Merged into the ``tool_resources`` dict (may be empty)
    tool_resources: dict[str, Any] = field(default_factory=dict)


# Type alias for builder functions
ToolBuilder = Callable[[Settings], ToolEntry]


# ─── Individual tool builders ─────────────────────────────────

def _build_ai_search(settings: Settings) -> ToolEntry:
    """Azure AI Search — grounded retrieval over a search index."""
    if not settings.ai_search_connection_id or not settings.ai_search_index_name:
        logger.warning(
            "ai_search requested but AI_SEARCH_CONNECTION_ID / AI_SEARCH_INDEX_NAME "
            "are not configured — tool will be registered without index bindings."
        )

    return ToolEntry(
        tool_def={"type": "azure_ai_search"},
        tool_resources={
            "azure_ai_search": {
                "indexes": [
                    {
                        "index_connection_id": settings.ai_search_connection_id,
                        "index_name": settings.ai_search_index_name,
                    }
                ]
            }
        },
    )


def _build_microsoft_learn_mcp(settings: Settings) -> ToolEntry:
    """Microsoft Learn MCP — remote tool connection provisioned in Foundry."""
    if not settings.mcp_connection_id:
        logger.warning(
            "microsoft_learn_mcp requested but MCP_CONNECTION_ID is not set."
        )

    return ToolEntry(
        tool_def={
            "type": "remote_mcp",
            "remote_mcp": {
                "connection_id": settings.mcp_connection_id,
            },
        },
    )


def _build_code_interpreter(_settings: Settings) -> ToolEntry:
    """Code Interpreter — sandboxed code execution (no extra config)."""
    return ToolEntry(tool_def={"type": "code_interpreter"})


# ─── Registry ─────────────────────────────────────────────────
# Map of short name → builder function.
# Add new tools here.

TOOL_REGISTRY: dict[str, ToolBuilder] = {
    "ai_search": _build_ai_search,
    "microsoft_learn_mcp": _build_microsoft_learn_mcp,
    "code_interpreter": _build_code_interpreter,
}


# ─── Public API ───────────────────────────────────────────────

def resolve_tools(
    tool_names: list[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Resolve a list of short tool names into SDK-ready structures.

    Returns
    -------
    tools : list[dict]
        The ``tools`` list to pass to ``create_agent()``.
    tool_resources : dict
        The merged ``tool_resources`` dict.
    """
    settings = get_settings()
    tools: list[dict[str, Any]] = []
    tool_resources: dict[str, Any] = {}

    for name in tool_names:
        builder = TOOL_REGISTRY.get(name)
        if builder is None:
            logger.error("Unknown tool '%s' — skipping. Known tools: %s", name, list(TOOL_REGISTRY))
            continue

        entry = builder(settings)
        tools.append(entry.tool_def)

        # Merge tool_resources (each tool owns a unique top-level key)
        for key, value in entry.tool_resources.items():
            if key in tool_resources:
                # Same resource type from two tools — merge lists
                for sub_key, sub_val in value.items():
                    existing = tool_resources[key].get(sub_key, [])
                    tool_resources[key][sub_key] = existing + sub_val
            else:
                tool_resources[key] = value

    return tools, tool_resources


def list_available_tools() -> list[str]:
    """Return the names of all registered tools."""
    return list(TOOL_REGISTRY)