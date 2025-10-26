# Voice Agent Backend - MVP Implementation Plan (TDD)

> **Version:** 1.0
> **Date:** 2025-10-25
> **Status:** Design Phase - Ready for TDD Implementation

---

## Table of Contents

1. [Overview](#1-overview)
2. [Backend Architecture](#2-backend-architecture)
3. [File Structure](#3-file-structure)
4. [WebSocket Implementation](#4-websocket-implementation)
5. [Service Layer](#5-service-layer)
6. [Agent Configuration](#6-agent-configuration)
7. [Audio Processing](#7-audio-processing)
8. [WebSocket Protocol](#8-websocket-protocol)
9. [Error Handling](#9-error-handling)
10. [TDD Implementation Plan](#10-tdd-implementation-plan)
11. [Testing Strategy](#11-testing-strategy)
12. [Configuration](#12-configuration)

---

## 1. Overview

### 1.1 Project Summary

Building the backend for a **real-time voice agent application** using FastAPI with WebSocket support for bidirectional audio streaming and processing.

### 1.2 Technology Stack

- **FastAPI** (Python 3.13+) - Web framework
- **WebSockets** (native FastAPI) - Real-time communication
- **OpenAI API** - Whisper (STT) + GPT (LLM)
- **ElevenLabs API** - Text-to-Speech
- **Pydantic** - Data validation
- **Pytest** - Testing framework (TDD)
- **UV** - Package manager

### 1.3 Core Responsibilities

1. **WebSocket Management** - Handle client connections and sessions
2. **Audio Processing** - Buffer and process incoming audio chunks
3. **Speech-to-Text** - Transcribe audio using OpenAI Whisper
4. **LLM Processing** - Generate responses using OpenAI GPT
5. **Text-to-Speech** - Synthesize speech using ElevenLabs
6. **Session Management** - In-memory session state (no database)

### 1.4 MVP Constraints

- ❌ No database (in-memory only)
- ❌ No authentication
- ❌ No persistence
- ❌ Single concurrent session support
- ✅ TDD approach (test-first development)

---

## 2. Backend Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT (Browser)                            │
│                                                                  │
│                    WebSocket Connection                          │
│                 ws://localhost:8000/ws/voice-agent/{agent_id}   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FASTAPI APPLICATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WebSocket Endpoint Layer                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  @router.websocket("/ws/voice-agent/{agent_id}")         │  │
│  │  - Accept connection                                      │  │
│  │  - Route messages                                         │  │
│  │  - Handle lifecycle                                       │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                             │
│  Connection Manager                                             │
│  ┌────────────────▼─────────────────────────────────────────┐  │
│  │  - Manage active connections                             │  │
│  │  - Session state (in-memory dict)                        │  │
│  │  - Audio buffering                                        │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                             │
│  Message Handler                                                │
│  ┌────────────────▼─────────────────────────────────────────┐  │
│  │  handle_audio_chunk()                                     │  │
│  │  - Buffer audio                                           │  │
│  │  - Trigger processing                                     │  │
│  │  - Orchestrate services                                   │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                             │
└───────────────────┼─────────────────────────────────────────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────────┐
│ STT      │  │ LLM      │  │ TTS          │
│ Service  │  │ Service  │  │ Service      │
│          │  │          │  │              │
│ OpenAI   │  │ OpenAI   │  │ ElevenLabs   │
│ Whisper  │  │ GPT      │  │              │
└────┬─────┘  └────┬─────┘  └──────┬───────┘
     │             │                │
     ▼             ▼                ▼
┌─────────────────────────────────────────┐
│        External API Calls               │
│  - POST to OpenAI Whisper              │
│  - POST to OpenAI Chat Completions     │
│  - POST to ElevenLabs TTS (streaming)  │
└─────────────────────────────────────────┘
```

### 2.2 Request Flow

```
1. Client connects via WebSocket
   └─> ConnectionManager.connect()
       └─> Generate session_id
       └─> Store connection and session state
       └─> Send CONNECTION_ESTABLISHED message

2. Client sends audio chunk
   └─> WebSocket receives JSON message
       └─> Parse WebSocketMessage
       └─> Route to handle_audio_chunk()
           └─> Buffer audio in session
           └─> Check if should process (is_final or buffer threshold)

3. Process audio pipeline
   └─> STTService.transcribe(audio_bytes)
       └─> Send TRANSCRIPTION message to client
   └─> LLMService.chat(transcription, agent_prompt, history)
       └─> Send LLM_RESPONSE message to client
   └─> TTSService.synthesize_stream(llm_response)
       └─> Stream AUDIO_RESPONSE chunks to client
   └─> Send STATUS_UPDATE (idle) to client

4. Client disconnects
   └─> ConnectionManager.disconnect()
       └─> Cleanup session
       └─> Close WebSocket
```

### 2.3 Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **WebSocket Endpoint** | Accept connections, route messages, lifecycle management |
| **ConnectionManager** | Manage connections, session state, send/broadcast messages |
| **Message Handlers** | Process incoming messages, orchestrate services |
| **STTService** | Transcribe audio to text via OpenAI Whisper |
| **LLMService** | Generate conversational responses via OpenAI GPT |
| **TTSService** | Synthesize speech from text via ElevenLabs |
| **AudioProcessor** | Format conversion, validation, utilities |
| **AgentConfig** | Load and provide agent configurations |

---

## 3. File Structure

### 3.1 Complete Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app initialization
│   ├── config.py                    # Configuration (Pydantic settings)
│   │
│   ├── websocket/
│   │   ├── __init__.py
│   │   ├── manager.py               # ConnectionManager class
│   │   ├── handlers.py              # WebSocket endpoint + handlers
│   │   └── types.py                 # WebSocket message types
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── stt_service.py           # OpenAI Whisper integration
│   │   ├── llm_service.py           # OpenAI GPT integration
│   │   ├── tts_service.py           # ElevenLabs integration
│   │   └── audio_processor.py       # Audio utilities
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── config.py                # Agent configurations
│   │   └── prompts.py               # Agent prompt templates
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py                # Logging configuration
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   │
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_connection_manager.py
│   │   ├── test_stt_service.py
│   │   ├── test_llm_service.py
│   │   ├── test_tts_service.py
│   │   └── test_audio_processor.py
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_websocket_flow.py
│   │   └── test_end_to_end.py
│   │
│   └── fixtures/
│       ├── __init__.py
│       ├── sample_audio.webm        # Sample audio files
│       └── mock_responses.py        # Mock API responses
│
├── pyproject.toml                   # Dependencies (UV)
├── pytest.ini                       # Pytest configuration
├── .env.example                     # Environment variables template
└── README.md                        # Project documentation
```

### 3.2 Files to Create

```
✅ Already Exists:
- pyproject.toml (from backend setup)
- backend/ directory

❌ Need to Create:
- All app/ modules
- All tests/ modules
- pytest.ini
- .env.example
```

---

## 4. WebSocket Implementation

### 4.1 Connection Manager

```python
# app/websocket/manager.py

from typing import Dict
from fastapi import WebSocket
from datetime import datetime
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
            'created_at': datetime.utcnow(),
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
```

### 4.2 WebSocket Endpoint

```python
# app/websocket/handlers.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.websocket.types import MessageType, WebSocketMessage
from app.services.stt_service import STTService
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService
from app.agents.config import get_agent_config
import base64
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/voice-agent/{agent_id}")
async def voice_agent_endpoint(websocket: WebSocket, agent_id: str):
    """
    Main WebSocket endpoint for voice agent interaction.

    Flow:
    1. Validate agent_id
    2. Accept connection
    3. Send connection confirmation
    4. Listen for messages
    5. Handle messages based on type
    6. Cleanup on disconnect

    Test Cases:
    - Should reject invalid agent_id
    - Should accept valid connection
    - Should send connection_established message
    - Should handle audio_chunk messages
    - Should handle end_session messages
    - Should cleanup on disconnect
    - Should handle WebSocketDisconnect gracefully
    - Should handle errors and send error messages
    """

    # Validate agent
    agent_config = get_agent_config(agent_id)
    if not agent_config:
        await websocket.close(code=1003, reason="Invalid agent ID")
        return

    # Initialize services
    stt_service = STTService()
    llm_service = LLMService()
    tts_service = TTSService()

    # Accept connection
    session_id = await manager.connect(websocket, agent_id)

    # Send connection confirmation
    await manager.send_message(session_id, {
        'type': MessageType.CONNECTION_ESTABLISHED,
        'session_id': session_id,
        'agent': agent_config.name,
    })

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = WebSocketMessage(**data)

            # Route message
            if message.type == MessageType.AUDIO_CHUNK:
                await handle_audio_chunk(
                    session_id, message,
                    stt_service, llm_service, tts_service,
                    agent_config
                )

            elif message.type == MessageType.END_SESSION:
                break

            else:
                # Unknown message type
                logger.warning(f"Unknown message type: {message.type}")
                await manager.send_message(session_id, {
                    'type': MessageType.ERROR,
                    'message': f'Unknown message type: {message.type}'
                })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")

    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}", exc_info=True)
        await manager.send_message(session_id, {
            'type': MessageType.ERROR,
            'message': str(e)
        })

    finally:
        # Cleanup
        manager.disconnect(session_id)
        logger.info(f"Session ended: {session_id}")


async def handle_audio_chunk(
    session_id: str,
    message: WebSocketMessage,
    stt_service: STTService,
    llm_service: LLMService,
    tts_service: TTSService,
    agent_config: dict
) -> None:
    """
    Process incoming audio chunk.

    Flow:
    1. Get session
    2. Decode audio data
    3. Add to buffer
    4. Check if should process (is_final or buffer threshold)
    5. If yes:
       a. Send STATUS_UPDATE (processing)
       b. Transcribe audio (STT)
       c. Send TRANSCRIPTION
       d. Get LLM response
       e. Send LLM_RESPONSE
       f. Send STATUS_UPDATE (generating_audio)
       g. Stream TTS audio
       h. Send STATUS_UPDATE (idle)

    Test Cases:
    - Should buffer audio chunks
    - Should process on is_final=True
    - Should process when buffer exceeds threshold
    - Should send correct status updates
    - Should handle STT errors
    - Should handle LLM errors
    - Should handle TTS errors
    - Should update conversation history
    """

    # Get session
    session = manager.get_session(session_id)
    if not session:
        logger.error(f"Session not found: {session_id}")
        return

    # Decode audio data
    if message.data:
        audio_data = base64.b64decode(message.data)
        session['audio_buffer'].extend(audio_data)

    # Check if we should process
    buffer_size = len(session['audio_buffer'])
    should_process = (
        message.is_final or
        buffer_size >= 48000  # ~1 second at 48kHz mono (approximate)
    )

    if not should_process:
        return

    # Send processing status
    await manager.send_message(session_id, {
        'type': MessageType.STATUS_UPDATE,
        'status': 'processing'
    })

    # Get buffered audio
    audio_bytes = bytes(session['audio_buffer'])
    session['audio_buffer'].clear()

    try:
        # 1. Speech-to-Text
        transcription = await stt_service.transcribe(audio_bytes)

        # Send transcription
        await manager.send_message(session_id, {
            'type': MessageType.TRANSCRIPTION,
            'text': transcription,
            'is_final': True
        })

        # Add to conversation history
        session['conversation_history'].append({
            'role': 'user',
            'content': transcription
        })

        # 2. LLM Processing
        llm_response = await llm_service.chat(
            message=transcription,
            agent_prompt=agent_config.prompt,
            conversation_history=session['conversation_history']
        )

        # Send LLM response text
        await manager.send_message(session_id, {
            'type': MessageType.LLM_RESPONSE,
            'text': llm_response
        })

        # Add to conversation history
        session['conversation_history'].append({
            'role': 'assistant',
            'content': llm_response
        })

        # 3. Text-to-Speech
        await manager.send_message(session_id, {
            'type': MessageType.STATUS_UPDATE,
            'status': 'generating_audio'
        })

        # Stream TTS audio
        async for audio_chunk in tts_service.synthesize_stream(
            text=llm_response,
            voice_id=agent_config.voice_id
        ):
            # Send audio chunk to client
            audio_b64 = base64.b64encode(audio_chunk).decode()
            await manager.send_message(session_id, {
                'type': MessageType.AUDIO_RESPONSE,
                'data': audio_b64
            })

        # Done
        await manager.send_message(session_id, {
            'type': MessageType.STATUS_UPDATE,
            'status': 'idle'
        })

    except Exception as e:
        logger.error(f"Error processing audio: {e}", exc_info=True)
        await manager.send_message(session_id, {
            'type': MessageType.ERROR,
            'message': 'Failed to process audio'
        })
```

### 4.3 WebSocket Message Types

```python
# app/websocket/types.py

from enum import Enum
from pydantic import BaseModel
from typing import Optional


class MessageType(str, Enum):
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
    data: Optional[str] = None  # Base64 encoded for audio
    text: Optional[str] = None
    is_final: Optional[bool] = False
    status: Optional[str] = None
    message: Optional[str] = None
    session_id: Optional[str] = None
    agent: Optional[str] = None

    class Config:
        use_enum_values = True
```

---

## 5. Service Layer

### 5.1 STT Service (OpenAI Whisper)

```python
# app/services/stt_service.py

from openai import AsyncOpenAI
from app.config import settings
import io
import logging

logger = logging.getLogger(__name__)


class STTService:
    """
    Speech-to-Text service using OpenAI Whisper.

    Responsibilities:
    - Transcribe audio bytes to text
    - Handle audio format conversion
    - Error handling and retries
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio to text.

        Args:
            audio_bytes: Raw audio data (WebM, MP3, WAV, etc.)

        Returns:
            Transcribed text

        Raises:
            ValueError: If audio_bytes is empty
            Exception: If API call fails

        Test Cases:
        - Should transcribe valid audio
        - Should raise ValueError for empty audio
        - Should handle API errors gracefully
        - Should return non-empty string
        - Should handle various audio formats
        """

        if not audio_bytes:
            raise ValueError("Audio bytes cannot be empty")

        try:
            # Create file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.webm"  # Whisper needs a filename

            # Call Whisper API
            response = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",  # Optional: auto-detect if omitted
                response_format="text"
            )

            logger.info(f"Transcription successful: {len(response)} chars")
            return response

        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            raise
```

### 5.2 LLM Service (OpenAI GPT)

```python
# app/services/llm_service.py

from openai import AsyncOpenAI
from app.config import settings
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service using OpenAI GPT.

    Responsibilities:
    - Generate conversational responses
    - Maintain conversation context
    - Handle errors and retries
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat(
        self,
        message: str,
        agent_prompt: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Get LLM response.

        Args:
            message: User's message
            agent_prompt: System prompt for agent role
            conversation_history: Previous messages (list of dicts)

        Returns:
            LLM response text

        Raises:
            ValueError: If message or agent_prompt is empty
            Exception: If API call fails

        Test Cases:
        - Should generate response for valid input
        - Should raise ValueError for empty message
        - Should raise ValueError for empty agent_prompt
        - Should handle conversation history correctly
        - Should limit response length
        - Should handle API errors gracefully
        """

        if not message:
            raise ValueError("Message cannot be empty")

        if not agent_prompt:
            raise ValueError("Agent prompt cannot be empty")

        try:
            # Build messages
            messages = [
                {"role": "system", "content": agent_prompt}
            ]

            # Add conversation history (limit to last 10 turns)
            if conversation_history:
                # Keep only last 10 messages to avoid token limits
                recent_history = conversation_history[-10:]
                messages.extend(recent_history)

            # Add current message
            messages.append({"role": "user", "content": message})

            # Call GPT API
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=150,  # Keep responses concise for voice
            )

            response_text = response.choices[0].message.content
            logger.info(f"LLM response generated: {len(response_text)} chars")

            return response_text

        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            raise
```

### 5.3 TTS Service (ElevenLabs)

```python
# app/services/tts_service.py

import aiohttp
from app.config import settings
from typing import AsyncIterator
import logging

logger = logging.getLogger(__name__)


class TTSService:
    """
    Text-to-Speech service using ElevenLabs.

    Responsibilities:
    - Convert text to speech
    - Stream audio chunks
    - Handle errors and retries
    """

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.api_url = "https://api.elevenlabs.io/v1"

    async def synthesize_stream(
        self,
        text: str,
        voice_id: str
    ) -> AsyncIterator[bytes]:
        """
        Convert text to speech with streaming.

        Args:
            text: Text to synthesize
            voice_id: ElevenLabs voice ID

        Yields:
            Audio chunks (MP3 format)

        Raises:
            ValueError: If text or voice_id is empty
            Exception: If API call fails

        Test Cases:
        - Should stream audio for valid input
        - Should raise ValueError for empty text
        - Should raise ValueError for empty voice_id
        - Should yield multiple chunks
        - Should handle API errors gracefully
        """

        if not text:
            raise ValueError("Text cannot be empty")

        if not voice_id:
            raise ValueError("Voice ID cannot be empty")

        url = f"{self.api_url}/text-to-speech/{voice_id}/stream"

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"TTS API error: {error_text}")

                    # Stream audio chunks
                    chunk_count = 0
                    async for chunk in response.content.iter_chunked(4096):
                        chunk_count += 1
                        yield chunk

                    logger.info(f"TTS streaming complete: {chunk_count} chunks")

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}", exc_info=True)
            raise
```

### 5.4 Audio Processor

```python
# app/services/audio_processor.py

import io
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """
    Audio format conversion and processing utilities.

    Responsibilities:
    - Convert between audio formats
    - Validate audio data
    - Calculate audio properties
    """

    @staticmethod
    def convert_webm_to_mp3(webm_bytes: bytes) -> bytes:
        """
        Convert WebM to MP3.

        Args:
            webm_bytes: WebM audio data

        Returns:
            MP3 audio data

        Test Cases:
        - Should convert valid WebM to MP3
        - Should raise exception for invalid data
        """

        try:
            # Load WebM
            audio = AudioSegment.from_file(
                io.BytesIO(webm_bytes),
                format="webm"
            )

            # Export as MP3
            output = io.BytesIO()
            audio.export(output, format="mp3", bitrate="128k")

            return output.getvalue()

        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise

    @staticmethod
    def detect_silence(audio_bytes: bytes, threshold: int = -40) -> bool:
        """
        Detect if audio is mostly silence.

        Args:
            audio_bytes: Audio data
            threshold: dBFS threshold for silence

        Returns:
            True if audio is silent, False otherwise

        Test Cases:
        - Should detect silence
        - Should detect non-silence
        """

        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            return audio.dBFS < threshold

        except Exception as e:
            logger.error(f"Silence detection failed: {e}")
            return False

    @staticmethod
    def get_duration(audio_bytes: bytes) -> float:
        """
        Get audio duration in seconds.

        Args:
            audio_bytes: Audio data

        Returns:
            Duration in seconds

        Test Cases:
        - Should return correct duration
        - Should handle various formats
        """

        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            return len(audio) / 1000.0  # Convert ms to seconds

        except Exception as e:
            logger.error(f"Duration calculation failed: {e}")
            return 0.0
```

---

## 6. Agent Configuration

### 6.1 Agent Config

```python
# app/agents/config.py

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class AgentConfig:
    """Agent configuration"""

    id: str
    name: str
    description: str
    prompt: str
    voice_id: str  # ElevenLabs voice ID
    temperature: float = 0.7
    max_tokens: int = 150


# Agent configurations
AGENTS: Dict[str, AgentConfig] = {
    'receptionist': AgentConfig(
        id='receptionist',
        name='Receptionist',
        description='Friendly receptionist for appointment scheduling',
        prompt="""You are a professional and friendly receptionist for a medical clinic.

Your responsibilities:
- Greet callers warmly
- Help schedule appointments
- Answer basic questions about clinic hours and services
- Collect patient information (name, phone, reason for visit)
- Be concise and clear in your responses

Guidelines:
- Keep responses under 2-3 sentences for natural conversation flow
- Be polite and professional
- If you don't know something, offer to transfer or take a message
- Confirm important information back to the caller""",
        voice_id='EXAVITQu4vr4xnSDxMaL',
    ),

    'sales': AgentConfig(
        id='sales',
        name='Sales Agent',
        description='Professional sales agent for product inquiries',
        prompt="""You are an experienced sales representative for a software company.

Your role:
- Understand customer needs
- Present product features and benefits
- Answer questions about pricing and plans
- Build rapport and trust
- Guide customers toward a purchase decision

Guidelines:
- Be enthusiastic but not pushy
- Listen actively and ask clarifying questions
- Provide specific, relevant information
- Keep responses concise (2-3 sentences)
- Focus on value, not just features""",
        voice_id='21m00Tcm4TlvDq8ikWAM',
    ),

    'callcenter': AgentConfig(
        id='callcenter',
        name='Call Center Agent',
        description='Customer support for technical issues',
        prompt="""You are a skilled customer support agent for a tech company.

Your mission:
- Help customers troubleshoot technical issues
- Provide step-by-step guidance
- Document issues and solutions
- Escalate complex problems when needed
- Ensure customer satisfaction

Guidelines:
- Be patient and empathetic
- Use simple, non-technical language
- Confirm understanding before moving forward
- Keep responses brief and actionable
- Stay calm under pressure""",
        voice_id='pNInz6obpgDQGcFmaJgB',
    ),
}


def get_agent_config(agent_id: str) -> Optional[AgentConfig]:
    """
    Get agent configuration by ID.

    Args:
        agent_id: Agent identifier

    Returns:
        AgentConfig or None if not found

    Test Cases:
    - Should return config for valid agent_id
    - Should return None for invalid agent_id
    """
    return AGENTS.get(agent_id)


def get_all_agents() -> Dict[str, AgentConfig]:
    """
    Get all agent configurations.

    Returns:
        Dict of all agents

    Test Cases:
    - Should return all agents
    - Should return dict with 3 agents
    """
    return AGENTS
```

---

## 7. Audio Processing

### 7.1 Audio Buffering Strategy

```python
# Buffer management in ConnectionManager

# Session state includes:
session = {
    'audio_buffer': bytearray(),  # Accumulated audio chunks
    'last_chunk_time': datetime,  # For silence detection
}

# Processing triggers:
# 1. is_final flag from client (user stopped talking)
# 2. Buffer size threshold (e.g., 48000 bytes ≈ 1 second)
# 3. Silence detection (optional, for auto-processing)

# Buffer is cleared after processing
```

### 7.2 Audio Format Specifications

```
Client → Server:
  Format: WebM with Opus codec
  Sample Rate: 48kHz
  Channels: 1 (mono)
  Bitrate: 128kbps
  Chunk Size: ~250ms worth of audio

Server Processing:
  Whisper accepts WebM directly (no conversion needed)

Server → Client:
  Format: MP3
  Bitrate: 128kbps
  Streamed in chunks of 4096 bytes
```

---

## 8. WebSocket Protocol

### 8.1 Message Flow

```
Connection Phase:
  Client → Server: WebSocket connect to /ws/voice-agent/{agent_id}
  Server → Client: {type: "connection_established", session_id: "...", agent: "..."}

Recording Phase:
  Client → Server: {type: "audio_chunk", data: "base64...", is_final: false}
  Client → Server: {type: "audio_chunk", data: "base64...", is_final: false}
  ...
  Client → Server: {type: "audio_chunk", data: "", is_final: true}

Processing Phase:
  Server → Client: {type: "status_update", status: "processing"}
  Server → Client: {type: "transcription", text: "...", is_final: true}
  Server → Client: {type: "llm_response", text: "..."}
  Server → Client: {type: "status_update", status: "generating_audio"}

Playback Phase:
  Server → Client: {type: "audio_response", data: "base64_chunk_1"}
  Server → Client: {type: "audio_response", data: "base64_chunk_2"}
  ...
  Server → Client: {type: "status_update", status: "idle"}

Error Handling:
  Server → Client: {type: "error", message: "Error description"}

Disconnection:
  Client → Server: {type: "end_session"}
  Client disconnects
```

### 8.2 Status Values

```python
STATUS_VALUES = [
    "idle",              # Ready for input
    "processing",        # Transcribing audio
    "generating_audio",  # Synthesizing speech
]
```

---

## 9. Error Handling

### 9.1 Error Categories

```python
# Error handling in services

class STTError(Exception):
    """Speech-to-text errors"""
    pass

class LLMError(Exception):
    """LLM generation errors"""
    pass

class TTSError(Exception):
    """Text-to-speech errors"""
    pass

class WebSocketError(Exception):
    """WebSocket communication errors"""
    pass
```

### 9.2 Error Response Format

```python
# Error message to client
{
    "type": "error",
    "message": "User-friendly error message",
    "code": "ERROR_CODE",  # Optional
    "retryable": True  # Optional
}
```

---

## 10. TDD Implementation Plan

### 10.1 TDD Workflow

```
For each feature:

1. ✍️  Write failing test
   - Define test case
   - Assert expected behavior
   - Run test (should fail)

2. ✅  Implement minimal code to pass
   - Write simplest implementation
   - Run test (should pass)

3. ♻️  Refactor
   - Improve code quality
   - Maintain passing tests

4. 🔁  Repeat for next feature
```

### 10.2 Implementation Order

```
Phase 1: Core Infrastructure (Days 1-2)
├── 1. ConnectionManager
│   ├── Test: connect() creates session
│   ├── Test: disconnect() cleans up
│   ├── Test: send_message() routes correctly
│   └── Test: get_session() retrieves data
│
├── 2. WebSocket Message Types
│   ├── Test: MessageType enum values
│   └── Test: WebSocketMessage validation
│
└── 3. Agent Configuration
    ├── Test: get_agent_config() returns config
    ├── Test: get_agent_config() returns None for invalid
    └── Test: get_all_agents() returns all

Phase 2: Service Layer (Days 3-5)
├── 4. STTService
│   ├── Test: transcribe() with valid audio
│   ├── Test: transcribe() raises on empty audio
│   ├── Test: transcribe() handles API errors
│   └── Mock: OpenAI API responses
│
├── 5. LLMService
│   ├── Test: chat() generates response
│   ├── Test: chat() raises on empty message
│   ├── Test: chat() handles conversation history
│   ├── Test: chat() handles API errors
│   └── Mock: OpenAI API responses
│
├── 6. TTSService
│   ├── Test: synthesize_stream() yields chunks
│   ├── Test: synthesize_stream() raises on empty text
│   ├── Test: synthesize_stream() handles API errors
│   └── Mock: ElevenLabs API responses
│
└── 7. AudioProcessor
    ├── Test: convert_webm_to_mp3()
    ├── Test: detect_silence()
    └── Test: get_duration()

Phase 3: WebSocket Handler (Days 6-7)
├── 8. WebSocket Endpoint
│   ├── Test: Reject invalid agent_id
│   ├── Test: Accept valid connection
│   ├── Test: Send connection_established
│   ├── Test: Handle audio_chunk message
│   ├── Test: Handle end_session message
│   └── Test: Cleanup on disconnect
│
└── 9. Audio Chunk Handler
    ├── Test: Buffer audio chunks
    ├── Test: Process on is_final=True
    ├── Test: Process on buffer threshold
    ├── Test: Send correct status updates
    ├── Test: Update conversation history
    └── Test: Handle service errors

Phase 4: Integration Testing (Days 8-9)
├── 10. End-to-End Flow
│    ├── Test: Complete voice interaction
│    ├── Test: Multiple turns conversation
│    ├── Test: Error recovery
│    └── Test: Concurrent sessions
│
└── 11. Performance Testing
     ├── Test: Latency measurements
     ├── Test: Memory usage
     └── Test: Connection stability

Phase 5: Refinement (Day 10)
├── 12. Error Handling
│    ├── Test: All error scenarios
│    └── Test: Error messages to client
│
└── 13. Documentation
     ├── API documentation
     ├── Setup guide
     └── Testing guide
```

---

## 11. Testing Strategy

### 11.1 Pytest Configuration

```ini
# pytest.ini

[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=html
    --cov-report=term-missing
```

### 11.2 Fixtures

```python
# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)


@pytest.fixture
def mock_openai():
    """Mock OpenAI API"""
    mock = AsyncMock()

    # Mock Whisper response
    mock.audio.transcriptions.create = AsyncMock(
        return_value="Hello, this is a test transcription"
    )

    # Mock GPT response
    mock.chat.completions.create = AsyncMock(
        return_value=MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="Hello! How can I help you today?"
                    )
                )
            ]
        )
    )

    return mock


@pytest.fixture
def mock_elevenlabs():
    """Mock ElevenLabs API"""
    async def mock_stream():
        yield b"audio_chunk_1"
        yield b"audio_chunk_2"
        yield b"audio_chunk_3"

    return mock_stream


@pytest.fixture
def sample_audio():
    """Sample audio data (WebM format)"""
    # In reality, load from tests/fixtures/sample_audio.webm
    # For now, return dummy bytes
    return b"WEBM_AUDIO_DATA_HERE"


@pytest.fixture
def sample_agent_config():
    """Sample agent configuration"""
    from app.agents.config import AgentConfig

    return AgentConfig(
        id='test_agent',
        name='Test Agent',
        description='Test agent description',
        prompt='You are a test agent',
        voice_id='test_voice_id'
    )
```

### 11.3 Example Test Cases

```python
# tests/unit/test_connection_manager.py

import pytest
from app.websocket.manager import ConnectionManager
from fastapi import WebSocket
from unittest.mock import AsyncMock, MagicMock


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
    assert session_id in manager.active_connections
    assert session_id in manager.sessions
    assert manager.sessions[session_id]['agent_id'] == agent_id
    mock_websocket.accept.assert_called_once()


def test_disconnect_removes_session():
    """Test that disconnect() removes session"""

    # Arrange
    manager = ConnectionManager()
    session_id = "test_session_id"

    # Manually add session
    manager.active_connections[session_id] = MagicMock()
    manager.sessions[session_id] = {'agent_id': 'test'}

    # Act
    manager.disconnect(session_id)

    # Assert
    assert session_id not in manager.active_connections
    assert session_id not in manager.sessions


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
```

```python
# tests/unit/test_stt_service.py

import pytest
from app.services.stt_service import STTService
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_transcribe_valid_audio(mock_openai, sample_audio):
    """Test transcription with valid audio"""

    # Arrange
    with patch('app.services.stt_service.AsyncOpenAI', return_value=mock_openai):
        service = STTService()

    # Act
    result = await service.transcribe(sample_audio)

    # Assert
    assert isinstance(result, str)
    assert len(result) > 0
    mock_openai.audio.transcriptions.create.assert_called_once()


@pytest.mark.asyncio
async def test_transcribe_empty_audio_raises_error():
    """Test that empty audio raises ValueError"""

    # Arrange
    service = STTService()

    # Act & Assert
    with pytest.raises(ValueError, match="Audio bytes cannot be empty"):
        await service.transcribe(b"")
```

### 11.4 Integration Test Example

```python
# tests/integration/test_websocket_flow.py

import pytest
from fastapi.testclient import TestClient
from app.main import app


def test_websocket_connection_flow(mock_openai, mock_elevenlabs, sample_audio):
    """Test complete WebSocket interaction flow"""

    client = TestClient(app)

    with client.websocket_connect("/ws/voice-agent/receptionist") as websocket:
        # 1. Receive connection confirmation
        data = websocket.receive_json()
        assert data['type'] == 'connection_established'
        assert 'session_id' in data
        assert data['agent'] == 'Receptionist'

        # 2. Send audio chunk
        import base64
        audio_b64 = base64.b64encode(sample_audio).decode()

        websocket.send_json({
            'type': 'audio_chunk',
            'data': audio_b64,
            'is_final': True
        })

        # 3. Receive processing status
        status = websocket.receive_json()
        assert status['type'] == 'status_update'
        assert status['status'] == 'processing'

        # 4. Receive transcription
        transcription = websocket.receive_json()
        assert transcription['type'] == 'transcription'
        assert 'text' in transcription

        # 5. Receive LLM response
        llm_response = websocket.receive_json()
        assert llm_response['type'] == 'llm_response'
        assert 'text' in llm_response

        # 6. Receive audio response
        audio_response = websocket.receive_json()
        assert audio_response['type'] == 'audio_response'
        assert 'data' in audio_response

        # 7. Receive idle status
        idle_status = websocket.receive_json()
        assert idle_status['type'] == 'status_update'
        assert idle_status['status'] == 'idle'
```

---

## 12. Configuration

### 12.1 Pydantic Settings

```python
# app/config.py

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # App
    PROJECT_NAME: str = "Voice Agent API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API Keys
    OPENAI_API_KEY: str
    ELEVENLABS_API_KEY: str

    # OpenAI Settings
    OPENAI_MODEL: str = "gpt-4o-mini"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### 12.2 Environment Variables

```bash
# .env.example

# API Keys
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...

# OpenAI Settings
OPENAI_MODEL=gpt-4o-mini

# CORS
FRONTEND_URL=http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

### 12.3 FastAPI Setup

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.websocket.handlers import router as websocket_router
from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real-time voice agent with WebSocket"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    websocket_router,
    prefix="/ws",
    tags=["websocket"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
```

---

## 13. Dependencies

### 13.1 pyproject.toml

```toml
[project]
name = "voice-agent-backend"
version = "1.0.0"
description = "Voice agent backend with FastAPI and WebSocket"
requires-python = ">=3.13"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "python-multipart>=0.0.12",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.5.0",
    "openai>=1.54.0",
    "aiohttp>=3.10.0",
    "python-dotenv>=1.0.0",
    "pydub>=0.25.0",  # For audio processing
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.27.0",
    "ruff>=0.7.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py313"
```

---

## 14. Running the Backend

### 14.1 Development

```bash
# Install dependencies
uv sync

# Run development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html
```

### 14.2 Testing Workflow

```bash
# Run specific test file
pytest tests/unit/test_connection_manager.py -v

# Run specific test
pytest tests/unit/test_stt_service.py::test_transcribe_valid_audio -v

# Run with output
pytest -s

# Run integration tests only
pytest tests/integration/ -v
```

---

## 15. Implementation Checklist

### Phase 1: Setup (Day 1)
- [ ] Create directory structure
- [ ] Install dependencies (UV)
- [ ] Configure pytest
- [ ] Create .env.example
- [ ] Set up logging

### Phase 2: Core (Days 2-3)
- [ ] Implement ConnectionManager (TDD)
- [ ] Implement WebSocket types (TDD)
- [ ] Implement Agent configuration (TDD)
- [ ] Test core infrastructure

### Phase 3: Services (Days 4-6)
- [ ] Implement STTService (TDD)
- [ ] Implement LLMService (TDD)
- [ ] Implement TTSService (TDD)
- [ ] Implement AudioProcessor (TDD)
- [ ] Test all services

### Phase 4: WebSocket (Days 7-8)
- [ ] Implement WebSocket endpoint (TDD)
- [ ] Implement message handlers (TDD)
- [ ] Test WebSocket flow
- [ ] Integration testing

### Phase 5: Polish (Days 9-10)
- [ ] Error handling
- [ ] Logging
- [ ] Documentation
- [ ] Performance testing
- [ ] Final integration tests

---

## Next Steps

1. ✅ Review this backend plan
2. ⏳ Set up development environment
3. ⏳ Obtain API keys (OpenAI, ElevenLabs)
4. ⏳ Start TDD implementation with Phase 1
5. ⏳ Coordinate with frontend team on protocol

---

**End of Backend MVP Plan**
