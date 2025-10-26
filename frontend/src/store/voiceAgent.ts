import { create } from 'zustand';
import type { Agent } from '@/types/agent';
import type { Message, ConversationStatus } from '@/types/conversation';

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

  // Connection state
  isConnected: boolean;
  setIsConnected: (isConnected: boolean) => void;

  // Recording state
  isRecording: boolean;
  setIsRecording: (isRecording: boolean) => void;

  // Reset all state
  reset: () => void;
}

export const useVoiceAgentStore = create<VoiceAgentState>((set, get) => ({
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

  // Connection
  isConnected: false,
  setIsConnected: (isConnected) => set({ isConnected }),

  // Recording
  isRecording: false,
  setIsRecording: (isRecording) => set({ isRecording }),

  // Reset
  reset: () => set({
    currentAgent: null,
    messages: [],
    status: 'idle',
    error: null,
    isConnected: false,
    isRecording: false,
  }),
}));