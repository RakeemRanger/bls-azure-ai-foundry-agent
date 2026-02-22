"""
foundry_client — Factory for the Azure AI Projects client.

Centralises credential + client creation so every function / module
gets the same configured client without duplicating boilerplate.
"""

from __future__ import annotations

from functools import lru_cache

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

from foundry_agents.configs import get_settings


def _build_credential():
    """
    Return the correct credential for the runtime environment.

    • When AZURE_CLIENT_ID is set (deployed Function App) → use
      ManagedIdentityCredential with the explicit client-id so the
      correct user-assigned MSI is picked.
    • Otherwise (local dev / CI) → fall back to DefaultAzureCredential.
    """
    settings = get_settings()
    if settings.azure_client_id:
        return ManagedIdentityCredential(client_id=settings.azure_client_id)
    return DefaultAzureCredential()


@lru_cache(maxsize=1)
def get_project_client() -> AIProjectClient:
    """Return a cached AIProjectClient wired to the Foundry project."""
    settings = get_settings()
    return AIProjectClient(
        endpoint=settings.foundry_project_endpoint,
        credential=_build_credential(),
    )
