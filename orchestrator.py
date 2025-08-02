import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import json

from .health_monitor import HealthMonitorAgent
from .planner import PlannerAgent, MaintenanceTask
from .communicator import CommunicatorAgent
from .logger import LoggerAgent

class OrchestratorAgent:
    """
    AI Agent that coordinates multi-agent workflows and manages the overall system
    """
    
    def __init__(self):
        self.health_monitor = HealthMonitorAgent()
        self.planner = PlannerAgent()
        self.communicator = CommunicatorAgent()
        self.logger_agent = LoggerAgent()
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.active_vehicles = {}
        self.pending_maintenance = []
        self.system_status = 'operational'
        
    async def process_vehicle_telemetry(self, vehicle_id: str, telemetry_data: Dict) -> Dict:
        """
        Process incoming vehicle telemetry through the complete workflow
        """
        try:
            self.logger.info(f"Processing telemetry for vehicle {vehicle_id}")
            
            # Step 1: Health monitoring
            health_analysis = self.health_monitor.analyze_telemetry(vehicle_id, telemetry_data)
            
            # Step 2: Log health check
            self.logger_agent.log_health_check(vehicle_id, health_analysis)
            
            # Step 3: Update vehicle state
            self.active_vehicles[vehicle_id] = {
                'last_telemetry': telemetry_data,
                'health_analysis': health_analysis,
                'last_updated': datetime.now().isoformat()
            }
            
            # Step 4: Check for critical issues
            if health_analysis.get('health_score', 100) < 50:
                await self._handle_critical_issue(vehicle_id, health_analysis)
            
            # Step 5: Process maintenance predictions
            if health_analysis.get('maintenance_predictions'):
                await self._process_maintenance_predictions(vehicle_id, health_analysis['maintenance_predictions'])
            
            # Step 6: Send alerts if needed
            if health_analysis.get('alerts'):
                await self._send_alerts(vehicle_id, health_analysis['alerts'])
            
            return {
                'vehicle_id': vehicle_id,
                'status': 'processed',
                'health_score': health_analysis.get('health_score'),
                'alerts_count': len(health_analysis.get('alerts', [])),
                'maintenance_predictions_count': len(health_analysis.get('maintenance_predictions', [])),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing telemetry for vehicle {vehicle_id}: {str(e)}")
            return {'error': str(e)}
    
    async def schedule_maintenance_workflow(self, vehicle_id: str, maintenance_tasks: List[Dict]) -> Dict:
        """
        Coordinate the complete maintenance scheduling workflow
        """
        try:
            self.logger.info(f"Scheduling maintenance for vehicle {vehicle_id}")
            
            # Step 1: Convert to MaintenanceTask objects
            tasks = []
            for task_data in maintenance_tasks:
                task = MaintenanceTask(
                    vehicle_id=vehicle_id,
                    task_type=task_data['task_type'],
                    urgency=task_data.get('urgency', 'medium'),
                    estimated_duration=task_data.get('estimated_duration', 2),
                    estimated_cost=task_data.get('estimated_cost', 100.0)
                )
                tasks.append(task)
            
            # Step 2: Schedule with planner
            scheduled_bookings = self.planner.schedule_maintenance(tasks)
            
            # Step 3: Log bookings
            for booking in scheduled_bookings:
                self.logger_agent.log_booking(booking)
                
                # Step 4: Send notifications
                await self._send_booking_notifications(booking)
            
            # Step 5: Log audit event
            self.logger_agent.log_audit_event(
                action_type='maintenance_scheduled',
                entity_type='vehicle',
                entity_id=vehicle_id,
                details={'bookings': scheduled_bookings}
            )
            
            return {
                'vehicle_id': vehicle_id,
                'scheduled_bookings': scheduled_bookings,
                'total_bookings': len(scheduled_bookings),
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling maintenance for vehicle {vehicle_id}: {str(e)}")
            return {'error': str(e)}
    
    async def handle_emergency_situation(self, vehicle_id: str, emergency_data: Dict) -> Dict:
        """
        Handle emergency situations with immediate response
        """
        try:
            self.logger.warning(f"Emergency situation for vehicle {vehicle_id}")
            
            # Step 1: Log emergency
            self.logger_agent.log_audit_event(
                action_type='emergency_declared',
                entity_type='vehicle',
                entity_id=vehicle_id,
                details=emergency_data
            )
            
            # Step 2: Send emergency notifications
            recipients = ['fleet-manager@company.com', 'emergency@company.com']
            notification_result = self.communicator.send_emergency_notification(
                vehicle_id, emergency_data, recipients
            )
            
            # Step 3: Update system status
            self.system_status = 'emergency'
            
            # Step 4: Create immediate maintenance task
            emergency_task = MaintenanceTask(
                vehicle_id=vehicle_id,
                task_type='emergency_repair',
                urgency='critical',
                estimated_duration=4,
                estimated_cost=500.0
            )
            
            # Step 5: Schedule emergency maintenance
            emergency_bookings = self.planner.schedule_maintenance([emergency_task])
            
            return {
                'vehicle_id': vehicle_id,
                'emergency_data': emergency_data,
                'notification_sent': notification_result,
                'emergency_bookings': emergency_bookings,
                'status': 'emergency_handled',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error handling emergency for vehicle {vehicle_id}: {str(e)}")
            return {'error': str(e)}
    
    async def generate_fleet_report(self, start_date: str, end_date: str) -> Dict:
        """
        Generate comprehensive fleet report
        """
        try:
            self.logger.info("Generating fleet report")
            
            report = {
                'period': {'start_date': start_date, 'end_date': end_date},
                'fleet_summary': {},
                'maintenance_summary': {},
                'health_summary': {},
                'cost_analysis': {},
                'generated_at': datetime.now().isoformat()
            }
            
            # Get fleet summary
            report['fleet_summary'] = {
                'total_vehicles': len(self.active_vehicles),
                'operational_vehicles': len([v for v in self.active_vehicles.values() 
                                           if v['health_analysis'].get('health_score', 0) > 70]),
                'maintenance_required': len([v for v in self.active_vehicles.values() 
                                           if v['health_analysis'].get('health_score', 0) < 50])
            }
            
            # Get maintenance summary for each vehicle
            maintenance_summary = {}
            total_cost = 0.0
            
            for vehicle_id in self.active_vehicles.keys():
                maintenance_report = self.logger_agent.export_maintenance_report(
                    vehicle_id, start_date, end_date
                )
                
                if 'error' not in maintenance_report:
                    maintenance_summary[vehicle_id] = maintenance_report
                    total_cost += maintenance_report.get('total_cost', 0.0)
            
            report['maintenance_summary'] = maintenance_summary
            report['cost_analysis'] = {
                'total_maintenance_cost': total_cost,
                'average_cost_per_vehicle': total_cost / len(self.active_vehicles) if self.active_vehicles else 0
            }
            
            # Get health summary
            health_scores = [v['health_analysis'].get('health_score', 0) 
                           for v in self.active_vehicles.values()]
            
            report['health_summary'] = {
                'average_health_score': sum(health_scores) / len(health_scores) if health_scores else 0,
                'vehicles_above_80': len([score for score in health_scores if score > 80]),
                'vehicles_below_50': len([score for score in health_scores if score < 50])
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating fleet report: {str(e)}")
            return {'error': str(e)}
    
    async def _handle_critical_issue(self, vehicle_id: str, health_analysis: Dict):
        """
        Handle critical vehicle issues
        """
        try:
            # Send immediate notification
            recipients = ['fleet-manager@company.com']
            self.communicator.send_maintenance_alert(vehicle_id, health_analysis, recipients)
            
            # Log critical issue
            self.logger_agent.log_audit_event(
                action_type='critical_issue_detected',
                entity_type='vehicle',
                entity_id=vehicle_id,
                details=health_analysis
            )
            
        except Exception as e:
            self.logger.error(f"Error handling critical issue: {str(e)}")
    
    async def _process_maintenance_predictions(self, vehicle_id: str, predictions: List[Dict]):
        """
        Process maintenance predictions and create tasks
        """
        try:
            for prediction in predictions:
                if prediction.get('urgency') == 'high':
                    # Create immediate maintenance task
                    task = MaintenanceTask(
                        vehicle_id=vehicle_id,
                        task_type=prediction['type'],
                        urgency=prediction['urgency'],
                        estimated_duration=prediction.get('estimated_duration', 2),
                        estimated_cost=prediction.get('estimated_cost', 100.0)
                    )
                    
                    # Schedule maintenance
                    bookings = self.planner.schedule_maintenance([task])
                    
                    if bookings:
                        # Log the booking
                        self.logger_agent.log_booking(bookings[0])
                        
                        # Send notification
                        await self._send_booking_notifications(bookings[0])
            
        except Exception as e:
            self.logger.error(f"Error processing maintenance predictions: {str(e)}")
    
    async def _send_alerts(self, vehicle_id: str, alerts: List[Dict]):
        """
        Send alerts to appropriate recipients
        """
        try:
            recipients = ['fleet-manager@company.com']
            
            for alert in alerts:
                if alert.get('type') == 'critical':
                    self.communicator.send_maintenance_alert(vehicle_id, alert, recipients)
                    
        except Exception as e:
            self.logger.error(f"Error sending alerts: {str(e)}")
    
    async def _send_booking_notifications(self, booking: Dict):
        """
        Send booking notifications to workshop
        """
        try:
            workshop_email = self.communicator._get_workshop_email(booking['workshop_id'])
            if workshop_email:
                self.communicator.send_booking_confirmation(booking, workshop_email)
                
        except Exception as e:
            self.logger.error(f"Error sending booking notifications: {str(e)}")
    
    def get_system_status(self) -> Dict:
        """
        Get current system status
        """
        return {
            'status': self.system_status,
            'active_vehicles': len(self.active_vehicles),
            'pending_maintenance': len(self.pending_maintenance),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_vehicle_status(self, vehicle_id: str) -> Optional[Dict]:
        """
        Get status of a specific vehicle
        """
        return self.active_vehicles.get(vehicle_id)
    
    async def shutdown(self):
        """
        Graceful shutdown of the orchestrator
        """
        try:
            self.logger.info("Shutting down orchestrator agent")
            self.system_status = 'shutdown'
            
            # Save final state
            final_state = {
                'active_vehicles': len(self.active_vehicles),
                'system_status': self.system_status,
                'shutdown_time': datetime.now().isoformat()
            }
            
            self.logger_agent.log_audit_event(
                action_type='system_shutdown',
                entity_type='system',
                entity_id='orchestrator',
                details=final_state
            )
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}") 