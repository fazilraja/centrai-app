import type { WebSocketMessage } from '@/types/websocket';
import type { ConnectionStatus, WebSocketClientOptions } from './types';

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  private options: WebSocketClientOptions;
  private reconnectTimeoutRef: NodeJS.Timeout | null = null;

  constructor(options: WebSocketClientOptions) {
    this.url = options.url;
    this.options = options;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        resolve();
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.options.onMessage(message);
        } catch (error) {
          console.error('Failed to parse message:', error);
        }
      };

      this.ws.onerror = () => {
        const error = new Error('WebSocket error');
        this.options.onError?.(error);
        reject(error);
      };

      this.ws.onclose = () => {
        this.handleReconnect();
      };
    });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts && this.options.autoReconnect) {
      this.reconnectAttempts++;
      const delay = this.options.reconnectDelay
        ? this.options.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)
        : this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

      this.reconnectTimeoutRef = setTimeout(() => {
        this.connect().catch(console.error);
      }, delay);
    }
  }

  send(message: Partial<WebSocketMessage>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }

  disconnect(): void {
    if (this.reconnectTimeoutRef) {
      clearTimeout(this.reconnectTimeoutRef);
    }
    this.ws?.close();
    this.ws = null;
  }

  getConnectionStatus(): ConnectionStatus {
    if (!this.ws) return 'disconnected';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED: return 'disconnected';
      default: return 'disconnected';
    }
  }
}