import { Link } from '@tanstack/react-router';
import { Mic, MessageSquare } from 'lucide-react';

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r bg-background">
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold">Voice Agent</h1>
      </div>

      <nav className="space-y-1 p-4">
        <Link
          to="/voice-agent"
          className="flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-accent"
          activeProps={{ className: 'bg-accent' }}
        >
          <Mic className="h-5 w-5" />
          <span>Voice Agent</span>
        </Link>

        <div className="flex items-center gap-3 rounded-lg px-3 py-2 opacity-50 cursor-not-allowed">
          <MessageSquare className="h-5 w-5" />
          <span>Chatbot</span>
          <span className="ml-auto text-xs text-muted-foreground">Soon</span>
        </div>
      </nav>
    </aside>
  );
}