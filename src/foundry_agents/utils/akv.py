"""
akv — Azure Key Vault secret client utility.

Provides a thin wrapper around SecretClient so every module
can call ``get_secret("secret-name")`` without building its own
credential or client.  Results are cached per process.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

logger = logging.getLogger(__name__)


def _build_credential():
    """Pick the right credential for the runtime environment."""
    client_id = os.environ.get("AZURE_CLIENT_ID", "")
    if client_id:
        return ManagedIdentityCredential(client_id=client_id)
    return DefaultAzureCredential()


@lru_cache(maxsize=1)
def _get_client() -> SecretClient:
    """Return a cached SecretClient pointing at the deployed Key Vault."""
    vault_uri = os.environ["KEY_VAULT_URI"]
    return SecretClient(vault_url=vault_uri, credential=_build_credential())


_secret_cache: dict[str, str] = {}


def get_secret(name: str, *, use_cache: bool = True) -> str:
    """
    Fetch a secret value from Azure Key Vault.

    Parameters
    ----------
    name : str
        The secret name (e.g. ``"foundry-project-endpoint"``).
    use_cache : bool
        If True (default), return a previously fetched value without
        another round-trip to KV.

    Returns
    -------
    str
        The secret value.

    Raises
    ------
    azure.core.exceptions.ResourceNotFoundError
        If the secret does not exist in the vault.
    """
    if use_cache and name in _secret_cache:
        return _secret_cache[name]

    value = _get_client().get_secret(name).value or ""
    _secret_cache[name] = value
    logger.debug("Fetched secret '%s' from Key Vault.", name)
    return value


def clear_cache() -> None:
    """Clear the in-process secret cache (useful for testing)."""
    _secret_cache.clear()
