from typing import Any, Dict, List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

from .base_agent import BaseAgent
from database.database import AsyncSessionLocal
from database.models import Notification, Vehicle, Booking, Workshop

class CommunicatorAgent(BaseAgent):
    """Agent responsible for communication with fleet managers and workshops"""
    
    def __init__(self):
        super().__init__("Communicator")
        self.notification_templates = {
            "critical_alert": {
                "title": "CRITICAL: Vehicle {vehicle_reg} requires immediate attention",
                "priority": "urgent",
                "urgency": 1
            },
            "maintenance_scheduled": {
                "title": "Maintenance scheduled for vehicle {vehicle_reg}",
                "priority": "normal",
                "urgency": 3
            },
            "booking_confirmation": {
                "title": "Booking confirmed for {workshop_name}",
                "priority": "normal",
                "urgency": 3
            },
            "health_report": {
                "title": "Weekly health report for fleet",
                "priority": "low",
                "urgency": 4
            }
        }
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process communication requests"""
        action_type = data.get("action", "send_notification")
        
        if action_type == "send_notification":
            return await self._send_notification(data)
        elif action_type == "send_alert":
            return await self._send_alert(data)
        elif action_type == "send_booking_confirmation":
            return await self._send_booking_confirmation(data)
        elif action_type == "send_report":
            return await self._send_report(data)
        elif action_type == "broadcast_message":
            return await self._broadcast_message(data)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def _send_notification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a general notification"""
        recipient_type = data.get("recipient_type", "fleet_manager")
        recipient_id = data.get("recipient_id", "default")
        message_type = data.get("message_type", "info")
        title = data.get("title", "Notification")
        message = data.get("message", "")
        severity = data.get("severity", "info")
        metadata = data.get("metadata", {})
        
        async with AsyncSessionLocal() as session:
            notification = Notification(
                recipient_type=recipient_type,
                recipient_id=recipient_id,
                message_type=message_type,
                title=title,
                message=message,
                severity=severity,
                action_required=severity in ["error", "critical"],
                metadata=metadata
            )
            
            session.add(notification)
            await session.commit()
            await session.refresh(notification)
            
            # Send via multiple channels
            delivery_results = await self._deliver_notification(notification)
            
            return {
                "notification_id": notification.id,
                "recipient": f"{recipient_type}:{recipient_id}",
                "title": title,
                "message_type": message_type,
                "severity": severity,
                "delivery_results": delivery_results,
                "confidence": self._calculate_confidence({
                    "delivery_confidence": delivery_results.get("success_rate", 0.5)
                }),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _send_alert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send critical alerts for urgent situations"""
        vehicle_id = data.get("vehicle_id")
        alert_type = data.get("alert_type", "anomaly")
        severity = data.get("severity", "critical")
        details = data.get("details", {})
        
        async with AsyncSessionLocal() as session:
            # Get vehicle information
            vehicle = await session.get(Vehicle, vehicle_id)
            if not vehicle:
                return {"error": "Vehicle not found", "confidence": 0.0}
            
            # Create alert message
            template = self.notification_templates.get("critical_alert")
            title = template["title"].format(vehicle_reg=vehicle.vehicle_reg)
            
            message = self._generate_alert_message(vehicle, alert_type, details)
            
            # Send to fleet managers
            fleet_notification = await self._create_notification(
                session,
                recipient_type="fleet_manager",
                recipient_id=vehicle.company_id,
                message_type="alert",
                title=title,
                message=message,
                severity=severity,
                metadata={
                    "vehicle_id": vehicle_id,
                    "alert_type": alert_type,
                    "details": details
                }
            )
            
            # Send immediate delivery
            delivery_results = await self._deliver_urgent_alert(fleet_notification, vehicle)
            
            return {
                "alert_id": fleet_notification.id,
                "vehicle_reg": vehicle.vehicle_reg,
                "alert_type": alert_type,
                "severity": severity,
                "recipients_notified": delivery_results.get("recipients_count", 0),
                "delivery_methods": delivery_results.get("methods_used", []),
                "confidence": 0.95,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _send_booking_confirmation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send booking confirmation to relevant parties"""
        booking_id = data.get("booking_id")
        
        async with AsyncSessionLocal() as session:
            # Get booking details
            stmt = select(Booking).where(Booking.id == booking_id)
            result = await session.execute(stmt)
            booking = result.scalar_one_or_none()
            
            if not booking:
                return {"error": "Booking not found", "confidence": 0.0}
            
            # Get vehicle and workshop details
            vehicle = await session.get(Vehicle, booking.vehicle_id)
            stmt = select(Workshop).where(Workshop.workshop_id == booking.workshop_id)
            result = await session.execute(stmt)
            workshop = result.scalar_one_or_none()
            
            notifications_sent = []
            
            # Notify fleet manager
            fleet_message = self._generate_booking_confirmation_message(booking, vehicle, workshop, "fleet")
            fleet_notification = await self._create_notification(
                session,
                recipient_type="fleet_manager",
                recipient_id=vehicle.company_id if vehicle else "default",
                message_type="booking",
                title=f"Booking confirmed for {vehicle.vehicle_reg if vehicle else 'Vehicle'}",
                message=fleet_message,
                severity="info",
                metadata={"booking_id": booking_id}
            )
            notifications_sent.append(fleet_notification.id)
            
            # Notify workshop
            if workshop:
                workshop_message = self._generate_booking_confirmation_message(booking, vehicle, workshop, "workshop")
                workshop_notification = await self._create_notification(
                    session,
                    recipient_type="workshop",
                    recipient_id=booking.workshop_id,
                    message_type="booking",
                    title=f"New booking: {vehicle.vehicle_reg if vehicle else 'Vehicle'}",
                    message=workshop_message,
                    severity="info",
                    metadata={"booking_id": booking_id}
                )
                notifications_sent.append(workshop_notification.id)
            
            # Deliver notifications
            delivery_results = []
            for notification_id in notifications_sent:
                notification = await session.get(Notification, notification_id)
                if notification:
                    result = await self._deliver_notification(notification)
                    delivery_results.append(result)
            
            return {
                "booking_id": booking_id,
                "notifications_sent": len(notifications_sent),
                "notification_ids": notifications_sent,
                "delivery_results": delivery_results,
                "confidence": 0.9,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _send_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send periodic reports to stakeholders"""
        report_type = data.get("report_type", "health")
        recipients = data.get("recipients", [])
        report_data = data.get("report_data", {})
        period = data.get("period", "weekly")
        
        async with AsyncSessionLocal() as session:
            report_content = await self._generate_report_content(report_type, report_data, period)
            
            notifications_sent = []
            
            for recipient in recipients:
                notification = await self._create_notification(
                    session,
                    recipient_type=recipient.get("type", "fleet_manager"),
                    recipient_id=recipient.get("id", "default"),
                    message_type="report",
                    title=f"{period.capitalize()} {report_type} report",
                    message=report_content,
                    severity="info",
                    metadata={
                        "report_type": report_type,
                        "period": period,
                        "generated_at": datetime.utcnow().isoformat()
                    }
                )
                notifications_sent.append(notification.id)
            
            # Deliver reports
            delivery_results = []
            for notification_id in notifications_sent:
                notification = await session.get(Notification, notification_id)
                if notification:
                    result = await self._deliver_notification(notification)
                    delivery_results.append(result)
            
            return {
                "report_type": report_type,
                "period": period,
                "recipients_count": len(recipients),
                "notifications_sent": len(notifications_sent),
                "delivery_results": delivery_results,
                "confidence": 0.85,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _broadcast_message(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Broadcast message to multiple recipients"""
        message = data.get("message", "")
        title = data.get("title", "System Broadcast")
        recipient_types = data.get("recipient_types", ["fleet_manager"])
        severity = data.get("severity", "info")
        metadata = data.get("metadata", {})
        
        async with AsyncSessionLocal() as session:
            notifications_sent = []
            
            for recipient_type in recipient_types:
                # Get all recipients of this type
                recipients = await self._get_recipients_by_type(session, recipient_type)
                
                for recipient_id in recipients:
                    notification = await self._create_notification(
                        session,
                        recipient_type=recipient_type,
                        recipient_id=recipient_id,
                        message_type="broadcast",
                        title=title,
                        message=message,
                        severity=severity,
                        metadata=metadata
                    )
                    notifications_sent.append(notification.id)
            
            # Deliver broadcasts
            delivery_results = []
            for notification_id in notifications_sent:
                notification = await session.get(Notification, notification_id)
                if notification:
                    result = await self._deliver_notification(notification)
                    delivery_results.append(result)
            
            return {
                "broadcast_title": title,
                "recipient_types": recipient_types,
                "total_recipients": len(notifications_sent),
                "delivery_results": delivery_results,
                "confidence": 0.8,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _create_notification(
        self,
        session,
        recipient_type: str,
        recipient_id: str,
        message_type: str,
        title: str,
        message: str,
        severity: str = "info",
        metadata: Dict[str, Any] = None
    ) -> Notification:
        """Create a notification in the database"""
        notification = Notification(
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            message_type=message_type,
            title=title,
            message=message,
            severity=severity,
            action_required=severity in ["error", "critical"],
            metadata=metadata or {}
        )
        
        session.add(notification)
        await session.commit()
        await session.refresh(notification)
        return notification
    
    async def _deliver_notification(self, notification: Notification) -> Dict[str, Any]:
        """Deliver notification via multiple channels"""
        delivery_methods = []
        success_count = 0
        
        # Email delivery (simulated)
        email_result = await self._send_email(notification)
        delivery_methods.append({"method": "email", "success": email_result})
        if email_result:
            success_count += 1
        
        # SMS delivery for critical notifications (simulated)
        if notification.severity in ["critical", "error"]:
            sms_result = await self._send_sms(notification)
            delivery_methods.append({"method": "sms", "success": sms_result})
            if sms_result:
                success_count += 1
        
        # WebSocket/push notification (simulated)
        push_result = await self._send_push_notification(notification)
        delivery_methods.append({"method": "push", "success": push_result})
        if push_result:
            success_count += 1
        
        # In-app notification (always succeeds for this demo)
        delivery_methods.append({"method": "in_app", "success": True})
        success_count += 1
        
        success_rate = success_count / len(delivery_methods)
        
        return {
            "notification_id": notification.id,
            "methods_used": [m["method"] for m in delivery_methods],
            "successful_deliveries": success_count,
            "total_attempts": len(delivery_methods),
            "success_rate": success_rate,
            "delivery_details": delivery_methods
        }
    
    async def _deliver_urgent_alert(self, notification: Notification, vehicle: Vehicle) -> Dict[str, Any]:
        """Deliver urgent alerts with priority channels"""
        delivery_methods = []
        
        # Immediate SMS to all relevant contacts
        sms_result = await self._send_urgent_sms(notification, vehicle)
        delivery_methods.append({"method": "urgent_sms", "success": sms_result})
        
        # Phone call for critical alerts (simulated)
        if notification.severity == "critical":
            call_result = await self._make_emergency_call(notification, vehicle)
            delivery_methods.append({"method": "emergency_call", "success": call_result})
        
        # High priority email
        email_result = await self._send_priority_email(notification)
        delivery_methods.append({"method": "priority_email", "success": email_result})
        
        # Dashboard alert
        dashboard_result = await self._send_dashboard_alert(notification)
        delivery_methods.append({"method": "dashboard_alert", "success": dashboard_result})
        
        successful_deliveries = sum(1 for m in delivery_methods if m["success"])
        
        return {
            "recipients_count": 1,  # Simplified for demo
            "methods_used": [m["method"] for m in delivery_methods],
            "successful_deliveries": successful_deliveries,
            "delivery_details": delivery_methods
        }
    
    def _generate_alert_message(self, vehicle: Vehicle, alert_type: str, details: Dict[str, Any]) -> str:
        """Generate alert message content"""
        base_message = f"""
CRITICAL ALERT - Vehicle {vehicle.vehicle_reg}

Alert Type: {alert_type.upper()}
Vehicle: {vehicle.brand} {vehicle.model}
VIN: {vehicle.vin}
Company: {vehicle.company_id}
Status: {vehicle.status}

Details:
"""
        
        for key, value in details.items():
            base_message += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        base_message += f"""
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

IMMEDIATE ACTION REQUIRED
Please check the vehicle immediately and take appropriate action.
"""
        
        return base_message
    
    def _generate_booking_confirmation_message(
        self, 
        booking: Booking, 
        vehicle: Vehicle, 
        workshop: Workshop, 
        recipient_type: str
    ) -> str:
        """Generate booking confirmation message"""
        if recipient_type == "fleet":
            return f"""
Booking Confirmation - Vehicle {vehicle.vehicle_reg if vehicle else 'Unknown'}

Service Details:
- Service Type: {booking.service_type}
- Priority: {booking.priority}
- Scheduled: {booking.booking_slot.strftime('%Y-%m-%d %H:%M')}
- Duration: {booking.estimated_duration} minutes
- Workshop: {workshop.name if workshop else booking.workshop_name}
- Location: {workshop.location if workshop else 'Unknown'}

Vehicle: {vehicle.brand} {vehicle.model} ({vehicle.vin}) if vehicle else 'Vehicle details unavailable'

Booking ID: {booking.id}
Status: {booking.status}
"""
        else:  # workshop
            return f"""
New Service Booking

Vehicle: {vehicle.vehicle_reg} - {vehicle.brand} {vehicle.model} if vehicle else 'Vehicle details unavailable'
Service: {booking.service_type}
Priority: {booking.priority}
Scheduled: {booking.booking_slot.strftime('%Y-%m-%d %H:%M')}
Duration: {booking.estimated_duration} minutes

Customer: {vehicle.company_id if vehicle else 'Unknown'}
Contact: Please use system for communication

Booking ID: {booking.id}
"""
    
    async def _generate_report_content(self, report_type: str, report_data: Dict[str, Any], period: str) -> str:
        """Generate report content"""
        if report_type == "health":
            return f"""
{period.capitalize()} Fleet Health Report

Summary:
- Total Vehicles: {report_data.get('total_vehicles', 0)}
- Operational: {report_data.get('operational', 0)}
- Warning Status: {report_data.get('warning', 0)}
- Critical Status: {report_data.get('critical', 0)}

Key Metrics:
- Average Health Score: {report_data.get('avg_health_score', 0):.1f}%
- Maintenance Events: {report_data.get('maintenance_events', 0)}
- Average Utilization: {report_data.get('avg_utilization', 0):.1f}%

Top Issues:
- Battery degradation: {report_data.get('battery_issues', 0)} vehicles
- Motor efficiency: {report_data.get('motor_issues', 0)} vehicles
- Cooling system: {report_data.get('cooling_issues', 0)} vehicles

Recommendations:
{self._generate_recommendations(report_data)}

Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
"""
        else:
            return f"{period.capitalize()} {report_type} report - Data not available"
    
    def _generate_recommendations(self, report_data: Dict[str, Any]) -> str:
        """Generate recommendations based on report data"""
        recommendations = []
        
        critical_count = report_data.get('critical', 0)
        warning_count = report_data.get('warning', 0)
        
        if critical_count > 0:
            recommendations.append(f"- Schedule immediate maintenance for {critical_count} critical vehicles")
        
        if warning_count > 0:
            recommendations.append(f"- Plan preventive maintenance for {warning_count} vehicles with warnings")
        
        if report_data.get('battery_issues', 0) > 0:
            recommendations.append("- Consider battery replacement program")
        
        return "\n".join(recommendations) if recommendations else "- Continue current maintenance schedule"
    
    async def _get_recipients_by_type(self, session, recipient_type: str) -> List[str]:
        """Get all recipients of a specific type"""
        # In a real implementation, this would query user/contact databases
        # For demo purposes, return sample recipients
        if recipient_type == "fleet_manager":
            return ["fleet_001", "fleet_002"]
        elif recipient_type == "workshop":
            return ["workshop_001", "workshop_002", "workshop_003"]
        else:
            return ["default"]
    
    # Simulated delivery methods (in real implementation, these would integrate with actual services)
    async def _send_email(self, notification: Notification) -> bool:
        """Send email notification (simulated)"""
        # Simulate email sending
        return True  # Assume success for demo
    
    async def _send_sms(self, notification: Notification) -> bool:
        """Send SMS notification (simulated)"""
        # Simulate SMS sending
        return True  # Assume success for demo
    
    async def _send_push_notification(self, notification: Notification) -> bool:
        """Send push notification (simulated)"""
        # Simulate push notification
        return True  # Assume success for demo
    
    async def _send_urgent_sms(self, notification: Notification, vehicle: Vehicle) -> bool:
        """Send urgent SMS (simulated)"""
        # Simulate urgent SMS
        return True  # Assume success for demo
    
    async def _make_emergency_call(self, notification: Notification, vehicle: Vehicle) -> bool:
        """Make emergency call (simulated)"""
        # Simulate emergency call
        return True  # Assume success for demo
    
    async def _send_priority_email(self, notification: Notification) -> bool:
        """Send priority email (simulated)"""
        # Simulate priority email
        return True  # Assume success for demo
    
    async def _send_dashboard_alert(self, notification: Notification) -> bool:
        """Send dashboard alert (simulated)"""
        # Simulate dashboard alert
        return True  # Assume success for demo