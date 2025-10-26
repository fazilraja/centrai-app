export interface AudioRecorderOptions {
  onDataAvailable: (blob: Blob) => void;
  onError?: (error: Error) => void;
  chunkInterval?: number; // ms
}

export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private stream: MediaStream | null = null;
  private animationFrameRef: number | null = null;
  private options: AudioRecorderOptions;

  constructor(options: AudioRecorderOptions) {
    this.options = options;
  }

  async start(): Promise<void> {
    try {
      // Request microphone access
      this.stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 48000,
        },
      });

      // Setup audio analysis for visualization
      this.audioContext = new AudioContext();
      this.analyser = this.audioContext.createAnalyser();
      const source = this.audioContext.createMediaStreamSource(this.stream);

      this.analyser.fftSize = 256;
      source.connect(this.analyser);

      // Setup MediaRecorder
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: 'audio/webm;codecs=opus',
        audioBitsPerSecond: 128000,
      });

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.options.onDataAvailable(event.data);
        }
      };

      this.mediaRecorder.onerror = () => {
        this.options.onError?.(new Error('MediaRecorder error'));
      };

      this.mediaRecorder.start(this.options.chunkInterval || 250);
    } catch (error) {
      this.options.onError?.(error as Error);
      throw error;
    }
  }

  stop(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }

    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
    }

    if (this.audioContext) {
      this.audioContext.close();
    }

    if (this.animationFrameRef) {
      cancelAnimationFrame(this.animationFrameRef);
    }

    this.cleanup();
  }

  private cleanup(): void {
    this.mediaRecorder = null;
    this.stream = null;
    this.audioContext = null;
    this.analyser = null;
    this.animationFrameRef = null;
  }

  getAudioLevel(): number {
    if (!this.analyser) return 0;

    const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
    this.analyser.getByteFrequencyData(dataArray);

    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    return average / 255;
  }

  isRecording(): boolean {
    return this.mediaRecorder?.state === 'recording';
  }

  static isSupported(): boolean {
    return !!(navigator.mediaDevices?.getUserMedia && window.MediaRecorder);
  }
}