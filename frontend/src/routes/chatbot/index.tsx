import { createFileRoute } from '@tanstack/react-router';
import { Card } from '@/components/ui/card';

export const Route = createFileRoute('/chatbot/')({
  component: ChatbotPage,
});

/**
 * Chatbot page component - Currently in development.
 * 
 * Displays a placeholder message indicating the chatbot feature
 * is under construction, with brand-aligned styling.
 * 
 * @returns {JSX.Element} The chatbot placeholder page
 */
function ChatbotPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="max-w-2xl mx-auto">
        <Card className="p-8 text-center">
          <h1 className="text-3xl font-bold mb-4 font-display text-foreground-strong">Chatbot Coming Soon</h1>
          <p className="text-muted-foreground mb-6">
            Our text-based chatbot interface is currently under development.
            In the meantime, try our voice agent feature!
          </p>
          {/* Using brand colors: Schematic Blue for info states */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg" style={{ backgroundColor: 'color-mix(in srgb, var(--schematic-blue) 20%, transparent)', color: 'var(--schematic-blue)' }}>
            <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--schematic-blue)' }}></span>
            <span className="text-sm font-medium font-ui">In Development</span>
          </div>
        </Card>
      </div>
    </div>
  );
}