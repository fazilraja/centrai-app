export interface AudioPlayerOptions {
  onEnded?: () => void;
  onError?: (error: Error) => void;
  autoPlay?: boolean;
}

export class AudioPlayer {
  private audio: HTMLAudioElement | null = null;
  private queue: Blob[] = [];
  private isPlaying = false;
  private options: AudioPlayerOptions;

  constructor(options: AudioPlayerOptions = {}) {
    this.options = options;
  }

  private ensureAudioElement(): HTMLAudioElement {
    if (!this.audio) {
      this.audio = new Audio();

      this.audio.onended = () => {
        this.isPlaying = false;
        this.options.onEnded?.();
        this.playNext();
      };

      this.audio.onerror = () => {
        this.isPlaying = false;
        this.options.onError?.(new Error('Audio playback error'));
      };
    }
    return this.audio;
  }

  async play(source: string | Blob): Promise<void> {
    try {
      const audio = this.ensureAudioElement();

      // Set audio source
      if (typeof source === 'string') {
        audio.src = source;
      } else {
        audio.src = URL.createObjectURL(source);
      }

      // Play audio
      if (this.options.autoPlay !== false) {
        await audio.play();
        this.isPlaying = true;
      }
    } catch (error) {
      this.options.onError?.(error as Error);
      throw error;
    }
  }

  pause(): void {
    this.audio?.pause();
    this.isPlaying = false;
  }

  stop(): void {
    if (this.audio) {
      this.audio.pause();
      this.audio.currentTime = 0;
    }
    this.isPlaying = false;
  }

  playChunk(chunk: Blob): void {
    if (this.isPlaying) {
      this.queue.push(chunk);
    } else {
      this.play(chunk);
    }
  }

  private playNext(): void {
    if (this.queue.length > 0) {
      const nextChunk = this.queue.shift();
      if (nextChunk) {
        this.play(nextChunk);
      }
    }
  }

  clearQueue(): void {
    this.queue = [];
  }

  getIsPlaying(): boolean {
    return this.isPlaying;
  }

  getDuration(): number {
    return this.audio?.duration || 0;
  }

  getCurrentTime(): number {
    return this.audio?.currentTime || 0;
  }

  isSupported(): boolean {
    return typeof Audio !== 'undefined';
  }
}