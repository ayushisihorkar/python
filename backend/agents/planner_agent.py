from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from .base_agent import BaseAgent
from database.database import AsyncSessionLocal
from database.models import Vehicle, Booking, Workshop, ServiceLog

class PlannerAgent(BaseAgent):
    """Agent responsible for coordinating bookings and managing workshop schedules"""
    
    def __init__(self):
        super().__init__("Planner")
        self.booking_priorities = {
            "critical": {"urgency": 1, "max_delay_hours": 24},
            "high": {"urgency": 2, "max_delay_hours": 72},
            "normal": {"urgency": 3, "max_delay_hours": 168},  # 1 week
            "low": {"urgency": 4, "max_delay_hours": 336}      # 2 weeks
        }
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process booking and scheduling requests"""
        action_type = data.get("action", "schedule_booking")
        
        if action_type == "schedule_booking":
            return await self._schedule_booking(data)
        elif action_type == "find_workshops":
            return await self._find_available_workshops(data)
        elif action_type == "optimize_schedule":
            return await self._optimize_booking_schedule(data)
        elif action_type == "update_booking":
            return await self._update_booking(data)
        elif action_type == "cancel_booking":
            return await self._cancel_booking(data)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def _schedule_booking(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a new booking for a vehicle"""
        vehicle_id = data.get("vehicle_id")
        service_type = data.get("service_type", "maintenance")
        priority = data.get("priority", "normal")
        predicted_issue = data.get("predicted_issue", "")
        confidence_score = data.get("confidence_score", 0.5)
        
        async with AsyncSessionLocal() as session:
            # Get vehicle information
            vehicle = await session.get(Vehicle, vehicle_id)
            if not vehicle:
                return {"error": "Vehicle not found", "confidence": 0.0}
            
            # Find available workshops
            workshops = await self._find_suitable_workshops(
                session, service_type, vehicle.location if hasattr(vehicle, 'location') else "default"
            )
            
            if not workshops:
                return {
                    "error": "No available workshops found",
                    "confidence": 0.0,
                    "recommendations": ["Try extending search radius", "Consider alternative service types"]
                }
            
            # Find optimal booking slot
            optimal_slot = await self._find_optimal_slot(
                session, workshops, priority, service_type
            )
            
            if not optimal_slot:
                return {
                    "error": "No available slots found",
                    "confidence": 0.0,
                    "workshops_checked": len(workshops)
                }
            
            # Create booking
            booking = Booking(
                vehicle_id=vehicle_id,
                workshop_id=optimal_slot["workshop_id"],
                workshop_name=optimal_slot["workshop_name"],
                booking_slot=optimal_slot["slot_time"],
                service_type=service_type,
                estimated_duration=optimal_slot["estimated_duration"],
                priority=priority,
                predicted_issue=predicted_issue,
                confidence_score=confidence_score,
                recommended_actions=data.get("recommended_actions", [])
            )
            
            session.add(booking)
            await session.commit()
            await session.refresh(booking)
            
            return {
                "booking_id": booking.id,
                "vehicle_id": vehicle_id,
                "workshop": {
                    "id": optimal_slot["workshop_id"],
                    "name": optimal_slot["workshop_name"],
                    "location": optimal_slot.get("location", "Unknown")
                },
                "booking_slot": optimal_slot["slot_time"].isoformat(),
                "estimated_duration": optimal_slot["estimated_duration"],
                "service_type": service_type,
                "priority": priority,
                "status": "scheduled",
                "confidence": self._calculate_confidence({
                    "workshop_availability": optimal_slot.get("availability_confidence", 0.8),
                    "scheduling_confidence": 0.9
                }),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _find_available_workshops(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Find available workshops based on criteria"""
        service_type = data.get("service_type", "maintenance")
        location = data.get("location", "default")
        urgency = data.get("urgency", "normal")
        max_distance = data.get("max_distance", 50)  # km
        
        async with AsyncSessionLocal() as session:
            workshops = await self._find_suitable_workshops(
                session, service_type, location, max_distance
            )
            
            workshop_details = []
            for workshop in workshops:
                availability = await self._get_workshop_availability(session, workshop.workshop_id)
                
                workshop_details.append({
                    "id": workshop.workshop_id,
                    "name": workshop.name,
                    "location": workshop.location,
                    "specialties": workshop.specialties,
                    "rating": workshop.rating,
                    "availability": availability,
                    "distance": 0,  # Would calculate actual distance in real implementation
                    "estimated_wait_time": availability.get("next_available_hours", 0)
                })
            
            # Sort by priority factors
            workshop_details.sort(key=lambda w: (
                w["estimated_wait_time"],
                -w["rating"],
                w["distance"]
            ))
            
            return {
                "workshops_found": len(workshop_details),
                "workshops": workshop_details,
                "search_criteria": {
                    "service_type": service_type,
                    "location": location,
                    "max_distance": max_distance
                },
                "confidence": 0.8 if workshop_details else 0.2,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _optimize_booking_schedule(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize booking schedule for efficiency"""
        workshop_id = data.get("workshop_id")
        date_range = data.get("date_range", 7)  # days
        
        async with AsyncSessionLocal() as session:
            # Get all bookings for the workshop in the date range
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=date_range)
            
            stmt = select(Booking).where(
                and_(
                    Booking.workshop_id == workshop_id,
                    Booking.booking_slot >= start_date,
                    Booking.booking_slot <= end_date,
                    Booking.status.in_(["scheduled", "confirmed"])
                )
            ).order_by(Booking.booking_slot)
            
            result = await session.execute(stmt)
            bookings = result.scalars().all()
            
            # Analyze current schedule
            optimization_suggestions = self._analyze_schedule_efficiency(bookings)
            
            # Generate optimized schedule
            optimized_schedule = self._generate_optimized_schedule(bookings)
            
            return {
                "workshop_id": workshop_id,
                "current_bookings": len(bookings),
                "optimization_suggestions": optimization_suggestions,
                "optimized_schedule": optimized_schedule,
                "efficiency_improvement": optimization_suggestions.get("efficiency_gain", 0),
                "confidence": 0.75,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _update_booking(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing booking"""
        booking_id = data.get("booking_id")
        updates = data.get("updates", {})
        
        async with AsyncSessionLocal() as session:
            booking = await session.get(Booking, booking_id)
            if not booking:
                return {"error": "Booking not found", "confidence": 0.0}
            
            # Update allowed fields
            allowed_updates = [
                "booking_slot", "service_type", "priority", "status",
                "estimated_duration", "predicted_issue", "confidence_score"
            ]
            
            updated_fields = []
            for field, value in updates.items():
                if field in allowed_updates and hasattr(booking, field):
                    if field == "booking_slot" and isinstance(value, str):
                        value = datetime.fromisoformat(value)
                    
                    setattr(booking, field, value)
                    updated_fields.append(field)
            
            await session.commit()
            await session.refresh(booking)
            
            return {
                "booking_id": booking_id,
                "updated_fields": updated_fields,
                "new_booking_slot": booking.booking_slot.isoformat(),
                "status": booking.status,
                "confidence": 0.9,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _cancel_booking(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a booking"""
        booking_id = data.get("booking_id")
        reason = data.get("reason", "User requested")
        
        async with AsyncSessionLocal() as session:
            booking = await session.get(Booking, booking_id)
            if not booking:
                return {"error": "Booking not found", "confidence": 0.0}
            
            if booking.status in ["completed", "cancelled"]:
                return {
                    "error": f"Cannot cancel booking with status: {booking.status}",
                    "confidence": 0.0
                }
            
            booking.status = "cancelled"
            await session.commit()
            
            # Find alternative slot if needed
            alternative_slots = []
            if data.get("find_alternative", False):
                workshops = await self._find_suitable_workshops(
                    session, booking.service_type, "default"
                )
                
                for workshop in workshops[:3]:  # Top 3 alternatives
                    slot = await self._find_next_available_slot(
                        session, workshop.workshop_id, booking.service_type
                    )
                    if slot:
                        alternative_slots.append({
                            "workshop_id": workshop.workshop_id,
                            "workshop_name": workshop.name,
                            "slot_time": slot.isoformat(),
                            "estimated_duration": 120  # default 2 hours
                        })
            
            return {
                "booking_id": booking_id,
                "status": "cancelled",
                "reason": reason,
                "alternative_slots": alternative_slots,
                "confidence": 1.0,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _find_suitable_workshops(
        self, 
        session, 
        service_type: str, 
        location: str, 
        max_distance: float = 50
    ) -> List[Workshop]:
        """Find workshops suitable for the service type and location"""
        stmt = select(Workshop).where(
            or_(
                Workshop.specialties.contains([service_type]),
                Workshop.specialties.contains(["all"]),
                Workshop.specialties.contains(["general"])
            )
        )
        
        result = await session.execute(stmt)
        workshops = result.scalars().all()
        
        # In a real implementation, you would filter by actual distance
        # For now, return all suitable workshops
        return workshops
    
    async def _find_optimal_slot(
        self, 
        session,
        workshops: List[Workshop],
        priority: str,
        service_type: str
    ) -> Optional[Dict[str, Any]]:
        """Find the optimal booking slot across available workshops"""
        priority_config = self.booking_priorities.get(priority, self.booking_priorities["normal"])
        max_delay_hours = priority_config["max_delay_hours"]
        
        best_slot = None
        best_score = float('inf')
        
        for workshop in workshops:
            slot_time = await self._find_next_available_slot(session, workshop.workshop_id, service_type)
            
            if not slot_time:
                continue
            
            # Calculate delay in hours
            delay_hours = (slot_time - datetime.utcnow()).total_seconds() / 3600
            
            if delay_hours > max_delay_hours:
                continue
            
            # Score based on delay, workshop rating, and other factors
            score = delay_hours - (workshop.rating * 10)  # Prefer higher rated workshops
            
            if score < best_score:
                best_score = score
                best_slot = {
                    "workshop_id": workshop.workshop_id,
                    "workshop_name": workshop.name,
                    "location": workshop.location,
                    "slot_time": slot_time,
                    "estimated_duration": self._estimate_service_duration(service_type),
                    "availability_confidence": 0.8
                }
        
        return best_slot
    
    async def _find_next_available_slot(
        self, 
        session, 
        workshop_id: str, 
        service_type: str
    ) -> Optional[datetime]:
        """Find the next available slot for a workshop"""
        # Get existing bookings
        stmt = select(Booking).where(
            and_(
                Booking.workshop_id == workshop_id,
                Booking.booking_slot >= datetime.utcnow(),
                Booking.status.in_(["scheduled", "confirmed", "in_progress"])
            )
        ).order_by(Booking.booking_slot)
        
        result = await session.execute(stmt)
        existing_bookings = result.scalars().all()
        
        # Find gaps in the schedule
        current_time = datetime.utcnow()
        
        # Round to next hour
        if current_time.minute > 0:
            current_time = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
        service_duration = self._estimate_service_duration(service_type)
        
        # Check for available slots in the next 30 days
        for day_offset in range(30):
            day_start = current_time + timedelta(days=day_offset)
            day_start = day_start.replace(hour=8, minute=0, second=0, microsecond=0)  # Start at 8 AM
            day_end = day_start.replace(hour=18)  # End at 6 PM
            
            # Check hourly slots
            slot_time = day_start
            while slot_time < day_end:
                slot_end = slot_time + timedelta(minutes=service_duration)
                
                # Check if slot conflicts with existing bookings
                conflict = False
                for booking in existing_bookings:
                    booking_end = booking.booking_slot + timedelta(minutes=booking.estimated_duration or 120)
                    
                    if (slot_time < booking_end and slot_end > booking.booking_slot):
                        conflict = True
                        break
                
                if not conflict:
                    return slot_time
                
                slot_time += timedelta(hours=1)
        
        return None
    
    async def _get_workshop_availability(self, session, workshop_id: str) -> Dict[str, Any]:
        """Get workshop availability information"""
        next_slot = await self._find_next_available_slot(session, workshop_id, "maintenance")
        
        if next_slot:
            hours_until_available = (next_slot - datetime.utcnow()).total_seconds() / 3600
        else:
            hours_until_available = 720  # 30 days
        
        return {
            "next_available": next_slot.isoformat() if next_slot else None,
            "next_available_hours": hours_until_available,
            "current_load": "normal"  # Would calculate based on bookings
        }
    
    def _estimate_service_duration(self, service_type: str) -> int:
        """Estimate service duration in minutes based on service type"""
        duration_mapping = {
            "inspection": 60,
            "preventive": 120,
            "corrective": 180,
            "emergency": 240,
            "battery_service": 90,
            "motor_service": 150,
            "cooling_service": 120,
            "general": 120
        }
        
        return duration_mapping.get(service_type, 120)
    
    def _analyze_schedule_efficiency(self, bookings: List[Booking]) -> Dict[str, Any]:
        """Analyze the efficiency of the current schedule"""
        if not bookings:
            return {"efficiency_gain": 0, "suggestions": []}
        
        total_duration = sum(booking.estimated_duration or 120 for booking in bookings)
        
        # Calculate gaps between bookings
        gaps = []
        for i in range(len(bookings) - 1):
            current_end = bookings[i].booking_slot + timedelta(minutes=bookings[i].estimated_duration or 120)
            next_start = bookings[i + 1].booking_slot
            gap_minutes = (next_start - current_end).total_seconds() / 60
            gaps.append(gap_minutes)
        
        avg_gap = sum(gaps) / len(gaps) if gaps else 0
        
        suggestions = []
        if avg_gap > 60:
            suggestions.append("Reduce gaps between bookings")
        
        # Check for priority ordering
        priority_order = {"critical": 1, "high": 2, "normal": 3, "low": 4}
        priorities = [priority_order.get(booking.priority, 3) for booking in bookings]
        
        if priorities != sorted(priorities):
            suggestions.append("Reorder bookings by priority")
        
        efficiency_gain = min(20, max(0, avg_gap - 30) / 30 * 20)  # Up to 20% improvement
        
        return {
            "efficiency_gain": efficiency_gain,
            "avg_gap_minutes": avg_gap,
            "suggestions": suggestions,
            "total_bookings": len(bookings),
            "total_duration": total_duration
        }
    
    def _generate_optimized_schedule(self, bookings: List[Booking]) -> List[Dict[str, Any]]:
        """Generate an optimized schedule"""
        if not bookings:
            return []
        
        # Sort by priority first, then by original slot time
        priority_order = {"critical": 1, "high": 2, "normal": 3, "low": 4}
        sorted_bookings = sorted(bookings, key=lambda b: (
            priority_order.get(b.priority, 3),
            b.booking_slot
        ))
        
        optimized_schedule = []
        current_time = min(booking.booking_slot for booking in bookings)
        
        for booking in sorted_bookings:
            optimized_schedule.append({
                "booking_id": booking.id,
                "vehicle_id": booking.vehicle_id,
                "original_slot": booking.booking_slot.isoformat(),
                "optimized_slot": current_time.isoformat(),
                "duration": booking.estimated_duration or 120,
                "priority": booking.priority,
                "service_type": booking.service_type
            })
            
            current_time += timedelta(minutes=booking.estimated_duration or 120)
            # Add 30 minute buffer between bookings
            current_time += timedelta(minutes=30)
        
        return optimized_schedule