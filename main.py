from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import asyncio
import logging

from .database import get_db, init_db
from .models import (
    Vehicle, VehicleCreate, VehicleUpdate, TelemetryData, HealthAnalysis,
    MaintenanceTask, MaintenanceTaskCreate, Booking, BookingCreate, BookingUpdate,
    Workshop, Alert, FleetReport, SystemStatus, HealthAnalysisResponse,
    BookingResponse, FleetReportResponse, ErrorResponse
)
from .crud import (
    get_vehicles, get_vehicle, create_vehicle, update_vehicle, delete_vehicle,
    create_telemetry_record, get_telemetry_history, get_latest_telemetry,
    create_health_analysis, get_health_history, get_latest_health_analysis,
    create_maintenance_task, get_maintenance_tasks, update_maintenance_task,
    create_booking, get_bookings, get_booking, update_booking, cancel_booking,
    get_workshops, get_workshop, get_workshops_by_service,
    create_alert, get_alerts, mark_alert_read,
    get_fleet_summary, get_maintenance_cost_summary, get_vehicle_analytics
)
from ..agents.orchestrator import OrchestratorAgent
from ..agents.health_monitor import HealthMonitorAgent
from ..agents.planner import PlannerAgent
from ..agents.communicator import CommunicatorAgent
from ..agents.logger import LoggerAgent

