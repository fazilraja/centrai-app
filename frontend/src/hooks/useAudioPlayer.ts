import { useState, useRef, useCallback } from 'react';
import { AudioPlayer } from '@/lib/audio/player';

interface UseAudioPlayerOptions {
  onEnded?: () => void;
  onError?: (error: Error) => void;
  autoPlay?: boolean;
}

export function useAudioPlayer({
  onEnded,
  onError,
  autoPlay = true,
}: UseAudioPlayerOptions = {}) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  const playerRef = useRef<AudioPlayer | null>(null);
  const intervalRef = useRef<NodeJS.Timeout>();

  const updateProgress = useCallback(() => {
    if (playerRef.current) {
      setCurrentTime(playerRef.current.getCurrentTime());
      setDuration(playerRef.current.getDuration());
    }
  }, []);

  const play = useCallback(
    async (audio: string | Blob) => {
      try {
        if (!playerRef.current) {
          playerRef.current = new AudioPlayer({
            onEnded: () => {
              setIsPlaying(false);
              onEnded?.();
              if (intervalRef.current) {
                clearInterval(intervalRef.current);
              }
            },
            onError: (error) => {
              setIsPlaying(false);
              onError?.(error);
              if (intervalRef.current) {
                clearInterval(intervalRef.current);
              }
            },
            autoPlay,
          });
        }

        await playerRef.current.play(audio);
        setIsPlaying(true);

        // Start progress tracking
        intervalRef.current = setInterval(updateProgress, 100);
      } catch (error) {
        onError?.(error as Error);
      }
    },
    [autoPlay, onEnded, onError, updateProgress]
  );

  const pause = useCallback(() => {
    playerRef.current?.pause();
    setIsPlaying(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  }, []);

  const stop = useCallback(() => {
    playerRef.current?.stop();
    setIsPlaying(false);
    setCurrentTime(0);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
  }, []);

  const playChunk = useCallback(
    (chunk: Blob) => {
      if (!playerRef.current) {
        playerRef.current = new AudioPlayer({
          onEnded,
          onError,
          autoPlay,
        });
      }

      playerRef.current.playChunk(chunk);
      setIsPlaying(true);
    },
    [onEnded, onError, autoPlay]
  );

  // Cleanup on unmount
  const cleanup = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    playerRef.current?.stop();
  }, []);

  return {
    isPlaying,
    duration,
    currentTime,
    play,
    pause,
    stop,
    playChunk,
    cleanup,
    isSupported: AudioPlayer.prototype.isSupported?.() ?? true,
  };
}