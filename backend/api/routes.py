from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from database.database import get_db
from database.models import Vehicle, VehicleTelemetry, Booking, ServiceLog, Workshop, Notification
from agents.agent_coordinator import AgentCoordinator
from .schemas import *

logger = logging.getLogger(__name__)

# Initialize routers
vehicle_router = APIRouter()
booking_router = APIRouter()
health_router = APIRouter()

# This will be injected from main.py
agent_coordinator: Optional[AgentCoordinator] = None

def get_agent_coordinator():
    """Dependency to get agent coordinator"""
    if agent_coordinator is None:
        raise HTTPException(status_code=500, detail="Agent coordinator not initialized")
    return agent_coordinator

# Vehicle endpoints
@vehicle_router.get("/", response_model=List[VehicleResponse])
async def get_vehicles(
    company_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get list of vehicles with optional filtering"""
    stmt = select(Vehicle)
    
    if company_id:
        stmt = stmt.where(Vehicle.company_id == company_id)
    if status:
        stmt = stmt.where(Vehicle.status == status)
    
    stmt = stmt.offset(skip).limit(limit).order_by(Vehicle.updated_at.desc())
    
    result = await db.execute(stmt)
    vehicles = result.scalars().all()
    
    return vehicles

@vehicle_router.get("/{vehicle_id}", response_model=VehicleDetailResponse)
async def get_vehicle(
    vehicle_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed vehicle information"""
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Get latest telemetry
    stmt = select(VehicleTelemetry).where(
        VehicleTelemetry.vehicle_id == vehicle_id
    ).order_by(VehicleTelemetry.timestamp.desc()).limit(1)
    
    result = await db.execute(stmt)
    latest_telemetry = result.scalar_one_or_none()
    
    # Get recent bookings
    stmt = select(Booking).where(
        Booking.vehicle_id == vehicle_id
    ).order_by(Booking.created_at.desc()).limit(5)
    
    result = await db.execute(stmt)
    recent_bookings = result.scalars().all()
    
    return VehicleDetailResponse(
        **vehicle.__dict__,
        latest_telemetry=latest_telemetry,
        recent_bookings=recent_bookings
    )

@vehicle_router.post("/", response_model=VehicleResponse)
async def create_vehicle(
    vehicle: VehicleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new vehicle"""
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle

@vehicle_router.post("/{vehicle_id}/telemetry")
async def ingest_telemetry(
    vehicle_id: int,
    telemetry: TelemetryData,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Ingest vehicle telemetry data and trigger agent processing"""
    # Verify vehicle exists
    vehicle = await db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    # Process telemetry through agent pipeline
    background_tasks.add_task(
        coordinator.process_vehicle_telemetry,
        vehicle_id,
        telemetry.dict()
    )
    
    return {
        "message": "Telemetry data received and processing started",
        "vehicle_id": vehicle_id,
        "timestamp": datetime.utcnow().isoformat()
    }

@vehicle_router.post("/{vehicle_id}/health-check")
async def perform_health_check(
    vehicle_id: int,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Perform health check on a vehicle"""
    result = await coordinator.perform_health_check(vehicle_id)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@vehicle_router.get("/{vehicle_id}/telemetry")
async def get_vehicle_telemetry(
    vehicle_id: int,
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get vehicle telemetry history"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    stmt = select(VehicleTelemetry).where(
        and_(
            VehicleTelemetry.vehicle_id == vehicle_id,
            VehicleTelemetry.timestamp >= cutoff_time
        )
    ).order_by(VehicleTelemetry.timestamp.desc())
    
    result = await db.execute(stmt)
    telemetry_data = result.scalars().all()
    
    return {
        "vehicle_id": vehicle_id,
        "period_hours": hours,
        "data_points": len(telemetry_data),
        "telemetry": telemetry_data
    }

# Booking endpoints
@booking_router.get("/", response_model=List[BookingResponse])
async def get_bookings(
    vehicle_id: Optional[int] = None,
    workshop_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get list of bookings with optional filtering"""
    stmt = select(Booking)
    
    if vehicle_id:
        stmt = stmt.where(Booking.vehicle_id == vehicle_id)
    if workshop_id:
        stmt = stmt.where(Booking.workshop_id == workshop_id)
    if status:
        stmt = stmt.where(Booking.status == status)
    
    stmt = stmt.offset(skip).limit(limit).order_by(Booking.booking_slot.desc())
    
    result = await db.execute(stmt)
    bookings = result.scalars().all()
    
    return bookings

@booking_router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get booking details"""
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@booking_router.post("/", response_model=BookingResponse)
async def create_booking(
    booking: BookingCreate,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Create a new booking using the planner agent"""
    result = await coordinator.schedule_maintenance(
        vehicle_id=booking.vehicle_id,
        service_type=booking.service_type,
        priority=booking.priority
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@booking_router.put("/{booking_id}")
async def update_booking(
    booking_id: int,
    updates: BookingUpdate,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Update an existing booking"""
    result = await coordinator.execute_agent_action(
        "planner",
        "update_booking",
        {"booking_id": booking_id, "updates": updates.dict(exclude_unset=True)}
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@booking_router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: int,
    reason: str = "User requested",
    find_alternative: bool = False,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Cancel a booking"""
    result = await coordinator.execute_agent_action(
        "planner",
        "cancel_booking",
        {
            "booking_id": booking_id,
            "reason": reason,
            "find_alternative": find_alternative
        }
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@booking_router.get("/workshops/available")
async def get_available_workshops(
    service_type: str = "maintenance",
    location: str = "default",
    max_distance: float = 50,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Find available workshops"""
    result = await coordinator.execute_agent_action(
        "planner",
        "find_workshops",
        {
            "service_type": service_type,
            "location": location,
            "max_distance": max_distance
        }
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

# Health monitoring endpoints
@health_router.get("/agent-status")
async def get_agent_status(
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Get status of all agents"""
    return await coordinator.get_agent_status()

@health_router.post("/emergency")
async def handle_emergency(
    emergency: EmergencyAlert,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Handle emergency situation"""
    result = await coordinator.handle_emergency(
        emergency.vehicle_id,
        emergency.dict()
    )
    
    if not result.get("emergency_handled", False):
        raise HTTPException(status_code=500, detail="Failed to handle emergency")
    
    return result

@health_router.post("/fleet-report")
async def generate_fleet_report(
    report_request: FleetReportRequest,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Generate fleet health report"""
    result = await coordinator.generate_fleet_report(
        company_id=report_request.company_id,
        report_type=report_request.report_type
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result

@health_router.get("/notifications")
async def get_notifications(
    recipient_type: str = "fleet_manager",
    recipient_id: str = "default",
    unread_only: bool = False,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get notifications for a recipient"""
    stmt = select(Notification).where(
        and_(
            Notification.recipient_type == recipient_type,
            Notification.recipient_id == recipient_id
        )
    )
    
    if unread_only:
        stmt = stmt.where(Notification.read == False)
    
    stmt = stmt.offset(skip).limit(limit).order_by(Notification.created_at.desc())
    
    result = await db.execute(stmt)
    notifications = result.scalars().all()
    
    return {
        "notifications": notifications,
        "total": len(notifications),
        "unread_only": unread_only
    }

@health_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read"""
    notification = await db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.read = True
    notification.read_at = datetime.utcnow()
    await db.commit()
    
    return {"message": "Notification marked as read"}

@health_router.post("/test-scenario")
async def simulate_test_scenario(
    scenario: TestScenario,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """Simulate test scenarios for agent testing"""
    if scenario.scenario_type == "critical_battery":
        # Simulate critical battery scenario
        telemetry_data = {
            "battery_soh": 65.0,  # Critical level
            "battery_temp": 47.0,  # High temperature
            "voltage_imbalance": 0.6,  # High imbalance
            "motor_efficiency": 78.0,
            "coolant_level": 85.0,
            "error_codes": ["BATT_001", "TEMP_002"]
        }
        
        result = await coordinator.process_vehicle_telemetry(
            scenario.vehicle_id,
            telemetry_data
        )
        
    elif scenario.scenario_type == "emergency":
        # Simulate emergency
        result = await coordinator.handle_emergency(
            scenario.vehicle_id,
            {
                "issue": "Motor overheating",
                "severity": "critical",
                "location": "Highway 101, Mile 45",
                "driver_status": "safe"
            }
        )
        
    elif scenario.scenario_type == "maintenance_due":
        # Simulate maintenance scheduling
        result = await coordinator.schedule_maintenance(
            scenario.vehicle_id,
            "preventive",
            "normal"
        )
        
    else:
        raise HTTPException(status_code=400, detail="Unknown scenario type")
    
    return {
        "scenario": scenario.scenario_type,
        "vehicle_id": scenario.vehicle_id,
        "simulation_result": result,
        "timestamp": datetime.utcnow().isoformat()
    }

# Utility function to set agent coordinator (called from main.py)
def set_agent_coordinator(coordinator: AgentCoordinator):
    global agent_coordinator
    agent_coordinator = coordinator