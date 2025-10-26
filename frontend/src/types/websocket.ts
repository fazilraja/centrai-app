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