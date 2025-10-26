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