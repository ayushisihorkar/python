from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from .database import (
    Vehicle, TelemetryRecord, HealthAnalysis, MaintenanceTask, 
    Booking, Workshop, Alert, MaintenanceHistory
)
from .models import VehicleCreate, VehicleUpdate, TelemetryData

# Vehicle CRUD operations
def get_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[Vehicle]:
    """Get all vehicles with pagination"""
    return db.query(Vehicle).offset(skip).limit(limit).all()

def get_vehicle(db: Session, vehicle_id: str) -> Optional[Vehicle]:
    """Get a specific vehicle by ID"""
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

def create_vehicle(db: Session, vehicle: VehicleCreate) -> Vehicle:
    """Create a new vehicle"""
    db_vehicle = Vehicle(
        id=vehicle.id,
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        license_plate=vehicle.license_plate,
        status=vehicle.status,
        location=vehicle.location
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def update_vehicle(db: Session, vehicle_id: str, vehicle_update: VehicleUpdate) -> Optional[Vehicle]:
    """Update a vehicle"""
    db_vehicle = get_vehicle(db, vehicle_id)
    if db_vehicle:
        update_data = vehicle_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vehicle, field, value)
        db_vehicle.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, vehicle_id: str) -> bool:
    """Delete a vehicle"""
    db_vehicle = get_vehicle(db, vehicle_id)
    if db_vehicle:
        db.delete(db_vehicle)
        db.commit()
        return True
    return False

def get_vehicles_by_status(db: Session, status: str) -> List[Vehicle]:
    """Get vehicles by status"""
    return db.query(Vehicle).filter(Vehicle.status == status).all()

def get_vehicles_needing_maintenance(db: Session, health_threshold: int = 50) -> List[Vehicle]:
    """Get vehicles that need maintenance based on health score"""
    return db.query(Vehicle).filter(Vehicle.health_score < health_threshold).all()

# Telemetry CRUD operations
def create_telemetry_record(db: Session, telemetry_data: TelemetryData) -> TelemetryRecord:
    """Create a new telemetry record"""
    db_telemetry = TelemetryRecord(
        vehicle_id=telemetry_data.vehicle_id,
        engine_temp=telemetry_data.engine_temp,
        oil_pressure=telemetry_data.oil_pressure,
        battery_voltage=telemetry_data.battery_voltage,
        tire_pressure=telemetry_data.tire_pressure,
        fuel_level=telemetry_data.fuel_level,
        mileage=telemetry_data.mileage,
        speed=telemetry_data.speed,
        latitude=telemetry_data.latitude,
        longitude=telemetry_data.longitude,
        timestamp=telemetry_data.timestamp
    )
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

def get_telemetry_history(db: Session, vehicle_id: str, limit: int = 100) -> List[TelemetryRecord]:
    """Get telemetry history for a vehicle"""
    return db.query(TelemetryRecord).filter(
        TelemetryRecord.vehicle_id == vehicle_id
    ).order_by(desc(TelemetryRecord.timestamp)).limit(limit).all()

def get_latest_telemetry(db: Session, vehicle_id: str) -> Optional[TelemetryRecord]:
    """Get the latest telemetry record for a vehicle"""
    return db.query(TelemetryRecord).filter(
        TelemetryRecord.vehicle_id == vehicle_id
    ).order_by(desc(TelemetryRecord.timestamp)).first()

# Health Analysis CRUD operations
def create_health_analysis(db: Session, vehicle_id: str, health_data: Dict[str, Any]) -> HealthAnalysis:
    """Create a new health analysis record"""
    db_health = HealthAnalysis(
        vehicle_id=vehicle_id,
        health_score=health_data.get('health_score', 0),
        anomalies=json.dumps(health_data.get('anomalies', [])),
        maintenance_predictions=json.dumps(health_data.get('maintenance_predictions', [])),
        alerts=json.dumps(health_data.get('alerts', [])),
        recommendations=json.dumps(health_data.get('recommendations', [])),
        timestamp=datetime.utcnow()
    )
    db.add(db_health)
    db.commit()
    db.refresh(db_health)
    return db_health

def get_health_history(db: Session, vehicle_id: str, limit: int = 50) -> List[HealthAnalysis]:
    """Get health analysis history for a vehicle"""
    return db.query(HealthAnalysis).filter(
        HealthAnalysis.vehicle_id == vehicle_id
    ).order_by(desc(HealthAnalysis.timestamp)).limit(limit).all()

