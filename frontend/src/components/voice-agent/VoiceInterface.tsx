import { useCallback } from 'react';
import { useVoiceAgent } from '@/hooks/useVoiceAgent';
import { getAgent } from '@/lib/agents';
import { AgentHeader } from './AgentHeader';
import { PromptDisplay } from './PromptDisplay';
import { VoiceRecorder } from './VoiceRecorder';
import { ConversationDisplay } from './ConversationDisplay';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

interface VoiceInterfaceProps {
  agentId: string;
  onBack: () => void;
}

export function VoiceInterface({ agentId, onBack }: VoiceInterfaceProps) {
  const agent = getAgent(agentId);
  const { messages, error, stopConnection } = useVoiceAgent(agentId);

  const handleBack = useCallback(() => {
    // Clean up connection when navigating away
    stopConnection();
    onBack();
  }, [stopConnection, onBack]);

  if (!agent) {
    return (
      <div className="container mx-auto py-8 text-center">
        <h1 className="text-2xl font-bold text-destructive">Agent not found</h1>
        <Button onClick={handleBack} className="mt-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Agent Selection
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <div className="border-b bg-background">
        <div className="container mx-auto flex items-center gap-4 py-4">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <AgentHeader agent={agent} />
        </div>
      </div>

      {/* Prompt Display */}
      <div className="border-b bg-muted/50">
        <div className="container mx-auto py-4">
          <PromptDisplay prompt={agent.prompt} />
        </div>
      </div>

      {/* Conversation */}
      <div className="flex-1 overflow-hidden">
        <ConversationDisplay messages={messages} />
      </div>

      {/* Voice Recorder */}
      <div className="border-t bg-background">
        <div className="container mx-auto py-6">
          <VoiceRecorder agentId={agentId} />
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="border-t bg-destructive/10 p-4 text-center text-sm text-destructive">
          {error.message}
        </div>
      )}
    </div>
  );
}