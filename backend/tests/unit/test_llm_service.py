import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.llm_service import LLMService


@pytest.mark.asyncio
async def test_chat_generates_response():
    """Test that chat() generates response for valid input"""
    # Arrange
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Hello! How can I help you today?"
            )
        )
    ]

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch('app.services.llm_service.AsyncOpenAI', return_value=mock_client):
        service = LLMService()

    # Act
    result = await service.chat(
        message="Hello",
        agent_prompt="You are a helpful assistant."
    )

    # Assert
    assert isinstance(result, str)
    assert len(result) > 0
    assert result == "Hello! How can I help you today?"
    mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_chat_empty_message_raises_error():
    """Test that empty message raises ValueError"""
    # Arrange
    service = LLMService()

    # Act & Assert
    with pytest.raises(ValueError, match="Message cannot be empty"):
        await service.chat(
            message="",
            agent_prompt="You are a helpful assistant."
        )


@pytest.mark.asyncio
async def test_chat_whitespace_message_raises_error():
    """Test that whitespace-only message raises ValueError"""
    # Arrange
    service = LLMService()

    # Act & Assert
    with pytest.raises(ValueError, match="Message cannot be empty"):
        await service.chat(
            message="   ",
            agent_prompt="You are a helpful assistant."
        )


@pytest.mark.asyncio
async def test_chat_empty_agent_prompt_raises_error():
    """Test that empty agent prompt raises ValueError"""
    # Arrange
    service = LLMService()

    # Act & Assert
    with pytest.raises(ValueError, match="Agent prompt cannot be empty"):
        await service.chat(
            message="Hello",
            agent_prompt=""
        )


@pytest.mark.asyncio
async def test_chat_handles_conversation_history():
    """Test that chat() properly handles conversation history"""
    # Arrange
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Based on our previous conversation..."
            )
        )
    ]

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch('app.services.llm_service.AsyncOpenAI', return_value=mock_client):
        service = LLMService()

    conversation_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

    # Act
    await service.chat(
        message="How are you?",
        agent_prompt="You are a helpful assistant.",
        conversation_history=conversation_history
    )

    # Assert
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]['messages']

    # Should have system prompt + history + current message
    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are a helpful assistant."
    assert messages[1] == {"role": "user", "content": "Hello"}
    assert messages[2] == {"role": "assistant", "content": "Hi there!"}
    assert messages[3] == {"role": "user", "content": "How are you?"}


@pytest.mark.asyncio
async def test_chat_limits_conversation_history():
    """Test that chat() limits conversation history to last 10 messages"""
    # Arrange
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Response from limited history"
            )
        )
    ]

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch('app.services.llm_service.AsyncOpenAI', return_value=mock_client):
        service = LLMService()

    # Create 15 messages of conversation history
    long_history = []
    for i in range(15):
        role = "user" if i % 2 == 0 else "assistant"
        long_history.append({"role": role, "content": f"Message {i}"})

    # Act
    await service.chat(
        message="Current message",
        agent_prompt="You are a helpful assistant.",
        conversation_history=long_history
    )

    # Assert
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]['messages']

    # Should have system prompt + last 10 history messages + current message
    # Total should be 1 + 10 + 1 = 12 messages
    assert len(messages) == 12

    # Check that it includes the last 10 messages from history
    history_in_call = messages[1:-1]  # Exclude system prompt and current message
    assert len(history_in_call) == 10
    assert history_in_call[0]["content"] == "Message 5"  # First of the last 10
    assert history_in_call[-1]["content"] == "Message 14"  # Last of the history


@pytest.mark.asyncio
async def test_chat_uses_correct_parameters():
    """Test that chat() uses correct model parameters"""
    # Arrange
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content="Test response")
        )
    ]

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch('app.services.llm_service.settings') as mock_settings, \
         patch('app.services.llm_service.AsyncOpenAI', return_value=mock_client):
        mock_settings.OPENAI_MODEL = "gpt-4o-mini"
        service = LLMService()

    # Act
    await service.chat(
        message="Test message",
        agent_prompt="You are a test assistant."
    )

    # Assert
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]['model'] == "gpt-4o-mini"
    assert call_args[1]['temperature'] == 0.7
    assert call_args[1]['max_tokens'] == 150


@pytest.mark.asyncio
async def test_chat_handles_api_error():
    """Test that chat() properly handles API errors"""
    # Arrange
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(
        side_effect=Exception("API Error: Rate limit exceeded")
    )

    with patch('app.services.llm_service.AsyncOpenAI', return_value=mock_client):
        service = LLMService()

    # Act & Assert
    with pytest.raises(Exception, match="API Error: Rate limit exceeded"):
        await service.chat(
            message="Test message",
            agent_prompt="You are a test assistant."
        )


@pytest.mark.asyncio
async def test_chat_with_no_history():
    """Test that chat() works with no conversation history"""
    # Arrange
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content="Response without history")
        )
    ]

    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch('app.services.llm_service.AsyncOpenAI', return_value=mock_client):
        service = LLMService()

    # Act
    result = await service.chat(
        message="Hello",
        agent_prompt="You are a helpful assistant."
    )

    # Assert
    assert result == "Response without history"
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args[1]['messages']

    # Should have system prompt + current message only
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hello"


@pytest.mark.asyncio
async def test_llm_service_initialization():
    """Test LLMService initialization"""
    # Arrange & Act
    with patch('app.services.llm_service.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = "test_api_key"

        service = LLMService()

        # Assert
        assert service.client is not None


def test_llm_service_repr():
    """Test LLMService string representation"""
    # Arrange
    with patch('app.services.llm_service.settings'):
        service = LLMService()

    # Act & Assert
    repr_str = repr(service)
    assert "LLMService" in repr_str