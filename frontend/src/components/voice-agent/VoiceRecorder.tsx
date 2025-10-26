import { useState, useCallback } from 'react';
import { RecordButton } from './RecordButton';
import { StatusIndicator } from './StatusIndicator';
import { AudioVisualizer } from './AudioVisualizer';
import { useVoiceAgentStore } from '@/store/voiceAgent';
import { useAudioRecorder } from '@/hooks/useAudioRecorder';
import { useVoiceAgent } from '@/hooks/useVoiceAgent';

interface VoiceRecorderProps {
  agentId: string;
}

export function VoiceRecorder({ agentId }: VoiceRecorderProps) {
  const [hasStartedRecording, setHasStartedRecording] = useState(false);
  const status = useVoiceAgentStore((state) => state.status);
  const { sendAudioChunk, startConnection, stopConnection } = useVoiceAgent(agentId);

  const { isRecording, audioLevel, startRecording, stopRecording } = useAudioRecorder({
    onDataAvailable: (blob) => {
      // Send audio chunk via WebSocket
      sendAudioChunk(blob, false);
    },
    onError: (error) => {
      console.error('Audio recording error:', error);
    },
  });

  const handleToggleRecording = useCallback(() => {
    // Start connection on first recording attempt
    if (!hasStartedRecording) {
      startConnection();
      setHasStartedRecording(true);
    }

    if (isRecording) {
      stopRecording();
      // Send final chunk
      sendAudioChunk(new Blob(), true);
    } else {
      startRecording();
    }
  }, [hasStartedRecording, isRecording, startRecording, stopRecording, sendAudioChunk, stopRecording]);

  const isDisabled = status === 'processing' || status === 'responding';

  return (
    <div className="flex flex-col items-center gap-4">
      <AudioVisualizer level={audioLevel} isActive={isRecording} />
      <RecordButton
        isRecording={isRecording}
        onClick={handleToggleRecording}
        disabled={isDisabled}
      />
      <StatusIndicator status={status} />
    </div>
  );
}