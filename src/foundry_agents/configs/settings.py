"""
Settings — single source of truth for all infra / runtime configuration.

Values are resolved from Azure Key Vault at runtime using secret names
defined in constants.py.  The AZURE_CLIENT_ID and KEY_VAULT_URI are the
only env-var bootstraps (set by Bicep app settings).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache

from foundry_agents.configs.constants import (
    AGENT_QUEUE_NAME,
    KV_AI_SEARCH_CONNECTION_ID,
    KV_AI_SEARCH_INDEX_NAME,
    KV_FOUNDRY_PROJECT_ENDPOINT,
    KV_MCP_CONNECTION_ID,
)
from foundry_agents.utils.akv import get_secret


@dataclass(frozen=True)
class Settings:
    """Immutable bag of configuration — secrets resolved from Key Vault."""

    # ── Azure AI Foundry ──────────────────────────────────────
    foundry_project_endpoint: str = field(
        default_factory=lambda: get_secret(KV_FOUNDRY_PROJECT_ENDPOINT)
    )

    # ── AI Search ─────────────────────────────────────────────
    ai_search_connection_id: str = field(
        default_factory=lambda: get_secret(KV_AI_SEARCH_CONNECTION_ID)
    )
    ai_search_index_name: str = field(
        default_factory=lambda: get_secret(KV_AI_SEARCH_INDEX_NAME)
    )

    # ── MCP Connections ───────────────────────────────────────
    mcp_connection_id: str = field(
        default_factory=lambda: get_secret(KV_MCP_CONNECTION_ID)
    )

    # ── Identity ──────────────────────────────────────────────
    # Bootstrap env vars — these are NOT secrets, set by Bicep app settings.
    azure_client_id: str = field(
        default_factory=lambda: os.environ.get("AZURE_CLIENT_ID", "")
    )
    key_vault_uri: str = field(
        default_factory=lambda: os.environ.get("KEY_VAULT_URI", "")
    )

    # ── Storage / Queue (plain-text constant) ─────────────────
    storage_queue_name: str = field(default=AGENT_QUEUE_NAME)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached, frozen Settings instance (created once per process)."""
    return Settings()
