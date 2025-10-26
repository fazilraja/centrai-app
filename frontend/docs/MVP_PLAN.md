# Voice Agent Frontend - MVP Implementation Plan

> **Version:** 1.0
> **Date:** 2025-10-25
> **Status:** Design Phase - Ready for Implementation

---

## Table of Contents

1. [Overview](#1-overview)
2. [Frontend Architecture](#2-frontend-architecture)
3. [File Structure](#3-file-structure)
4. [Routing Structure](#4-routing-structure)
5. [Component Specifications](#5-component-specifications)
6. [Custom Hooks](#6-custom-hooks)
7. [State Management](#7-state-management)
8. [WebSocket Integration](#8-websocket-integration)
9. [Audio Processing](#9-audio-processing)
10. [Error Handling](#10-error-handling)
11. [UI Components](#11-ui-components)
12. [Implementation Phases](#12-implementation-phases)

---

## 1. Overview

### 1.1 Project Summary

Building the frontend for a **real-time voice agent application** that allows users to have natural voice conversations with AI agents specialized for different roles.

### 1.2 Technology Stack

- **React 19** with TypeScript
- **TanStack Router** (file-based routing)
- **TanStack Query** (server state management)
- **Zustand** (client state management)
- **Tailwind CSS v4** (styling)
- **Shadcn/UI** (component library)
- **Lucide React** (icons)
- **Web Audio API** / **MediaRecorder API** (audio handling)

### 1.3 Current Setup Status

Based on exploration, the frontend has:
- ✅ TanStack Router configured with file-based routing
- ✅ TanStack Query with basic setup
- ✅ Tailwind CSS v4 configured
- ✅ TypeScript with strict mode
- ✅ Vite build tool
- ❌ Shadcn/UI (not yet installed)
- ❌ WebSocket client (needs implementation)
- ❌ Audio handling (needs implementation)
- ❌ State management (needs Zustand)

---

## 2. Frontend Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         BROWSER                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  UI Layer (React Components)                                    │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │   Sidebar    │   │ Agent Select │   │   Voice UI   │       │
│  │  Navigation  │   │   Component  │   │  (Recording) │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
│                                                                  │
│  State Management Layer                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │
│  │   Zustand    │   │   TanStack   │   │    Router    │       │
│  │    Store     │   │     Query    │   │     State    │       │
│  └──────────────┘   └──────────────┘   └──────────────┘       │
│                                                                  │
│  Communication Layer                                            │
│  ┌──────────────┐   ┌──────────────┐                           │
│  │  WebSocket   │   │  Audio API   │                           │
│  │    Client    │   │   Manager    │                           │
│  └──────────────┘   └──────────────┘                           │
│                                                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          │ WebSocket + Audio Stream
                          │
                  ┌───────▼────────┐
                  │  Backend API   │
                  │   (FastAPI)    │
                  └────────────────┘
```

### 2.2 Component Hierarchy

```
App
└─ TanStackRouterProvider
   └─ TanStackQueryProvider
      └─ Root Layout (__root.tsx)
         ├─ Sidebar
         │  ├─ VoiceAgentLink (active)
         │  └─ ChatbotLink (disabled for MVP)
         │
         └─ MainContent (Outlet)
            │
            ├─ / (index.tsx)
            │  └─ Redirect to /voice-agent
            │
            ├─ /voice-agent
            │  └─ VoiceAgentPage
            │     ├─ AgentSelector (initial state)
            │     │  ├─ AgentCard (Receptionist)
            │     │  ├─ AgentCard (Sales Agent)
            │     │  └─ AgentCard (Call Center)
            │     │
            │     └─ VoiceInterface (after selection)
            │        ├─ AgentHeader
            │        ├─ PromptDisplay
            │        ├─ VoiceRecorder
            │        │  ├─ RecordButton
            │        │  ├─ StatusIndicator
            │        │  └─ AudioVisualizer
            │        └─ ConversationDisplay
            │
            └─ /chatbot
               └─ PlaceholderPage ("Coming Soon")
```

### 2.3 Data Flow

```
User Action (Click "Start Talking")
         │
         ▼
VoiceRecorder Component
         │
         ├─ useWebSocket.connect()
         │  └─ Establishes WebSocket connection
         │
         ├─ useAudioRecorder.startRecording()
         │  └─ Requests mic permission
         │  └─ Starts MediaRecorder
         │
         ▼
Audio Chunks Generated (every 250ms)
         │
         ├─ Convert to Base64
         ├─ Send via WebSocket
         │
         ▼
WebSocket Message Received
         │
         ├─ type: "transcription"
         │  └─ Update conversation display
         │
         ├─ type: "llm_response"
         │  └─ Update conversation display
         │
         ├─ type: "audio_response"
         │  └─ useAudioPlayer.play()
         │
         └─ type: "status_update"
            └─ Update status indicator
```

---

## 3. File Structure

### 3.1 Complete Directory Structure

```
frontend/src/
├── routes/
│   ├── __root.tsx                    # Root layout with sidebar
│   ├── index.tsx                     # Landing/redirect to /voice-agent
│   ├── voice-agent/
│   │   └── index.tsx                 # Voice agent main page
│   └── chatbot/
│       └── index.tsx                 # Placeholder (future)
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx               # Main navigation sidebar
│   │   └── AppLayout.tsx             # Overall app layout wrapper
│   │
│   ├── voice-agent/
│   │   ├── AgentSelector.tsx         # Agent selection grid
│   │   ├── AgentCard.tsx             # Individual agent card
│   │   ├── VoiceInterface.tsx        # Main voice interface container
│   │   ├── AgentHeader.tsx           # Selected agent header
│   │   ├── PromptDisplay.tsx         # Shows agent system prompt
│   │   ├── VoiceRecorder.tsx         # Recording controls orchestrator
│   │   ├── RecordButton.tsx          # Start/stop button UI
│   │   ├── StatusIndicator.tsx       # Status display (idle/recording/etc)
│   │   ├── AudioVisualizer.tsx       # Visual feedback (optional)
│   │   └── ConversationDisplay.tsx   # Transcription + responses list
│   │
│   └── ui/                           # Shadcn components
│       ├── button.tsx
│       ├── card.tsx
│       ├── badge.tsx
│       ├── scroll-area.tsx
│       └── separator.tsx
│
├── hooks/
│   ├── useVoiceAgent.ts              # Main orchestrator hook
│   ├── useWebSocket.ts               # WebSocket connection hook
│   ├── useAudioRecorder.ts           # Audio recording hook
│   ├── useAudioPlayer.ts             # Audio playback hook
│   └── useAgentConfig.ts             # Agent configuration hook
│
├── lib/
│   ├── websocket/
│   │   ├── client.ts                 # WebSocket client class
│   │   ├── types.ts                  # WebSocket message types
│   │   └── protocol.ts               # Protocol constants
│   │
│   ├── audio/
│   │   ├── recorder.ts               # AudioRecorder class
│   │   ├── player.ts                 # AudioPlayer class
│   │   └── utils.ts                  # Audio utilities
│   │
│   ├── agents.ts                     # Agent configurations
│   └── utils.ts                      # General utilities (cn, etc.)
│
├── types/
│   ├── agent.ts                      # Agent type definitions
│   ├── conversation.ts               # Message/conversation types
│   └── websocket.ts                  # WebSocket message types
│
├── store/
│   └── voiceAgent.ts                 # Zustand store for voice agent
│
└── styles.css                        # Global styles + Tailwind
```

### 3.2 New Files to Create

```
✅ Already Exists:
- src/routes/__root.tsx
- src/routes/index.tsx
- src/components/Header.tsx
- src/lib/utils.ts
- src/styles.css

❌ Need to Create:
- src/routes/voice-agent/index.tsx
- src/routes/chatbot/index.tsx
- All components in src/components/layout/
- All components in src/components/voice-agent/
- All hooks in src/hooks/
- All lib files in src/lib/websocket/
- All lib files in src/lib/audio/
- All type definitions in src/types/
- src/store/voiceAgent.ts
- Shadcn UI components in src/components/ui/
```

---

## 4. Routing Structure

### 4.1 Route Definitions

```typescript
// TanStack Router file-based routes

/ (index.tsx)
  Purpose: Landing page
  Action: Redirects to /voice-agent
  Component: Redirect component

/voice-agent
  Purpose: Main voice agent interface
  Component: VoiceAgentPage
  State: Shows AgentSelector OR VoiceInterface
  URL Params: ?agent=receptionist|sales|callcenter

/chatbot
  Purpose: Text chatbot (future)
  Component: PlaceholderPage
  Content: "Coming Soon" message
```

### 4.2 Route Implementation

```typescript
// src/routes/index.tsx

import { createFileRoute, Navigate } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  component: IndexPage,
});

function IndexPage() {
  return <Navigate to="/voice-agent" />;
}
```

```typescript
// src/routes/voice-agent/index.tsx

import { createFileRoute } from '@tanstack/react-router';
import { VoiceAgentPage } from '@/components/voice-agent/VoiceAgentPage';

type VoiceAgentSearch = {
  agent?: 'receptionist' | 'sales' | 'callcenter';
};

export const Route = createFileRoute('/voice-agent/')({
  component: VoiceAgentPage,
  validateSearch: (search: Record<string, unknown>): VoiceAgentSearch => {
    return {
      agent: search.agent as VoiceAgentSearch['agent'],
    };
  },
});

function VoiceAgentPage() {
  const { agent } = Route.useSearch();
  const navigate = Route.useNavigate();

  // Show AgentSelector if no agent selected
  if (!agent) {
    return <AgentSelector onSelectAgent={(id) => navigate({ search: { agent: id } })} />;
  }

  // Show VoiceInterface if agent selected
  return (
    <VoiceInterface
      agentId={agent}
      onBack={() => navigate({ search: {} })}
    />
  );
}
```

---

## 5. Component Specifications

### 5.1 Layout Components

#### Sidebar Component

```typescript
// src/components/layout/Sidebar.tsx

import { Link } from '@tanstack/react-router';
import { Mic, MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r bg-background">
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold">Voice Agent</h1>
      </div>

      <nav className="space-y-1 p-4">
        <Link
          to="/voice-agent"
          className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-accent"
          activeProps={{ className: 'bg-accent' }}
        >
          <Mic className="h-5 w-5" />
          <span>Voice Agent</span>
        </Link>

        <Link
          to="/chatbot"
          className="flex items-center gap-3 rounded-lg px-3 py-2 opacity-50 cursor-not-allowed"
        >
          <MessageSquare className="h-5 w-5" />
          <span>Chatbot</span>
          <span className="ml-auto text-xs text-muted-foreground">Soon</span>
        </Link>
      </nav>
    </aside>
  );
}
```

### 5.2 Voice Agent Components

#### AgentSelector Component

```typescript
// src/components/voice-agent/AgentSelector.tsx

import { getAllAgents } from '@/lib/agents';
import { AgentCard } from './AgentCard';

interface AgentSelectorProps {
  onSelectAgent: (agentId: string) => void;
}

export function AgentSelector({ onSelectAgent }: AgentSelectorProps) {
  const agents = getAllAgents();

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold">Choose Your Agent</h1>
        <p className="mt-2 text-muted-foreground">
          Select an AI agent to start your conversation
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onClick={() => onSelectAgent(agent.id)}
          />
        ))}
      </div>
    </div>
  );
}
```

#### AgentCard Component

```typescript
// src/components/voice-agent/AgentCard.tsx

import { Card } from '@/components/ui/card';
import { Agent } from '@/types/agent';
import * as Icons from 'lucide-react';

interface AgentCardProps {
  agent: Agent;
  onClick: () => void;
}

export function AgentCard({ agent, onClick }: AgentCardProps) {
  const Icon = Icons[agent.icon as keyof typeof Icons];

  return (
    <Card
      className="cursor-pointer transition-all hover:shadow-lg hover:scale-105"
      onClick={onClick}
    >
      <div className="p-6">
        <div className={`inline-flex rounded-lg bg-${agent.color}-100 p-3`}>
          <Icon className={`h-6 w-6 text-${agent.color}-600`} />
        </div>

        <h3 className="mt-4 text-xl font-semibold">{agent.name}</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          {agent.description}
        </p>
      </div>
    </Card>
  );
}
```

#### VoiceInterface Component

```typescript
// src/components/voice-agent/VoiceInterface.tsx

import { useVoiceAgent } from '@/hooks/useVoiceAgent';
import { getAgent } from '@/lib/agents';
import { AgentHeader } from './AgentHeader';
import { PromptDisplay } from './PromptDisplay';
import { VoiceRecorder } from './VoiceRecorder';
import { ConversationDisplay } from './ConversationDisplay';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

interface VoiceInterfaceProps {
  agentId: string;
  onBack: () => void;
}

export function VoiceInterface({ agentId, onBack }: VoiceInterfaceProps) {
  const agent = getAgent(agentId);
  const { messages, status, error } = useVoiceAgent(agentId);

  if (!agent) {
    return <div>Agent not found</div>;
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <div className="border-b bg-background">
        <div className="container mx-auto flex items-center gap-4 py-4">
          <Button variant="ghost" size="sm" onClick={onBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <AgentHeader agent={agent} />
        </div>
      </div>

      {/* Prompt Display */}
      <div className="border-b bg-muted/50">
        <div className="container mx-auto py-4">
          <PromptDisplay prompt={agent.prompt} />
        </div>
      </div>

      {/* Conversation */}
      <div className="flex-1 overflow-hidden">
        <ConversationDisplay messages={messages} />
      </div>

      {/* Voice Recorder */}
      <div className="border-t bg-background">
        <div className="container mx-auto py-6">
          <VoiceRecorder agentId={agentId} />
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="border-t bg-destructive/10 p-4 text-center text-sm text-destructive">
          {error.message}
        </div>
      )}
    </div>
  );
}
```

#### VoiceRecorder Component

```typescript
// src/components/voice-agent/VoiceRecorder.tsx

import { RecordButton } from './RecordButton';
import { StatusIndicator } from './StatusIndicator';
import { AudioVisualizer } from './AudioVisualizer';
import { useVoiceAgentStore } from '@/store/voiceAgent';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { useWebSocket } from '@/hooks/useWebSocket';

interface VoiceRecorderProps {
  agentId: string;
}

export function VoiceRecorder({ agentId }: VoiceRecorderProps) {
  const status = useVoiceAgentStore((state) => state.status);
  const { send } = useWebSocket();
  const { isRecording, audioLevel, startRecording, stopRecording } = useAudioRecorder({
    onDataAvailable: (blob) => {
      // Convert blob to base64 and send via WebSocket
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result?.toString().split(',')[1];
        send({
          type: 'audio_chunk',
          data: base64,
          is_final: false,
        });
      };
      reader.readAsDataURL(blob);
    },
  });

  const handleToggleRecording = () => {
    if (isRecording) {
      stopRecording();
      // Send final chunk
      send({ type: 'audio_chunk', data: '', is_final: true });
    } else {
      startRecording();
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <AudioVisualizer level={audioLevel} isActive={isRecording} />
      <RecordButton
        isRecording={isRecording}
        onClick={handleToggleRecording}
        disabled={status === 'processing' || status === 'responding'}
      />
      <StatusIndicator status={status} />
    </div>
  );
}
```

#### RecordButton Component

```typescript
// src/components/voice-agent/RecordButton.tsx

import { Button } from '@/components/ui/button';
import { Mic, Square } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RecordButtonProps {
  isRecording: boolean;
  onClick: () => void;
  disabled?: boolean;
}

export function RecordButton({ isRecording, onClick, disabled }: RecordButtonProps) {
  return (
    <Button
      size="lg"
      variant={isRecording ? 'destructive' : 'default'}
      className={cn(
        'h-20 w-20 rounded-full',
        isRecording && 'animate-pulse'
      )}
      onClick={onClick}
      disabled={disabled}
    >
      {isRecording ? (
        <Square className="h-8 w-8" />
      ) : (
        <Mic className="h-8 w-8" />
      )}
    </Button>
  );
}
```

#### StatusIndicator Component

```typescript
// src/components/voice-agent/StatusIndicator.tsx

import { Badge } from '@/components/ui/badge';
import { ConversationStatus } from '@/types/conversation';

interface StatusIndicatorProps {
  status: ConversationStatus;
}

const STATUS_CONFIG: Record<ConversationStatus, { label: string; variant: string }> = {
  idle: { label: 'Ready', variant: 'secondary' },
  connecting: { label: 'Connecting...', variant: 'secondary' },
  connected: { label: 'Connected', variant: 'secondary' },
  recording: { label: 'Listening...', variant: 'default' },
  processing: { label: 'Thinking...', variant: 'secondary' },
  responding: { label: 'Speaking...', variant: 'default' },
  error: { label: 'Error', variant: 'destructive' },
  disconnected: { label: 'Disconnected', variant: 'destructive' },
};

export function StatusIndicator({ status }: StatusIndicatorProps) {
  const config = STATUS_CONFIG[status];

  return (
    <Badge variant={config.variant as any}>
      {config.label}
    </Badge>
  );
}
```

#### ConversationDisplay Component

```typescript
// src/components/voice-agent/ConversationDisplay.tsx

import { ScrollArea } from '@/components/ui/scroll-area';
import { Message } from '@/types/conversation';
import { cn } from '@/lib/utils';

interface ConversationDisplayProps {
  messages: Message[];
}

export function ConversationDisplay({ messages }: ConversationDisplayProps) {
  return (
    <ScrollArea className="h-full">
      <div className="container mx-auto space-y-4 py-6">
        {messages.length === 0 ? (
          <div className="text-center text-muted-foreground">
            <p>Start talking to begin the conversation</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                'flex',
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={cn(
                  'max-w-[80%] rounded-lg p-4',
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                )}
              >
                <p className="text-sm">{message.text}</p>
                <span className="mt-1 block text-xs opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </ScrollArea>
  );
}
```

---

## 6. Custom Hooks

### 6.1 useWebSocket Hook

```typescript
// src/hooks/useWebSocket.ts

import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketMessage, MessageType } from '@/types/websocket';

interface UseWebSocketOptions {
  url: string;
  onMessage: (message: WebSocketMessage) => void;
  onError?: (error: Error) => void;
  autoReconnect?: boolean;
  reconnectDelay?: number;
}

type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

export function useWebSocket({
  url,
  onMessage,
  onError,
  autoReconnect = true,
  reconnectDelay = 2000,
}: UseWebSocketOptions) {
  const [status, setStatus] = useState<ConnectionStatus>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttemptsRef = useRef(0);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus('connecting');

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        setStatus('connected');
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          onMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (event) => {
        setStatus('error');
        const error = new Error('WebSocket error');
        onError?.(error);
      };

      ws.onclose = () => {
        setStatus('disconnected');
        wsRef.current = null;

        // Auto-reconnect with exponential backoff
        if (autoReconnect) {
          const delay = reconnectDelay * Math.pow(2, reconnectAttemptsRef.current);
          const maxDelay = 30000; // 30 seconds max

          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++;
            connect();
          }, Math.min(delay, maxDelay));
        }
      };

      wsRef.current = ws;
    } catch (error) {
      setStatus('error');
      onError?.(error as Error);
    }
  }, [url, onMessage, onError, autoReconnect, reconnectDelay]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setStatus('disconnected');
  }, []);

  const send = useCallback((message: Partial<WebSocketMessage>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }, []);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    status,
    connect,
    disconnect,
    send,
    isConnected: status === 'connected',
  };
}
```

### 6.2 useAudioRecorder Hook

```typescript
// src/hooks/useAudioRecorder.ts

