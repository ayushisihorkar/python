import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Workshop:
    id: str
    name: str
    location: str
    services: List[str]
    availability: Dict[str, List[str]]  # day -> time slots
    rating: float
    cost_multiplier: float

@dataclass
class MaintenanceTask:
    vehicle_id: str
    task_type: str
    urgency: str
    estimated_duration: int
    estimated_cost: float
    preferred_date: Optional[datetime] = None
    workshop_id: Optional[str] = None

class PlannerAgent:
    """
    AI Agent for scheduling maintenance bookings with workshops
    """
    
    def __init__(self):
        self.workshops = self._initialize_workshops()
        self.logger = logging.getLogger(__name__)
        
    def _initialize_workshops(self) -> List[Workshop]:
        """
        Initialize available workshops
        """
        return [
            Workshop(
                id="ws_001",
                name="Premium Auto Service",
                location="Downtown",
                services=["oil_change", "tire_rotation", "battery_replacement", "brake_service"],
                availability={
                    "monday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                    "tuesday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                    "wednesday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                    "thursday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
                    "friday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
                },
                rating=4.8,
                cost_multiplier=1.2
            ),
            Workshop(
                id="ws_002",
                name="Quick Fix Garage",
                location="Suburbs",
                services=["oil_change", "tire_rotation", "battery_replacement"],
                availability={
                    "monday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"],
                    "tuesday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"],
                    "wednesday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"],
                    "thursday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"],
                    "friday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"]
                },
                rating=4.2,
                cost_multiplier=0.9
            ),
            Workshop(
                id="ws_003",
                name="Express Maintenance",
                location="Airport Area",
                services=["oil_change", "tire_rotation"],
                availability={
                    "monday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"],
                    "tuesday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"],
                    "wednesday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"],
                    "thursday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"],
                    "friday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"]
                },
                rating=4.5,
                cost_multiplier=1.0
            )
        ]
    
    def schedule_maintenance(self, maintenance_tasks: List[MaintenanceTask]) -> List[Dict]:
        """
        Schedule maintenance tasks with optimal workshop selection
        """
        scheduled_bookings = []
        
        for task in maintenance_tasks:
            try:
                # Find suitable workshops
                suitable_workshops = self._find_suitable_workshops(task)
                
                if not suitable_workshops:
                    self.logger.warning(f"No suitable workshops found for task {task.task_type}")
                    continue
                
                # Select optimal workshop and time slot
                booking = self._optimize_booking(task, suitable_workshops)
                
                if booking:
                    scheduled_bookings.append(booking)
                    
            except Exception as e:
                self.logger.error(f"Error scheduling task for vehicle {task.vehicle_id}: {str(e)}")
        
        return scheduled_bookings
    
    def _find_suitable_workshops(self, task: MaintenanceTask) -> List[Workshop]:
        """
        Find workshops that can handle the maintenance task
        """
        suitable_workshops = []
        
        for workshop in self.workshops:
            if task.task_type in workshop.services:
                suitable_workshops.append(workshop)
        
        return suitable_workshops
    
    def _optimize_booking(self, task: MaintenanceTask, workshops: List[Workshop]) -> Optional[Dict]:
        """
        Optimize workshop selection and time slot booking
        """
        best_booking = None
        best_score = float('-inf')
        
        for workshop in workshops:
            # Find available time slots
            available_slots = self._find_available_slots(workshop, task)
            
            for slot in available_slots:
                score = self._calculate_booking_score(task, workshop, slot)
                
                if score > best_score:
                    best_score = score
                    best_booking = {
                        'booking_id': f"booking_{datetime.now().timestamp()}",
                        'vehicle_id': task.vehicle_id,
                        'workshop_id': workshop.id,
                        'workshop_name': workshop.name,
                        'task_type': task.task_type,
                        'scheduled_date': slot['date'],
                        'scheduled_time': slot['time'],
                        'estimated_duration': task.estimated_duration,
                        'estimated_cost': task.estimated_cost * workshop.cost_multiplier,
                        'urgency': task.urgency,
                        'status': 'scheduled'
                    }
        
        return best_booking
    
    def _find_available_slots(self, workshop: Workshop, task: MaintenanceTask) -> List[Dict]:
        """
        Find available time slots for the workshop
        """
        available_slots = []
        current_date = datetime.now()
        
        # Look for slots in the next 14 days
        for day_offset in range(14):
            check_date = current_date + timedelta(days=day_offset)
            day_name = check_date.strftime('%A').lower()
            
            if day_name in workshop.availability:
                for time_slot in workshop.availability[day_name]:
                    # Check if slot is available (simplified - in real app would check against existing bookings)
                    slot = {
                        'date': check_date.strftime('%Y-%m-%d'),
                        'time': time_slot,
                        'datetime': check_date.replace(
                            hour=int(time_slot.split(':')[0]),
                            minute=int(time_slot.split(':')[1])
                        )
                    }
                    available_slots.append(slot)
        
        return available_slots
    
    def _calculate_booking_score(self, task: MaintenanceTask, workshop: Workshop, slot: Dict) -> float:
        """
        Calculate booking score based on multiple factors
        """
        score = 0.0
        
        # Workshop rating (0-5 scale)
        score += workshop.rating * 10
        
        # Cost factor (lower is better)
        cost_factor = 1.0 / workshop.cost_multiplier
        score += cost_factor * 20
        
        # Urgency factor
        urgency_multiplier = {
            'high': 1.5,
            'medium': 1.0,
            'low': 0.8
        }
        score *= urgency_multiplier.get(task.urgency, 1.0)
        
        # Time preference (earlier slots get higher scores)
        slot_hour = int(slot['time'].split(':')[0])
        if 9 <= slot_hour <= 11:  # Morning slots preferred
            score += 10
        elif 14 <= slot_hour <= 16:  # Afternoon slots
            score += 5
        
        return score
    
    def get_workshop_availability(self, workshop_id: str, date: str) -> Dict:
        """
        Get workshop availability for a specific date
        """
        workshop = next((w for w in self.workshops if w.id == workshop_id), None)
        
        if not workshop:
            return {'error': 'Workshop not found'}
        
        day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A').lower()
        available_slots = workshop.availability.get(day_name, [])
        
        return {
            'workshop_id': workshop_id,
            'workshop_name': workshop.name,
            'date': date,
            'available_slots': available_slots,
            'services': workshop.services,
            'rating': workshop.rating
        }
    
    def cancel_booking(self, booking_id: str) -> Dict:
        """
        Cancel a scheduled booking
        """
        # In a real implementation, this would update the database
        return {
            'booking_id': booking_id,
            'status': 'cancelled',
            'cancelled_at': datetime.now().isoformat()
        }
    
    def reschedule_booking(self, booking_id: str, new_date: str, new_time: str) -> Dict:
        """
        Reschedule a booking to a new date and time
        """
        # In a real implementation, this would update the database
        return {
            'booking_id': booking_id,
            'new_date': new_date,
            'new_time': new_time,
            'status': 'rescheduled',
            'rescheduled_at': datetime.now().isoformat()
        } 