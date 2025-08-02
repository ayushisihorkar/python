import React, { useState, useRef, useEffect } from 'react'
import { 
  MessageCircle, 
  X, 
  Send, 
  Bot, 
  User, 
  Wrench, 
  Calendar, 
  AlertTriangle,
  TrendingUp,
  Minimize2,
  Maximize2
} from 'lucide-react'

const AIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      content: 'Hello! I\'m your AI fleet maintenance assistant. I can help you with vehicle diagnostics, scheduling maintenance, and analyzing fleet health. What would you like to know?',
      timestamp: new Date(),
      actions: ['Schedule Maintenance', 'Run Diagnostics', 'Fleet Report']
    }
  ])
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!message.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setMessage('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(message)
      setMessages(prev => [...prev, aiResponse])
      setIsTyping(false)
    }, 1500)
  }

  const generateAIResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase()
    
    let response = {
      id: Date.now() + 1,
      type: 'ai',
      timestamp: new Date(),
      actions: []
    }

    if (lowerMessage.includes('maintenance') || lowerMessage.includes('service')) {
      response.content = 'I can help you schedule maintenance! I\'ve analyzed your fleet and found 3 vehicles that need attention. Vehicle EV001 has a critical battery warning, EV003 needs routine maintenance, and EV007 has a coolant level alert.'
      response.actions = ['Schedule for EV001', 'View Maintenance History', 'Generate Report']
    } else if (lowerMessage.includes('health') || lowerMessage.includes('status')) {
      response.content = 'Your fleet health overview: 85% operational, 12% need attention, 3% critical. The main issues are battery degradation in older vehicles and cooling system maintenance needs. Would you like me to prioritize the critical issues?'
      response.actions = ['View Critical Issues', 'Fleet Health Report', 'Optimize Schedule']
    } else if (lowerMessage.includes('diagnostic') || lowerMessage.includes('problem')) {
      response.content = 'I can run diagnostics on any vehicle. Based on recent telemetry, I recommend checking vehicles with error codes: EV001 (BATT_001), EV005 (TEMP_002), and EV009 (MOTOR_003). Which vehicle would you like me to analyze?'
      response.actions = ['Analyze EV001', 'Run Full Diagnostics', 'View Error History']
    } else if (lowerMessage.includes('book') || lowerMessage.includes('schedule')) {
      response.content = 'I can help you book maintenance slots. I found 5 available workshops within 50km. AutoTech Center has immediate availability, while EV Specialists has the best rating. What\'s your priority - speed or quality?'
      response.actions = ['Book at AutoTech', 'Book at EV Specialists', 'See All Options']
    } else {
      response.content = 'I understand you\'re asking about fleet management. I can help with vehicle diagnostics, maintenance scheduling, health monitoring, and predictive analytics. What specific aspect would you like assistance with?'
      response.actions = ['Vehicle Diagnostics', 'Schedule Maintenance', 'Fleet Analytics', 'Emergency Support']
    }

    return response
  }

  const handleActionClick = (action) => {
    const actionMessage = {
      id: Date.now(),
      type: 'user',
      content: `Execute: ${action}`,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, actionMessage])
    setIsTyping(true)

    setTimeout(() => {
      const response = {
        id: Date.now() + 1,
        type: 'ai',
        content: `I'm processing "${action}" for you. This will take a moment...`,
        timestamp: new Date(),
        actions: ['View Progress', 'Cancel Action']
      }
      setMessages(prev => [...prev, response])
      setIsTyping(false)
    }, 1000)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-primary-600 hover:bg-primary-700 text-white p-4 rounded-full shadow-float transition-all duration-300 hover:scale-110 z-50"
      >
        <MessageCircle className="w-6 h-6" />
      </button>
    )
  }

  return (
    <div className={`fixed bottom-6 right-6 z-50 transition-all duration-300 ${
      isMinimized ? 'w-80' : 'w-96'
    }`}>
      {/* AI Assistant Panel */}
      <div className={`bg-white rounded-2xl shadow-float border border-secondary-200 overflow-hidden ${
        isMinimized ? 'h-16' : 'h-[600px]'
      }`}>
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-semibold">AI Assistant</h3>
              <p className="text-xs text-primary-100">Fleet Maintenance Helper</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 hover:bg-white/20 rounded transition-colors"
            >
              {isMinimized ? <Maximize2 className="w-4 h-4" /> : <Minimize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 hover:bg-white/20 rounded transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 p-4 space-y-4 max-h-[440px] overflow-y-auto scrollbar-thin">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] ${
                    msg.type === 'user' 
                      ? 'bg-primary-600 text-white rounded-2xl rounded-br-md' 
                      : 'bg-secondary-100 text-secondary-900 rounded-2xl rounded-bl-md'
                  } p-3`}>
                    <div className="flex items-start space-x-2">
                      {msg.type === 'ai' && (
                        <Bot className="w-4 h-4 mt-0.5 text-primary-600 flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <p className="text-sm">{msg.content}</p>
                        
                        {/* Action Buttons */}
                        {msg.actions && msg.actions.length > 0 && (
                          <div className="mt-3 space-y-1">
                            {msg.actions.map((action, index) => (
                              <button
                                key={index}
                                onClick={() => handleActionClick(action)}
                                className="block w-full text-left text-xs bg-white/20 hover:bg-white/30 rounded-lg px-3 py-2 transition-colors"
                              >
                                {action}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-secondary-100 rounded-2xl rounded-bl-md p-3 flex items-center space-x-2">
                    <Bot className="w-4 h-4 text-primary-600" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-secondary-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            <div className="px-4 py-2 border-t border-secondary-200">
              <div className="flex space-x-2">
                <button
                  onClick={() => handleActionClick('Run Fleet Health Check')}
                  className="flex-1 flex items-center justify-center space-x-1 bg-success-100 text-success-700 rounded-lg px-3 py-2 text-xs font-medium hover:bg-success-200 transition-colors"
                >
                  <TrendingUp className="w-3 h-3" />
                  <span>Health Check</span>
                </button>
                <button
                  onClick={() => handleActionClick('Schedule Emergency Maintenance')}
                  className="flex-1 flex items-center justify-center space-x-1 bg-danger-100 text-danger-700 rounded-lg px-3 py-2 text-xs font-medium hover:bg-danger-200 transition-colors"
                >
                  <AlertTriangle className="w-3 h-3" />
                  <span>Emergency</span>
                </button>
              </div>
            </div>

            {/* Input */}
            <div className="p-4 border-t border-secondary-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me about your fleet..."
                  className="flex-1 border border-secondary-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!message.trim()}
                  className="bg-primary-600 text-white p-2 rounded-xl hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default AIAssistant