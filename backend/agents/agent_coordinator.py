import asyncio
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .health_monitor_agent import HealthMonitorAgent
from .planner_agent import PlannerAgent
from .communicator_agent import CommunicatorAgent
from .logger_agent import LoggerAgent

class AgentCoordinator:
    """Coordinates all agents in the fleet maintenance system"""
    
    def __init__(self):
        self.logger = logging.getLogger("agent_coordinator")
        
        # Initialize all agents
        self.health_monitor = HealthMonitorAgent()
        self.planner = PlannerAgent()
        self.communicator = CommunicatorAgent()
        self.logger_agent = LoggerAgent()
        
        self.agents = {
            "health_monitor": self.health_monitor,
            "planner": self.planner,
            "communicator": self.communicator,
            "logger": self.logger_agent
        }
        
        self.running = False
        self._coordinator_task = None
        
    async def start(self):
        """Start all agents and the coordinator"""
        self.logger.info("Starting Agent Coordinator...")
        
        # Start all individual agents
        for name, agent in self.agents.items():
            try:
                await agent.start()
                self.logger.info(f"Started {name} agent")
            except Exception as e:
                self.logger.error(f"Failed to start {name} agent: {e}")
        
        self.running = True
        self._coordinator_task = asyncio.create_task(self._coordination_loop())
        self.logger.info("Agent Coordinator started successfully")
        
    async def stop(self):
        """Stop all agents and the coordinator"""
        self.logger.info("Stopping Agent Coordinator...")
        self.running = False
        
        # Stop coordination loop
        if self._coordinator_task:
            self._coordinator_task.cancel()
            try:
                await self._coordinator_task
            except asyncio.CancelledError:
                pass
        
        # Stop all individual agents
        for name, agent in self.agents.items():
            try:
                await agent.stop()
                self.logger.info(f"Stopped {name} agent")
            except Exception as e:
                self.logger.error(f"Failed to stop {name} agent: {e}")
        
        self.logger.info("Agent Coordinator stopped")
        
    async def _coordination_loop(self):
        """Main coordination loop that orchestrates agent interactions"""
        while self.running:
            try:
                # Coordinator runs at a slower interval than individual agents
                await asyncio.sleep(10)
                
                # Perform periodic coordination tasks
                await self._check_agent_health()
                await self._process_multi_agent_workflows()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in coordination loop: {e}")
                await asyncio.sleep(30)  # Back off on error
    
    async def process_vehicle_telemetry(self, vehicle_id: int, telemetry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming vehicle telemetry through the multi-agent pipeline"""
        workflow_results = {}
        
        try:
            # Step 1: Log the telemetry data
            log_result = await self.logger_agent.execute_with_logging(
                "log_telemetry",
                {
                    "vehicle_id": vehicle_id,
                    "telemetry": telemetry_data,
                    "timestamp": datetime.utcnow().isoformat()
                },
                vehicle_id
            )
            workflow_results["logging"] = log_result
            
            # Step 2: Health monitoring and anomaly detection
            health_result = await self.health_monitor.execute_with_logging(
                "anomaly_detection",
                {
                    "vehicle_id": vehicle_id,
                    "telemetry": telemetry_data
                },
                vehicle_id
            )
            workflow_results["health_monitoring"] = health_result
            
            # Step 3: If anomalies detected, trigger planning and communication
            if health_result.get("anomalies_detected", 0) > 0:
                severity = health_result.get("overall_severity", 0)
                
                # Determine priority based on severity
                if severity >= 0.8:
                    priority = "critical"
                elif severity >= 0.6:
                    priority = "high"
                else:
                    priority = "normal"
                
                # Create booking if needed
                if severity >= 0.6:  # High or critical severity
                    booking_result = await self.planner.execute_with_logging(
                        "schedule_booking",
                        {
                            "vehicle_id": vehicle_id,
                            "service_type": "corrective",
                            "priority": priority,
                            "predicted_issue": health_result.get("anomalies", [{}])[0].get("message", ""),
                            "confidence_score": health_result.get("confidence", 0.5),
                            "recommended_actions": ["Immediate inspection required"]
                        },
                        vehicle_id
                    )
                    workflow_results["booking"] = booking_result
                    
                    # Send booking confirmation
                    if booking_result.get("booking_id"):
                        comm_result = await self.communicator.execute_with_logging(
                            "send_booking_confirmation",
                            {"booking_id": booking_result["booking_id"]},
                            vehicle_id
                        )
                        workflow_results["booking_communication"] = comm_result
                
                # Send alert for high/critical issues
                if severity >= 0.6:
                    alert_result = await self.communicator.execute_with_logging(
                        "send_alert",
                        {
                            "vehicle_id": vehicle_id,
                            "alert_type": "anomaly_detected",
                            "severity": "critical" if severity >= 0.8 else "warning",
                            "details": {
                                "anomalies": health_result.get("anomalies", []),
                                "overall_severity": severity,
                                "telemetry_snapshot": telemetry_data
                            }
                        },
                        vehicle_id
                    )
                    workflow_results["alert_communication"] = alert_result
            
            return {
                "vehicle_id": vehicle_id,
                "workflow_completed": True,
                "steps_executed": list(workflow_results.keys()),
                "results": workflow_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing telemetry for vehicle {vehicle_id}: {e}")
            return {
                "vehicle_id": vehicle_id,
                "workflow_completed": False,
                "error": str(e),
                "partial_results": workflow_results,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def perform_health_check(self, vehicle_id: int) -> Dict[str, Any]:
        """Perform comprehensive health check using health monitor agent"""
        try:
            result = await self.health_monitor.execute_with_logging(
                "health_check",
                {"vehicle_id": vehicle_id},
                vehicle_id
            )
            
            # If issues found, trigger follow-up actions
            if result.get("status") in ["warning", "critical"]:
                # Log the health status change
                await self.logger_agent.execute_with_logging(
                    "update_vehicle_status",
                    {
                        "vehicle_id": vehicle_id,
                        "status": result.get("status"),
                        "reason": "Health check results",
                        "metadata": {
                            "health_score": result.get("overall_health_score"),
                            "issues": result.get("recommendations", [])
                        }
                    },
                    vehicle_id
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error performing health check for vehicle {vehicle_id}: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def schedule_maintenance(self, vehicle_id: int, service_type: str = "preventive", priority: str = "normal") -> Dict[str, Any]:
        """Schedule maintenance using planner agent"""
        try:
            # Get health assessment first
            health_result = await self.health_monitor.execute_with_logging(
                "health_check",
                {"vehicle_id": vehicle_id},
                vehicle_id
            )
            
            # Schedule booking
            booking_result = await self.planner.execute_with_logging(
                "schedule_booking",
                {
                    "vehicle_id": vehicle_id,
                    "service_type": service_type,
                    "priority": priority,
                    "predicted_issue": f"{service_type} maintenance",
                    "confidence_score": health_result.get("confidence", 0.8),
                    "recommended_actions": health_result.get("recommendations", [])
                },
                vehicle_id
            )
            
            # Send confirmation if booking successful
            if booking_result.get("booking_id"):
                await self.communicator.execute_with_logging(
                    "send_booking_confirmation",
                    {"booking_id": booking_result["booking_id"]},
                    vehicle_id
                )
                
                # Log the maintenance scheduling
                await self.logger_agent.execute_with_logging(
                    "log_service_event",
                    {
                        "vehicle_id": vehicle_id,
                        "service_type": service_type,
                        "description": f"Scheduled {service_type} maintenance",
                        "completed": False,
                        "notes": f"Auto-scheduled with priority: {priority}"
                    },
                    vehicle_id
                )
            
            return booking_result
            
        except Exception as e:
            self.logger.error(f"Error scheduling maintenance for vehicle {vehicle_id}: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def generate_fleet_report(self, company_id: str = "all", report_type: str = "health") -> Dict[str, Any]:
        """Generate comprehensive fleet report"""
        try:
            # This would typically query multiple vehicles
            # For demo, we'll use sample data
            report_data = {
                "total_vehicles": 50,
                "operational": 45,
                "warning": 4,
                "critical": 1,
                "avg_health_score": 87.5,
                "maintenance_events": 12,
                "avg_utilization": 75.2,
                "battery_issues": 2,
                "motor_issues": 1,
                "cooling_issues": 1
            }
            
            recipients = [
                {"type": "fleet_manager", "id": company_id}
            ]
            
            result = await self.communicator.execute_with_logging(
                "send_report",
                {
                    "report_type": report_type,
                    "recipients": recipients,
                    "report_data": report_data,
                    "period": "weekly"
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error generating fleet report: {e}")
            return {"error": str(e), "confidence": 0.0}
    
    async def handle_emergency(self, vehicle_id: int, emergency_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle emergency situations with highest priority"""
        try:
            workflow_results = {}
            
            # Immediate alert
            alert_result = await self.communicator.execute_with_logging(
                "send_alert",
                {
                    "vehicle_id": vehicle_id,
                    "alert_type": "emergency",
                    "severity": "critical",
                    "details": emergency_data
                },
                vehicle_id
            )
            workflow_results["emergency_alert"] = alert_result
            
            # Emergency booking
            booking_result = await self.planner.execute_with_logging(
                "schedule_booking",
                {
                    "vehicle_id": vehicle_id,
                    "service_type": "emergency",
                    "priority": "critical",
                    "predicted_issue": emergency_data.get("issue", "Emergency situation"),
                    "confidence_score": 1.0
                },
                vehicle_id
            )
            workflow_results["emergency_booking"] = booking_result
            
            # Update vehicle status
            status_result = await self.logger_agent.execute_with_logging(
                "update_vehicle_status",
                {
                    "vehicle_id": vehicle_id,
                    "status": "critical",
                    "reason": "Emergency situation",
                    "metadata": emergency_data
                },
                vehicle_id
            )
            workflow_results["status_update"] = status_result
            
            return {
                "emergency_handled": True,
                "vehicle_id": vehicle_id,
                "actions_taken": list(workflow_results.keys()),
                "results": workflow_results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error handling emergency for vehicle {vehicle_id}: {e}")
            return {"error": str(e), "emergency_handled": False}
    
    async def _check_agent_health(self):
        """Check health of all agents"""
        for name, agent in self.agents.items():
            if not agent.running:
                self.logger.warning(f"Agent {name} is not running")
                # Could implement restart logic here
    
    async def _process_multi_agent_workflows(self):
        """Process any pending multi-agent workflows"""
        # This could check for scheduled tasks, pending approvals, etc.
        # For now, it's a placeholder for future expansion
        pass
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        status = {
            "coordinator_running": self.running,
            "agents": {}
        }
        
        for name, agent in self.agents.items():
            status["agents"][name] = {
                "running": agent.running,
                "name": agent.name
            }
        
        return status
    
    async def execute_agent_action(self, agent_name: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action on a specific agent"""
        if agent_name not in self.agents:
            return {"error": f"Agent {agent_name} not found", "confidence": 0.0}
        
        agent = self.agents[agent_name]
        
        try:
            data["action"] = action
            result = await agent.execute_with_logging(
                action,
                data,
                data.get("vehicle_id")
            )
            return result
        except Exception as e:
            self.logger.error(f"Error executing {action} on {agent_name}: {e}")
            return {"error": str(e), "confidence": 0.0}