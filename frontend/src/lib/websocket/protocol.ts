// WebSocket protocol constants and utilities
export const WS_ENDPOINTS = {
  VOICE_AGENT: (agentId: string) => `/ws/voice-agent/${agentId}`,
} as const;

export const CHUNK_INTERVAL = 250; // ms
export const MAX_RECONNECT_ATTEMPTS = 5;
export const BASE_RECONNECT_DELAY = 2000; // ms