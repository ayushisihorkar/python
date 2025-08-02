from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Vehicle schemas
class VehicleBase(BaseModel):
    company_id: str
    vehicle_reg: str
    vin: str
    brand: str
    model: str

class VehicleCreate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    id: int
    status: str
    battery_soh: Optional[float] = None
    battery_soc: Optional[float] = None
    motor_efficiency: Optional[float] = None
    coolant_level: Optional[float] = None
    last_service_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VehicleDetailResponse(VehicleResponse):
    battery_temp: Optional[float] = None
    motor_rpm: Optional[float] = None
    motor_temp: Optional[float] = None
    coolant_temp: Optional[float] = None
    voltage_imbalance: Optional[float] = None
    charge_cycles: Optional[int] = None
    firmware_version: Optional[str] = None
    error_codes: Optional[List[str]] = None
    latest_telemetry: Optional[Dict[str, Any]] = None
    recent_bookings: Optional[List[Dict[str, Any]]] = None

# Telemetry schemas
class TelemetryData(BaseModel):
    battery_soh: Optional[float] = Field(None, ge=0, le=100, description="Battery State of Health (%)")
    battery_soc: Optional[float] = Field(None, ge=0, le=100, description="Battery State of Charge (%)")
    charge_cycles: Optional[int] = Field(None, ge=0, description="Number of charge cycles")
    voltage_imbalance: Optional[float] = Field(None, ge=0, description="Voltage imbalance (V)")
    battery_temp: Optional[float] = Field(None, description="Battery temperature (°C)")
    motor_rpm: Optional[float] = Field(None, ge=0, description="Motor RPM")
    motor_efficiency: Optional[float] = Field(None, ge=0, le=100, description="Motor efficiency (%)")
    motor_temp: Optional[float] = Field(None, description="Motor temperature (°C)")
    coolant_temp: Optional[float] = Field(None, description="Coolant temperature (°C)")
    coolant_level: Optional[float] = Field(None, ge=0, le=100, description="Coolant level (%)")
    error_codes: Optional[List[str]] = Field(default_factory=list, description="Active error codes")

# Booking schemas
class BookingBase(BaseModel):
    vehicle_id: int
    service_type: str = Field(default="maintenance", description="Type of service")
    priority: str = Field(default="normal", pattern="^(low|normal|high|critical)$")

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    booking_slot: Optional[datetime] = None
    service_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    estimated_duration: Optional[int] = None

class BookingResponse(BookingBase):
    id: int
    workshop_id: str
    workshop_name: Optional[str] = None
    booking_slot: datetime
    estimated_duration: Optional[int] = None
    status: str
    predicted_issue: Optional[str] = None
    confidence_score: Optional[float] = None
    recommended_actions: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Health monitoring schemas
class EmergencyAlert(BaseModel):
    vehicle_id: int
    issue: str
    severity: str = Field(pattern="^(warning|critical|emergency)$")
    location: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class FleetReportRequest(BaseModel):
    company_id: str = "all"
    report_type: str = Field(default="health", pattern="^(health|maintenance|utilization)$")

# Test scenarios
class TestScenario(BaseModel):
    vehicle_id: int
    scenario_type: str = Field(pattern="^(critical_battery|emergency|maintenance_due|motor_overheat|cooling_failure)$")
    parameters: Optional[Dict[str, Any]] = None

# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class VehicleStatusUpdate(BaseModel):
    vehicle_id: int
    status: str
    health_score: Optional[float] = None
    alerts: Optional[List[str]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentStatusUpdate(BaseModel):
    agent_name: str
    status: str
    last_action: Optional[str] = None
    confidence: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class BookingStatusUpdate(BaseModel):
    booking_id: int
    vehicle_id: int
    status: str
    workshop_name: Optional[str] = None
    booking_slot: Optional[datetime] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Notification schemas
class NotificationResponse(BaseModel):
    id: int
    recipient_type: str
    recipient_id: str
    message_type: str
    title: str
    message: str
    severity: str
    read: bool
    action_required: bool
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Workshop schemas
class WorkshopResponse(BaseModel):
    id: int
    workshop_id: str
    name: str
    location: str
    phone: Optional[str] = None
    email: Optional[str] = None
    specialties: Optional[List[str]] = None
    rating: Optional[float] = None
    availability: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Service log schemas
class ServiceLogResponse(BaseModel):
    id: int
    vehicle_id: int
    service_type: str
    description: Optional[str] = None
    service_date: datetime
    completed: bool
    technician: Optional[str] = None
    workshop_id: Optional[str] = None
    cost: Optional[float] = None
    parts_replaced: Optional[List[str]] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Agent action schemas
class AgentActionResponse(BaseModel):
    id: int
    agent_name: str
    action_type: str
    vehicle_id: Optional[int] = None
    status: str
    confidence_score: Optional[float] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True