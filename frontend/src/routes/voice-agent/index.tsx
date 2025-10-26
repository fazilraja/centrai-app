import { createFileRoute } from '@tanstack/react-router';
import { AgentSelector } from '@/components/voice-agent/AgentSelector';
import { VoiceInterface } from '@/components/voice-agent/VoiceInterface';

type VoiceAgentSearch = {
  agent?: 'receptionist' | 'sales' | 'callcenter';
};

export const Route = createFileRoute('/voice-agent/')({
  component: VoiceAgentPage,
  validateSearch: (search: Record<string, unknown>): VoiceAgentSearch => {
    return {
      agent: search.agent as VoiceAgentSearch['agent'],
    };
  },
});

function VoiceAgentPage() {
  const { agent } = Route.useSearch();
  const navigate = Route.useNavigate();

  // Show AgentSelector if no agent selected
  if (!agent) {
    return <AgentSelector onSelectAgent={(id) => navigate({ search: { agent: id as 'receptionist' | 'sales' | 'callcenter' } })} />;
  }

  // Show VoiceInterface if agent selected
  return (
    <VoiceInterface
      agentId={agent}
      onBack={() => navigate({ search: {} })}
    />
  );
}