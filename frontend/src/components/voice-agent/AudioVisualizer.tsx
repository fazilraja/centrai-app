import { cn } from '@/lib/utils';

interface AudioVisualizerProps {
  level: number;
  isActive: boolean;
}

export function AudioVisualizer({ level, isActive }: AudioVisualizerProps) {
  const barCount = 20;
  const bars = Array.from({ length: barCount }, (_, i) => {
    const height = isActive ? Math.random() * level * 100 : 2;
    return {
      height: `${height}%`,
      delay: `${i * 0.05}s`,
    };
  });

  return (
    <div className="flex items-center justify-center gap-1 h-16 w-64">
      {bars.map((bar, index) => (
        <div
          key={index}
          className={cn(
            'w-1 bg-primary rounded-full transition-all duration-150',
            isActive ? 'opacity-100' : 'opacity-30'
          )}
          style={{
            height: bar.height,
            transitionDelay: bar.delay,
          }}
        />
      ))}
    </div>
  );
}