"""
constants — Hardcoded names and non-secret values.

This file is safe to commit.  It contains:
  • Key Vault **secret names** (just the label, not the value)
  • Resource SKUs, queue names, and other plain-text defaults

Secret *values* are resolved at runtime via ``akv.get_secret()``.
Non-secret constants are plain strings used directly.
"""

from __future__ import annotations

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Key Vault secret names  (the labels stored in AKV)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Azure AI Foundry
KV_FOUNDRY_PROJECT_ENDPOINT = "foundry-project-endpoint"

# AI Search
KV_AI_SEARCH_CONNECTION_ID = "ai-search-connection-id"
KV_AI_SEARCH_INDEX_NAME = "ai-search-index-name"

# MCP connections
KV_MCP_CONNECTION_ID = "mcp-connection-id"

# Storage
KV_STORAGE_CONNECTION_STRING = "AzureWebJobsStorage"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  Plain-text constants  (not secrets — safe as-is)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Queue
AGENT_QUEUE_NAME = "agent-jobs"

# Function App runtime
FUNCTIONS_WORKER_RUNTIME = "python"
PYTHON_VERSION = "3.11"

# Hosting
HOSTING_SKU_NAME = "Y1"
HOSTING_SKU_TIER = "Dynamic"
STORAGE_SKU = "Standard_LRS"
STORAGE_KIND = "StorageV2"

# Default agent model
DEFAULT_AGENT_MODEL = "gpt-4.1"
DEFAULT_AGENT_NAME = "default-agent"
