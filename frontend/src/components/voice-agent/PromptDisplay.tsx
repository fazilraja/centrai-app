import { Card } from '@/components/ui/card';

interface PromptDisplayProps {
  prompt: string;
}

export function PromptDisplay({ prompt }: PromptDisplayProps) {
  return (
    <Card className="p-4">
      <div className="flex items-start gap-3">
        <div className="w-2 h-2 rounded-full bg-blue-500 mt-2 flex-shrink-0"></div>
        <div className="flex-1">
          <h3 className="text-sm font-medium text-muted-foreground mb-1">System Prompt</h3>
          <p className="text-sm">{prompt}</p>
        </div>
      </div>
    </Card>
  );
}