import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import WebSocket
from app.websocket.manager import ConnectionManager
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_connect_creates_session():
    """Test that connect() creates a new session"""
    # Arrange
    manager = ConnectionManager()
    mock_websocket = AsyncMock(spec=WebSocket)
    agent_id = "receptionist"

    # Act
    session_id = await manager.connect(mock_websocket, agent_id)

    # Assert
    assert session_id is not None
    assert len(session_id) > 0
    assert session_id in manager.active_connections
    assert session_id in manager.sessions
    assert manager.sessions[session_id]['agent_id'] == agent_id
    assert isinstance(manager.sessions[session_id]['created_at'], datetime)
    assert manager.sessions[session_id]['created_at'].tzinfo is not None
    assert manager.sessions[session_id]['message_count'] == 0
    assert isinstance(manager.sessions[session_id]['audio_buffer'], bytearray)
    assert manager.sessions[session_id]['conversation_history'] == []
    mock_websocket.accept.assert_called_once()


@pytest.mark.asyncio
async def test_connect_creates_unique_session_ids():
    """Test that connect() creates unique session IDs"""
    # Arrange
    manager = ConnectionManager()
    mock_websocket1 = AsyncMock(spec=WebSocket)
    mock_websocket2 = AsyncMock(spec=WebSocket)
    agent_id = "receptionist"

    # Act
    session_id1 = await manager.connect(mock_websocket1, agent_id)
    session_id2 = await manager.connect(mock_websocket2, agent_id)

    # Assert
    assert session_id1 != session_id2
    assert len(manager.active_connections) == 2
    assert len(manager.sessions) == 2


def test_disconnect_removes_session():
    """Test that disconnect() removes session"""
    # Arrange
    manager = ConnectionManager()
    session_id = "test_session_id"

    # Manually add session
    manager.active_connections[session_id] = MagicMock()
    manager.sessions[session_id] = {
        'agent_id': 'test',
        'created_at': datetime.now(timezone.utc),
        'message_count': 0,
        'audio_buffer': bytearray(),
        'conversation_history': []
    }

    # Act
    manager.disconnect(session_id)

    # Assert
    assert session_id not in manager.active_connections
    assert session_id not in manager.sessions


def test_disconnect_handles_nonexistent_session():
    """Test that disconnect() handles non-existent session gracefully"""
    # Arrange
    manager = ConnectionManager()
    session_id = "nonexistent_session_id"

    # Act & Assert (should not raise exception)
    manager.disconnect(session_id)

    # Assert
    assert len(manager.active_connections) == 0
    assert len(manager.sessions) == 0


@pytest.mark.asyncio
async def test_send_message_sends_json():
    """Test that send_message() sends JSON to WebSocket"""
    # Arrange
    manager = ConnectionManager()
    session_id = "test_session_id"
    mock_websocket = AsyncMock(spec=WebSocket)
    manager.active_connections[session_id] = mock_websocket

    message = {"type": "test", "data": "hello"}

    # Act
    await manager.send_message(session_id, message)

    # Assert
    mock_websocket.send_json.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_send_message_handles_disconnected_session():
    """Test that send_message() handles disconnected session gracefully"""
    # Arrange
    manager = ConnectionManager()
    session_id = "nonexistent_session_id"
    message = {"type": "test", "data": "hello"}

    # Act & Assert (should not raise exception)
    await manager.send_message(session_id, message)


def test_get_session_returns_session():
    """Test that get_session() returns session dict if exists"""
    # Arrange
    manager = ConnectionManager()
    session_id = "test_session_id"
    test_session = {
        'agent_id': 'test',
        'created_at': datetime.now(timezone.utc),
        'message_count': 5,
        'audio_buffer': bytearray(b'test'),
        'conversation_history': [{'role': 'user', 'content': 'hello'}]
    }
    manager.sessions[session_id] = test_session

    # Act
    result = manager.get_session(session_id)

    # Assert
    assert result == test_session


def test_get_session_returns_none_for_nonexistent():
    """Test that get_session() returns None if session doesn't exist"""
    # Arrange
    manager = ConnectionManager()
    session_id = "nonexistent_session_id"

    # Act
    result = manager.get_session(session_id)

    # Assert
    assert result is None


def test_update_session_updates_fields():
    """Test that update_session() updates session fields"""
    # Arrange
    manager = ConnectionManager()
    session_id = "test_session_id"
    original_session = {
        'agent_id': 'test',
        'created_at': datetime.now(timezone.utc),
        'message_count': 5,
        'audio_buffer': bytearray(b'test'),
        'conversation_history': []
    }
    manager.sessions[session_id] = original_session

    updates = {
        'message_count': 10,
        'new_field': 'new_value'
    }

    # Act
    manager.update_session(session_id, updates)

    # Assert
    updated_session = manager.sessions[session_id]
    assert updated_session['agent_id'] == 'test'  # unchanged
    assert updated_session['message_count'] == 10  # updated
    assert updated_session['new_field'] == 'new_value'  # added
    assert updated_session['audio_buffer'] == bytearray(b'test')  # unchanged


def test_update_session_handles_nonexistent():
    """Test that update_session() handles non-existent session gracefully"""
    # Arrange
    manager = ConnectionManager()
    session_id = "nonexistent_session_id"
    updates = {'message_count': 10}

    # Act & Assert (should not raise exception)
    manager.update_session(session_id, updates)

    # Assert
    assert len(manager.sessions) == 0