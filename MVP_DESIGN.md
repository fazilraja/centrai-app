# Voice Agent MVP - Ultra-Detailed Design Document

> **Version:** 1.0
> **Date:** 2025-10-25
> **Status:** Design Phase - DO NOT IMPLEMENT YET

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Frontend Architecture](#3-frontend-architecture)
4. [Backend Architecture](#4-backend-architecture)
5. [WebSocket Protocol](#5-websocket-protocol)
6. [Agent Configuration System](#6-agent-configuration-system)
7. [Audio Processing Pipeline](#7-audio-processing-pipeline)
8. [State Management](#8-state-management)
9. [Error Handling Strategy](#9-error-handling-strategy)
10. [TDD Implementation Plan](#10-tdd-implementation-plan)
11. [MVP Scope & Boundaries](#11-mvp-scope--boundaries)
12. [Technical Decisions & Rationale](#12-technical-decisions--rationale)

---

## 1. Executive Summary

### 1.1 Project Overview

Building a **real-time voice agent application** that allows users to have natural conversations with AI agents specialized for different roles (receptionist, sales agent, call center).

### 1.2 Core Features (MVP)

- Voice-based conversation interface
- Three pre-configured AI agents (receptionist, sales, call center)
- Real-time audio streaming via WebSocket
- Speech-to-text (OpenAI Whisper)
- LLM conversation (OpenAI GPT)
- Text-to-speech (ElevenLabs)

### 1.3 Technology Stack

**Frontend:**
- React 19 + TypeScript
- TanStack Router (file-based routing)
- TanStack Query (server state)
- Tailwind CSS v4
- Lucide React (icons)
- Web Audio API / MediaRecorder API

**Backend:**
- FastAPI (Python 3.13+)
- WebSockets (native FastAPI)
- OpenAI API (Whisper + GPT)
- ElevenLabs API (TTS)
- Pydantic (validation)
- Pytest (TDD)

**Infrastructure (MVP):**
- No database (in-memory only)
- No authentication
- No persistence

### 1.4 Key Constraints

- **No Database:** All state is ephemeral (session-based)
- **No Auth:** Public access (for MVP)
- **Single User Session:** No concurrent user support needed
- **TDD Approach:** Test-first development for backend

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
│  (Browser - React + TanStack)                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │   Sidebar    │   │ Agent Select │   │   Voice UI   │       │
│  │  Navigation  │   │   Component  │   │  (Recording) │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
│                                                                  │
│                  WebSocket Connection                            │
│                         ↕                                       │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          │ ws://localhost:8000/ws/voice-agent
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                      BACKEND LAYER                               │
│  (FastAPI + WebSocket)                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         WebSocket Connection Manager                      │  │
│  │  - Connection lifecycle                                   │  │
│  │  - Message routing                                        │  │
│  │  - Session management                                     │  │
│  └───────────────┬──────────────────────────────────────────┘  │
│                  │                                               │
│  ┌───────────────▼──────────────────────────────────────────┐  │
│  │         Audio Processing Pipeline                         │  │
│  │                                                            │  │
│  │  Audio → Buffer → STT → LLM → TTS → Audio Response       │  │
│  └───────────────┬──────────────────────────────────────────┘  │
│                  │                                               │
└──────────────────┼───────────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────┐  ┌─────────┐  ┌─────────────┐
│ OpenAI  │  │ OpenAI  │  │ ElevenLabs  │
│ Whisper │  │   GPT   │  │     TTS     │
│  (STT)  │  │  (LLM)  │  │             │
└─────────┘  └─────────┘  └─────────────┘
```

### 2.2 Data Flow Diagram

```
User Speaks
    │
    ▼
┌─────────────────────────────────────┐
│ 1. Browser MediaRecorder captures   │
│    audio chunks (WebM Opus)         │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 2. Send via WebSocket               │
│    {type: "audio_chunk", data: ...} │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 3. Backend buffers audio chunks     │
│    until silence detected or size   │
│    threshold reached                │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 4. Send to OpenAI Whisper API       │
│    Returns: transcription text      │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 5. Send transcription to OpenAI GPT │
│    with agent-specific prompt       │
│    Returns: LLM response text       │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 6. Send text to ElevenLabs TTS      │
│    Returns: audio stream (MP3)      │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 7. Send audio chunks to client      │
│    {type: "audio_response", ...}    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│ 8. Client plays audio via           │
│    Web Audio API                    │
└─────────────────────────────────────┘
              │
              ▼
         User Hears Response
```

### 2.3 Component Interaction

```
┌──────────────────────────────────────────────────────────────┐
│                      Frontend Components                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  AppLayout                                                    │
│  ├─ Sidebar                                                   │
│  │  ├─ VoiceAgentLink (active)                              │
│  │  └─ ChatbotLink (disabled for MVP)                       │
│  │                                                            │
│  └─ MainContent                                               │
│     └─ VoiceAgentPage                                        │
│        ├─ AgentSelector                                      │
│        │  ├─ AgentCard (Receptionist)                       │
│        │  ├─ AgentCard (Sales Agent)                        │
│        │  └─ AgentCard (Call Center)                        │
│        │                                                      │
│        └─ VoiceInterface (when agent selected)               │
│           ├─ AgentHeader                                     │
│           ├─ PromptDisplay                                   │
│           ├─ VoiceRecorder                                   │
│           │  ├─ RecordButton                                │
│           │  ├─ StatusIndicator                             │
│           │  └─ AudioVisualizer (optional)                  │
│           │                                                   │
│           └─ ConversationDisplay                             │
│              ├─ TranscriptionView                            │
│              └─ ResponseView                                 │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 3. Frontend Architecture

### 3.1 File Structure

```
frontend/src/
├── routes/
│   ├── __root.tsx                    # Root layout with sidebar
│   ├── index.tsx                     # Landing/redirect page
│   ├── voice-agent/
│   │   └── index.tsx                 # Voice agent main page
│   └── chatbot/
│       └── index.tsx                 # Chatbot (future, placeholder)
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx               # Main navigation sidebar
│   │   └── AppLayout.tsx             # Overall app layout
│   │
│   ├── voice-agent/
│   │   ├── AgentSelector.tsx         # Agent selection grid
│   │   ├── AgentCard.tsx             # Individual agent card
│   │   ├── VoiceInterface.tsx        # Main voice interface
│   │   ├── AgentHeader.tsx           # Selected agent header
│   │   ├── PromptDisplay.tsx         # Shows agent prompt
│   │   ├── VoiceRecorder.tsx         # Recording controls
│   │   ├── RecordButton.tsx          # Start/stop button
│   │   ├── StatusIndicator.tsx       # Status (idle/recording/processing)
│   │   ├── AudioVisualizer.tsx       # Visual feedback (optional)
│   │   └── ConversationDisplay.tsx   # Transcription + responses
│   │
│   └── ui/
│       ├── button.tsx                # Shadcn button (to add)
│       ├── card.tsx                  # Shadcn card (to add)
│       └── badge.tsx                 # Shadcn badge (to add)
│
├── hooks/
│   ├── useVoiceAgent.ts              # Main voice agent hook
│   ├── useWebSocket.ts               # WebSocket connection hook
│   ├── useAudioRecorder.ts           # Audio recording hook
│   ├── useAudioPlayer.ts             # Audio playback hook
│   └── useAgentConfig.ts             # Agent configuration hook
│
├── lib/
│   ├── websocket/
│   │   ├── client.ts                 # WebSocket client wrapper
│   │   ├── types.ts                  # Message types
│   │   └── protocol.ts               # Protocol constants
│   │
│   ├── audio/
│   │   ├── recorder.ts               # Audio recording utilities
│   │   ├── player.ts                 # Audio playback utilities
│   │   └── formats.ts                # Audio format conversion
│   │
│   └── api/
│       ├── client.ts                 # HTTP client (if needed)
│       └── agents.ts                 # Agent config API (if needed)
│
├── types/
│   ├── agent.ts                      # Agent type definitions
│   ├── conversation.ts               # Conversation types
│   └── websocket.ts                  # WebSocket message types
│
└── store/
    └── voiceAgent.ts                 # Client state (Zustand)
```

### 3.2 Route Structure

```typescript
// Route definitions

/ (index)
  → Redirects to /voice-agent

/voice-agent
  → Main voice agent interface
  → Shows AgentSelector OR VoiceInterface based on state
  → URL params: ?agent=receptionist|sales|callcenter

/chatbot (future)
  → Placeholder for MVP
  → Shows "Coming soon" message
```

### 3.3 Component Specifications

#### 3.3.1 Sidebar Component

```typescript
// components/layout/Sidebar.tsx

interface SidebarProps {
  // No props needed
}

// Features:
// - Fixed position on left
// - Two navigation items: Voice Agent, Chatbot
// - Active state highlighting
// - Responsive (collapsible on mobile)
// - Icons from Lucide React

// State:
// - isOpen (mobile only)
// - activeRoute (from TanStack Router)
```

#### 3.3.2 AgentSelector Component

```typescript
// components/voice-agent/AgentSelector.tsx

interface Agent {
  id: 'receptionist' | 'sales' | 'callcenter';
  name: string;
  description: string;
  icon: LucideIcon;
  prompt: string;
}

interface AgentSelectorProps {
  onSelectAgent: (agentId: string) => void;
}

// Features:
// - Grid of 3 agent cards
// - Card shows: icon, name, description
// - Click to select agent
// - Visual feedback on hover

// State:
// - agents: Agent[] (static config)
```

#### 3.3.3 VoiceInterface Component

```typescript
// components/voice-agent/VoiceInterface.tsx

interface VoiceInterfaceProps {
  agent: Agent;
  onBack: () => void; // Return to agent selection
}

// Features:
// - Shows selected agent header
// - Displays agent prompt
// - Voice recorder controls
// - Conversation display (transcription + responses)
// - Back button

// State:
// - conversationHistory: Message[]
// - isRecording: boolean
// - status: 'idle' | 'recording' | 'processing' | 'speaking' | 'error'
```

#### 3.3.4 VoiceRecorder Component

```typescript
// components/voice-agent/VoiceRecorder.tsx

interface VoiceRecorderProps {
  agentId: string;
  onTranscription: (text: string) => void;
  onResponse: (text: string, audioUrl: string) => void;
  onError: (error: Error) => void;
}

// Features:
// - Large circular button (start/stop)
// - Status indicator (idle/recording/processing)
// - Audio level visualization (optional)
// - Error display

// State:
// - isRecording: boolean
// - status: RecordingStatus
// - audioLevel: number (0-100)
// - error: Error | null

// Uses hooks:
// - useWebSocket
// - useAudioRecorder
// - useAudioPlayer
```

### 3.4 Custom Hooks

#### 3.4.1 useWebSocket Hook

```typescript
// hooks/useWebSocket.ts

interface UseWebSocketOptions {
  url: string;
  onMessage: (message: WebSocketMessage) => void;
  onError: (error: Error) => void;
  autoReconnect?: boolean;
}

interface UseWebSocketReturn {
  // Connection state
  status: 'disconnected' | 'connecting' | 'connected' | 'error';
  error: Error | null;

  // Methods
  connect: () => void;
  disconnect: () => void;
  send: (message: WebSocketMessage) => void;

  // Metadata
  isConnected: boolean;
}

// Features:
// - Automatic reconnection with exponential backoff
// - Message queuing when disconnected
// - Typed message validation
// - Error handling
// - Cleanup on unmount
```

#### 3.4.2 useAudioRecorder Hook

```typescript
// hooks/useAudioRecorder.ts

interface UseAudioRecorderOptions {
  onDataAvailable: (audioBlob: Blob) => void;
  onError: (error: Error) => void;
  chunkInterval?: number; // ms, default 250ms
}

interface UseAudioRecorderReturn {
  // State
  isRecording: boolean;
  audioLevel: number; // 0-100
  error: Error | null;

  // Methods
  startRecording: () => Promise<void>;
  stopRecording: () => void;

  // Metadata
  isSupported: boolean;
  hasPermission: boolean | null;
}

// Features:
// - Uses MediaRecorder API
// - Requests microphone permission
// - Captures audio in WebM Opus format
// - Chunks audio at specified interval
// - Audio level detection via AudioContext
// - Error handling for device issues
```

#### 3.4.3 useAudioPlayer Hook

```typescript
// hooks/useAudioPlayer.ts

interface UseAudioPlayerOptions {
  onEnded: () => void;
  onError: (error: Error) => void;
  autoPlay?: boolean;
}

interface UseAudioPlayerReturn {
  // State
  isPlaying: boolean;
  duration: number;
  currentTime: number;

  // Methods
  play: (audioUrl: string | Blob) => Promise<void>;
  pause: () => void;
  stop: () => void;

  // Volume control (optional for MVP)
  volume: number;
  setVolume: (volume: number) => void;
}

// Features:
// - Uses Web Audio API or <audio> element
// - Queue support for streaming chunks
// - Playback controls
// - Error handling
```

#### 3.4.4 useVoiceAgent Hook

```typescript
// hooks/useVoiceAgent.ts

interface Message {
  id: string;
  role: 'user' | 'agent';
  text: string;
  audioUrl?: string;
  timestamp: Date;
}

interface UseVoiceAgentReturn {
  // State
  messages: Message[];
  isRecording: boolean;
  status: 'idle' | 'recording' | 'processing' | 'speaking' | 'error';
  error: Error | null;

  // Methods
  startConversation: (agentId: string) => void;
  stopConversation: () => void;
  startRecording: () => void;
  stopRecording: () => void;

  // Metadata
  currentAgent: Agent | null;
}

// Features:
// - Orchestrates WebSocket, recorder, and player
// - Manages conversation state
// - Handles message history
// - Error recovery
```

### 3.5 State Management Strategy

#### 3.5.1 State Layers

```typescript
// 1. Server State (TanStack Query)
// - Agent configurations (if fetched from API)
// - None for MVP (static config)

// 2. WebSocket State (Custom hook)
// - Connection status
// - Incoming/outgoing messages
// - Session data

// 3. Client State (Zustand store)
// - Current agent selection
// - Conversation history
// - UI state (sidebar open, etc.)

// 4. Component State (useState)
// - Form inputs
// - Local UI state
```

#### 3.5.2 Zustand Store

```typescript
// store/voiceAgent.ts

interface VoiceAgentState {
  // Selected agent
  currentAgent: Agent | null;
  setCurrentAgent: (agent: Agent | null) => void;

  // Conversation
  messages: Message[];
  addMessage: (message: Message) => void;
  clearMessages: () => void;

  // Status
  status: ConversationStatus;
  setStatus: (status: ConversationStatus) => void;

  // Error
  error: Error | null;
  setError: (error: Error | null) => void;
}

const useVoiceAgentStore = create<VoiceAgentState>((set) => ({
  currentAgent: null,
  setCurrentAgent: (agent) => set({ currentAgent: agent }),

  messages: [],
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  clearMessages: () => set({ messages: [] }),

  status: 'idle',
  setStatus: (status) => set({ status }),

  error: null,
  setError: (error) => set({ error }),
}));
```

---

## 4. Backend Architecture

### 4.1 File Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app initialization
│   ├── config.py                    # Configuration (env vars)
│   │
│   ├── websocket/
│   │   ├── __init__.py
│   │   ├── manager.py               # WebSocket connection manager
│   │   ├── handlers.py              # Message handlers
│   │   └── types.py                 # WebSocket message types
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── stt_service.py           # OpenAI Whisper integration
│   │   ├── llm_service.py           # OpenAI GPT integration
│   │   ├── tts_service.py           # ElevenLabs integration
│   │   └── audio_processor.py       # Audio format handling
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── config.py                # Agent configurations
│   │   └── prompts.py               # Agent prompt templates
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py                # Logging setup
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_websocket.py            # WebSocket tests
│   ├── test_stt_service.py          # STT service tests
│   ├── test_llm_service.py          # LLM service tests
│   ├── test_tts_service.py          # TTS service tests
│   └── test_integration.py          # End-to-end tests
│
├── pyproject.toml                   # Dependencies (UV)
├── pytest.ini                       # Pytest configuration
└── .env.example                     # Environment variables template
```

### 4.2 FastAPI Application Setup

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.websocket.handlers import router as websocket_router
from app.config import settings

app = FastAPI(
    title="Voice Agent API",
    version="1.0.0",
    description="Real-time voice agent with WebSocket"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket routes
app.include_router(websocket_router, prefix="/ws", tags=["websocket"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### 4.3 WebSocket Manager

```python
# app/websocket/manager.py

from typing import Dict
from fastapi import WebSocket
import asyncio
import uuid

class ConnectionManager:
    """Manages WebSocket connections and message routing"""

    def __init__(self):
        # Active connections: session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # Session metadata: session_id -> dict
        self.sessions: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, agent_id: str) -> str:
        """Accept connection and create session"""
        await websocket.accept()

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Store connection
        self.active_connections[session_id] = websocket

        # Initialize session
        self.sessions[session_id] = {
            'agent_id': agent_id,
            'created_at': datetime.utcnow(),
            'message_count': 0,
            'audio_buffer': bytearray(),
        }

        return session_id

    def disconnect(self, session_id: str):
        """Remove connection and cleanup session"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        if session_id in self.sessions:
            del self.sessions[session_id]

    async def send_message(self, session_id: str, message: dict):
        """Send message to specific session"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        for websocket in self.active_connections.values():
            await websocket.send_json(message)

    def get_session(self, session_id: str) -> dict | None:
        """Get session metadata"""
        return self.sessions.get(session_id)

# Singleton instance
manager = ConnectionManager()
```

### 4.4 WebSocket Handler

```python
# app/websocket/handlers.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.websocket.types import MessageType, WebSocketMessage
from app.services.stt_service import STTService
from app.services.llm_service import LLMService
from app.services.tts_service import TTSService
from app.agents.config import get_agent_config
import asyncio
import json
import base64

router = APIRouter()

@router.websocket("/voice-agent/{agent_id}")
async def voice_agent_endpoint(websocket: WebSocket, agent_id: str):
    """
    Main WebSocket endpoint for voice agent interaction

    Protocol:
    1. Client connects
    2. Backend sends connection confirmation
    3. Client sends audio chunks
    4. Backend processes and responds
    5. Client disconnects
    """

    # Initialize services
    stt_service = STTService()
    llm_service = LLMService()
    tts_service = TTSService()

    # Validate agent
    agent_config = get_agent_config(agent_id)
    if not agent_config:
        await websocket.close(code=1003, reason="Invalid agent ID")
        return

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

            # Handle message based on type
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
                await manager.send_message(session_id, {
                    'type': MessageType.ERROR,
                    'message': f'Unknown message type: {message.type}'
                })

    except WebSocketDisconnect:
        pass

    except Exception as e:
        # Send error to client
        await manager.send_message(session_id, {
            'type': MessageType.ERROR,
            'message': str(e)
        })

    finally:
        # Cleanup
        manager.disconnect(session_id)


async def handle_audio_chunk(
    session_id: str,
    message: WebSocketMessage,
    stt_service: STTService,
    llm_service: LLMService,
    tts_service: TTSService,
    agent_config: dict
):
    """Process incoming audio chunk"""

    # Get session
    session = manager.get_session(session_id)
    if not session:
        return

    # Decode audio data
    audio_data = base64.b64decode(message.data)

    # Add to buffer
    session['audio_buffer'].extend(audio_data)

    # Check if we should process (is_final flag or buffer size)
    should_process = (
        message.is_final or
        len(session['audio_buffer']) >= 48000  # ~1 second at 48kHz
    )

    if not should_process:
        return

    # Update status
    await manager.send_message(session_id, {
        'type': MessageType.STATUS_UPDATE,
        'status': 'processing'
    })

    # Get buffered audio
    audio_bytes = bytes(session['audio_buffer'])
    session['audio_buffer'].clear()

    # 1. Speech-to-Text
    transcription = await stt_service.transcribe(audio_bytes)

    # Send transcription to client
    await manager.send_message(session_id, {
        'type': MessageType.TRANSCRIPTION,
        'text': transcription,
        'is_final': True
    })

    # 2. LLM Processing
    llm_response = await llm_service.chat(
        message=transcription,
        agent_prompt=agent_config.prompt,
        conversation_history=[]  # TODO: Add history management
    )

    # Send LLM response text
    await manager.send_message(session_id, {
        'type': MessageType.LLM_RESPONSE,
        'text': llm_response
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
```

### 4.5 Service Layer

#### 4.5.1 STT Service (OpenAI Whisper)

```python
# app/services/stt_service.py

from openai import AsyncOpenAI
from app.config import settings
import io

class STTService:
    """Speech-to-Text service using OpenAI Whisper"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio to text

        Args:
            audio_bytes: Raw audio data (WebM, MP3, WAV, etc.)

        Returns:
            Transcribed text
        """

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

        return response
```

#### 4.5.2 LLM Service (OpenAI GPT)

```python
# app/services/llm_service.py

from openai import AsyncOpenAI
from app.config import settings
from typing import List, Dict

class LLMService:
    """LLM service using OpenAI GPT"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat(
        self,
        message: str,
        agent_prompt: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Get LLM response

        Args:
            message: User's message
            agent_prompt: System prompt for agent role
            conversation_history: Previous messages

        Returns:
            LLM response text
        """

        # Build messages
        messages = [
            {"role": "system", "content": agent_prompt}
        ]

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call GPT API
        response = await self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,  # e.g., "gpt-4o-mini"
            messages=messages,
            temperature=0.7,
            max_tokens=150,  # Keep responses concise for voice
        )

        return response.choices[0].message.content
```

#### 4.5.3 TTS Service (ElevenLabs)

```python
# app/services/tts_service.py

import aiohttp
from app.config import settings
from typing import AsyncIterator

class TTSService:
    """Text-to-Speech service using ElevenLabs"""

    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.api_url = "https://api.elevenlabs.io/v1"

    async def synthesize_stream(
        self,
        text: str,
        voice_id: str
    ) -> AsyncIterator[bytes]:
        """
        Convert text to speech with streaming

        Args:
            text: Text to synthesize
            voice_id: ElevenLabs voice ID

        Yields:
            Audio chunks (MP3)
        """

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

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"TTS API error: {error_text}")

                # Stream audio chunks
                async for chunk in response.content.iter_chunked(4096):
                    yield chunk
```

### 4.6 Configuration

```python
# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
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

settings = Settings()
```

---

## 5. WebSocket Protocol

### 5.1 Message Types

```python
# app/websocket/types.py

from enum import Enum
from pydantic import BaseModel
from typing import Optional

class MessageType(str, Enum):
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
    type: MessageType
    data: Optional[str] = None  # Base64 encoded for audio
    text: Optional[str] = None
    is_final: Optional[bool] = False
    status: Optional[str] = None
    message: Optional[str] = None
```

### 5.2 Protocol Flow

```
Client                                Server
  │                                     │
  ├─────── Connect ────────────────────►│
  │                                     │
  │◄──── connection_established ────────┤
  │     {type, session_id, agent}      │
  │                                     │
  ├─────── audio_chunk ────────────────►│
  │     {type, data, is_final}         │
  │                                     │
  │◄──── status_update ─────────────────┤
  │     {type, status: "processing"}   │
  │                                     │
  │◄──── transcription ─────────────────┤
  │     {type, text, is_final}         │
  │                                     │
  │◄──── llm_response ──────────────────┤
  │     {type, text}                    │
  │                                     │
  │◄──── status_update ─────────────────┤
  │     {type, status: "generating"}   │
  │                                     │
  │◄──── audio_response ────────────────┤
  │     {type, data} (chunk 1)         │
  │                                     │
  │◄──── audio_response ────────────────┤
  │     {type, data} (chunk 2)         │
  │                                     │
  │◄──── status_update ─────────────────┤
  │     {type, status: "idle"}         │
  │                                     │
  ├─────── audio_chunk ────────────────►│
  │     (next user input)               │
  │                                     │
  ├─────── end_session ────────────────►│
  │                                     │
  ├─────── Disconnect ─────────────────►│
  │                                     │
```

### 5.3 Message Examples

```json
// Client → Server: Audio chunk
{
  "type": "audio_chunk",
  "data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEA...",
  "is_final": false
}

// Server → Client: Connection established
{
  "type": "connection_established",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent": "Receptionist"
}

// Server → Client: Transcription
{
  "type": "transcription",
  "text": "Hello, I'd like to schedule an appointment",
  "is_final": true
}

// Server → Client: LLM response
{
  "type": "llm_response",
  "text": "Of course! I'd be happy to help you schedule an appointment. What date works best for you?"
}

// Server → Client: Audio response chunk
{
  "type": "audio_response",
  "data": "SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2Z..."
}

// Server → Client: Status update
{
  "type": "status_update",
  "status": "processing"  // or "generating_audio", "idle", "speaking"
}

// Server → Client: Error
{
  "type": "error",
  "message": "Failed to transcribe audio"
}
```

### 5.4 Error Handling

```typescript
// Frontend error handling

interface ErrorRecoveryStrategy {
  // Retry with exponential backoff
  maxRetries: 3;
  baseDelay: 1000; // ms

  // Automatic reconnection
  reconnect: boolean;
  reconnectDelay: 2000; // ms

  // User notification
  showError: boolean;
  errorMessage: string;
}

// Common error scenarios:
// 1. WebSocket connection failed → Auto-reconnect
// 2. Audio device not available → Show permission dialog
// 3. STT API error → Retry with same audio
// 4. LLM API error → Retry with exponential backoff
// 5. TTS API error → Show error, allow user retry
```

---

## 6. Agent Configuration System

### 6.1 Agent Definitions

```python
# app/agents/config.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class AgentConfig:
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
        voice_id='EXAVITQu4vr4xnSDxMaL',  # ElevenLabs voice
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
        voice_id='21m00Tcm4TlvDq8ikWAM',  # Different voice
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
        voice_id='pNInz6obpgDQGcFmaJgB',  # Another voice
    ),
}

def get_agent_config(agent_id: str) -> AgentConfig | None:
    """Get agent configuration by ID"""
    return AGENTS.get(agent_id)

def get_all_agents() -> Dict[str, AgentConfig]:
    """Get all agent configurations"""
    return AGENTS
```

### 6.2 Frontend Agent Interface

```typescript
// types/agent.ts

export interface Agent {
  id: 'receptionist' | 'sales' | 'callcenter';
  name: string;
  description: string;
  prompt: string;
  icon: string; // Lucide icon name
  color: string; // Tailwind color class
}

// lib/agents.ts

import { Phone, TrendingUp, Headphones } from 'lucide-react';

export const AGENTS: Record<string, Agent> = {
  receptionist: {
    id: 'receptionist',
    name: 'Receptionist',
    description: 'Friendly receptionist for appointment scheduling and general inquiries',
    prompt: 'Professional medical clinic receptionist focused on scheduling and patient care',
    icon: 'Phone',
    color: 'blue',
  },

  sales: {
    id: 'sales',
    name: 'Sales Agent',
    description: 'Expert sales representative for product demos and closing deals',
    prompt: 'Experienced sales professional guiding customers through product selection',
    icon: 'TrendingUp',
    color: 'green',
  },

  callcenter: {
    id: 'callcenter',
    name: 'Call Center',
    description: 'Technical support specialist for troubleshooting and issue resolution',
    prompt: 'Patient customer support agent helping with technical problems',
    icon: 'Headphones',
    color: 'purple',
  },
};

export const getAgent = (id: string): Agent | undefined => {
  return AGENTS[id];
};

export const getAllAgents = (): Agent[] => {
  return Object.values(AGENTS);
};
```

---

## 7. Audio Processing Pipeline

### 7.1 Client-Side Audio Capture

```typescript
// lib/audio/recorder.ts

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private stream: MediaStream | null = null;

  async start(onDataAvailable: (blob: Blob) => void): Promise<void> {
    // Request microphone access
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 48000,
      }
    });

    // Setup MediaRecorder
    this.mediaRecorder = new MediaRecorder(this.stream, {
      mimeType: 'audio/webm;codecs=opus',
      audioBitsPerSecond: 128000,
    });

    // Setup audio analysis for visualization
    this.audioContext = new AudioContext();
    this.analyser = this.audioContext.createAnalyser();
    const source = this.audioContext.createMediaStreamSource(this.stream);
    source.connect(this.analyser);

    // Send chunks every 250ms
    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        onDataAvailable(event.data);
      }
    };

    this.mediaRecorder.start(250); // 250ms chunks
  }

  stop(): void {
    if (this.mediaRecorder) {
      this.mediaRecorder.stop();
    }

    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }

    if (this.audioContext) {
      this.audioContext.close();
    }
  }

  getAudioLevel(): number {
    if (!this.analyser) return 0;

    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(dataArray);

    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    return average / 255; // Normalize to 0-1
  }
}
```

### 7.2 Server-Side Audio Processing

```python
# app/services/audio_processor.py