import { useState, useRef, useCallback } from 'react';

interface UseAudioRecorderOptions {
  onDataAvailable: (blob: Blob) => void;
  onError?: (error: Error) => void;
  chunkInterval?: number; // ms
}

export function useAudioRecorder({
  onDataAvailable,
  onError,
  chunkInterval = 250,
}: UseAudioRecorderOptions) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const animationFrameRef = useRef<number>();

  const startRecording = useCallback(async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 48000,
        },
      });

      setHasPermission(true);
      streamRef.current = stream;

      // Setup audio analysis for visualization
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);

      analyser.fftSize = 256;
      source.connect(analyser);

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      // Update audio level for visualization
      const updateLevel = () => {
        if (!analyserRef.current) return;

        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);

        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(average / 255);

        animationFrameRef.current = requestAnimationFrame(updateLevel);
      };
      updateLevel();

      // Setup MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 128000,
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          onDataAvailable(event.data);
        }
      };

      mediaRecorder.onerror = (event) => {
        onError?.(new Error('MediaRecorder error'));
      };

      mediaRecorder.start(chunkInterval);
      mediaRecorderRef.current = mediaRecorder;
      setIsRecording(true);
    } catch (error) {
      setHasPermission(false);
      onError?.(error as Error);
    }
  }, [onDataAvailable, onError, chunkInterval]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    setIsRecording(false);
    setAudioLevel(0);
  }, []);

  return {
    isRecording,
    audioLevel,
    hasPermission,
    startRecording,
    stopRecording,
    isSupported: !!navigator.mediaDevices?.getUserMedia,
  };
}
```

### 6.3 useAudioPlayer Hook

```typescript
// src/hooks/useAudioPlayer.ts

