import { createFileRoute } from '@tanstack/react-router';
import { Card } from '@/components/ui/card';

export const Route = createFileRoute('/chatbot/')({
  component: ChatbotPage,
});

function ChatbotPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="max-w-2xl mx-auto">
        <Card className="p-8 text-center">
          <h1 className="text-3xl font-bold mb-4">Chatbot Coming Soon</h1>
          <p className="text-muted-foreground mb-6">
            Our text-based chatbot interface is currently under development.
            In the meantime, try our voice agent feature!
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 rounded-lg">
            <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
            <span className="text-sm font-medium">In Development</span>
          </div>
        </Card>
      </div>
    </div>
  );
}