import io
from pydub import AudioSegment

class AudioProcessor:
    """Audio format conversion and processing"""

    @staticmethod
    def convert_webm_to_mp3(webm_bytes: bytes) -> bytes:
        """Convert WebM to MP3"""

        # Load WebM
        audio = AudioSegment.from_file(
            io.BytesIO(webm_bytes),
            format="webm"
        )

        # Export as MP3
        output = io.BytesIO()
        audio.export(output, format="mp3", bitrate="128k")

        return output.getvalue()

    @staticmethod
    def detect_silence(audio_bytes: bytes, threshold: int = -40) -> bool:
        """Detect if audio is mostly silence"""

        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

        # Check if audio is below threshold
        return audio.dBFS < threshold

    @staticmethod
    def get_duration(audio_bytes: bytes) -> float:
        """Get audio duration in seconds"""

        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        return len(audio) / 1000.0  # Convert ms to seconds
```

### 7.3 Latency Optimization

```python
# Optimization strategies

# 1. Parallel Processing
async def process_audio_parallel(audio_bytes: bytes):
    """Process STT and prepare LLM context in parallel"""

    async with asyncio.TaskGroup() as tg:
        # Start STT
        stt_task = tg.create_task(stt_service.transcribe(audio_bytes))

        # Preload agent context
        context_task = tg.create_task(load_conversation_context())

    transcription = await stt_task
    context = await context_task

    # Now run LLM with both ready
    response = await llm_service.chat(transcription, context)