import { useState, useRef, useCallback } from 'react';

interface UseAudioPlayerOptions {
  onEnded?: () => void;
  onError?: (error: Error) => void;
  autoPlay?: boolean;
}

export function useAudioPlayer({
  onEnded,
  onError,
  autoPlay = true,
}: UseAudioPlayerOptions = {}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const queueRef = useRef<Blob[]>([]);

  const play = useCallback(
    async (audio: string | Blob) => {
      try {
        // Create audio element if it doesn't exist
        if (!audioRef.current) {
          audioRef.current = new Audio();

          audioRef.current.onended = () => {
            setIsPlaying(false);
            onEnded?.();
          };

          audioRef.current.onerror = () => {
            onError?.(new Error('Audio playback error'));
          };

          audioRef.current.ontimeupdate = () => {
            setCurrentTime(audioRef.current?.currentTime || 0);
          };

          audioRef.current.onloadedmetadata = () => {
            setDuration(audioRef.current?.duration || 0);
          };
        }

        // Set audio source
        if (typeof audio === 'string') {
          audioRef.current.src = audio;
        } else {
          audioRef.current.src = URL.createObjectURL(audio);
        }

        // Play audio
        if (autoPlay) {
          await audioRef.current.play();
          setIsPlaying(true);
        }
      } catch (error) {
        onError?.(error as Error);
      }
    },
    [autoPlay, onEnded, onError]
  );

  const pause = useCallback(() => {
    audioRef.current?.pause();
    setIsPlaying(false);
  }, []);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlaying(false);
  }, []);

  const playChunk = useCallback(
    (chunk: Blob) => {
      queueRef.current.push(chunk);

      // If not currently playing, start playing the queue
      if (!isPlaying) {
        play(chunk);
      }
    },
    [isPlaying, play]
  );

  return {
    isPlaying,
    duration,
    currentTime,
    play,
    pause,
    stop,
    playChunk,
  };
}
```

### 6.4 useVoiceAgent Hook (Orchestrator)

```typescript
// src/hooks/useVoiceAgent.ts

