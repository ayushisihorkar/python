import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { WebSocketProvider } from './hooks/useWebSocket'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import VehicleDetail from './pages/VehicleDetail'
import BookingManagement from './pages/BookingManagement'
import AIAssistant from './components/AIAssistant'

function App() {
  return (
    <WebSocketProvider>
      <div className="min-h-screen bg-secondary-50">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/vehicle/:id" element={<VehicleDetail />} />
            <Route path="/bookings" element={<BookingManagement />} />
          </Routes>
          
          {/* Floating AI Assistant */}
          <AIAssistant />
        </Layout>
      </div>
    </WebSocketProvider>
  )
}

export default App