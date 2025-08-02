from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(String, nullable=False, index=True)
    vehicle_reg = Column(String, unique=True, nullable=False, index=True)
    vin = Column(String, unique=True, nullable=False)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    
    # Battery metrics
    battery_soh = Column(Float)  # State of Health (%)
    battery_soc = Column(Float)  # State of Charge (%)
    charge_cycles = Column(Integer)
    voltage_imbalance = Column(Float)
    battery_temp = Column(Float)
    
    # Motor metrics
    motor_rpm = Column(Float)
    motor_efficiency = Column(Float)
    motor_temp = Column(Float)
    
    # Cooling system
    coolant_temp = Column(Float)
    coolant_level = Column(Float)
    
    # System info
    firmware_version = Column(String)
    error_codes = Column(JSON)  # Store as JSON array
    last_service_date = Column(DateTime)
    
    # Status and timestamps
    status = Column(String, default="operational")  # operational, warning, critical, maintenance
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    telemetry_data = relationship("VehicleTelemetry", back_populates="vehicle")
    service_logs = relationship("ServiceLog", back_populates="vehicle")
    bookings = relationship("Booking", back_populates="vehicle")

class VehicleTelemetry(Base):
    __tablename__ = "vehicle_telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    
    # Real-time metrics (same as Vehicle but timestamped)
    battery_soh = Column(Float)
    battery_soc = Column(Float)
    charge_cycles = Column(Integer)
    voltage_imbalance = Column(Float)
    battery_temp = Column(Float)
    motor_rpm = Column(Float)
    motor_efficiency = Column(Float)
    motor_temp = Column(Float)
    coolant_temp = Column(Float)
    coolant_level = Column(Float)
    error_codes = Column(JSON)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="telemetry_data")

class ServiceLog(Base):
    __tablename__ = "service_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    service_type = Column(String, nullable=False)  # preventive, corrective, inspection
    description = Column(Text)
    service_date = Column(DateTime, nullable=False)
    completed = Column(Boolean, default=False)
    technician = Column(String)
    workshop_id = Column(String)
    cost = Column(Float)
    parts_replaced = Column(JSON)
    notes = Column(Text)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="service_logs")

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    workshop_id = Column(String, nullable=False)
    workshop_name = Column(String)
    booking_slot = Column(DateTime, nullable=False)
    service_type = Column(String, nullable=False)
    estimated_duration = Column(Integer)  # minutes
    priority = Column(String, default="normal")  # low, normal, high, critical
    status = Column(String, default="scheduled")  # scheduled, confirmed, in_progress, completed, cancelled
    
    # AI predictions and recommendations
    predicted_issue = Column(Text)
    confidence_score = Column(Float)
    recommended_actions = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="bookings")

class AgentAction(Base):
    __tablename__ = "agent_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, nullable=False, index=True)
    action_type = Column(String, nullable=False)  # detect, predict, book, notify, log
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    confidence_score = Column(Float)
    processing_time = Column(Float)  # seconds
    error_message = Column(Text)
    
    timestamp = Column(DateTime, default=func.now())
    
class Workshop(Base):
    __tablename__ = "workshops"
    
    id = Column(Integer, primary_key=True, index=True)
    workshop_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    specialties = Column(JSON)  # Array of service types
    availability = Column(JSON)  # Schedule data
    rating = Column(Float)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_type = Column(String, nullable=False)  # fleet_manager, workshop, system
    recipient_id = Column(String, nullable=False)
    message_type = Column(String, nullable=False)  # alert, booking, maintenance, report
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String, default="info")  # info, warning, error, critical
    read = Column(Boolean, default=False)
    action_required = Column(Boolean, default=False)
    metadata = Column(JSON)
    
    created_at = Column(DateTime, default=func.now())
    read_at = Column(DateTime)