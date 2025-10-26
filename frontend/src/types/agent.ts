export interface Agent {
  id: 'receptionist' | 'sales' | 'callcenter';
  name: string;
  description: string;
  prompt: string;
  icon: string; // Lucide icon name
  color: string; // Tailwind color
}