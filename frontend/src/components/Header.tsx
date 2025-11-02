import { Link } from '@tanstack/react-router'

import { useState } from 'react'
import { Menu, X, MessageSquare, Mic } from 'lucide-react'
import { ThemeToggle } from '@/components/ui/ThemeToggle'

/**
 * Header component with sidebar toggle, branding, and theme switcher.
 * 
 * Features:
 * - Hamburger menu button to toggle sidebar
 * - centrAI branding with logo (crosshair/targeting reticle motif)
 * - Theme toggle button (light/dark/system)
 * - Responsive design
 * 
 * Brand-aligned design:
 * - Uses brand color variables
 * - Warm, muted aesthetic
 * - Clean, minimal interface
 * - Monospace font for technical authority
 * 
 * @returns {JSX.Element} The header component with navigation drawer
 */
export default function Header() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      <header className="p-4 flex items-center justify-between bg-card text-foreground shadow-sm border-b border-border">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsOpen(true)}
            className="p-2 hover:bg-accent rounded-lg transition-colors duration-200"
            aria-label="Open menu"
          >
            <Menu size={24} className="text-foreground" />
          </button>
          {/* Logo + Wordmark: centrAI branding with crosshair symbol */}
          <Link to="/" className="flex items-center gap-2 group">
            <img 
              src="/favicon.png" 
              alt="centrAI logo" 
              className="h-8 w-8"
            />
            <h1 className="text-xl font-semibold font-display text-foreground-strong group-hover:text-primary transition-colors duration-200">
              centrAI
            </h1>
          </Link>
        </div>
        
        {/* Theme toggle button */}
        <ThemeToggle />
      </header>

      {/* Sidebar navigation drawer */}
      <aside
        className={`fixed top-0 left-0 h-full w-80 bg-sidebar text-sidebar-foreground shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
          <h2 className="text-xl font-bold text-foreground-strong font-display">Navigation</h2>
          <button
            onClick={() => setIsOpen(false)}
            className="p-2 hover:bg-sidebar-accent rounded-lg transition-colors duration-200"
            aria-label="Close menu"
          >
            <X size={24} />
          </button>
        </div>

        <nav className="flex-1 p-4 overflow-y-auto font-ui">
          {/* Chatbot Link - Default Option */}
          <Link
            to="/chatbot"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 p-3 rounded-[4px] hover:bg-sidebar-accent transition-colors duration-200 mb-2"
            activeProps={{
              className:
                'flex items-center gap-3 p-3 rounded-[4px] bg-sidebar-primary text-sidebar-primary-foreground hover:bg-[var(--primary-hover)] transition-colors duration-200 mb-2',
            }}
          >
            <MessageSquare size={20} />
            <span className="font-medium">Chatbot</span>
          </Link>

          {/* Voice Agents Link */}
          <Link
            to="/voice-agent"
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-3 p-3 rounded-[4px] hover:bg-sidebar-accent transition-colors duration-200 mb-2"
            activeProps={{
              className:
                'flex items-center gap-3 p-3 rounded-[4px] bg-sidebar-primary text-sidebar-primary-foreground hover:bg-[var(--primary-hover)] transition-colors duration-200 mb-2',
            }}
          >
            <Mic size={20} />
            <span className="font-medium">Voice Agents</span>
          </Link>
        </nav>
      </aside>
    </>
  )
}