import { useEffect, useCallback } from 'react';
import { useWebSocket } from './useWebSocket';
import { useAudioPlayer } from './useAudioPlayer';
import { useVoiceAgentStore } from '@/store/voiceAgent';
import { WebSocketMessage } from '@/types/websocket';

export function useVoiceAgent(agentId: string) {
  const {
    messages,
    status,
    error,
    addMessage,
    setStatus,
    setError,
    clearMessages,
  } = useVoiceAgentStore();

  const { playChunk } = useAudioPlayer({
    onEnded: () => setStatus('connected'),
    onError: (error) => setError(error),
  });

  const handleWebSocketMessage = useCallback(
    (message: WebSocketMessage) => {
      switch (message.type) {
        case 'connection_established':
          setStatus('connected');
          break;

        case 'transcription':
          if (message.text) {
            addMessage({
              id: crypto.randomUUID(),
              role: 'user',
              text: message.text,
              timestamp: new Date(),
            });
          }
          break;

        case 'llm_response':
          if (message.text) {
            addMessage({
              id: crypto.randomUUID(),
              role: 'agent',
              text: message.text,
              timestamp: new Date(),
            });
          }
          break;

        case 'audio_response':
          if (message.data) {
            setStatus('responding');
            // Convert base64 to Blob
            const audioBlob = base64ToBlob(message.data, 'audio/mpeg');
            playChunk(audioBlob);
          }
          break;

        case 'status_update':
          if (message.status) {
            setStatus(message.status as any);
          }
          break;

        case 'error':
          setError(new Error(message.message || 'Unknown error'));
          break;
      }
    },
    [addMessage, setStatus, setError, playChunk]
  );

  const { status: wsStatus, connect, disconnect, send } = useWebSocket({
    url: `ws://localhost:8000/ws/voice-agent/${agentId}`,
    onMessage: handleWebSocketMessage,
    onError: setError,
  });

  // Connect on mount
  useEffect(() => {
    connect();
    return () => {
      disconnect();
      clearMessages();
    };
  }, [connect, disconnect, clearMessages]);

  return {
    messages,
    status,
    error,
    isConnected: wsStatus === 'connected',
  };
}

