import { getAllAgents } from '@/lib/agents';
import { AgentCard } from './AgentCard';

interface AgentSelectorProps {
  onSelectAgent: (agentId: string) => void;
}

export function AgentSelector({ onSelectAgent }: AgentSelectorProps) {
  const agents = getAllAgents();

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold">Choose Your Agent</h1>
        <p className="mt-2 text-muted-foreground">
          Select an AI agent to start your conversation
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {agents.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            onClick={() => onSelectAgent(agent.id)}
          />
        ))}
      </div>
    </div>
  );
}