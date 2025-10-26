import { Button } from '@/components/ui/button';
import { Mic, Square } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RecordButtonProps {
  isRecording: boolean;
  onClick: () => void;
  disabled?: boolean;
}

export function RecordButton({ isRecording, onClick, disabled }: RecordButtonProps) {
  return (
    <Button
      size="lg"
      variant={isRecording ? 'destructive' : 'default'}
      className={cn(
        'h-20 w-20 rounded-full transition-all',
        isRecording && 'animate-pulse hover:scale-105'
      )}
      onClick={onClick}
      disabled={disabled}
    >
      {isRecording ? (
        <Square className="h-8 w-8" />
      ) : (
        <Mic className="h-8 w-8" />
      )}
    </Button>
  );
}