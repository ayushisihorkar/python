import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rental_fleet.db")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Database Models
class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(String, primary_key=True, index=True)
    make = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    license_plate = Column(String, unique=True, nullable=False)
    status = Column(String, default="active")
    location = Column(String, nullable=True)
    health_score = Column(Integer, nullable=True)
    last_maintenance = Column(DateTime, nullable=True)
    mileage = Column(Integer, nullable=True)
    fuel_level = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    engine_temp = Column(Float, nullable=False)
    oil_pressure = Column(Float, nullable=False)
    battery_voltage = Column(Float, nullable=False)
    tire_pressure = Column(Float, nullable=False)
    fuel_level = Column(Float, nullable=False)
    mileage = Column(Integer, nullable=False)
    speed = Column(Float, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class HealthAnalysis(Base):
    __tablename__ = "health_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    health_score = Column(Integer, nullable=False)
    anomalies = Column(Text, nullable=True)  # JSON string
    maintenance_predictions = Column(Text, nullable=True)  # JSON string
    alerts = Column(Text, nullable=True)  # JSON string
    recommendations = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)

class MaintenanceTask(Base):
    __tablename__ = "maintenance_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    task_type = Column(String, nullable=False)
    urgency = Column(String, nullable=False)
    estimated_duration = Column(Integer, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    preferred_date = Column(DateTime, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(String, unique=True, nullable=False, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    workshop_id = Column(String, nullable=False)
    workshop_name = Column(String, nullable=False)
    task_type = Column(String, nullable=False)
    scheduled_date = Column(String, nullable=False)
    scheduled_time = Column(String, nullable=False)
    estimated_duration = Column(Integer, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    urgency = Column(String, nullable=False)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Workshop(Base):
    __tablename__ = "workshops"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    services = Column(Text, nullable=False)  # JSON string
    rating = Column(Float, nullable=False)
    cost_multiplier = Column(Float, nullable=False)
    availability = Column(Text, nullable=False)  # JSON string
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, nullable=False, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    action_required = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

class MaintenanceHistory(Base):
    __tablename__ = "maintenance_history"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, nullable=False, index=True)
    task_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    performed_by = Column(String, nullable=True)
    workshop_id = Column(String, nullable=True)
    cost = Column(Float, nullable=True)
    duration_hours = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")
    notes = Column(Text, nullable=True)

# Database dependency
def get_db():
    """
    Database dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database initialization
def init_db():
    """
    Initialize database tables
    """
    Base.metadata.create_all(bind=engine)
    
    # Create default workshops if they don't exist
    db = SessionLocal()
    try:
        # Check if workshops exist
        existing_workshops = db.query(Workshop).count()
        if existing_workshops == 0:
            # Add default workshops
            default_workshops = [
                {
                    "id": "ws_001",
                    "name": "Premium Auto Service",
                    "location": "Downtown",
                    "services": '["oil_change", "tire_rotation", "battery_replacement", "brake_service"]',
                    "rating": 4.8,
                    "cost_multiplier": 1.2,
                    "availability": '{"monday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"], "tuesday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"], "wednesday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"], "thursday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"], "friday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]}',
                    "email": "premium@autoservice.com"
                },
                {
                    "id": "ws_002",
                    "name": "Quick Fix Garage",
                    "location": "Suburbs",
                    "services": '["oil_change", "tire_rotation", "battery_replacement"]',
                    "rating": 4.2,
                    "cost_multiplier": 0.9,
                    "availability": '{"monday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"], "tuesday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"], "wednesday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"], "thursday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"], "friday": ["08:00", "09:00", "10:00", "13:00", "14:00", "15:00"]}',
                    "email": "quickfix@garage.com"
                },
                {
                    "id": "ws_003",
                    "name": "Express Maintenance",
                    "location": "Airport Area",
                    "services": '["oil_change", "tire_rotation"]',
                    "rating": 4.5,
                    "cost_multiplier": 1.0,
                    "availability": '{"monday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"], "tuesday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"], "wednesday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"], "thursday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"], "friday": ["07:00", "08:00", "09:00", "12:00", "13:00", "14:00"]}',
                    "email": "express@maintenance.com"
                }
            ]
            
            for workshop_data in default_workshops:
                workshop = Workshop(**workshop_data)
                db.add(workshop)
            
            db.commit()
            print("Default workshops created successfully")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

# Database utilities
def get_vehicle_by_id(db, vehicle_id: str):
    """
    Get vehicle by ID
    """
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

def get_vehicles(db, skip: int = 0, limit: int = 100):
    """
    Get all vehicles with pagination
    """
    return db.query(Vehicle).offset(skip).limit(limit).all()

def create_vehicle(db, vehicle_data: dict):
    """
    Create a new vehicle
    """
    vehicle = Vehicle(**vehicle_data)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

def update_vehicle(db, vehicle_id: str, vehicle_data: dict):
    """
    Update a vehicle
    """
    vehicle = get_vehicle_by_id(db, vehicle_id)
    if vehicle:
        for key, value in vehicle_data.items():
            if value is not None:
                setattr(vehicle, key, value)
        vehicle.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(vehicle)
    return vehicle

def delete_vehicle(db, vehicle_id: str):
    """
    Delete a vehicle
    """
    vehicle = get_vehicle_by_id(db, vehicle_id)
    if vehicle:
        db.delete(vehicle)
        db.commit()
        return True
    return False 