# 2. Streaming TTS
async def stream_tts_immediately(text: str):
    """Start streaming TTS as soon as LLM starts responding"""

    async for text_chunk in llm_service.stream_chat(...):
        # Stream to TTS immediately without waiting for full response
        async for audio_chunk in tts_service.synthesize_stream(text_chunk):
            yield audio_chunk

# 3. Prefetching
# Cache common responses for instant playback
PREFETCH_PHRASES = [
    "Hello, how can I help you?",
    "Could you please repeat that?",
    "Let me check that for you.",
]

# Pre-generate TTS for common phrases on startup
```

---

## 8. State Management

### 8.1 State Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend State                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  URL State (TanStack Router)                                │
│  ├─ /voice-agent?agent=receptionist                        │
│  └─ Synced with browser history                             │
│                                                              │
│  Zustand Store                                               │
│  ├─ currentAgent: Agent | null                              │
│  ├─ messages: Message[]                                     │
│  ├─ status: ConversationStatus                              │
│  └─ error: Error | null                                     │
│                                                              │
│  WebSocket Hook State                                        │
│  ├─ connectionStatus: ConnectionStatus                      │
│  ├─ sessionId: string | null                                │
│  └─ messageQueue: WebSocketMessage[]                        │
│                                                              │
│  Audio Hook State                                            │
│  ├─ isRecording: boolean                                    │
│  ├─ audioLevel: number                                      │
│  ├─ isPlaying: boolean                                      │
│  └─ playbackQueue: Blob[]                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 State Transitions

```typescript
// Conversation status state machine