// Utility function
function base64ToBlob(base64: string, mimeType: string): Blob {
  const byteCharacters = atob(base64);
  const byteArrays = [];

  for (let i = 0; i < byteCharacters.length; i++) {
    byteArrays.push(byteCharacters.charCodeAt(i));
  }

  return new Blob([new Uint8Array(byteArrays)], { type: mimeType });
}
```

---

## 7. State Management

### 7.1 Zustand Store

```typescript
// src/store/voiceAgent.ts

import { create } from 'zustand';
import { Agent } from '@/types/agent';
import { Message, ConversationStatus } from '@/types/conversation';

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

export const useVoiceAgentStore = create<VoiceAgentState>((set) => ({
  // Agent
  currentAgent: null,
  setCurrentAgent: (agent) => set({ currentAgent: agent }),

  // Messages
  messages: [],
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  clearMessages: () => set({ messages: [] }),

  // Status
  status: 'idle',
  setStatus: (status) => set({ status }),

  // Error
  error: null,
  setError: (error) => set({ error }),
}));
```

### 7.2 Type Definitions

```typescript
// src/types/conversation.ts

export type ConversationStatus =
  | 'idle'
  | 'connecting'
  | 'connected'
  | 'recording'
  | 'processing'
  | 'responding'
  | 'error'
  | 'disconnected';

