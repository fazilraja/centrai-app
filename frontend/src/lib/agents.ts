import type { Agent } from '@/types/agent';

export const AGENTS: Record<string, Agent> = {
  receptionist: {
    id: 'receptionist',
    name: 'Receptionist',
    description: 'Friendly receptionist for appointment scheduling and general inquiries',
    prompt: 'Professional medical clinic receptionist focused on scheduling and patient care',
    icon: 'Phone',
    color: 'blue',
  },

  sales: {
    id: 'sales',
    name: 'Sales Agent',
    description: 'Expert sales representative for product demos and closing deals',
    prompt: 'Experienced sales professional guiding customers through product selection',
    icon: 'TrendingUp',
    color: 'green',
  },

  callcenter: {
    id: 'callcenter',
    name: 'Call Center',
    description: 'Technical support specialist for troubleshooting and issue resolution',
    prompt: 'Patient customer support agent helping with technical problems',
    icon: 'Headphones',
    color: 'purple',
  },
};

export const getAgent = (id: string): Agent | undefined => {
  return AGENTS[id];
};

export const getAllAgents = (): Agent[] => {
  return Object.values(AGENTS);
};