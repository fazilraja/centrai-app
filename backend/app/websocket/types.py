from enum import StrEnum
from pydantic import BaseModel, Field
from typing import Optional


class MessageType(StrEnum):
    """WebSocket message types"""

    # Client → Server
    AUDIO_CHUNK = "audio_chunk"
    END_SESSION = "end_session"

    # Server → Client
    CONNECTION_ESTABLISHED = "connection_established"
    TRANSCRIPTION = "transcription"
    LLM_RESPONSE = "llm_response"
    AUDIO_RESPONSE = "audio_response"
    STATUS_UPDATE = "status_update"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    """WebSocket message format"""

    type: MessageType
    data: Optional[str] = Field(default=None, description="Base64 encoded for audio")
    text: Optional[str] = Field(default=None, description="Text content")
    is_final: Optional[bool] = Field(default=False, description="Whether this is the final message in a sequence")
    status: Optional[str] = Field(default=None, description="Status information")
    message: Optional[str] = Field(default=None, description="Error or info message")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    agent: Optional[str] = Field(default=None, description="Agent name")

    model_config = {
        "use_enum_values": True
    }