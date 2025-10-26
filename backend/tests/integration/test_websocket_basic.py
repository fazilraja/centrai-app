import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_websocket_connection():
    """Test basic WebSocket connection flow"""
    client = TestClient(app)

    with client.websocket_connect("/ws/voice-agent/receptionist") as websocket:
        # 1. Receive connection confirmation
        data = websocket.receive_json()
        assert data['type'] == 'connection_established'
        assert 'session_id' in data
        assert data['agent'] == 'Receptionist'

        # 2. Send end session message
        websocket.send_json({
            'type': 'end_session'
        })

        # WebSocket should still be connected within context
        # (The WebSocketTestSession doesn't have a 'closed' attribute)


def test_websocket_invalid_agent():
    """Test WebSocket connection with invalid agent ID"""
    client = TestClient(app)

    with pytest.raises(Exception):  # Should raise an exception for invalid agent
        with client.websocket_connect("/ws/voice-agent/invalid_agent"):
            pass


def test_health_endpoint():
    """Test health check endpoint"""
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test root endpoint"""
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Voice Agent API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "healthy"