export interface Message {
  id: string;
  role: 'user' | 'agent';
  text: string;
  audioUrl?: string;
  timestamp: Date;
}
```

```typescript
// src/types/agent.ts

export interface Agent {
  id: 'receptionist' | 'sales' | 'callcenter';
  name: string;
  description: string;
  prompt: string;
  icon: string; // Lucide icon name
  color: string; // Tailwind color
}
```

```typescript
// src/types/websocket.ts

export enum MessageType {
  // Client → Server
  AUDIO_CHUNK = 'audio_chunk',
  END_SESSION = 'end_session',

  // Server → Client
  CONNECTION_ESTABLISHED = 'connection_established',
  TRANSCRIPTION = 'transcription',
  LLM_RESPONSE = 'llm_response',
  AUDIO_RESPONSE = 'audio_response',
  STATUS_UPDATE = 'status_update',
  ERROR = 'error',
}

export interface WebSocketMessage {
  type: MessageType;
  data?: string; // Base64 encoded audio
  text?: string;
  is_final?: boolean;
  status?: string;
  message?: string;
  session_id?: string;
  agent?: string;
}
```

---

## 8. WebSocket Integration

### 8.1 WebSocket Client

```typescript
// src/lib/websocket/client.ts

import { WebSocketMessage } from '@/types/websocket';

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;

  constructor(url: string) {
    this.url = url;
  }

  connect(
    onMessage: (message: WebSocketMessage) => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          onMessage(message);
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      this.ws.onerror = (event) => {
        const error = new Error('WebSocket error');
        onError?.(error);
        reject(error);
      };

      this.ws.onclose = () => {
        this.handleReconnect(onMessage, onError);
      };
    });
  }

  private handleReconnect(
    onMessage: (message: WebSocketMessage) => void,
    onError?: (error: Error) => void
  ) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

      setTimeout(() => {
        this.connect(onMessage, onError);
      }, delay);
    }
  }

  send(message: Partial<WebSocketMessage>) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  disconnect() {
    this.ws?.close();
    this.ws = null;
  }
}
```

---

## 9. Audio Processing

### 9.1 Audio Recorder Class

```typescript
// src/lib/audio/recorder.ts

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private stream: MediaStream | null = null;

  async start(
    onDataAvailable: (blob: Blob) => void,
    chunkInterval: number = 250
  ): Promise<void> {
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: 48000,
      },
    });

    this.audioContext = new AudioContext();
    this.analyser = this.audioContext.createAnalyser();
    const source = this.audioContext.createMediaStreamSource(this.stream);
    source.connect(this.analyser);

    this.mediaRecorder = new MediaRecorder(this.stream, {
      mimeType: 'audio/webm;codecs=opus',
      audioBitsPerSecond: 128000,
    });

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        onDataAvailable(event.data);
      }
    };

    this.mediaRecorder.start(chunkInterval);
  }

  stop(): void {
    this.mediaRecorder?.stop();
    this.stream?.getTracks().forEach((track) => track.stop());
    this.audioContext?.close();
  }

  getAudioLevel(): number {
    if (!this.analyser) return 0;

    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(dataArray);

    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    return average / 255;
  }
}
```

### 9.2 Audio Player Class

```typescript
// src/lib/audio/player.ts

