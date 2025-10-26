import type { Message } from '@/types/conversation';
import { cn } from '@/lib/utils';

interface ConversationDisplayProps {
  messages: Message[];
}

export function ConversationDisplay({ messages }: ConversationDisplayProps) {
  return (
    <div className="h-full overflow-y-auto">
      <div className="container mx-auto space-y-4 py-6">
        {messages.length === 0 ? (
          <div className="text-center text-muted-foreground">
            <p>Start talking to begin the conversation</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                'flex',
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={cn(
                  'max-w-[80%] rounded-lg p-4',
                  message.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted'
                )}
              >
                <p className="text-sm">{message.text}</p>
                <span className="mt-1 block text-xs opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}