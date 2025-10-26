import pytest
from pydantic import ValidationError
from app.websocket.types import MessageType, WebSocketMessage


def test_message_type_enum_values():
    """Test that MessageType enum has all required values"""
    # Arrange & Act & Assert
    assert MessageType.AUDIO_CHUNK == "audio_chunk"
    assert MessageType.END_SESSION == "end_session"
    assert MessageType.CONNECTION_ESTABLISHED == "connection_established"
    assert MessageType.TRANSCRIPTION == "transcription"
    assert MessageType.LLM_RESPONSE == "llm_response"
    assert MessageType.AUDIO_RESPONSE == "audio_response"
    assert MessageType.STATUS_UPDATE == "status_update"
    assert MessageType.ERROR == "error"


def test_message_type_enum_is_string():
    """Test that MessageType is a string enum"""
    # Arrange & Act & Assert
    assert isinstance(MessageType.AUDIO_CHUNK, str)
    assert str(MessageType.AUDIO_CHUNK) == "audio_chunk"


def test_websocket_message_minimal():
    """Test WebSocketMessage with minimal required fields"""
    # Arrange & Act
    message = WebSocketMessage(type=MessageType.AUDIO_CHUNK)

    # Assert
    assert message.type == MessageType.AUDIO_CHUNK
    assert message.data is None
    assert message.text is None
    assert message.is_final is False
    assert message.status is None
    assert message.message is None
    assert message.session_id is None
    assert message.agent is None


def test_websocket_message_all_fields():
    """Test WebSocketMessage with all fields populated"""
    # Arrange
    message_data = {
        "type": MessageType.TRANSCRIPTION,
        "data": "base64encodedaudio",
        "text": "Hello world",
        "is_final": True,
        "status": "processing",
        "message": "Success",
        "session_id": "session123",
        "agent": "receptionist"
    }

    # Act
    message = WebSocketMessage(**message_data)

    # Assert
    assert message.type == MessageType.TRANSCRIPTION
    assert message.data == "base64encodedaudio"
    assert message.text == "Hello world"
    assert message.is_final is True
    assert message.status == "processing"
    assert message.message == "Success"
    assert message.session_id == "session123"
    assert message.agent == "receptionist"


def test_websocket_message_serialization():
    """Test that WebSocketMessage can be serialized to dict"""
    # Arrange
    message = WebSocketMessage(
        type=MessageType.AUDIO_RESPONSE,
        data="audiob64",
        session_id="session123"
    )

    # Act
    message_dict = message.model_dump()

    # Assert
    assert message_dict["type"] == "audio_response"
    assert message_dict["data"] == "audiob64"
    assert message_dict["session_id"] == "session123"
    assert "text" not in message_dict or message_dict["text"] is None


def test_websocket_message_json_serialization():
    """Test that WebSocketMessage can be serialized to JSON"""
    # Arrange
    message = WebSocketMessage(
        type=MessageType.ERROR,
        message="Something went wrong"
    )

    # Act
    json_str = message.model_dump_json()

    # Assert
    assert '"type":"error"' in json_str
    assert '"message":"Something went wrong"' in json_str


def test_websocket_message_invalid_type():
    """Test WebSocketMessage rejects invalid message type"""
    # Arrange & Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        WebSocketMessage(type="invalid_type")

    # Check that the error is about the type field
    errors = exc_info.value.errors()
    assert any("type" in str(error).lower() for error in errors)


def test_websocket_message_from_dict():
    """Test WebSocketMessage can be created from dict"""
    # Arrange
    message_dict = {
        "type": "llm_response",
        "text": "Hello! How can I help you?",
        "session_id": "session456"
    }

    # Act
    message = WebSocketMessage(**message_dict)

    # Assert
    assert message.type == MessageType.LLM_RESPONSE
    assert message.text == "Hello! How can I help you?"
    assert message.session_id == "session456"


def test_connection_established_message():
    """Test creating a connection established message"""
    # Arrange & Act
    message = WebSocketMessage(
        type=MessageType.CONNECTION_ESTABLISHED,
        session_id="session789",
        agent="Receptionist"
    )

    # Assert
    assert message.type == MessageType.CONNECTION_ESTABLISHED
    assert message.session_id == "session789"
    assert message.agent == "Receptionist"


def test_status_update_message():
    """Test creating a status update message"""
    # Arrange & Act
    message = WebSocketMessage(
        type=MessageType.STATUS_UPDATE,
        status="processing"
    )

    # Assert
    assert message.type == MessageType.STATUS_UPDATE
    assert message.status == "processing"


def test_audio_chunk_message():
    """Test creating an audio chunk message"""
    # Arrange & Act
    message = WebSocketMessage(
        type=MessageType.AUDIO_CHUNK,
        data="base64encodedaudiodata",
        is_final=False
    )

    # Assert
    assert message.type == MessageType.AUDIO_CHUNK
    assert message.data == "base64encodedaudiodata"
    assert message.is_final is False