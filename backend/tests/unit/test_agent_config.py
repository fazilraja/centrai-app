import pytest
from app.agents.config import AgentConfig, get_agent_config, get_all_agents


def test_agent_config_creation():
    """Test creating an AgentConfig"""
    # Arrange & Act
    config = AgentConfig(
        id='test_agent',
        name='Test Agent',
        description='A test agent',
        prompt='You are a test agent',
        voice_id='test_voice_id'
    )

    # Assert
    assert config.id == 'test_agent'
    assert config.name == 'Test Agent'
    assert config.description == 'A test agent'
    assert config.prompt == 'You are a test agent'
    assert config.voice_id == 'test_voice_id'
    assert config.temperature == 0.7  # default value
    assert config.max_tokens == 150  # default value


def test_agent_config_with_custom_settings():
    """Test creating an AgentConfig with custom settings"""
    # Arrange & Act
    config = AgentConfig(
        id='custom_agent',
        name='Custom Agent',
        description='A custom agent',
        prompt='You are a custom agent',
        voice_id='custom_voice_id',
        temperature=0.9,
        max_tokens=200
    )

    # Assert
    assert config.temperature == 0.9
    assert config.max_tokens == 200


def test_get_agent_config_valid():
    """Test get_agent_config returns config for valid agent_id"""
    # Arrange & Act
    config = get_agent_config('receptionist')

    # Assert
    assert config is not None
    assert config.id == 'receptionist'
    assert config.name == 'Receptionist'
    assert config.voice_id == 'EXAVITQu4vr4xnSDxMaL'
    assert len(config.prompt) > 0


def test_get_agent_config_sales():
    """Test get_agent_config returns sales agent config"""
    # Arrange & Act
    config = get_agent_config('sales')

    # Assert
    assert config is not None
    assert config.id == 'sales'
    assert config.name == 'Sales Agent'
    assert config.voice_id == '21m00Tcm4TlvDq8ikWAM'
    assert len(config.prompt) > 0


def test_get_agent_config_callcenter():
    """Test get_agent_config returns callcenter agent config"""
    # Arrange & Act
    config = get_agent_config('callcenter')

    # Assert
    assert config is not None
    assert config.id == 'callcenter'
    assert config.name == 'Call Center Agent'
    assert config.voice_id == 'pNInz6obpgDQGcFmaJgB'
    assert len(config.prompt) > 0


def test_get_agent_config_invalid():
    """Test get_agent_config returns None for invalid agent_id"""
    # Arrange & Act
    config = get_agent_config('nonexistent_agent')

    # Assert
    assert config is None


def test_get_all_agents():
    """Test get_all_agents returns all agent configurations"""
    # Arrange & Act
    agents = get_all_agents()

    # Assert
    assert isinstance(agents, dict)
    assert len(agents) == 3
    assert 'receptionist' in agents
    assert 'sales' in agents
    assert 'callcenter' in agents

    # Verify each agent is an AgentConfig instance
    for agent_id, config in agents.items():
        assert isinstance(config, AgentConfig)
        assert config.id == agent_id


def test_receptionist_prompt_content():
    """Test that receptionist agent has appropriate prompt"""
    # Arrange & Act
    config = get_agent_config('receptionist')

    # Assert
    assert 'receptionist' in config.prompt.lower()
    assert 'medical clinic' in config.prompt.lower()
    assert 'appointments' in config.prompt.lower()


def test_sales_agent_prompt_content():
    """Test that sales agent has appropriate prompt"""
    # Arrange & Act
    config = get_agent_config('sales')

    # Assert
    assert 'sales' in config.prompt.lower()
    assert 'software company' in config.prompt.lower()
    assert 'customer' in config.prompt.lower()


def test_callcenter_agent_prompt_content():
    """Test that callcenter agent has appropriate prompt"""
    # Arrange & Act
    config = get_agent_config('callcenter')

    # Assert
    assert 'customer support' in config.prompt.lower()
    assert 'tech company' in config.prompt.lower()
    assert 'technical' in config.prompt.lower()


def test_agent_voice_ids():
    """Test that all agents have valid voice IDs"""
    # Arrange
    agents = get_all_agents()

    # Act & Assert
    for agent_id, config in agents.items():
        assert isinstance(config.voice_id, str)
        assert len(config.voice_id) > 0
        # ElevenLabs voice IDs are typically alphanumeric
        assert config.voice_id.replace('_', '').replace('-', '').isalnum()


def test_agent_descriptions():
    """Test that all agents have descriptions"""
    # Arrange
    agents = get_all_agents()

    # Act & Assert
    for agent_id, config in agents.items():
        assert isinstance(config.description, str)
        assert len(config.description) > 0
        assert config.description != config.name  # Description should be different from name