type ConversationStatus =
  | 'idle'           // No active conversation
  | 'connecting'     // Establishing WebSocket
  | 'connected'      // WebSocket established
  | 'recording'      // User is speaking
  | 'processing'     // Backend processing audio
  | 'responding'     // Agent is speaking
  | 'error'          // Error state
  | 'disconnected';  // Connection lost

// Valid transitions:
const VALID_TRANSITIONS: Record<ConversationStatus, ConversationStatus[]> = {
  idle: ['connecting'],
  connecting: ['connected', 'error', 'disconnected'],
  connected: ['recording', 'disconnected', 'error'],
  recording: ['processing', 'connected', 'error'],
  processing: ['responding', 'error', 'connected'],
  responding: ['connected', 'error', 'disconnected'],
  error: ['idle', 'connecting'],
  disconnected: ['idle', 'connecting'],
};
```

---

## 9. Error Handling Strategy

### 9.1 Error Categories

```typescript
// types/errors.ts

export enum ErrorCategory {
  // Client-side errors
  MICROPHONE_PERMISSION_DENIED = 'microphone_permission_denied',
  MICROPHONE_NOT_AVAILABLE = 'microphone_not_available',
  AUDIO_PLAYBACK_FAILED = 'audio_playback_failed',

  // Network errors
  WEBSOCKET_CONNECTION_FAILED = 'websocket_connection_failed',
  WEBSOCKET_DISCONNECTED = 'websocket_disconnected',
  NETWORK_TIMEOUT = 'network_timeout',

