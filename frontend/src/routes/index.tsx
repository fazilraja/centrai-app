import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { MessageSquare, Mic } from 'lucide-react'
import { Card } from '@/components/ui/card'

export const Route = createFileRoute('/')({
  component: App,
})

/**
 * Landing page component with navigation tabs for Chatbot and Voice Agents.
 * Displays chatbot as the default view with ability to switch to voice agents.
 * 
 * @returns {JSX.Element} The landing page with navigation tabs.
 */
function App() {
  const navigate = useNavigate()
  // Default to 'chatbot' as requested
  const [activeTab, setActiveTab] = useState<'chatbot' | 'voice-agent'>('chatbot')

  /**
   * Handles navigation when user selects a tab.
   * Navigates to the corresponding route for the selected option.
   * 
   * @param {string} tab - The selected tab ('chatbot' or 'voice-agent').
   */
  const handleNavigate = (tab: 'chatbot' | 'voice-agent') => {
    navigate({ to: `/${tab}` })
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          {/* centrAI logo - crosshair/targeting reticle motif */}
          <img
            src="/favicon.png"
            className="h-32 w-32 mx-auto mb-6"
            alt="centrAI Logo"
          />
          <h1 className="text-5xl font-bold text-foreground-strong mb-4 font-display">
            Welcome to centrAI
          </h1>
          <p className="text-xl text-foreground max-w-2xl mx-auto font-body">
            Experience the future of AI-powered communication with our advanced chatbot and voice agent solutions
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex gap-4 p-2 bg-card rounded-lg border border-border">
            {/* Chatbot Tab */}
            <button
              onClick={() => setActiveTab('chatbot')}
              className={`flex-1 flex items-center justify-center gap-3 px-6 py-4 rounded-lg font-semibold transition-all duration-200 ${
                activeTab === 'chatbot'
                  ? 'bg-primary text-primary-foreground shadow-md'
                  : 'bg-transparent text-foreground hover:bg-accent'
              }`}
            >
              <MessageSquare size={24} />
              <span className="text-lg">Chatbot</span>
            </button>

            {/* Voice Agent Tab */}
            <button
              onClick={() => setActiveTab('voice-agent')}
              className={`flex-1 flex items-center justify-center gap-3 px-6 py-4 rounded-lg font-semibold transition-all duration-200 ${
                activeTab === 'voice-agent'
                  ? 'bg-secondary text-secondary-foreground shadow-md'
                  : 'bg-transparent text-foreground hover:bg-accent'
              }`}
            >
              <Mic size={24} />
              <span className="text-lg">Voice Agents</span>
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="max-w-4xl mx-auto">
          {activeTab === 'chatbot' ? (
            <Card className="p-8 bg-card border-border">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/20 mb-6">
                  <MessageSquare size={40} className="text-primary" />
                </div>
                <h2 className="text-3xl font-bold text-foreground-strong mb-4 font-display">
                  AI-Powered Chatbot
                </h2>
                <p className="text-foreground text-lg mb-8 max-w-2xl mx-auto font-body">
                  Engage in intelligent conversations with our text-based AI assistant. 
                  Get instant responses, support, and information through natural language interaction.
                </p>
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                  <div className="p-4 bg-muted rounded-lg border border-border">
                    <h3 className="font-semibold text-primary mb-2 font-ui">Instant Responses</h3>
                    <p className="text-sm text-muted-foreground font-body">Get immediate answers to your questions 24/7</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg border border-border">
                    <h3 className="font-semibold text-primary mb-2 font-ui">Natural Language</h3>
                    <p className="text-sm text-muted-foreground font-body">Communicate naturally as you would with a human</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg border border-border">
                    <h3 className="font-semibold text-primary mb-2 font-ui">Smart & Contextual</h3>
                    <p className="text-sm text-muted-foreground font-body">AI that understands context and provides relevant answers</p>
                  </div>
                </div>
                <button
                  onClick={() => handleNavigate('chatbot')}
                  className="px-8 py-4 bg-primary hover:bg-[var(--primary-hover)] text-primary-foreground text-lg font-semibold rounded-[4px] transition-colors duration-200 shadow-md font-ui"
                >
                  Start Chatting
                </button>
              </div>
            </Card>
          ) : (
            <Card className="p-8 bg-card border-border">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-secondary/20 mb-6">
                  <Mic size={40} className="text-secondary" />
                </div>
                <h2 className="text-3xl font-bold text-foreground-strong mb-4 font-display">
                  Voice AI Agents
                </h2>
                <p className="text-foreground text-lg mb-8 max-w-2xl mx-auto font-body">
                  Experience natural voice conversations with our specialized AI agents. 
                  Talk to AI receptionists, sales assistants, and call center representatives.
                </p>
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                  <div className="p-4 bg-muted rounded-lg border border-border">
                    <h3 className="font-semibold text-secondary mb-2 font-ui">Receptionist</h3>
                    <p className="text-sm text-muted-foreground font-body">Handle calls and schedule appointments efficiently</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg border border-border">
                    <h3 className="font-semibold text-secondary mb-2 font-ui">Sales Agent</h3>
                    <p className="text-sm text-muted-foreground font-body">Engage customers and close deals with AI assistance</p>
                  </div>
                  <div className="p-4 bg-muted rounded-lg border border-border">
                    <h3 className="font-semibold text-secondary mb-2 font-ui">Call Center</h3>
                    <p className="text-sm text-muted-foreground font-body">Provide 24/7 customer support at scale</p>
                  </div>
                </div>
                <button
                  onClick={() => handleNavigate('voice-agent')}
                  className="px-8 py-4 bg-secondary hover:bg-[var(--primary-hover)] text-secondary-foreground text-lg font-semibold rounded-[4px] transition-colors duration-200 shadow-md font-ui"
                >
                  Try Voice Agent
                </button>
              </div>
            </Card>
          )}
        </div>

        {/* Footer Info */}
        <div className="text-center mt-12 text-muted-foreground">
          <p className="text-sm font-ui">
            Powered by advanced AI technology • Secure • Reliable • Available 24/7
          </p>
        </div>
      </div>
    </div>
  )
}
