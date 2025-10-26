export type { WebSocketMessage, MessageType } from '@/types/websocket';

export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

export interface WebSocketClientOptions {
  url: string;
  onMessage: (message: import('@/types/websocket').WebSocketMessage) => void;
  onError?: (error: Error) => void;
  autoReconnect?: boolean;
  reconnectDelay?: number;
}