import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { MessageSquare, Mic } from 'lucide-react'
import { Card } from '@/components/ui/card'
import logo from '../logo.svg'

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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <img
            src={logo}
            className="h-32 w-32 mx-auto mb-6 animate-[spin_20s_linear_infinite]"
            alt="logo"
          />
          <h1 className="text-5xl font-bold text-white mb-4">
            Welcome to CentrAI
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Experience the future of AI-powered communication with our advanced chatbot and voice agent solutions
          </p>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-4xl mx-auto mb-8">
          <div className="flex gap-4 p-2 bg-gray-800/50 rounded-lg backdrop-blur-sm">
            {/* Chatbot Tab */}
            <button
              onClick={() => setActiveTab('chatbot')}
              className={`flex-1 flex items-center justify-center gap-3 px-6 py-4 rounded-lg font-semibold transition-all duration-200 ${
                activeTab === 'chatbot'
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                  : 'bg-transparent text-gray-300 hover:bg-gray-700/50'
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
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                  : 'bg-transparent text-gray-300 hover:bg-gray-700/50'
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
            <Card className="p-8 bg-gray-800/80 backdrop-blur-sm border-gray-700">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-blue-600/20 mb-6">
                  <MessageSquare size={40} className="text-blue-500" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-4">
                  AI-Powered Chatbot
                </h2>
                <p className="text-gray-300 text-lg mb-8 max-w-2xl mx-auto">
                  Engage in intelligent conversations with our text-based AI assistant. 
                  Get instant responses, support, and information through natural language interaction.
                </p>
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                  <div className="p-4 bg-gray-700/50 rounded-lg">
                    <h3 className="font-semibold text-blue-400 mb-2">Instant Responses</h3>
                    <p className="text-sm text-gray-400">Get immediate answers to your questions 24/7</p>
                  </div>
                  <div className="p-4 bg-gray-700/50 rounded-lg">
                    <h3 className="font-semibold text-blue-400 mb-2">Natural Language</h3>
                    <p className="text-sm text-gray-400">Communicate naturally as you would with a human</p>
                  </div>
                  <div className="p-4 bg-gray-700/50 rounded-lg">
                    <h3 className="font-semibold text-blue-400 mb-2">Smart & Contextual</h3>
                    <p className="text-sm text-gray-400">AI that understands context and provides relevant answers</p>
                  </div>
                </div>
                <button
                  onClick={() => handleNavigate('chatbot')}
                  className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white text-lg font-semibold rounded-lg transition-colors shadow-lg shadow-blue-500/50"
                >
                  Start Chatting
                </button>
              </div>
            </Card>
          ) : (
            <Card className="p-8 bg-gray-800/80 backdrop-blur-sm border-gray-700">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-purple-600/20 mb-6">
                  <Mic size={40} className="text-purple-500" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-4">
                  Voice AI Agents
                </h2>
                <p className="text-gray-300 text-lg mb-8 max-w-2xl mx-auto">
                  Experience natural voice conversations with our specialized AI agents. 
                  Talk to AI receptionists, sales assistants, and call center representatives.
                </p>
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                  <div className="p-4 bg-gray-700/50 rounded-lg">
                    <h3 className="font-semibold text-purple-400 mb-2">Receptionist</h3>
                    <p className="text-sm text-gray-400">Handle calls and schedule appointments efficiently</p>
                  </div>
                  <div className="p-4 bg-gray-700/50 rounded-lg">
                    <h3 className="font-semibold text-purple-400 mb-2">Sales Agent</h3>
                    <p className="text-sm text-gray-400">Engage customers and close deals with AI assistance</p>
                  </div>
                  <div className="p-4 bg-gray-700/50 rounded-lg">
                    <h3 className="font-semibold text-purple-400 mb-2">Call Center</h3>
                    <p className="text-sm text-gray-400">Provide 24/7 customer support at scale</p>
                  </div>
                </div>
                <button
                  onClick={() => handleNavigate('voice-agent')}
                  className="px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white text-lg font-semibold rounded-lg transition-colors shadow-lg shadow-purple-500/50"
                >
                  Try Voice Agent
                </button>
              </div>
            </Card>
          )}
        </div>

        {/* Footer Info */}
        <div className="text-center mt-12 text-gray-400">
          <p className="text-sm">
            Powered by advanced AI technology • Secure • Reliable • Available 24/7
          </p>
        </div>
      </div>
    </div>
  )
}
