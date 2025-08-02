import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'

const WebSocketContext = createContext(null)

export const useWebSocket = () => {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}

export const WebSocketProvider = ({ children }) => {
  const [ws, setWs] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState(null)
  const [subscriptions, setSubscriptions] = useState(new Set())

  const connect = useCallback(() => {
    try {
      const websocket = new WebSocket(`ws://${window.location.host}/ws`)
      
      websocket.onopen = () => {
        console.log('WebSocket connected')
        setIsConnected(true)
        setWs(websocket)
        
        // Re-subscribe to all subscriptions after reconnection
        subscriptions.forEach(subscription => {
          websocket.send(JSON.stringify({
            type: 'subscribe',
            subscription: subscription
          }))
        })
      }
      
      websocket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          setLastMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      websocket.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        setWs(null)
        
        // Attempt to reconnect after 3 seconds
        setTimeout(connect, 3000)
      }
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
      
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
      // Retry connection after 5 seconds
      setTimeout(connect, 5000)
    }
  }, [subscriptions])

  useEffect(() => {
    connect()
    
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [])

  const subscribe = useCallback((subscriptionType) => {
    setSubscriptions(prev => new Set([...prev, subscriptionType]))
    
    if (ws && isConnected) {
      ws.send(JSON.stringify({
        type: 'subscribe',
        subscription: subscriptionType
      }))
    }
  }, [ws, isConnected])

  const unsubscribe = useCallback((subscriptionType) => {
    setSubscriptions(prev => {
      const newSet = new Set(prev)
      newSet.delete(subscriptionType)
      return newSet
    })
    
    if (ws && isConnected) {
      ws.send(JSON.stringify({
        type: 'unsubscribe',
        subscription: subscriptionType
      }))
    }
  }, [ws, isConnected])

  const sendMessage = useCallback((message) => {
    if (ws && isConnected) {
      ws.send(JSON.stringify(message))
    }
  }, [ws, isConnected])

  const value = {
    isConnected,
    lastMessage,
    subscribe,
    unsubscribe,
    sendMessage,
    subscriptions: Array.from(subscriptions)
  }

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  )
}