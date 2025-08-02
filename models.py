from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

class VehicleStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    RENTED = "rented"

class MaintenanceUrgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertType(str, Enum):
    WARNING = "warning"
    CRITICAL = "critical"
    INFO = "info"

class BookingStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Vehicle Models
class VehicleBase(BaseModel):
    id: str = Field(..., description="Unique vehicle identifier")
    make: str = Field(..., description="Vehicle make")
    model: str = Field(..., description="Vehicle model")
    year: int = Field(..., description="Vehicle year")
    license_plate: str = Field(..., description="License plate number")
    status: VehicleStatus = Field(default=VehicleStatus.ACTIVE, description="Current vehicle status")
    location: Optional[str] = Field(None, description="Current vehicle location")

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    license_plate: Optional[str] = None
    status: Optional[VehicleStatus] = None
    location: Optional[str] = None

class Vehicle(VehicleBase):
    health_score: Optional[int] = Field(None, description="Current health score (0-100)")
    last_maintenance: Optional[datetime] = Field(None, description="Last maintenance date")
    mileage: Optional[int] = Field(None, description="Current mileage")
    fuel_level: Optional[float] = Field(None, description="Current fuel level percentage")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

# Telemetry Models
class TelemetryData(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle identifier")
    engine_temp: float = Field(..., description="Engine temperature in Celsius")
    oil_pressure: float = Field(..., description="Oil pressure in PSI")
    battery_voltage: float = Field(..., description="Battery voltage")
    tire_pressure: float = Field(..., description="Tire pressure in PSI")
    fuel_level: float = Field(..., description="Fuel level percentage")
    mileage: int = Field(..., description="Current mileage")
    speed: float = Field(..., description="Current speed in mph")
    latitude: Optional[float] = Field(None, description="GPS latitude")
    longitude: Optional[float] = Field(None, description="GPS longitude")
    timestamp: datetime = Field(default_factory=datetime.now)

# Health Analysis Models
class Anomaly(BaseModel):
    type: str = Field(..., description="Anomaly type (warning/critical)")
    metric: str = Field(..., description="Metric name")
    value: float = Field(..., description="Current value")
    threshold: float = Field(..., description="Threshold value")
    message: str = Field(..., description="Anomaly message")

class MaintenancePrediction(BaseModel):
    type: str = Field(..., description="Maintenance type")
    urgency: MaintenanceUrgency = Field(..., description="Urgency level")
    estimated_date: datetime = Field(..., description="Estimated maintenance date")
    description: str = Field(..., description="Maintenance description")

class HealthAnalysis(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle identifier")
    health_score: int = Field(..., description="Health score (0-100)")
    anomalies: List[Anomaly] = Field(default_factory=list, description="Detected anomalies")
    maintenance_predictions: List[MaintenancePrediction] = Field(default_factory=list, description="Maintenance predictions")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="Generated alerts")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="Maintenance recommendations")
    timestamp: datetime = Field(default_factory=datetime.now)

# Alert Models
class Alert(BaseModel):
    id: str = Field(..., description="Alert identifier")
    type: AlertType = Field(..., description="Alert type")
    message: str = Field(..., description="Alert message")
    timestamp: datetime = Field(default_factory=datetime.now)
    action_required: bool = Field(default=True, description="Whether action is required")
    vehicle_id: str = Field(..., description="Associated vehicle")

# Maintenance Models
class MaintenanceTask(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle identifier")
    task_type: str = Field(..., description="Maintenance task type")
    urgency: MaintenanceUrgency = Field(..., description="Task urgency")
    estimated_duration: int = Field(..., description="Estimated duration in hours")
    estimated_cost: float = Field(..., description="Estimated cost")
    description: Optional[str] = Field(None, description="Task description")
    preferred_date: Optional[datetime] = Field(None, description="Preferred maintenance date")

class MaintenanceTaskCreate(MaintenanceTask):
    pass

class MaintenanceTaskUpdate(BaseModel):
    task_type: Optional[str] = None
    urgency: Optional[MaintenanceUrgency] = None
    estimated_duration: Optional[int] = None
    estimated_cost: Optional[float] = None
    description: Optional[str] = None
    preferred_date: Optional[datetime] = None

# Booking Models
class BookingBase(BaseModel):
    vehicle_id: str = Field(..., description="Vehicle identifier")
    workshop_id: str = Field(..., description="Workshop identifier")
    task_type: str = Field(..., description="Maintenance task type")
    scheduled_date: str = Field(..., description="Scheduled date (YYYY-MM-DD)")
    scheduled_time: str = Field(..., description="Scheduled time (HH:MM)")
    estimated_duration: int = Field(..., description="Estimated duration in hours")
    estimated_cost: float = Field(..., description="Estimated cost")
    urgency: MaintenanceUrgency = Field(..., description="Booking urgency")

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    scheduled_date: Optional[str] = None
    scheduled_time: Optional[str] = None
    estimated_duration: Optional[int] = None
    estimated_cost: Optional[float] = None
    urgency: Optional[MaintenanceUrgency] = None
    status: Optional[BookingStatus] = None

class Booking(BookingBase):
    booking_id: str = Field(..., description="Unique booking identifier")
    workshop_name: str = Field(..., description="Workshop name")
    status: BookingStatus = Field(default=BookingStatus.SCHEDULED, description="Booking status")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True

# Workshop Models
class Workshop(BaseModel):
    id: str = Field(..., description="Workshop identifier")
    name: str = Field(..., description="Workshop name")
    location: str = Field(..., description="Workshop location")
    services: List[str] = Field(..., description="Available services")
    rating: float = Field(..., description="Workshop rating")
    cost_multiplier: float = Field(..., description="Cost multiplier")
    availability: Dict[str, List[str]] = Field(..., description="Availability schedule")

# Report Models
class FleetReport(BaseModel):
    period: Dict[str, str] = Field(..., description="Report period")
    fleet_summary: Dict[str, Any] = Field(..., description="Fleet summary")
    maintenance_summary: Dict[str, Any] = Field(..., description="Maintenance summary")
    health_summary: Dict[str, Any] = Field(..., description="Health summary")
    cost_analysis: Dict[str, Any] = Field(..., description="Cost analysis")
    generated_at: datetime = Field(default_factory=datetime.now)

# System Status Models
class SystemStatus(BaseModel):
    status: str = Field(..., description="System status")
    active_vehicles: int = Field(..., description="Number of active vehicles")
    pending_maintenance: int = Field(..., description="Number of pending maintenance tasks")
    last_updated: datetime = Field(default_factory=datetime.now)

# Response Models
class HealthAnalysisResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: HealthAnalysis = Field(..., description="Health analysis data")
    message: Optional[str] = Field(None, description="Response message")

class BookingResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: Booking = Field(..., description="Booking data")
    message: Optional[str] = Field(None, description="Response message")

class FleetReportResponse(BaseModel):
    success: bool = Field(..., description="Request success status")
    data: FleetReport = Field(..., description="Fleet report data")
    message: Optional[str] = Field(None, description="Response message")

class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details") 