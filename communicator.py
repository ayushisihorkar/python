import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
import json

class CommunicatorAgent:
    """
    AI Agent for notifying rental companies and workshops
    """
    
    def __init__(self, smtp_config: Optional[Dict] = None):
        self.smtp_config = smtp_config or {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password'
        }
        self.logger = logging.getLogger(__name__)
        self.notification_history = []
        
    def send_maintenance_alert(self, vehicle_id: str, alert_data: Dict, recipients: List[str]) -> Dict:
        """
        Send maintenance alert to rental company
        """
        try:
            subject = f"Maintenance Alert - Vehicle {vehicle_id}"
            
            # Create email content
            body = self._create_maintenance_alert_email(vehicle_id, alert_data)
            
            # Send email to each recipient
            for recipient in recipients:
                self._send_email(recipient, subject, body)
            
            notification = {
                'type': 'maintenance_alert',
                'vehicle_id': vehicle_id,
                'recipients': recipients,
                'timestamp': datetime.now().isoformat(),
                'status': 'sent'
            }
            
            self.notification_history.append(notification)
            return notification
            
        except Exception as e:
            self.logger.error(f"Error sending maintenance alert: {str(e)}")
            return {'error': str(e)}
    
    def send_booking_confirmation(self, booking_data: Dict, workshop_email: str) -> Dict:
        """
        Send booking confirmation to workshop
        """
        try:
            subject = f"New Maintenance Booking - {booking_data['workshop_name']}"
            
            # Create email content
            body = self._create_booking_confirmation_email(booking_data)
            
            # Send email to workshop
            self._send_email(workshop_email, subject, body)
            
            notification = {
                'type': 'booking_confirmation',
                'booking_id': booking_data['booking_id'],
                'workshop_email': workshop_email,
                'timestamp': datetime.now().isoformat(),
                'status': 'sent'
            }
            
            self.notification_history.append(notification)
            return notification
            
        except Exception as e:
            self.logger.error(f"Error sending booking confirmation: {str(e)}")
            return {'error': str(e)}
    
    def send_workshop_availability_request(self, workshop_id: str, date: str, services: List[str]) -> Dict:
        """
        Send availability request to workshop
        """
        try:
            subject = f"Availability Request - {date}"
            
            # Create email content
            body = self._create_availability_request_email(workshop_id, date, services)
            
            # Get workshop email (in real app, this would come from database)
            workshop_email = self._get_workshop_email(workshop_id)
            
            if workshop_email:
                self._send_email(workshop_email, subject, body)
                
                notification = {
                    'type': 'availability_request',
                    'workshop_id': workshop_id,
                    'date': date,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'sent'
                }
                
                self.notification_history.append(notification)
                return notification
            else:
                return {'error': 'Workshop email not found'}
                
        except Exception as e:
            self.logger.error(f"Error sending availability request: {str(e)}")
            return {'error': str(e)}
    
    def send_emergency_notification(self, vehicle_id: str, emergency_data: Dict, recipients: List[str]) -> Dict:
        """
        Send emergency notification for critical issues
        """
        try:
            subject = f"EMERGENCY - Vehicle {vehicle_id} Critical Issue"
            
            # Create email content
            body = self._create_emergency_notification_email(vehicle_id, emergency_data)
            
            # Send email to each recipient
            for recipient in recipients:
                self._send_email(recipient, subject, body, priority='high')
            
            notification = {
                'type': 'emergency_notification',
                'vehicle_id': vehicle_id,
                'recipients': recipients,
                'timestamp': datetime.now().isoformat(),
                'status': 'sent'
            }
            
            self.notification_history.append(notification)
            return notification
            
        except Exception as e:
            self.logger.error(f"Error sending emergency notification: {str(e)}")
            return {'error': str(e)}
    
    def _create_maintenance_alert_email(self, vehicle_id: str, alert_data: Dict) -> str:
        """
        Create maintenance alert email content
        """
        body = f"""
        <html>
        <body>
            <h2>Maintenance Alert</h2>
            <p><strong>Vehicle ID:</strong> {vehicle_id}</p>
            <p><strong>Alert Type:</strong> {alert_data.get('type', 'Unknown')}</p>
            <p><strong>Message:</strong> {alert_data.get('message', 'No message')}</p>
            <p><strong>Timestamp:</strong> {alert_data.get('timestamp', datetime.now().isoformat())}</p>
            
            <h3>Details:</h3>
            <ul>
        """
        
        if 'anomalies' in alert_data:
            for anomaly in alert_data['anomalies']:
                body += f"<li><strong>{anomaly['metric']}:</strong> {anomaly['value']} (Threshold: {anomaly['threshold']})</li>"
        
        body += """
            </ul>
            
            <p>Please review and take appropriate action.</p>
            <p>Best regards,<br>Rental Fleet Dashboard</p>
        </body>
        </html>
        """
        
        return body
    
    def _create_booking_confirmation_email(self, booking_data: Dict) -> str:
        """
        Create booking confirmation email content
        """
        body = f"""
        <html>
        <body>
            <h2>New Maintenance Booking</h2>
            <p><strong>Booking ID:</strong> {booking_data['booking_id']}</p>
            <p><strong>Vehicle ID:</strong> {booking_data['vehicle_id']}</p>
            <p><strong>Task Type:</strong> {booking_data['task_type']}</p>
            <p><strong>Scheduled Date:</strong> {booking_data['scheduled_date']}</p>
            <p><strong>Scheduled Time:</strong> {booking_data['scheduled_time']}</p>
            <p><strong>Estimated Duration:</strong> {booking_data['estimated_duration']} hours</p>
            <p><strong>Estimated Cost:</strong> ${booking_data['estimated_cost']:.2f}</p>
            <p><strong>Urgency:</strong> {booking_data['urgency']}</p>
            
            <p>Please confirm this booking and prepare accordingly.</p>
            <p>Best regards,<br>Rental Fleet Dashboard</p>
        </body>
        </html>
        """
        
        return body
    
    def _create_availability_request_email(self, workshop_id: str, date: str, services: List[str]) -> str:
        """
        Create availability request email content
        """
        body = f"""
        <html>
        <body>
            <h2>Availability Request</h2>
            <p><strong>Workshop ID:</strong> {workshop_id}</p>
            <p><strong>Date:</strong> {date}</p>
            <p><strong>Required Services:</strong> {', '.join(services)}</p>
            
            <p>Please provide your availability for the requested date and services.</p>
            <p>Best regards,<br>Rental Fleet Dashboard</p>
        </body>
        </html>
        """
        
        return body
    
    def _create_emergency_notification_email(self, vehicle_id: str, emergency_data: Dict) -> str:
        """
        Create emergency notification email content
        """
        body = f"""
        <html>
        <body style="color: red;">
            <h2>🚨 EMERGENCY ALERT 🚨</h2>
            <p><strong>Vehicle ID:</strong> {vehicle_id}</p>
            <p><strong>Issue:</strong> {emergency_data.get('issue', 'Critical system failure')}</p>
            <p><strong>Severity:</strong> {emergency_data.get('severity', 'Critical')}</p>
            <p><strong>Timestamp:</strong> {emergency_data.get('timestamp', datetime.now().isoformat())}</p>
            
            <p><strong>IMMEDIATE ACTION REQUIRED</strong></p>
            <p>Please contact the vehicle operator and arrange for immediate service.</p>
            
            <p>Best regards,<br>Rental Fleet Dashboard</p>
        </body>
        </html>
        """
        
        return body
    
    def _send_email(self, recipient: str, subject: str, body: str, priority: str = 'normal') -> bool:
        """
        Send email using SMTP
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_config['username']
            msg['To'] = recipient
            
            if priority == 'high':
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            
            # Attach HTML content
            html_part = MIMEText(body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False
    
    def _get_workshop_email(self, workshop_id: str) -> Optional[str]:
        """
        Get workshop email address (simplified - in real app would query database)
        """
        workshop_emails = {
            'ws_001': 'premium@autoservice.com',
            'ws_002': 'quickfix@garage.com',
            'ws_003': 'express@maintenance.com'
        }
        return workshop_emails.get(workshop_id)
    
    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """
        Get recent notification history
        """
        return self.notification_history[-limit:]
    
    def send_sms_notification(self, phone_number: str, message: str) -> Dict:
        """
        Send SMS notification (placeholder - would integrate with SMS service)
        """
        # In a real implementation, this would integrate with Twilio or similar service
        notification = {
            'type': 'sms',
            'phone_number': phone_number,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        self.notification_history.append(notification)
        return notification 