  // Server errors
  STT_API_ERROR = 'stt_api_error',
  LLM_API_ERROR = 'llm_api_error',
  TTS_API_ERROR = 'tts_api_error',
  INVALID_AUDIO_FORMAT = 'invalid_audio_format',

  // Application errors
  INVALID_AGENT_ID = 'invalid_agent_id',
  SESSION_EXPIRED = 'session_expired',
  UNKNOWN_ERROR = 'unknown_error',
}

export interface VoiceAgentError {
  category: ErrorCategory;
  message: string;
  retryable: boolean;
  userMessage: string;
}
```

### 9.2 Error Recovery

```typescript
// Error recovery strategies

const ERROR_RECOVERY: Record<ErrorCategory, {
  retryable: boolean;
  autoRetry: boolean;
  maxRetries: number;
  userAction?: string;
}> = {
  [ErrorCategory.MICROPHONE_PERMISSION_DENIED]: {
    retryable: false,
    autoRetry: false,
    maxRetries: 0,
    userAction: 'Please allow microphone access in your browser settings',
  },

  [ErrorCategory.WEBSOCKET_DISCONNECTED]: {
    retryable: true,
    autoRetry: true,
    maxRetries: 3,
    userAction: 'Reconnecting...',
  },

  [ErrorCategory.STT_API_ERROR]: {
    retryable: true,
    autoRetry: true,
    maxRetries: 2,
    userAction: 'Failed to transcribe audio, retrying...',
  },

  // ... etc
};
```

### 9.3 User-Facing Error Messages

```typescript
// User-friendly error messages

