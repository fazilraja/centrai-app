import { Badge } from '@/components/ui/badge';
import type { ConversationStatus } from '@/types/conversation';

interface StatusIndicatorProps {
  status: ConversationStatus;
}

const STATUS_CONFIG: Record<ConversationStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline' }> = {
  idle: { label: 'Ready', variant: 'secondary' },
  connecting: { label: 'Connecting...', variant: 'secondary' },
  connected: { label: 'Connected', variant: 'secondary' },
  recording: { label: 'Listening...', variant: 'default' },
  processing: { label: 'Thinking...', variant: 'secondary' },
  responding: { label: 'Speaking...', variant: 'default' },
  error: { label: 'Error', variant: 'destructive' },
  disconnected: { label: 'Disconnected', variant: 'destructive' },
};

export function StatusIndicator({ status }: StatusIndicatorProps) {
  const config = STATUS_CONFIG[status];

  return (
    <Badge variant={config.variant}>
      {config.label}
    </Badge>
  );
}