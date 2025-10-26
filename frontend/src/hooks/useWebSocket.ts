import { useRef, useState, useCallback } from 'react';
import type { WebSocketMessage } from '@/types/websocket';
import { WS_ENDPOINTS } from '@/lib/websocket/protocol';

interface UseWebSocketOptions {
  agentId: string;
  onMessage: (message: WebSocketMessage) => void;
  onError?: (error: Error) => void;
  autoReconnect?: boolean;
  reconnectDelay?: number;
  wsUrl?: string;
}

export function useWebSocket({
  agentId,
  onMessage,
  onError,
  autoReconnect = true,
  reconnectDelay = 2000,
  wsUrl = 'ws://localhost:8000',
}: UseWebSocketOptions) {
  const [status, setStatus] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Clear any existing connection and timeouts
  const cleanup = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onerror = null;
      wsRef.current.onclose = null;
      wsRef.current.close();
      wsRef.current = null;
    }

    setStatus('disconnected');
  }, []);

  // Manual connection control
  const connect = useCallback(() => {
    // Clean up existing connection
    cleanup();

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setStatus('connecting');

    try {
      const ws = new WebSocket(`${wsUrl}${WS_ENDPOINTS.VOICE_AGENT(agentId)}`);

      ws.onopen = () => {
        setStatus('connected');
        wsRef.current = ws;
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          onMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = () => {
        setStatus('error');
        onError?.(new Error('WebSocket error'));
      };

      ws.onclose = () => {
        setStatus('disconnected');
        wsRef.current = null;

        // Auto-reconnect logic
        if (autoReconnect) {
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectDelay);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      setStatus('error');
      onError?.(error as Error);
    }
  }, [agentId, onMessage, onError, autoReconnect, reconnectDelay, wsUrl, cleanup]);

  // Manual disconnection
  const disconnect = useCallback(() => {
    cleanup();
  }, [cleanup]);

  // Send message
  const send = useCallback((message: Partial<WebSocketMessage>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }, []);

  return {
    status,
    connect,
    disconnect,
    send,
    isConnected: status === 'connected',
  };
}