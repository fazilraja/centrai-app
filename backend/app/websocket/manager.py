from typing import Dict
from fastapi import WebSocket
from datetime import datetime, timezone
import uuid


class ConnectionManager:
    """
    Manages WebSocket connections and session state.

    Responsibilities:
    - Accept and store WebSocket connections
    - Manage session metadata (agent, history, audio buffer)
    - Send messages to specific sessions
    - Cleanup on disconnect
    """

    def __init__(self):
        # Active connections: session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # Session metadata: session_id -> dict
        # Each session contains:
        #   - agent_id: str
        #   - created_at: datetime
        #   - message_count: int
        #   - audio_buffer: bytearray
        #   - conversation_history: list[dict]
        self.sessions: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, agent_id: str) -> str:
        """
        Accept WebSocket connection and create session.

        Args:
            websocket: FastAPI WebSocket object
            agent_id: Agent identifier (receptionist, sales, callcenter)

        Returns:
            session_id: Unique session identifier

        Test Cases:
        - Should accept connection
        - Should generate unique session_id
        - Should store connection in active_connections
        - Should initialize session metadata
        - Should return session_id
        """
        await websocket.accept()

        # Generate unique session ID
        session_id = str(uuid.uuid4())

        # Store connection
        self.active_connections[session_id] = websocket

        # Initialize session
        self.sessions[session_id] = {
            'agent_id': agent_id,
            'created_at': datetime.now(timezone.utc),
            'message_count': 0,
            'audio_buffer': bytearray(),
            'conversation_history': [],
        }

        return session_id

    def disconnect(self, session_id: str) -> None:
        """
        Remove connection and cleanup session.

        Args:
            session_id: Session identifier

        Test Cases:
        - Should remove connection from active_connections
        - Should remove session from sessions
        - Should handle non-existent session_id gracefully
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        if session_id in self.sessions:
            del self.sessions[session_id]

    async def send_message(self, session_id: str, message: dict) -> None:
        """
        Send message to specific session.

        Args:
            session_id: Target session
            message: Message dict to send

        Test Cases:
        - Should send JSON message to correct WebSocket
        - Should handle disconnected session gracefully
        - Should not raise exception if session doesn't exist
        """
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)

    def get_session(self, session_id: str) -> dict | None:
        """
        Get session metadata.

        Args:
            session_id: Session identifier

        Returns:
            Session dict or None if not found

        Test Cases:
        - Should return session dict if exists
        - Should return None if session doesn't exist
        """
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, updates: dict) -> None:
        """
        Update session metadata.

        Args:
            session_id: Session identifier
            updates: Dict of updates to apply

        Test Cases:
        - Should update session fields
        - Should preserve non-updated fields
        - Should handle non-existent session_id
        """
        if session_id in self.sessions:
            self.sessions[session_id].update(updates)


# Singleton instance
manager = ConnectionManager()