const ERROR_MESSAGES: Record<ErrorCategory, string> = {
  [ErrorCategory.MICROPHONE_PERMISSION_DENIED]:
    'Microphone access is required. Please enable it in your browser settings.',

  [ErrorCategory.WEBSOCKET_CONNECTION_FAILED]:
    'Could not connect to voice agent. Please check your internet connection.',

  [ErrorCategory.STT_API_ERROR]:
    'Sorry, I couldn\'t understand that. Could you try again?',

  [ErrorCategory.LLM_API_ERROR]:
    'Sorry, I\'m having trouble processing your request. Please try again.',

  [ErrorCategory.TTS_API_ERROR]:
    'Could not generate voice response. Showing text response instead.',

  // ... etc
};
```

---

## 10. TDD Implementation Plan

### 10.1 Test-Driven Development Workflow

```
For each feature:

1. ✍️  Write failing test
2. ✅  Implement minimal code to pass
3. ♻️  Refactor for quality
4. 🔁  Repeat
```

### 10.2 Backend Test Structure

```python
# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def mock_openai():
    """Mock OpenAI API responses"""
    # Mock implementation
    pass

@pytest.fixture
def mock_elevenlabs():
    """Mock ElevenLabs API responses"""
    # Mock implementation
    pass

@pytest.fixture
def sample_audio():
    """Sample audio data for testing"""
    # Return sample WebM bytes
    pass
