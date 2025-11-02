import { Moon, Sun, Monitor } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/hooks/useTheme';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

/**
 * Theme toggle component with dropdown menu for light/dark/system theme selection.
 * 
 * Features:
 * - Displays current effective theme icon (sun/moon)
 * - Dropdown menu with three options: Light, Dark, System
 * - Persists theme preference via useTheme hook
 * - Smooth transitions between themes
 * - Accessible with keyboard navigation
 * 
 * Brand-aligned design:
 * - Warm, muted colors from centrAI brand palette
 * - Subtle hover states (no aggressive animations)
 * - Clean, minimal interface
 * 
 * @returns {JSX.Element} The theme toggle dropdown component
 * 
 * @example
 * ```tsx
 * import { ThemeToggle } from '@/components/ui/ThemeToggle';
 * 
 * function Header() {
 *   return (
 *     <header>
 *       <ThemeToggle />
 *     </header>
 *   );
 * }
 * ```
 */
export function ThemeToggle() {
  const { theme, setTheme, effectiveTheme } = useTheme();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="h-10 w-10 rounded-lg transition-colors hover:bg-accent"
          aria-label="Toggle theme"
        >
          {/* Display sun icon in light mode, moon icon in dark mode */}
          {effectiveTheme === 'light' ? (
            <Sun className="h-5 w-5 text-foreground transition-transform hover:rotate-12" />
          ) : (
            <Moon className="h-5 w-5 text-foreground transition-transform hover:-rotate-12" />
          )}
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent
        align="end"
        className="w-36 bg-card border-border"
      >
        {/* Light mode option */}
        <DropdownMenuItem
          onClick={() => setTheme('light')}
          className={`cursor-pointer ${
            theme === 'light' ? 'bg-accent text-accent-foreground' : ''
          }`}
        >
          <Sun className="mr-2 h-4 w-4" />
          <span>Light</span>
        </DropdownMenuItem>
        
        {/* Dark mode option */}
        <DropdownMenuItem
          onClick={() => setTheme('dark')}
          className={`cursor-pointer ${
            theme === 'dark' ? 'bg-accent text-accent-foreground' : ''
          }`}
        >
          <Moon className="mr-2 h-4 w-4" />
          <span>Dark</span>
        </DropdownMenuItem>
        
        {/* System preference option */}
        <DropdownMenuItem
          onClick={() => setTheme('system')}
          className={`cursor-pointer ${
            theme === 'system' ? 'bg-accent text-accent-foreground' : ''
          }`}
        >
          <Monitor className="mr-2 h-4 w-4" />
          <span>System</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