export class AudioPlayer {
  private audio: HTMLAudioElement;
  private queue: Blob[] = [];
  private isPlaying = false;

  constructor() {
    this.audio = new Audio();
  }

  async play(source: string | Blob): Promise<void> {
    if (typeof source === 'string') {
      this.audio.src = source;
    } else {
      this.audio.src = URL.createObjectURL(source);
    }

    await this.audio.play();
    this.isPlaying = true;
  }

  pause(): void {
    this.audio.pause();
    this.isPlaying = false;
  }

  stop(): void {
    this.audio.pause();
    this.audio.currentTime = 0;
    this.isPlaying = false;
  }

  async playQueue(chunks: Blob[]): Promise<void> {
    for (const chunk of chunks) {
      await this.play(chunk);
      await new Promise((resolve) => {
        this.audio.onended = resolve;
      });
    }
  }
}
```

---

## 10. Error Handling

### 10.1 Error Types

```typescript
// src/types/errors.ts

export enum ErrorCategory {
  MICROPHONE_PERMISSION_DENIED = 'microphone_permission_denied',
  MICROPHONE_NOT_AVAILABLE = 'microphone_not_available',
  WEBSOCKET_CONNECTION_FAILED = 'websocket_connection_failed',
  WEBSOCKET_DISCONNECTED = 'websocket_disconnected',
  AUDIO_PLAYBACK_FAILED = 'audio_playback_failed',
  UNKNOWN_ERROR = 'unknown_error',
}

export interface VoiceAgentError {
  category: ErrorCategory;
  message: string;
  retryable: boolean;
  userMessage: string;
}
```

### 10.2 Error Messages

```typescript
// src/lib/errors.ts

import { ErrorCategory, VoiceAgentError } from '@/types/errors';

