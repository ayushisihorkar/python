from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload

from .base_agent import BaseAgent
from database.database import AsyncSessionLocal
from database.models import Vehicle, VehicleTelemetry, ServiceLog, AgentAction, Booking

class LoggerAgent(BaseAgent):
    """Agent responsible for logging and maintaining historical records"""
    
    def __init__(self):
        super().__init__("Logger")
        self.log_retention_days = {
            "telemetry": 365,  # 1 year
            "agent_actions": 90,  # 3 months
            "service_logs": 1095,  # 3 years
            "notifications": 30  # 1 month
        }
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process logging requests"""
        action_type = data.get("action", "log_telemetry")
        
        if action_type == "log_telemetry":
            return await self._log_telemetry_data(data)
        elif action_type == "log_service_event":
            return await self._log_service_event(data)
        elif action_type == "update_vehicle_status":
            return await self._update_vehicle_status(data)
        elif action_type == "archive_old_data":
            return await self._archive_old_data(data)
        elif action_type == "generate_history_report":
            return await self._generate_history_report(data)
        elif action_type == "audit_trail":
            return await self._create_audit_trail(data)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def _log_telemetry_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Log incoming telemetry data"""
        vehicle_id = data.get("vehicle_id")
        telemetry_data = data.get("telemetry", {})
        timestamp = data.get("timestamp")
        
        if timestamp:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
        else:
            timestamp = datetime.utcnow()
        
        async with AsyncSessionLocal() as session:
            # Verify vehicle exists
            vehicle = await session.get(Vehicle, vehicle_id)
            if not vehicle:
                return {"error": "Vehicle not found", "confidence": 0.0}
            
            # Create telemetry record
            telemetry = VehicleTelemetry(
                vehicle_id=vehicle_id,
                timestamp=timestamp,
                battery_soh=telemetry_data.get("battery_soh"),
                battery_soc=telemetry_data.get("battery_soc"),
                charge_cycles=telemetry_data.get("charge_cycles"),
                voltage_imbalance=telemetry_data.get("voltage_imbalance"),
                battery_temp=telemetry_data.get("battery_temp"),
                motor_rpm=telemetry_data.get("motor_rpm"),
                motor_efficiency=telemetry_data.get("motor_efficiency"),
                motor_temp=telemetry_data.get("motor_temp"),
                coolant_temp=telemetry_data.get("coolant_temp"),
                coolant_level=telemetry_data.get("coolant_level"),
                error_codes=telemetry_data.get("error_codes", [])
            )
            
            session.add(telemetry)
            
            # Update vehicle's current status with latest values
            await self._update_vehicle_current_values(session, vehicle, telemetry_data)
            
            await session.commit()
            await session.refresh(telemetry)
            
            # Check if archiving is needed
            archive_result = await self._check_and_archive_telemetry(session, vehicle_id)
            
            return {
                "telemetry_id": telemetry.id,
                "vehicle_id": vehicle_id,
                "timestamp": timestamp.isoformat(),
                "data_points_logged": len([v for v in telemetry_data.values() if v is not None]),
                "archive_triggered": archive_result.get("archived", False),
                "confidence": 1.0,
                "log_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _log_service_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Log service events and maintenance actions"""
        vehicle_id = data.get("vehicle_id")
        service_type = data.get("service_type", "maintenance")
        description = data.get("description", "")
        service_date = data.get("service_date")
        completed = data.get("completed", False)
        technician = data.get("technician", "")
        workshop_id = data.get("workshop_id", "")
        cost = data.get("cost")
        parts_replaced = data.get("parts_replaced", [])
        notes = data.get("notes", "")
        
        if service_date:
            if isinstance(service_date, str):
                service_date = datetime.fromisoformat(service_date)
        else:
            service_date = datetime.utcnow()
        
        async with AsyncSessionLocal() as session:
            # Verify vehicle exists
            vehicle = await session.get(Vehicle, vehicle_id)
            if not vehicle:
                return {"error": "Vehicle not found", "confidence": 0.0}
            
            # Create service log
            service_log = ServiceLog(
                vehicle_id=vehicle_id,
                service_type=service_type,
                description=description,
                service_date=service_date,
                completed=completed,
                technician=technician,
                workshop_id=workshop_id,
                cost=cost,
                parts_replaced=parts_replaced,
                notes=notes
            )
            
            session.add(service_log)
            
            # Update vehicle's last service date if completed
            if completed:
                vehicle.last_service_date = service_date
                
                # Update vehicle status if it was in maintenance
                if vehicle.status == "maintenance":
                    vehicle.status = "operational"
            
            await session.commit()
            await session.refresh(service_log)
            
            # Create audit trail
            audit_data = {
                "event_type": "service_completed" if completed else "service_scheduled",
                "vehicle_id": vehicle_id,
                "service_log_id": service_log.id,
                "details": {
                    "service_type": service_type,
                    "technician": technician,
                    "workshop_id": workshop_id,
                    "cost": cost
                }
            }
            
            audit_result = await self._create_audit_entry(session, audit_data)
            
            return {
                "service_log_id": service_log.id,
                "vehicle_id": vehicle_id,
                "service_type": service_type,
                "service_date": service_date.isoformat(),
                "completed": completed,
                "audit_trail_id": audit_result.get("audit_id"),
                "confidence": 1.0,
                "log_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _update_vehicle_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update vehicle status and log the change"""
        vehicle_id = data.get("vehicle_id")
        new_status = data.get("status")
        reason = data.get("reason", "System update")
        metadata = data.get("metadata", {})
        
        async with AsyncSessionLocal() as session:
            vehicle = await session.get(Vehicle, vehicle_id)
            if not vehicle:
                return {"error": "Vehicle not found", "confidence": 0.0}
            
            old_status = vehicle.status
            vehicle.status = new_status
            vehicle.updated_at = datetime.utcnow()
            
            await session.commit()
            
            # Create audit trail for status change
            audit_data = {
                "event_type": "status_change",
                "vehicle_id": vehicle_id,
                "details": {
                    "old_status": old_status,
                    "new_status": new_status,
                    "reason": reason,
                    "metadata": metadata
                }
            }
            
            audit_result = await self._create_audit_entry(session, audit_data)
            
            return {
                "vehicle_id": vehicle_id,
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason,
                "audit_trail_id": audit_result.get("audit_id"),
                "confidence": 1.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _archive_old_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Archive or delete old data based on retention policies"""
        data_type = data.get("data_type", "all")
        force_archive = data.get("force", False)
        
        async with AsyncSessionLocal() as session:
            archived_counts = {}
            
            if data_type in ["all", "telemetry"]:
                count = await self._archive_telemetry_data(session, force_archive)
                archived_counts["telemetry"] = count
            
            if data_type in ["all", "agent_actions"]:
                count = await self._archive_agent_actions(session, force_archive)
                archived_counts["agent_actions"] = count
            
            if data_type in ["all", "notifications"]:
                count = await self._archive_notifications(session, force_archive)
                archived_counts["notifications"] = count
            
            await session.commit()
            
            total_archived = sum(archived_counts.values())
            
            return {
                "data_type": data_type,
                "total_records_archived": total_archived,
                "breakdown": archived_counts,
                "confidence": 1.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _generate_history_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate historical analysis report"""
        vehicle_id = data.get("vehicle_id")
        report_type = data.get("report_type", "comprehensive")
        days_back = data.get("days_back", 30)
        
        async with AsyncSessionLocal() as session:
            vehicle = await session.get(Vehicle, vehicle_id)
            if not vehicle:
                return {"error": "Vehicle not found", "confidence": 0.0}
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get telemetry history
            telemetry_stats = await self._get_telemetry_statistics(session, vehicle_id, cutoff_date)
            
            # Get service history
            service_history = await self._get_service_history(session, vehicle_id, cutoff_date)
            
            # Get agent actions history
            agent_activity = await self._get_agent_activity(session, vehicle_id, cutoff_date)
            
            # Generate insights
            insights = self._generate_historical_insights(telemetry_stats, service_history, agent_activity)
            
            report = {
                "vehicle_id": vehicle_id,
                "vehicle_reg": vehicle.vehicle_reg,
                "report_type": report_type,
                "period_days": days_back,
                "period_start": cutoff_date.isoformat(),
                "period_end": datetime.utcnow().isoformat(),
                "telemetry_statistics": telemetry_stats,
                "service_history": service_history,
                "agent_activity": agent_activity,
                "insights": insights,
                "confidence": 0.9,
                "generated_at": datetime.utcnow().isoformat()
            }
            
            return report
    
    async def _create_audit_trail(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create audit trail entry"""
        async with AsyncSessionLocal() as session:
            audit_result = await self._create_audit_entry(session, data)
            await session.commit()
            
            return {
                "audit_trail_id": audit_result.get("audit_id"),
                "event_type": data.get("event_type"),
                "confidence": 1.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _update_vehicle_current_values(self, session, vehicle: Vehicle, telemetry_data: Dict[str, Any]):
        """Update vehicle's current values from telemetry"""
        for field, value in telemetry_data.items():
            if value is not None and hasattr(vehicle, field):
                setattr(vehicle, field, value)
        
        vehicle.updated_at = datetime.utcnow()
    
    async def _check_and_archive_telemetry(self, session, vehicle_id: int) -> Dict[str, Any]:
        """Check if telemetry archiving is needed and perform it"""
        retention_days = self.log_retention_days["telemetry"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Count old records
        stmt = select(func.count(VehicleTelemetry.id)).where(
            and_(
                VehicleTelemetry.vehicle_id == vehicle_id,
                VehicleTelemetry.timestamp < cutoff_date
            )
        )
        result = await session.execute(stmt)
        old_count = result.scalar()
        
        if old_count > 1000:  # Archive if more than 1000 old records
            # In a real implementation, you would move data to archive storage
            # For now, we'll just mark it as archived
            return {"archived": True, "count": old_count}
        
        return {"archived": False, "count": old_count}
    
    async def _archive_telemetry_data(self, session, force: bool = False) -> int:
        """Archive old telemetry data"""
        retention_days = self.log_retention_days["telemetry"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # In a real implementation, this would move data to archive storage
        # For demo, we'll count what would be archived
        stmt = select(func.count(VehicleTelemetry.id)).where(
            VehicleTelemetry.timestamp < cutoff_date
        )
        result = await session.execute(stmt)
        count = result.scalar()
        
        return count
    
    async def _archive_agent_actions(self, session, force: bool = False) -> int:
        """Archive old agent actions"""
        retention_days = self.log_retention_days["agent_actions"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        stmt = select(func.count(AgentAction.id)).where(
            AgentAction.timestamp < cutoff_date
        )
        result = await session.execute(stmt)
        count = result.scalar()
        
        return count
    
    async def _archive_notifications(self, session, force: bool = False) -> int:
        """Archive old notifications"""
        from database.models import Notification
        
        retention_days = self.log_retention_days["notifications"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        stmt = select(func.count(Notification.id)).where(
            Notification.created_at < cutoff_date
        )
        result = await session.execute(stmt)
        count = result.scalar()
        
        return count
    
    async def _get_telemetry_statistics(self, session, vehicle_id: int, cutoff_date: datetime) -> Dict[str, Any]:
        """Get telemetry statistics for the period"""
        stmt = select(VehicleTelemetry).where(
            and_(
                VehicleTelemetry.vehicle_id == vehicle_id,
                VehicleTelemetry.timestamp >= cutoff_date
            )
        ).order_by(VehicleTelemetry.timestamp)
        
        result = await session.execute(stmt)
        telemetry_records = result.scalars().all()
        
        if not telemetry_records:
            return {"records_count": 0, "metrics": {}}
        
        # Calculate statistics
        battery_soh_values = [t.battery_soh for t in telemetry_records if t.battery_soh is not None]
        battery_temp_values = [t.battery_temp for t in telemetry_records if t.battery_temp is not None]
        motor_efficiency_values = [t.motor_efficiency for t in telemetry_records if t.motor_efficiency is not None]
        
        stats = {
            "records_count": len(telemetry_records),
            "metrics": {
                "battery_soh": self._calculate_metric_stats(battery_soh_values),
                "battery_temp": self._calculate_metric_stats(battery_temp_values),
                "motor_efficiency": self._calculate_metric_stats(motor_efficiency_values)
            },
            "error_codes_frequency": self._analyze_error_codes(telemetry_records),
            "data_quality": {
                "completeness": self._calculate_data_completeness(telemetry_records),
                "consistency": self._check_data_consistency(telemetry_records)
            }
        }
        
        return stats
    
    async def _get_service_history(self, session, vehicle_id: int, cutoff_date: datetime) -> Dict[str, Any]:
        """Get service history for the period"""
        stmt = select(ServiceLog).where(
            and_(
                ServiceLog.vehicle_id == vehicle_id,
                ServiceLog.service_date >= cutoff_date
            )
        ).order_by(ServiceLog.service_date)
        
        result = await session.execute(stmt)
        service_logs = result.scalars().all()
        
        # Analyze service patterns
        service_types = {}
        total_cost = 0
        completed_services = 0
        
        for log in service_logs:
            service_types[log.service_type] = service_types.get(log.service_type, 0) + 1
            if log.cost:
                total_cost += log.cost
            if log.completed:
                completed_services += 1
        
        return {
            "total_services": len(service_logs),
            "completed_services": completed_services,
            "service_types": service_types,
            "total_cost": total_cost,
            "average_cost": total_cost / len(service_logs) if service_logs else 0,
            "completion_rate": completed_services / len(service_logs) if service_logs else 0
        }
    
    async def _get_agent_activity(self, session, vehicle_id: int, cutoff_date: datetime) -> Dict[str, Any]:
        """Get agent activity for the period"""
        stmt = select(AgentAction).where(
            and_(
                AgentAction.vehicle_id == vehicle_id,
                AgentAction.timestamp >= cutoff_date
            )
        ).order_by(AgentAction.timestamp)
        
        result = await session.execute(stmt)
        actions = result.scalars().all()
        
        # Analyze agent activity
        agent_stats = {}
        action_types = {}
        successful_actions = 0
        
        for action in actions:
            agent_stats[action.agent_name] = agent_stats.get(action.agent_name, 0) + 1
            action_types[action.action_type] = action_types.get(action.action_type, 0) + 1
            if action.status == "completed":
                successful_actions += 1
        
        return {
            "total_actions": len(actions),
            "successful_actions": successful_actions,
            "success_rate": successful_actions / len(actions) if actions else 0,
            "agent_activity": agent_stats,
            "action_types": action_types,
            "average_processing_time": self._calculate_average_processing_time(actions)
        }
    
    def _calculate_metric_stats(self, values: List[float]) -> Dict[str, Any]:
        """Calculate statistics for a metric"""
        if not values:
            return {"count": 0}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "average": sum(values) / len(values),
            "latest": values[-1],
            "trend": "stable"  # Simplified trend analysis
        }
    
    def _analyze_error_codes(self, telemetry_records: List[VehicleTelemetry]) -> Dict[str, int]:
        """Analyze frequency of error codes"""
        error_frequency = {}
        
        for record in telemetry_records:
            if record.error_codes:
                for code in record.error_codes:
                    error_frequency[code] = error_frequency.get(code, 0) + 1
        
        return error_frequency
    
    def _calculate_data_completeness(self, telemetry_records: List[VehicleTelemetry]) -> float:
        """Calculate data completeness percentage"""
        if not telemetry_records:
            return 0.0
        
        total_fields = 10  # Number of telemetry fields
        complete_records = 0
        
        for record in telemetry_records:
            filled_fields = sum(1 for field in [
                record.battery_soh, record.battery_soc, record.charge_cycles,
                record.voltage_imbalance, record.battery_temp, record.motor_rpm,
                record.motor_efficiency, record.motor_temp, record.coolant_temp,
                record.coolant_level
            ] if field is not None)
            
            if filled_fields >= total_fields * 0.8:  # 80% complete
                complete_records += 1
        
        return complete_records / len(telemetry_records)
    
    def _check_data_consistency(self, telemetry_records: List[VehicleTelemetry]) -> float:
        """Check data consistency (simplified)"""
        if len(telemetry_records) < 2:
            return 1.0
        
        # Simple consistency check - no dramatic jumps in values
        consistent_records = 0
        
        for i in range(1, len(telemetry_records)):
            current = telemetry_records[i]
            previous = telemetry_records[i-1]
            
            # Check battery SOH consistency (shouldn't jump more than 5% between readings)
            if (current.battery_soh is not None and previous.battery_soh is not None):
                if abs(current.battery_soh - previous.battery_soh) <= 5:
                    consistent_records += 1
        
        return consistent_records / (len(telemetry_records) - 1) if len(telemetry_records) > 1 else 1.0
    
    def _calculate_average_processing_time(self, actions: List[AgentAction]) -> float:
        """Calculate average processing time for actions"""
        processing_times = [action.processing_time for action in actions if action.processing_time is not None]
        return sum(processing_times) / len(processing_times) if processing_times else 0.0
    
    def _generate_historical_insights(
        self, 
        telemetry_stats: Dict[str, Any], 
        service_history: Dict[str, Any], 
        agent_activity: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from historical data"""
        insights = []
        
        # Telemetry insights
        battery_metrics = telemetry_stats.get("metrics", {}).get("battery_soh", {})
        if battery_metrics.get("count", 0) > 0:
            avg_soh = battery_metrics.get("average", 0)
            if avg_soh < 80:
                insights.append(f"Battery health declining - average SOH: {avg_soh:.1f}%")
            elif avg_soh > 95:
                insights.append("Battery health excellent")
        
        # Service insights
        completion_rate = service_history.get("completion_rate", 0)
        if completion_rate < 0.8:
            insights.append(f"Service completion rate low: {completion_rate:.1%}")
        
        # Agent activity insights
        success_rate = agent_activity.get("success_rate", 0)
        if success_rate < 0.9:
            insights.append(f"Agent processing issues - success rate: {success_rate:.1%}")
        
        if not insights:
            insights.append("All systems operating normally")
        
        return insights
    
    async def _create_audit_entry(self, session, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an audit trail entry"""
        # In a real implementation, this would use a dedicated audit table
        # For now, we'll use the AgentAction table to store audit information
        audit_action = AgentAction(
            agent_name="Logger",
            action_type="audit_trail",
            vehicle_id=audit_data.get("vehicle_id"),
            input_data=audit_data,
            output_data={"audit_created": True},
            status="completed",
            confidence_score=1.0,
            processing_time=0.1
        )
        
        session.add(audit_action)
        await session.commit()
        await session.refresh(audit_action)
        
        return {"audit_id": audit_action.id}