```

```python
# tests/test_websocket.py

import pytest
from fastapi.websockets import WebSocket

@pytest.mark.asyncio
async def test_websocket_connection(client):
    """Test WebSocket connection establishment"""

    with client.websocket_connect("/ws/voice-agent/receptionist") as websocket:
        # Should receive connection confirmation
        data = websocket.receive_json()

        assert data['type'] == 'connection_established'
        assert 'session_id' in data
        assert data['agent'] == 'Receptionist'

@pytest.mark.asyncio
async def test_audio_chunk_processing(client, mock_openai, mock_elevenlabs, sample_audio):
    """Test audio chunk processing flow"""

    with client.websocket_connect("/ws/voice-agent/receptionist") as websocket:
        # Skip connection message
        websocket.receive_json()

        # Send audio chunk
        websocket.send_json({
            'type': 'audio_chunk',
            'data': sample_audio,
            'is_final': True
        })

        # Should receive status update
        status = websocket.receive_json()
        assert status['type'] == 'status_update'
        assert status['status'] == 'processing'

        # Should receive transcription
        transcription = websocket.receive_json()
        assert transcription['type'] == 'transcription'
        assert 'text' in transcription

        # Should receive LLM response
        llm_response = websocket.receive_json()
        assert llm_response['type'] == 'llm_response'
        assert 'text' in llm_response

        # Should receive audio response chunks
        audio_response = websocket.receive_json()
        assert audio_response['type'] == 'audio_response'
        assert 'data' in audio_response

@pytest.mark.asyncio
async def test_invalid_agent_id(client):
    """Test connection with invalid agent ID"""

    with pytest.raises(Exception):  # Should close connection
        with client.websocket_connect("/ws/voice-agent/invalid"):
            pass
```

```python
# tests/test_stt_service.py

import pytest
from app.services.stt_service import STTService

@pytest.mark.asyncio
async def test_transcribe_audio(mock_openai, sample_audio):
    """Test audio transcription"""

    service = STTService()
    result = await service.transcribe(sample_audio)

    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_transcribe_empty_audio():
    """Test transcription with empty audio"""

    service = STTService()

    with pytest.raises(ValueError):
        await service.transcribe(b'')
```

```python
# tests/test_llm_service.py

import pytest
from app.services.llm_service import LLMService

@pytest.mark.asyncio
async def test_chat_response(mock_openai):
    """Test LLM chat response"""

    service = LLMService()
    response = await service.chat(
        message="Hello",
        agent_prompt="You are a receptionist",
        conversation_history=[]
    )

    assert isinstance(response, str)
    assert len(response) > 0

@pytest.mark.asyncio
async def test_chat_with_history(mock_openai):
    """Test LLM with conversation history"""

    service = LLMService()
    history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

    response = await service.chat(
        message="How are you?",
        agent_prompt="You are friendly",
        conversation_history=history
    )

    assert isinstance(response, str)
```

### 10.3 Frontend Test Structure

```typescript
// __tests__/components/VoiceRecorder.test.tsx

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { VoiceRecorder } from '@/components/voice-agent/VoiceRecorder';

describe('VoiceRecorder', () => {
  it('renders start button initially', () => {
    render(<VoiceRecorder agentId="receptionist" />);

    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('Start Talking');
  });

  it('requests microphone permission on start', async () => {
    const mockGetUserMedia = jest.fn().mockResolvedValue({});
    global.navigator.mediaDevices = {
      getUserMedia: mockGetUserMedia
    };

    render(<VoiceRecorder agentId="receptionist" />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(mockGetUserMedia).toHaveBeenCalledWith({
        audio: expect.any(Object)
      });
    });
  });

  it('shows recording status when active', async () => {
    // ... test implementation
  });

  it('sends audio chunks via WebSocket', async () => {
    // ... test implementation
  });
});
```

### 10.4 Implementation Order (TDD)

```
Backend (Week 1-2):
1. ✅ WebSocket connection manager
   - Test: Connection establishment
   - Test: Message routing
   - Test: Session cleanup

2. ✅ STT Service
   - Test: Transcribe valid audio
   - Test: Handle invalid audio
   - Test: API error handling

3. ✅ LLM Service
   - Test: Generate response
   - Test: With conversation history
   - Test: API error handling

4. ✅ TTS Service
   - Test: Synthesize speech
   - Test: Streaming chunks
   - Test: API error handling

5. ✅ Audio processor
   - Test: Format conversion
   - Test: Silence detection
   - Test: Duration calculation

6. ✅ Agent configuration
   - Test: Load agent config
   - Test: Invalid agent ID
   - Test: All agents present