export const ERROR_MESSAGES: Record<ErrorCategory, string> = {
  [ErrorCategory.MICROPHONE_PERMISSION_DENIED]:
    'Microphone access is required. Please enable it in your browser settings.',
  [ErrorCategory.MICROPHONE_NOT_AVAILABLE]:
    'No microphone found. Please connect a microphone and try again.',
  [ErrorCategory.WEBSOCKET_CONNECTION_FAILED]:
    'Could not connect to voice agent. Please check your internet connection.',
  [ErrorCategory.WEBSOCKET_DISCONNECTED]:
    'Connection lost. Attempting to reconnect...',
  [ErrorCategory.AUDIO_PLAYBACK_FAILED]:
    'Could not play audio response. Please check your audio output.',
  [ErrorCategory.UNKNOWN_ERROR]:
    'An unexpected error occurred. Please try again.',
};

export function createError(
  category: ErrorCategory,
  originalError?: Error
): VoiceAgentError {
  return {
    category,
    message: originalError?.message || ERROR_MESSAGES[category],
    retryable: [
      ErrorCategory.WEBSOCKET_CONNECTION_FAILED,
      ErrorCategory.WEBSOCKET_DISCONNECTED,
      ErrorCategory.AUDIO_PLAYBACK_FAILED,
    ].includes(category),
    userMessage: ERROR_MESSAGES[category],
  };
}
```

---

## 11. UI Components

### 11.1 Shadcn Setup

Install Shadcn components:

```bash
npx shadcn@latest init
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add badge
npx shadcn@latest add scroll-area
npx shadcn@latest add separator
```

### 11.2 Agent Configuration

```typescript
// src/lib/agents.ts

import { Agent } from '@/types/agent';

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

## 12. Implementation Phases

### Phase 1: Setup & Dependencies (Day 1)

**Tasks:**
1. ✅ Install dependencies
   ```bash
   npm install zustand
   npm install @tanstack/react-router@latest
   npm install @tanstack/react-query@latest
   npx shadcn@latest init
   npx shadcn@latest add button card badge scroll-area separator
   ```

2. ✅ Create directory structure
   - Create all directories in src/
   - Set up empty files

3. ✅ Configure TypeScript
   - Add path aliases if needed
   - Configure strict mode

### Phase 2: Core Infrastructure (Day 2-3)

**Tasks:**
1. ✅ Implement type definitions
   - src/types/agent.ts
   - src/types/conversation.ts
   - src/types/websocket.ts

2. ✅ Implement lib utilities
   - src/lib/agents.ts
   - src/lib/websocket/client.ts
   - src/lib/audio/recorder.ts
   - src/lib/audio/player.ts

3. ✅ Create Zustand store
   - src/store/voiceAgent.ts

### Phase 3: Custom Hooks (Day 4-5)

**Tasks:**
1. ✅ Implement useWebSocket
2. ✅ Implement useAudioRecorder
3. ✅ Implement useAudioPlayer
4. ✅ Implement useVoiceAgent (orchestrator)
5. ✅ Test hooks in isolation

### Phase 4: Layout Components (Day 6)

**Tasks:**
1. ✅ Update __root.tsx with Sidebar
2. ✅ Create Sidebar component
3. ✅ Create AppLayout component
4. ✅ Test navigation

### Phase 5: Voice Agent Components (Day 7-9)

**Tasks:**
1. ✅ Create AgentSelector
2. ✅ Create AgentCard
3. ✅ Create VoiceInterface
4. ✅ Create AgentHeader
5. ✅ Create PromptDisplay
6. ✅ Create VoiceRecorder
7. ✅ Create RecordButton
8. ✅ Create StatusIndicator
9. ✅ Create AudioVisualizer (optional)
10. ✅ Create ConversationDisplay

### Phase 6: Routes (Day 10)

**Tasks:**
1. ✅ Update routes/index.tsx (redirect)
2. ✅ Create routes/voice-agent/index.tsx
3. ✅ Create routes/chatbot/index.tsx (placeholder)
4. ✅ Test routing

### Phase 7: Integration & Testing (Day 11-12)

**Tasks:**
1. ✅ Connect components to hooks
2. ✅ Test WebSocket communication with backend
3. ✅ Test audio recording
4. ✅ Test audio playback
5. ✅ Test error handling
6. ✅ Test state management

### Phase 8: Polish & Optimization (Day 13-14)

**Tasks:**
1. ✅ Add loading states
2. ✅ Add error boundaries
3. ✅ Optimize re-renders
4. ✅ Add accessibility
5. ✅ Mobile responsive design
6. ✅ Visual polish

---

## Dependencies to Install

```json
{
  "dependencies": {
    "zustand": "^4.5.0"
  }
}
```

---

## Environment Variables

```env
# .env.local
VITE_WS_URL=ws://localhost:8000
```

---

## Next Steps

1. ✅ Review this frontend plan
2. ⏳ Install dependencies
3. ⏳ Create directory structure
4. ⏳ Start Phase 1 implementation
5. ⏳ Backend team to provide WebSocket endpoint

---

**End of Frontend MVP Plan**