# Initialize FastAPI app
app = FastAPI(
    title="Rental Fleet Dashboard API",
    description="AI-powered rental fleet management system with predictive maintenance",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
orchestrator = OrchestratorAgent()
health_monitor = HealthMonitorAgent()
planner = PlannerAgent()
communicator = CommunicatorAgent()
logger_agent = LoggerAgent()

# Initialize database
init_db()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# System status endpoint
@app.get("/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get current system status"""
    return orchestrator.get_system_status()

# Vehicle endpoints
@app.get("/vehicles", response_model=List[Vehicle])
async def read_vehicles(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all vehicles with optional filtering"""
    if status:
        vehicles = get_vehicles_by_status(db, status)
    else:
        vehicles = get_vehicles(db, skip=skip, limit=limit)
    return vehicles

@app.get("/vehicles/{vehicle_id}", response_model=Vehicle)
async def read_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Get a specific vehicle by ID"""
    vehicle = get_vehicle(db, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@app.post("/vehicles", response_model=Vehicle)
async def create_new_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    """Create a new vehicle"""
    db_vehicle = get_vehicle(db, vehicle.id)
    if db_vehicle:
        raise HTTPException(status_code=400, detail="Vehicle ID already registered")
    return create_vehicle(db, vehicle)

@app.put("/vehicles/{vehicle_id}", response_model=Vehicle)
async def update_existing_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    db: Session = Depends(get_db)
):
    """Update a vehicle"""
    vehicle = update_vehicle(db, vehicle_id, vehicle_update)
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@app.delete("/vehicles/{vehicle_id}")
async def delete_existing_vehicle(vehicle_id: str, db: Session = Depends(get_db)):
    """Delete a vehicle"""
    success = delete_vehicle(db, vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"message": "Vehicle deleted successfully"}

# Telemetry endpoints
@app.post("/telemetry")
async def submit_telemetry(
    telemetry_data: TelemetryData,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit vehicle telemetry data"""
    try:
        # Store telemetry in database
        telemetry_record = create_telemetry_record(db, telemetry_data)
        
        # Process telemetry with AI agents in background
        background_tasks.add_task(
            process_telemetry_background,
            telemetry_data.vehicle_id,
            telemetry_data.dict(),
            db
        )
        
        return {
            "success": True,
            "message": "Telemetry data received and processing started",
            "telemetry_id": telemetry_record.id
        }
    except Exception as e:
        logger.error(f"Error processing telemetry: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing telemetry")

async def process_telemetry_background(vehicle_id: str, telemetry_data: Dict, db: Session):
    """Background task to process telemetry with AI agents"""
    try:
        # Process with orchestrator
        result = await orchestrator.process_vehicle_telemetry(vehicle_id, telemetry_data)
        
        # Update vehicle health score in database
        if 'health_score' in result:
            update_vehicle(db, vehicle_id, {'health_score': result['health_score']})
        
        logger.info(f"Telemetry processed for vehicle {vehicle_id}: {result}")
        
    except Exception as e:
        logger.error(f"Error in background telemetry processing: {str(e)}")

@app.get("/vehicles/{vehicle_id}/telemetry")
async def get_vehicle_telemetry(
    vehicle_id: str,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get telemetry history for a vehicle"""
    telemetry_records = get_telemetry_history(db, vehicle_id, limit)
    return telemetry_records

@app.get("/vehicles/{vehicle_id}/telemetry/latest")
async def get_latest_vehicle_telemetry(vehicle_id: str, db: Session = Depends(get_db)):
    """Get latest telemetry for a vehicle"""
    telemetry = get_latest_telemetry(db, vehicle_id)
    if telemetry is None:
        raise HTTPException(status_code=404, detail="No telemetry data found")
    return telemetry

# Health analysis endpoints
@app.get("/vehicles/{vehicle_id}/health", response_model=HealthAnalysisResponse)
async def get_vehicle_health(vehicle_id: str, db: Session = Depends(get_db)):
    """Get latest health analysis for a vehicle"""
    health_analysis = get_latest_health_analysis(db, vehicle_id)
    if health_analysis is None:
        raise HTTPException(status_code=404, detail="No health analysis found")
    
    # Parse JSON fields
    health_data = {
        "vehicle_id": health_analysis.vehicle_id,
        "health_score": health_analysis.health_score,
        "anomalies": json.loads(health_analysis.anomalies) if health_analysis.anomalies else [],
        "maintenance_predictions": json.loads(health_analysis.maintenance_predictions) if health_analysis.maintenance_predictions else [],
        "alerts": json.loads(health_analysis.alerts) if health_analysis.alerts else [],
        "recommendations": json.loads(health_analysis.recommendations) if health_analysis.recommendations else [],
        "timestamp": health_analysis.timestamp
    }
    
    return HealthAnalysisResponse(
        success=True,
        data=HealthAnalysis(**health_data),
        message="Health analysis retrieved successfully"
    )

@app.get("/vehicles/{vehicle_id}/health/history")
async def get_vehicle_health_history(
    vehicle_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get health analysis history for a vehicle"""
    health_records = get_health_history(db, vehicle_id, limit)
    return health_records

# Maintenance endpoints
@app.post("/maintenance/tasks")
async def create_maintenance_task_endpoint(
    task: MaintenanceTaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new maintenance task"""
    try:
        task_data = task.dict()
        db_task = create_maintenance_task(db, task_data)
        
        # Schedule maintenance in background
        background_tasks.add_task(
            schedule_maintenance_background,
            task.vehicle_id,
            [task_data],
            db
        )
        
        return {
            "success": True,
            "message": "Maintenance task created and scheduling started",
            "task_id": db_task.id
        }
    except Exception as e:
        logger.error(f"Error creating maintenance task: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating maintenance task")

async def schedule_maintenance_background(vehicle_id: str, tasks: List[Dict], db: Session):
    """Background task to schedule maintenance"""
    try:
        result = await orchestrator.schedule_maintenance_workflow(vehicle_id, tasks)
        logger.info(f"Maintenance scheduled for vehicle {vehicle_id}: {result}")
    except Exception as e:
        logger.error(f"Error scheduling maintenance: {str(e)}")

@app.get("/maintenance/tasks")
async def get_maintenance_tasks_endpoint(
    vehicle_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get maintenance tasks with optional filtering"""
    tasks = get_maintenance_tasks(db, vehicle_id=vehicle_id, status=status)
    return tasks

@app.put("/maintenance/tasks/{task_id}")
async def update_maintenance_task_endpoint(
    task_id: int,
    task_update: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Update a maintenance task"""
    task = update_maintenance_task(db, task_id, task_update)
    if task is None:
        raise HTTPException(status_code=404, detail="Maintenance task not found")
    return task

# Booking endpoints
@app.post("/bookings", response_model=BookingResponse)
async def create_booking_endpoint(
    booking: BookingCreate,
    db: Session = Depends(get_db)
):
    """Create a new maintenance booking"""
    try:
        booking_data = booking.dict()
        booking_data['booking_id'] = f"booking_{int(datetime.now().timestamp())}"
        
        # Get workshop name
        workshop = get_workshop(db, booking.workshop_id)
        if workshop:
            booking_data['workshop_name'] = workshop.name
        
        db_booking = create_booking(db, booking_data)
        
        return BookingResponse(
            success=True,
            data=db_booking,
            message="Booking created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating booking")

@app.get("/bookings", response_model=List[Booking])
async def get_bookings_endpoint(
    vehicle_id: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get bookings with optional filtering"""
    bookings = get_bookings(db, vehicle_id=vehicle_id, status=status)
    return bookings

@app.get("/bookings/{booking_id}", response_model=Booking)
async def get_booking_endpoint(booking_id: str, db: Session = Depends(get_db)):
    """Get a specific booking by ID"""
    booking = get_booking(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@app.put("/bookings/{booking_id}", response_model=Booking)
async def update_booking_endpoint(
    booking_id: str,
    booking_update: BookingUpdate,
    db: Session = Depends(get_db)
):
    """Update a booking"""
    booking = update_booking(db, booking_id, booking_update.dict(exclude_unset=True))
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@app.delete("/bookings/{booking_id}")
async def cancel_booking_endpoint(booking_id: str, db: Session = Depends(get_db)):
    """Cancel a booking"""
    booking = cancel_booking(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"message": "Booking cancelled successfully"}

# Workshop endpoints
@app.get("/workshops", response_model=List[Workshop])
async def get_workshops_endpoint(db: Session = Depends(get_db)):
    """Get all workshops"""
    workshops = get_workshops(db)
    return workshops

@app.get("/workshops/{workshop_id}", response_model=Workshop)
async def get_workshop_endpoint(workshop_id: str, db: Session = Depends(get_db)):
    """Get a specific workshop by ID"""
    workshop = get_workshop(db, workshop_id)
    if workshop is None:
        raise HTTPException(status_code=404, detail="Workshop not found")
    return workshop

@app.get("/workshops/service/{service}")
async def get_workshops_by_service_endpoint(service: str, db: Session = Depends(get_db)):
    """Get workshops that provide a specific service"""
    workshops = get_workshops_by_service(db, service)
    return workshops

# Alert endpoints
@app.get("/alerts")
async def get_alerts_endpoint(
    vehicle_id: Optional[str] = None,
    unread_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get alerts with optional filtering"""
    alerts = get_alerts(db, vehicle_id=vehicle_id, unread_only=unread_only)
    return alerts

@app.put("/alerts/{alert_id}/read")
async def mark_alert_read_endpoint(alert_id: str, db: Session = Depends(get_db)):
    """Mark an alert as read"""
    alert = mark_alert_read(db, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert marked as read"}

# Analytics and reporting endpoints
@app.get("/analytics/fleet")
async def get_fleet_analytics(db: Session = Depends(get_db)):
    """Get fleet analytics and summary"""
    summary = get_fleet_summary(db)
    return summary

@app.get("/analytics/vehicles/{vehicle_id}")
async def get_vehicle_analytics_endpoint(vehicle_id: str, db: Session = Depends(get_db)):
    """Get analytics for a specific vehicle"""
    analytics = get_vehicle_analytics(db, vehicle_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return analytics

@app.get("/reports/fleet", response_model=FleetReportResponse)
async def generate_fleet_report(
    start_date: str,
    end_date: str,
    background_tasks: BackgroundTasks
):
    """Generate comprehensive fleet report"""
    try:
        # Generate report in background
        background_tasks.add_task(
            generate_fleet_report_background,
            start_date,
            end_date
        )
        
        return FleetReportResponse(
            success=True,
            data=FleetReport(
                period={"start_date": start_date, "end_date": end_date},
                fleet_summary={},
                maintenance_summary={},
                health_summary={},
                cost_analysis={}
            ),
            message="Fleet report generation started"
        )
    except Exception as e:
        logger.error(f"Error generating fleet report: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating fleet report")

async def generate_fleet_report_background(start_date: str, end_date: str):
    """Background task to generate fleet report"""
    try:
        report = await orchestrator.generate_fleet_report(start_date, end_date)
        logger.info(f"Fleet report generated: {report}")
    except Exception as e:
        logger.error(f"Error generating fleet report: {str(e)}")

# Emergency endpoints
@app.post("/emergency")
async def handle_emergency_endpoint(
    vehicle_id: str,
    emergency_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Handle emergency situation"""
    try:
        # Process emergency in background
        background_tasks.add_task(
            handle_emergency_background,
            vehicle_id,
            emergency_data
        )
        
        return {
            "success": True,
            "message": "Emergency situation being handled",
            "vehicle_id": vehicle_id
        }
    except Exception as e:
        logger.error(f"Error handling emergency: {str(e)}")
        raise HTTPException(status_code=500, detail="Error handling emergency")

async def handle_emergency_background(vehicle_id: str, emergency_data: Dict[str, Any]):
    """Background task to handle emergency"""
    try:
        result = await orchestrator.handle_emergency_situation(vehicle_id, emergency_data)
        logger.info(f"Emergency handled for vehicle {vehicle_id}: {result}")
    except Exception as e:
        logger.error(f"Error handling emergency: {str(e)}")

# Import json for JSON parsing
import json 