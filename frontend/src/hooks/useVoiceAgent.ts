import { useCallback, useRef } from 'react';
import { useWebSocket } from './useWebSocket';
import { useAudioPlayer } from './useAudioPlayer';
import { useVoiceAgentStore } from '@/store/voiceAgent';
import type { WebSocketMessage } from '@/types/websocket';
import { MessageType } from '@/types/websocket';
import { base64ToBlob } from '@/lib/audio/utils';

export function useVoiceAgent(agentId: string) {
  const {
    messages,
    status,
    error,
    addMessage,
    setStatus,
    setError,
    clearMessages,
    setIsConnected,
  } = useVoiceAgentStore();

  const { playChunk } = useAudioPlayer({
    onEnded: () => setStatus('connected'),
    onError: (error) => setError(error),
  });

  const handleWebSocketMessage = useCallback(
    (message: WebSocketMessage) => {
      switch (message.type) {
        case MessageType.CONNECTION_ESTABLISHED:
          setStatus('connected');
          setIsConnected(true);
          break;

        case MessageType.TRANSCRIPTION:
          if (message.text) {
            addMessage({
              id: crypto.randomUUID(),
              role: 'user',
              text: message.text,
              timestamp: new Date(),
            });
          }
          break;

        case MessageType.LLM_RESPONSE:
          if (message.text) {
            addMessage({
              id: crypto.randomUUID(),
              role: 'agent',
              text: message.text,
              timestamp: new Date(),
            });
          }
          break;

        case MessageType.AUDIO_RESPONSE:
          if (message.data) {
            setStatus('responding');
            try {
              // Convert base64 to Blob
              const audioBlob = base64ToBlob(message.data, 'audio/mpeg');
              playChunk(audioBlob);
            } catch (error) {
              console.error('Failed to process audio response:', error);
              setError(error as Error);
            }
          }
          break;

        case MessageType.STATUS_UPDATE:
          if (message.status) {
            setStatus(message.status as any);
          }
          break;

        case MessageType.ERROR:
          setError(new Error(message.message || 'Unknown error'));
          break;

        default:
          console.warn('Unknown message type:', message.type);
      }
    },
    [addMessage, setStatus, setError, playChunk, setIsConnected]
  );

  const { status: wsStatus, connect, disconnect, send, isConnected } = useWebSocket({
    agentId,
    onMessage: handleWebSocketMessage,
    onError: setError,
    wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:8000',
  });

  // Update connection status based on WebSocket status
  const updateConnectionStatus = useCallback(() => {
    setIsConnected(wsStatus === 'connected');
  }, [wsStatus, setIsConnected]);

  // Handle audio chunk sending
  const sendAudioChunk = useCallback(
    (blob: Blob, isFinal: boolean = false) => {
      // Convert blob to base64 and send via WebSocket
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result?.toString().split(',')[1];
        if (base64) {
          send({
            type: MessageType.AUDIO_CHUNK,
            data: base64,
            is_final: isFinal,
          });
        }
      };
      reader.readAsDataURL(blob);
    },
    [send]
  );

  // End session
  const endSession = useCallback(() => {
    send({
      type: MessageType.END_SESSION,
    });
  }, [send]);

  // Manual connection management
  const startConnection = useCallback(() => {
    clearMessages();
    connect();
  }, [clearMessages, connect]);

  const stopConnection = useCallback(() => {
    endSession();
    disconnect();
  }, [endSession, disconnect]);

  return {
    messages,
    status,
    error,
    isConnected,
    sendAudioChunk,
    endSession,
    startConnection,
    stopConnection,
    updateConnectionStatus,
  };
}