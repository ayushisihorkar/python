import React, { useState, useEffect } from 'react';
import { 
  Bot, 
  MessageCircle, 
  Send, 
  X, 
  ChevronUp, 
  ChevronDown,
  AlertTriangle,
  CheckCircle,
  Info,
  Lightbulb,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const AIAssistantPanel = ({ vehicles, alerts, onAction }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Initialize with welcome message and recommendations
  useEffect(() => {
    const welcomeMessage = {
      id: 1,
      type: 'ai',
      content: "Hello! I'm your AI fleet assistant. I can help you with maintenance scheduling, vehicle health analysis, and fleet optimization. How can I assist you today?",
      timestamp: new Date()
    };

    const recommendations = generateRecommendations(vehicles, alerts);
    setMessages([welcomeMessage, ...recommendations]);
  }, [vehicles, alerts]);

  const generateRecommendations = (vehicles, alerts) => {
    const recommendations = [];

    // Check for vehicles needing maintenance
    const vehiclesNeedingMaintenance = vehicles.filter(v => v.health_score < 50);
    if (vehiclesNeedingMaintenance.length > 0) {
      recommendations.push({
        id: 2,
        type: 'ai',
        content: `⚠️ ${vehiclesNeedingMaintenance.length} vehicle(s) need immediate attention. Health scores below 50%.`,
        action: 'view_maintenance',
        timestamp: new Date()
      });
    }

    // Check for critical alerts
    const criticalAlerts = alerts.filter(a => a.type === 'critical');
    if (criticalAlerts.length > 0) {
      recommendations.push({
        id: 3,
        type: 'ai',
        content: `🚨 ${criticalAlerts.length} critical alert(s) detected. Immediate action required.`,
        action: 'view_alerts',
        timestamp: new Date()
      });
    }

    // Fleet health summary
    const avgHealth = vehicles.reduce((sum, v) => sum + (v.health_score || 0), 0) / vehicles.length;
    if (avgHealth < 70) {
      recommendations.push({
        id: 4,
        type: 'ai',
        content: `📊 Fleet health average: ${avgHealth.toFixed(1)}%. Consider preventive maintenance.`,
        action: 'fleet_health',
        timestamp: new Date()
      });
    }

    return recommendations;
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputMessage, vehicles, alerts);
      setMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1000);
  };

  const generateAIResponse = (message, vehicles, alerts) => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('maintenance') || lowerMessage.includes('service')) {
      const vehiclesNeedingMaintenance = vehicles.filter(v => v.health_score < 60);
      return {
        id: Date.now() + 1,
        type: 'ai',
        content: `I found ${vehiclesNeedingMaintenance.length} vehicle(s) that need maintenance. Would you like me to help schedule appointments?`,
        action: 'schedule_maintenance',
        timestamp: new Date()
      };
    }

    if (lowerMessage.includes('alert') || lowerMessage.includes('issue')) {
      const activeAlerts = alerts.filter(a => a.action_required);
      return {
        id: Date.now() + 1,
        type: 'ai',
        content: `There are ${activeAlerts.length} active alerts requiring attention. Let me show you the details.`,
        action: 'view_alerts',
        timestamp: new Date()
      };
    }

    if (lowerMessage.includes('health') || lowerMessage.includes('status')) {
      const avgHealth = vehicles.reduce((sum, v) => sum + (v.health_score || 0), 0) / vehicles.length;
      return {
        id: Date.now() + 1,
        type: 'ai',
        content: `Fleet health overview: Average score ${avgHealth.toFixed(1)}%. ${vehicles.filter(v => v.health_score >= 80).length} vehicles in excellent condition.`,
        action: 'fleet_overview',
        timestamp: new Date()
      };
    }

    if (lowerMessage.includes('cost') || lowerMessage.includes('expense')) {
      return {
        id: Date.now() + 1,
        type: 'ai',
        content: "I can help you analyze maintenance costs and optimize your fleet expenses. Would you like to see the cost breakdown?",
        action: 'cost_analysis',
        timestamp: new Date()
      };
    }

    return {
      id: Date.now() + 1,
      type: 'ai',
      content: "I can help you with maintenance scheduling, vehicle health analysis, cost optimization, and fleet management. What specific information do you need?",
      timestamp: new Date()
    };
  };

  const handleAction = (action) => {
    if (onAction) {
      onAction(action);
    }
  };

  const getMessageIcon = (type) => {
    switch (type) {
      case 'ai':
        return <Bot className="w-5 h-5 text-blue-500" />;
      case 'user':
        return <MessageCircle className="w-5 h-5 text-gray-500" />;
      default:
        return <Info className="w-5 h-5 text-gray-400" />;
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'view_maintenance':
        return <AlertTriangle className="w-4 h-4" />;
      case 'view_alerts':
        return <AlertTriangle className="w-4 h-4" />;
      case 'fleet_health':
        return <TrendingUp className="w-4 h-4" />;
      case 'schedule_maintenance':
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Lightbulb className="w-4 h-4" />;
    }
  };

  if (!isOpen) {
    return (
      <motion.button
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        whileHover={{ scale: 1.1 }}
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-colors z-50"
      >
        <Bot className="w-6 h-6" />
      </motion.button>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="fixed bottom-6 right-6 w-96 bg-white rounded-lg shadow-xl border border-gray-200 z-50"
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-t-lg">
        <div className="flex items-center space-x-2">
          <Bot className="w-5 h-5" />
          <span className="font-semibold">AI Assistant</span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 hover:bg-blue-600 rounded"
          >
            {isMinimized ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 hover:bg-blue-600 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <AnimatePresence>
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            {/* Messages */}
            <div className="h-96 overflow-y-auto p-4 space-y-4">
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, x: message.type === 'user' ? 20 : -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-2 max-w-xs ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className="flex-shrink-0 mt-1">
                      {getMessageIcon(message.type)}
                    </div>
                    <div className={`p-3 rounded-lg ${
                      message.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="text-sm">{message.content}</p>
                      {message.action && (
                        <button
                          onClick={() => handleAction(message.action)}
                          className="mt-2 flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-700"
                        >
                          {getActionIcon(message.action)}
                          <span>Take Action</span>
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="flex items-start space-x-2">
                    <Bot className="w-5 h-5 text-blue-500 mt-1" />
                    <div className="bg-gray-100 p-3 rounded-lg">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 border-t">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask me anything about your fleet..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputMessage.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      )}
    </motion.div>
  );
};

export default AIAssistantPanel; 