def get_latest_health_analysis(db: Session, vehicle_id: str) -> Optional[HealthAnalysis]:
    """Get the latest health analysis for a vehicle"""
    return db.query(HealthAnalysis).filter(
        HealthAnalysis.vehicle_id == vehicle_id
    ).order_by(desc(HealthAnalysis.timestamp)).first()

# Maintenance Task CRUD operations
def create_maintenance_task(db: Session, task_data: Dict[str, Any]) -> MaintenanceTask:
    """Create a new maintenance task"""
    db_task = MaintenanceTask(
        vehicle_id=task_data['vehicle_id'],
        task_type=task_data['task_type'],
        urgency=task_data['urgency'],
        estimated_duration=task_data['estimated_duration'],
        estimated_cost=task_data['estimated_cost'],
        description=task_data.get('description'),
        preferred_date=task_data.get('preferred_date'),
        status=task_data.get('status', 'pending')
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def get_maintenance_tasks(db: Session, vehicle_id: Optional[str] = None, status: Optional[str] = None) -> List[MaintenanceTask]:
    """Get maintenance tasks with optional filters"""
    query = db.query(MaintenanceTask)
    
    if vehicle_id:
        query = query.filter(MaintenanceTask.vehicle_id == vehicle_id)
    
    if status:
        query = query.filter(MaintenanceTask.status == status)
    
    return query.order_by(desc(MaintenanceTask.created_at)).all()

def update_maintenance_task(db: Session, task_id: int, task_data: Dict[str, Any]) -> Optional[MaintenanceTask]:
    """Update a maintenance task"""
    db_task = db.query(MaintenanceTask).filter(MaintenanceTask.id == task_id).first()
    if db_task:
        for field, value in task_data.items():
            if value is not None:
                setattr(db_task, field, value)
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
    return db_task

# Booking CRUD operations
def create_booking(db: Session, booking_data: Dict[str, Any]) -> Booking:
    """Create a new booking"""
    db_booking = Booking(
        booking_id=booking_data['booking_id'],
        vehicle_id=booking_data['vehicle_id'],
        workshop_id=booking_data['workshop_id'],
        workshop_name=booking_data['workshop_name'],
        task_type=booking_data['task_type'],
        scheduled_date=booking_data['scheduled_date'],
        scheduled_time=booking_data['scheduled_time'],
        estimated_duration=booking_data['estimated_duration'],
        estimated_cost=booking_data['estimated_cost'],
        urgency=booking_data['urgency'],
        status=booking_data.get('status', 'scheduled')
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_bookings(db: Session, vehicle_id: Optional[str] = None, status: Optional[str] = None) -> List[Booking]:
    """Get bookings with optional filters"""
    query = db.query(Booking)
    
    if vehicle_id:
        query = query.filter(Booking.vehicle_id == vehicle_id)
    
    if status:
        query = query.filter(Booking.status == status)
    
    return query.order_by(desc(Booking.created_at)).all()

def get_booking(db: Session, booking_id: str) -> Optional[Booking]:
    """Get a specific booking by ID"""
    return db.query(Booking).filter(Booking.booking_id == booking_id).first()

def update_booking(db: Session, booking_id: str, booking_data: Dict[str, Any]) -> Optional[Booking]:
    """Update a booking"""
    db_booking = get_booking(db, booking_id)
    if db_booking:
        for field, value in booking_data.items():
            if value is not None:
                setattr(db_booking, field, value)
        db_booking.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_booking)
    return db_booking

def cancel_booking(db: Session, booking_id: str) -> Optional[Booking]:
    """Cancel a booking"""
    return update_booking(db, booking_id, {'status': 'cancelled'})

# Workshop CRUD operations
def get_workshops(db: Session) -> List[Workshop]:
    """Get all workshops"""
    return db.query(Workshop).all()

def get_workshop(db: Session, workshop_id: str) -> Optional[Workshop]:
    """Get a specific workshop by ID"""
    return db.query(Workshop).filter(Workshop.id == workshop_id).first()

def get_workshops_by_service(db: Session, service: str) -> List[Workshop]:
    """Get workshops that provide a specific service"""
    workshops = db.query(Workshop).all()
    return [w for w in workshops if service in json.loads(w.services)]

# Alert CRUD operations
def create_alert(db: Session, alert_data: Dict[str, Any]) -> Alert:
    """Create a new alert"""
    db_alert = Alert(
        alert_id=alert_data['id'],
        vehicle_id=alert_data['vehicle_id'],
        type=alert_data['type'],
        message=alert_data['message'],
        action_required=alert_data.get('action_required', True),
        timestamp=alert_data.get('timestamp', datetime.utcnow())
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_alerts(db: Session, vehicle_id: Optional[str] = None, unread_only: bool = False) -> List[Alert]:
    """Get alerts with optional filters"""
    query = db.query(Alert)
    
    if vehicle_id:
        query = query.filter(Alert.vehicle_id == vehicle_id)
    
    if unread_only:
        query = query.filter(Alert.read == False)
    
    return query.order_by(desc(Alert.timestamp)).all()

def mark_alert_read(db: Session, alert_id: str) -> Optional[Alert]:
    """Mark an alert as read"""
    db_alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if db_alert:
        db_alert.read = True
        db.commit()
        db.refresh(db_alert)
    return db_alert

# Maintenance History CRUD operations
def create_maintenance_history(db: Session, history_data: Dict[str, Any]) -> MaintenanceHistory:
    """Create a new maintenance history record"""
    db_history = MaintenanceHistory(
        vehicle_id=history_data['vehicle_id'],
        task_type=history_data['task_type'],
        description=history_data.get('description'),
        performed_by=history_data.get('performed_by'),
        workshop_id=history_data.get('workshop_id'),
        cost=history_data.get('cost'),
        duration_hours=history_data.get('duration_hours'),
        status=history_data.get('status', 'completed'),
        notes=history_data.get('notes')
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_maintenance_history(db: Session, vehicle_id: str, limit: int = 50) -> List[MaintenanceHistory]:
    """Get maintenance history for a vehicle"""
    return db.query(MaintenanceHistory).filter(
        MaintenanceHistory.vehicle_id == vehicle_id
    ).order_by(desc(MaintenanceHistory.timestamp)).limit(limit).all()

# Analytics and Reporting
def get_fleet_summary(db: Session) -> Dict[str, Any]:
    """Get fleet summary statistics"""
    total_vehicles = db.query(Vehicle).count()
    active_vehicles = db.query(Vehicle).filter(Vehicle.status == 'active').count()
    maintenance_vehicles = db.query(Vehicle).filter(Vehicle.status == 'maintenance').count()
    
    # Get average health score
    vehicles_with_health = db.query(Vehicle).filter(Vehicle.health_score.isnot(None)).all()
    avg_health_score = 0
    if vehicles_with_health:
        avg_health_score = sum(v.health_score for v in vehicles_with_health) / len(vehicles_with_health)
    
    return {
        'total_vehicles': total_vehicles,
        'active_vehicles': active_vehicles,
        'maintenance_vehicles': maintenance_vehicles,
        'average_health_score': round(avg_health_score, 2),
        'vehicles_needing_maintenance': db.query(Vehicle).filter(Vehicle.health_score < 50).count()
    }

def get_maintenance_cost_summary(db: Session, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """Get maintenance cost summary for a date range"""
    history_records = db.query(MaintenanceHistory).filter(
        and_(
            MaintenanceHistory.timestamp >= start_date,
            MaintenanceHistory.timestamp <= end_date
        )
    ).all()
    
    total_cost = sum(record.cost or 0 for record in history_records)
    total_duration = sum(record.duration_hours or 0 for record in history_records)
    
    return {
        'total_cost': total_cost,
        'total_duration': total_duration,
        'maintenance_count': len(history_records),
        'average_cost_per_maintenance': total_cost / len(history_records) if history_records else 0
    }

def get_vehicle_analytics(db: Session, vehicle_id: str) -> Dict[str, Any]:
    """Get analytics for a specific vehicle"""
    vehicle = get_vehicle(db, vehicle_id)
    if not vehicle:
        return {}
    
    # Get latest telemetry
    latest_telemetry = get_latest_telemetry(db, vehicle_id)
    
    # Get latest health analysis
    latest_health = get_latest_health_analysis(db, vehicle_id)
    
    # Get recent maintenance history
    maintenance_history = get_maintenance_history(db, vehicle_id, limit=10)
    
    # Get recent bookings
    recent_bookings = get_bookings(db, vehicle_id=vehicle_id, status='scheduled')
    
    return {
        'vehicle': vehicle,
        'latest_telemetry': latest_telemetry,
        'latest_health': latest_health,
        'recent_maintenance': maintenance_history,
        'scheduled_bookings': recent_bookings,
        'total_maintenance_cost': sum(record.cost or 0 for record in maintenance_history)
    } 