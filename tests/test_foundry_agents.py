"""Unit tests for foundry_agents module"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add foundry_agents to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSettings:
    """Test settings module"""
    
    @patch.dict('os.environ', {
        'FOUNDRY_PROJECT_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
    })
    def test_settings_initialization(self):
        """Test Settings dataclass initialization"""
        from foundry_agents.configs.settings import Settings
        
        settings = Settings(
            foundry_project_endpoint='https://test.cognitiveservices.azure.com/',
            ai_search_connection_id='test-search',
            mcp_connection_id='test-mcp'
        )
        
        assert settings.foundry_project_endpoint == 'https://test.cognitiveservices.azure.com/'
        assert settings.ai_search_connection_id == 'test-search'
        assert settings.mcp_connection_id == 'test-mcp'
    
    @patch('foundry_agents.configs.settings.SecretClient')
    def test_settings_get_settings(self, mock_secret_client):
        """Test get_settings function"""
        from foundry_agents.configs.settings import get_settings
        
        # Mock the secret client
        mock_client = MagicMock()
        mock_secret_client.return_value = mock_client
        
        # This will use cached settings if already loaded
        # In tests, we should create a fresh instance
        with patch.dict('os.environ', {
            'FOUNDRY_PROJECT_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
            'AI_SEARCH_CONNECTION_ID': 'test-search',
            'MCP_CONNECTION_ID': 'test-mcp'
        }):
            settings = get_settings()
            assert settings is not None
            assert hasattr(settings, 'foundry_project_endpoint')


class TestToolsRegistry:
    """Test tools registry module"""
    
    def test_tool_registry_structure(self):
        """Test that TOOL_REGISTRY has expected structure"""
        from foundry_agents.configs.tools_registry import TOOL_REGISTRY
        
        assert isinstance(TOOL_REGISTRY, dict)
        assert len(TOOL_REGISTRY) > 0
        
        for tool_name, tool_config in TOOL_REGISTRY.items():
            assert isinstance(tool_name, str)
            assert 'type' in tool_config
            assert 'endpoint' in tool_config or 'package' in tool_config or 'api' in tool_config
    
    @patch('foundry_agents.configs.settings.get_settings')
    def test_resolve_tools(self, mock_get_settings):
        """Test resolve_tools function"""
        from foundry_agents.configs.tools_registry import resolve_tools
        
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.ai_search_connection_id = 'test-search'
        mock_settings.mcp_connection_id = 'test-mcp'
        mock_get_settings.return_value = mock_settings
        
        # Test with empty tool list
        tools, resources = resolve_tools([])
        assert isinstance(tools, list)
        assert isinstance(resources, dict)
    
    def test_tool_registry_coverage(self):
        """Test that essential tools are registered"""
        from foundry_agents.configs.tools_registry import TOOL_REGISTRY
        
        essential_tools = ['ai_search', 'code_interpreter']
        for tool in essential_tools:
            assert tool in TOOL_REGISTRY, f"Missing essential tool: {tool}"


class TestFoundryClient:
    """Test foundry client factory"""
    
    @patch('foundry_agents.utils.foundry_client.DefaultAzureCredential')
    @patch('foundry_agents.utils.foundry_client.AIProjectClient')
    def test_get_project_client(self, mock_client_class, mock_credential):
        """Test get_project_client function"""
        from foundry_agents.utils.foundry_client import get_project_client
        
        # Mock the client
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        
        with patch.dict('os.environ', {
            'FOUNDRY_PROJECT_ENDPOINT': 'https://test.cognitiveservices.azure.com/',
        }):
            client = get_project_client()
            assert client is not None
    
    @patch.dict('os.environ', {'AZURE_CLIENT_ID': 'test-id'})
    def test_credential_selection_with_managed_identity(self):
        """Test that ManagedIdentityCredential is used when AZURE_CLIENT_ID is set"""
        from foundry_agents.utils.foundry_client import _build_credential
        
        with patch('foundry_agents.utils.foundry_client.ManagedIdentityCredential') as mock_mi:
            _build_credential()
            mock_mi.assert_called_once()
    
    @patch.dict('os.environ', {}, clear=True)
    def test_credential_selection_default(self):
        """Test that DefaultAzureCredential is used when AZURE_CLIENT_ID is not set"""
        from foundry_agents.utils.foundry_client import _build_credential
        
        with patch('foundry_agents.utils.foundry_client.DefaultAzureCredential') as mock_default:
            _build_credential()
            mock_default.assert_called_once()


class TestPrompts:
    """Test prompts module"""
    
    def test_prompts_exist(self):
        """Test that prompt templates are defined"""
        from foundry_agents.prompts.agent_prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
        
        assert isinstance(SYSTEM_PROMPT, str)
        assert len(SYSTEM_PROMPT) > 0
        assert isinstance(USER_PROMPT_TEMPLATE, str)
        assert len(USER_PROMPT_TEMPLATE) > 0
    
    def test_system_prompt_content(self):
        """Test that system prompt has expected content"""
        from foundry_agents.prompts.agent_prompts import SYSTEM_PROMPT
        
        # Check for key phrases that should be in the prompt
        assert any(keyword in SYSTEM_PROMPT.lower() for keyword in 
                  ['agent', 'assistant', 'help', 'task'])


class TestIntegration:
    """Integration tests"""
    
    def test_foundry_agents_imports(self):
        """Test that all public APIs can be imported"""
        from foundry_agents.configs import get_settings, resolve_tools
        from foundry_agents.utils import get_project_client
        from foundry_agents.prompts import get_prompt
        
        assert callable(get_settings)
        assert callable(resolve_tools)
        assert callable(get_project_client)
        assert callable(get_prompt)
    
    def test_module_structure(self):
        """Test module structure and organization"""
        import foundry_agents
        
        assert hasattr(foundry_agents, 'configs')
        assert hasattr(foundry_agents, 'utils')
        assert hasattr(foundry_agents, 'prompts')


# Test fixtures for common setup
@pytest.fixture
def mock_settings():
    """Fixture for mocked settings"""
    return {
        'foundry_project_endpoint': 'https://test.cognitiveservices.azure.com/',
        'ai_search_connection_id': 'test-search',
        'mcp_connection_id': 'test-mcp'
    }


@pytest.fixture
def mock_azure_credentials():
    """Fixture for mocked Azure credentials"""
    with patch('foundry_agents.utils.foundry_client.DefaultAzureCredential'):
        yield


@pytest.fixture
def mock_project_client():
    """Fixture for mocked project client"""
    return MagicMock()
