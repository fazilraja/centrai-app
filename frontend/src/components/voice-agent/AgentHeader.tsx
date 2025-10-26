import type { Agent } from '@/types/agent';
import * as Icons from 'lucide-react';
import { cn } from '@/lib/utils';

interface AgentHeaderProps {
  agent: Agent;
}

export function AgentHeader({ agent }: AgentHeaderProps) {
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
    <div className="flex items-center gap-4">
      <div className={cn('inline-flex rounded-lg p-3', colors.bg)}>
        <Icon className={cn('h-6 w-6', colors.icon)} />
      </div>
      <div>
        <h2 className="text-2xl font-semibold">{agent.name}</h2>
        <p className="text-sm text-muted-foreground">AI Assistant</p>
      </div>
    </div>
  );
}