7. ✅ Integration tests
   - Test: Full voice flow
   - Test: Error recovery
   - Test: Concurrent sessions

Frontend (Week 2-3):
1. ✅ WebSocket hook
   - Test: Connection lifecycle
   - Test: Message sending
   - Test: Auto-reconnect

2. ✅ Audio recorder hook
   - Test: Start/stop recording
   - Test: Permission handling
   - Test: Chunk generation

3. ✅ Audio player hook
   - Test: Playback control
   - Test: Queue management
   - Test: Error handling

4. ✅ Voice agent hook
   - Test: Session management
   - Test: Message history
   - Test: Status transitions

5. ✅ Components
   - Test: Rendering
   - Test: User interactions
   - Test: Error states

6. ✅ Integration tests
   - Test: E2E voice flow
   - Test: Agent selection
   - Test: Conversation flow
```

---

## 11. MVP Scope & Boundaries

### 11.1 In-Scope (Must Have)

✅ **Core Features:**
- Voice recording (push-to-talk)
- Real-time transcription
- AI agent responses
- Voice playback
- Three agent types (receptionist, sales, call center)
- Agent selection interface
- Basic error handling

✅ **Technical:**
- WebSocket communication
- OpenAI Whisper (STT)
- OpenAI GPT (LLM)
- ElevenLabs (TTS)
- Responsive UI
- Status indicators

### 11.2 Out-of-Scope (Future)

❌ **Features:**
- Chatbot mode (text-only)
- Conversation history/persistence
- User authentication
- Multiple concurrent conversations
- Conversation editing
- Audio file upload
- Custom agent creation
- Multi-language support
- Voice interruption
- Background noise filtering (beyond browser defaults)

❌ **Technical:**
- Database integration
- User accounts
- Session persistence
- Analytics/tracking
- Advanced audio processing
- Video support
- Screen sharing
- File uploads

### 11.3 Assumptions

1. **Single user** - No multi-user concurrency needed
2. **Ephemeral sessions** - No data persistence required
3. **Modern browsers** - Chrome, Firefox, Safari, Edge (latest versions)
4. **Good network** - Assumes stable internet connection
5. **English only** - Single language support for MVP
6. **Desktop first** - Mobile as secondary consideration

### 11.4 Success Criteria

MVP is successful if:
1. ✅ User can select an agent
2. ✅ User can record voice input
3. ✅ System transcribes voice accurately
4. ✅ Agent responds contextually
5. ✅ Response plays back as voice
6. ✅ Conversation flows naturally
7. ✅ Errors are handled gracefully
8. ✅ UI is intuitive and responsive

---

## 12. Technical Decisions & Rationale

### 12.1 Why WebSocket over HTTP?

**Decision:** Use WebSocket for real-time bidirectional communication

**Rationale:**
- Low latency for voice interaction
- Persistent connection reduces overhead
- Enables streaming audio in both directions
- Natural fit for conversational interface
- Simpler state management than polling

**Alternative Considered:** HTTP with polling
- ❌ Higher latency
- ❌ More complex client code
- ❌ Increased server load
- ❌ Not suitable for audio streaming

### 12.2 Why OpenAI Whisper for STT?

**Decision:** Use OpenAI Whisper API for speech-to-text

**Rationale:**
- High accuracy across accents
- Fast processing (<2s typical)
- Simple API integration
- Handles various audio formats
- Good value for quality

**Alternative Considered:** Google Speech-to-Text
- ✅ Also good quality
- ❌ More complex setup
- ❌ Different pricing model

### 12.3 Why ElevenLabs for TTS?

**Decision:** Use ElevenLabs for text-to-speech

**Rationale:**
- Natural-sounding voices
- Streaming support for low latency
- Good voice variety
- Excellent quality
- Simple API

**Alternative Considered:** Google Text-to-Speech
- ✅ Reliable and fast
- ❌ Less natural sounding
- ❌ Limited voice options

### 12.4 Why No Database for MVP?

**Decision:** Keep all state in-memory, no persistence

**Rationale:**
- Faster development
- Simpler testing
- No migration complexity
- Easier to iterate
- Sufficient for proof-of-concept

**When to Add:**
- User accounts needed
- Conversation history required
- Analytics/reporting needed
- Production deployment

### 12.5 Why TDD Approach?

**Decision:** Test-Driven Development for backend

**Rationale:**
- Ensures code quality
- Catches bugs early
- Documents expected behavior
- Easier refactoring
- Better architecture

**Trade-off:**
- Slower initial development
- ✅ Faster debugging
- ✅ More maintainable code

### 12.6 Why Zustand over Redux?

**Decision:** Use Zustand for client state management

**Rationale:**
- Simpler API
- Less boilerplate
- Better TypeScript support
- Smaller bundle size
- Easier to learn

**Alternative:** TanStack Query only
- ❌ Not designed for UI state
- ❌ Would need more useState

---

## Next Steps

### Before Implementation:

1. **Review this design document** ✅
2. **Confirm technical approach** ⏳
3. **Set up development environment** ⏳
4. **Obtain API keys** ⏳
   - OpenAI API key
   - ElevenLabs API key

### Implementation Phase 1: Backend Foundation (TDD)

1. Set up FastAPI project with UV
2. Configure environment variables
3. Implement WebSocket connection manager (TDD)
4. Implement STT service (TDD)
5. Implement LLM service (TDD)
6. Implement TTS service (TDD)
7. Implement agent configuration
8. Integration testing

### Implementation Phase 2: Frontend Core

1. Set up Shadcn UI components
2. Implement routing structure
3. Create layout components
4. Implement agent selection
5. Implement WebSocket hook
6. Implement audio recorder hook
7. Implement audio player hook
8. Create voice interface components

### Implementation Phase 3: Integration & Testing

1. Connect frontend to backend
2. End-to-end testing
3. Error handling refinement
4. UI polish
5. Performance optimization
6. Documentation

---

**Document End**

