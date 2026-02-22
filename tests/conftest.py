"""Pytest configuration and shared fixtures"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(autouse=True)
def setup_environment():
    """Setup environment variables for tests"""
    test_env = {
        'FOUNDRY_PROJECT_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        'AI_SEARCH_CONNECTION_ID': 'test-search-id',
        'MCP_CONNECTION_ID': 'test-mcp-id',
        'AZURE_TENANT_ID': '00000000-0000-0000-0000-000000000000',
    }
    
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original environment
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def mock_azure_credential():
    """Mock Azure credential for testing"""
    with patch('foundry_agents.utils.foundry_client.DefaultAzureCredential') as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_project_client():
    """Mock AI Project Client"""
    client = MagicMock()
    client.agents = MagicMock()
    client.agents.create_agent = MagicMock(return_value={
        'id': 'test-agent-id',
        'name': 'test-agent',
        'status': 'created'
    })
    return client


@pytest.fixture
def mock_queue_message():
    """Mock Azure Queue Message"""
    message = MagicMock()
    message.get_body.return_value.decode.return_value = '{"agent_name": "test-agent"}'
    return message


def pytest_configure(config):
    """Configure pytest"""
    # Register custom markers
    config.addinivalue_line(
        "markers", "azure: mark test as requiring Azure credentials"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    skip_azure = pytest.mark.skip(reason="Azure credentials required")
    skip_slow = pytest.mark.skip(reason="Slow test")
    
    for item in items:
        # Skip Azure tests if not authenticated
        if "azure" in item.keywords:
            if not os.getenv('AZURE_SUBSCRIPTION_ID'):
                item.add_marker(skip_azure)
        
        # Skip slow tests in CI
        if "slow" in item.keywords:
            if os.getenv('CI'):
                item.add_marker(skip_slow)
