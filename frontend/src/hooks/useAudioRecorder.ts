import { useState, useRef, useCallback } from 'react';
import { AudioRecorder } from '@/lib/audio/recorder';
import { CHUNK_INTERVAL } from '@/lib/websocket/protocol';

interface UseAudioRecorderOptions {
  onDataAvailable: (blob: Blob) => void;
  onError?: (error: Error) => void;
  chunkInterval?: number; // ms
}

export function useAudioRecorder({
  onDataAvailable,
  onError,
  chunkInterval = CHUNK_INTERVAL,
}: UseAudioRecorderOptions) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  const recorderRef = useRef<AudioRecorder | null>(null);
  const animationFrameRef = useRef<number>();

  const updateAudioLevel = useCallback(() => {
    if (recorderRef.current && recorderRef.current.isRecording()) {
      const level = recorderRef.current.getAudioLevel();
      setAudioLevel(level);
      animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
    }
  }, []);

  const startRecording = useCallback(async () => {
    try {
      if (recorderRef.current?.isRecording()) {
        return; // Already recording
      }

      const recorder = new AudioRecorder({
        onDataAvailable,
        onError,
        chunkInterval,
      });

      await recorder.start();
      recorderRef.current = recorder;
      setIsRecording(true);
      setHasPermission(true);

      // Start audio level monitoring
      updateAudioLevel();
    } catch (error) {
      setHasPermission(false);
      onError?.(error as Error);
    }
  }, [onDataAvailable, onError, chunkInterval, updateAudioLevel]);

  const stopRecording = useCallback(() => {
    if (recorderRef.current) {
      recorderRef.current.stop();
      recorderRef.current = null;
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    setIsRecording(false);
    setAudioLevel(0);
  }, []);

  // Manual cleanup function
  const cleanup = useCallback(() => {
    stopRecording();
  }, [stopRecording]);

  return {
    isRecording,
    audioLevel,
    hasPermission,
    startRecording,
    stopRecording,
    cleanup,
    isSupported: AudioRecorder.isSupported(),
  };
}