import { Card } from '@/components/ui/card';
import type { Agent } from '@/types/agent';
import * as Icons from 'lucide-react';
import { cn } from '@/lib/utils';

interface AgentCardProps {
  agent: Agent;
  onClick: () => void;
}

export function AgentCard({ agent, onClick }: AgentCardProps) {
  const Icon = Icons[agent.icon as keyof typeof Icons] as React.ComponentType<{ className?: string }>;

  const getColorClasses = (color: string) => {
    const colorMap: Record<string, { bg: string; icon: string }> = {
      blue: { bg: 'bg-blue-100', icon: 'text-blue-600' },
      green: { bg: 'bg-green-100', icon: 'text-green-600' },
      purple: { bg: 'bg-purple-100', icon: 'text-purple-600' },
    };
    return colorMap[color] || { bg: 'bg-gray-100', icon: 'text-gray-600' };
  };

  const colors = getColorClasses(agent.color);

  return (
    <Card
      className="cursor-pointer transition-all hover:shadow-lg hover:scale-105"
      onClick={onClick}
    >
      <div className="p-6">
        <div className={cn('inline-flex rounded-lg p-3', colors.bg)}>
          <Icon className={cn('h-6 w-6', colors.icon)} />
        </div>

        <h3 className="mt-4 text-xl font-semibold">{agent.name}</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          {agent.description}
        </p>
      </div>
    </Card>
  );
}