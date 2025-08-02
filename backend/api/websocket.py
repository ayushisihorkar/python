from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {
            "vehicle_updates": [],
            "agent_status": [],
            "bookings": [],
            "notifications": [],
            "alerts": []
        }
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connection established. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self._send_to_websocket(websocket, {
            "type": "connection_established",
            "message": "Connected to Fleet Maintenance Dashboard",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass  # Connection already removed
        
        # Remove from all subscriptions
        for subscription_list in self.subscriptions.values():
            try:
                subscription_list.remove(websocket)
            except ValueError:
                pass
        
        logger.info(f"WebSocket connection closed. Total connections: {len(self.active_connections)}")
    
    async def subscribe(self, websocket: WebSocket, subscription_type: str):
        """Subscribe a connection to specific updates"""
        if subscription_type in self.subscriptions:
            if websocket not in self.subscriptions[subscription_type]:
                self.subscriptions[subscription_type].append(websocket)
                
                await self._send_to_websocket(websocket, {
                    "type": "subscription_confirmed",
                    "subscription": subscription_type,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                logger.info(f"WebSocket subscribed to {subscription_type}")
        else:
            await self._send_to_websocket(websocket, {
                "type": "error",
                "message": f"Unknown subscription type: {subscription_type}",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def unsubscribe(self, websocket: WebSocket, subscription_type: str):
        """Unsubscribe a connection from specific updates"""
        if subscription_type in self.subscriptions:
            try:
                self.subscriptions[subscription_type].remove(websocket)
                await self._send_to_websocket(websocket, {
                    "type": "subscription_cancelled",
                    "subscription": subscription_type,
                    "timestamp": datetime.utcnow().isoformat()
                })
                logger.info(f"WebSocket unsubscribed from {subscription_type}")
            except ValueError:
                pass  # Not subscribed
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected clients"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_subscription(self, subscription_type: str, data: Dict[str, Any]):
        """Broadcast data to subscribers of a specific type"""
        if subscription_type not in self.subscriptions:
            logger.warning(f"Unknown subscription type: {subscription_type}")
            return
        
        message = {
            "type": subscription_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.subscriptions[subscription_type]:
            try:
                await connection.send_text(message_str)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error sending to WebSocket subscriber: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_vehicle_update(self, vehicle_id: int, status: str, health_score: float = None, alerts: List[str] = None):
        """Send vehicle status update to subscribers"""
        await self.broadcast_to_subscription("vehicle_updates", {
            "vehicle_id": vehicle_id,
            "status": status,
            "health_score": health_score,
            "alerts": alerts or []
        })
    
    async def send_agent_status(self, agent_name: str, status: str, last_action: str = None, confidence: float = None):
        """Send agent status update to subscribers"""
        await self.broadcast_to_subscription("agent_status", {
            "agent_name": agent_name,
            "status": status,
            "last_action": last_action,
            "confidence": confidence
        })
    
    async def send_booking_update(self, booking_id: int, vehicle_id: int, status: str, workshop_name: str = None, booking_slot: str = None):
        """Send booking status update to subscribers"""
        await self.broadcast_to_subscription("bookings", {
            "booking_id": booking_id,
            "vehicle_id": vehicle_id,
            "status": status,
            "workshop_name": workshop_name,
            "booking_slot": booking_slot
        })
    
    async def send_notification(self, notification_id: int, title: str, message: str, severity: str, recipient_type: str):
        """Send notification to subscribers"""
        await self.broadcast_to_subscription("notifications", {
            "notification_id": notification_id,
            "title": title,
            "message": message,
            "severity": severity,
            "recipient_type": recipient_type
        })
    
    async def send_alert(self, vehicle_id: int, alert_type: str, severity: str, message: str):
        """Send critical alert to subscribers"""
        await self.broadcast_to_subscription("alerts", {
            "vehicle_id": vehicle_id,
            "alert_type": alert_type,
            "severity": severity,
            "message": message
        })
    
    async def handle_client_message(self, websocket: WebSocket, message: str):
        """Handle incoming messages from clients"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                subscription_type = data.get("subscription")
                await self.subscribe(websocket, subscription_type)
                
            elif message_type == "unsubscribe":
                subscription_type = data.get("subscription")
                await self.unsubscribe(websocket, subscription_type)
                
            elif message_type == "ping":
                await self._send_to_websocket(websocket, {
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            elif message_type == "get_status":
                await self._send_status_update(websocket)
                
            else:
                await self._send_to_websocket(websocket, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        except json.JSONDecodeError:
            await self._send_to_websocket(websocket, {
                "type": "error",
                "message": "Invalid JSON format",
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            await self._send_to_websocket(websocket, {
                "type": "error",
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            })
    
    async def _send_to_websocket(self, websocket: WebSocket, data: Dict[str, Any]):
        """Send data to a specific WebSocket connection"""
        try:
            message = json.dumps(data)
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)
        except Exception as e:
            logger.error(f"Error sending to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def _send_status_update(self, websocket: WebSocket):
        """Send current system status to a WebSocket"""
        status = {
            "type": "system_status",
            "data": {
                "active_connections": len(self.active_connections),
                "subscriptions": {
                    sub_type: len(connections) 
                    for sub_type, connections in self.subscriptions.items()
                },
                "agents_running": True,  # This would be actual status from agent coordinator
                "database_connected": True,  # This would be actual database status
                "last_update": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._send_to_websocket(websocket, status)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about WebSocket connections"""
        return {
            "total_connections": len(self.active_connections),
            "subscriptions": {
                sub_type: len(connections) 
                for sub_type, connections in self.subscriptions.items()
            }
        }