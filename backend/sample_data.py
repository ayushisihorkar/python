"""
Sample data population script for Fleet Maintenance Dashboard
Run this script to populate the database with sample vehicles and workshops
"""

import asyncio
from datetime import datetime, timedelta
from database.database import init_db, AsyncSessionLocal
from database.models import Vehicle, Workshop, Booking, VehicleTelemetry, ServiceLog

async def populate_sample_data():
    """Populate the database with sample data"""
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Sample Vehicles
        vehicles = [
            Vehicle(
                company_id="fleet_001",
                vehicle_reg="EV001",
                vin="1HGCR2F30EA100001",
                brand="Tesla",
                model="Model 3",
                battery_soh=95.0,
                battery_soc=87.0,
                motor_efficiency=92.0,
                coolant_level=85.0,
                battery_temp=32.0,
                motor_temp=45.0,
                coolant_temp=38.0,
                charge_cycles=1250,
                voltage_imbalance=0.1,
                firmware_version="2024.1.3",
                status="operational",
                last_service_date=datetime.utcnow() - timedelta(days=30)
            ),
            Vehicle(
                company_id="fleet_001",
                vehicle_reg="EV002",
                vin="1HGCR2F30EA100002",
                brand="BMW",
                model="i4",
                battery_soh=78.0,
                battery_soc=45.0,
                motor_efficiency=88.0,
                coolant_level=65.0,
                battery_temp=42.0,
                motor_temp=52.0,
                coolant_temp=44.0,
                charge_cycles=2800,
                voltage_imbalance=0.3,
                firmware_version="2023.12.1",
                status="warning",
                error_codes=["TEMP_002"],
                last_service_date=datetime.utcnow() - timedelta(days=60)
            ),
            Vehicle(
                company_id="fleet_001",
                vehicle_reg="EV003",
                vin="1HGCR2F30EA100003",
                brand="Audi",
                model="e-tron",
                battery_soh=68.0,
                battery_soc=23.0,
                motor_efficiency=74.0,
                coolant_level=18.0,
                battery_temp=47.0,
                motor_temp=58.0,
                coolant_temp=51.0,
                charge_cycles=3500,
                voltage_imbalance=0.6,
                firmware_version="2023.8.2",
                status="critical",
                error_codes=["BATT_001", "COOL_003"],
                last_service_date=datetime.utcnow() - timedelta(days=90)
            ),
            Vehicle(
                company_id="fleet_001",
                vehicle_reg="EV004",
                vin="1HGCR2F30EA100004",
                brand="Volkswagen",
                model="ID.4",
                battery_soh=91.0,
                battery_soc=78.0,
                motor_efficiency=89.0,
                coolant_level=92.0,
                battery_temp=35.0,
                motor_temp=41.0,
                coolant_temp=39.0,
                charge_cycles=980,
                voltage_imbalance=0.15,
                firmware_version="2024.1.1",
                status="operational",
                last_service_date=datetime.utcnow() - timedelta(days=20)
            ),
            Vehicle(
                company_id="fleet_001",
                vehicle_reg="EV005",
                vin="1HGCR2F30EA100005",
                brand="Mercedes",
                model="EQS",
                battery_soh=85.0,
                battery_soc=0.0,
                motor_efficiency=90.0,
                coolant_level=88.0,
                battery_temp=28.0,
                motor_temp=30.0,
                coolant_temp=32.0,
                charge_cycles=1800,
                voltage_imbalance=0.08,
                firmware_version="2024.1.2",
                status="maintenance",
                last_service_date=datetime.utcnow() - timedelta(days=5)
            ),
            Vehicle(
                company_id="fleet_001",
                vehicle_reg="EV006",
                vin="1HGCR2F30EA100006",
                brand="Nissan",
                model="Ariya",
                battery_soh=88.0,
                battery_soc=91.0,
                motor_efficiency=87.0,
                coolant_level=78.0,
                battery_temp=31.0,
                motor_temp=43.0,
                coolant_temp=37.0,
                charge_cycles=1650,
                voltage_imbalance=0.12,
                firmware_version="2023.11.4",
                status="operational",
                last_service_date=datetime.utcnow() - timedelta(days=40)
            )
        ]
        
        # Sample Workshops
        workshops = [
            Workshop(
                workshop_id="ws_001",
                name="AutoTech Center",
                location="123 Industrial Ave, Tech City",
                phone="+1-555-0101",
                email="bookings@autotech.com",
                specialties=["battery_service", "motor_service", "general"],
                rating=4.5,
                availability={"hours": "8:00-18:00", "days": "Mon-Sat"}
            ),
            Workshop(
                workshop_id="ws_002",
                name="EV Specialists",
                location="456 Electric Blvd, Green Valley",
                phone="+1-555-0102",
                email="service@evspecialists.com",
                specialties=["battery_service", "cooling_service", "diagnostics"],
                rating=4.8,
                availability={"hours": "7:00-19:00", "days": "Mon-Sun"}
            ),
            Workshop(
                workshop_id="ws_003",
                name="Fleet Maintenance Pro",
                location="789 Service Road, Industrial Park",
                phone="+1-555-0103",
                email="fleet@maintenancepro.com",
                specialties=["general", "preventive", "emergency"],
                rating=4.3,
                availability={"hours": "6:00-20:00", "days": "Mon-Sun"}
            ),
            Workshop(
                workshop_id="ws_004",
                name="Quick Fix Motors",
                location="321 Repair Lane, Downtown",
                phone="+1-555-0104",
                email="info@quickfixmotors.com",
                specialties=["emergency", "diagnostics", "general"],
                rating=4.1,
                availability={"hours": "24/7", "days": "Mon-Sun"}
            )
        ]
        
        # Add vehicles and workshops to session
        for vehicle in vehicles:
            session.add(vehicle)
        
        for workshop in workshops:
            session.add(workshop)
        
        await session.commit()
        
        # Refresh to get IDs
        for vehicle in vehicles:
            await session.refresh(vehicle)
        
        # Sample Bookings
        bookings = [
            Booking(
                vehicle_id=vehicles[1].id,  # EV002 (warning status)
                workshop_id="ws_001",
                workshop_name="AutoTech Center",
                booking_slot=datetime.utcnow() + timedelta(days=2, hours=10),
                service_type="preventive",
                estimated_duration=120,
                priority="high",
                status="scheduled",
                predicted_issue="Battery temperature monitoring",
                confidence_score=0.85,
                recommended_actions=["Battery inspection", "Cooling system check"]
            ),
            Booking(
                vehicle_id=vehicles[2].id,  # EV003 (critical status)
                workshop_id="ws_002",
                workshop_name="EV Specialists",
                booking_slot=datetime.utcnow() + timedelta(days=1, hours=9),
                service_type="corrective",
                estimated_duration=240,
                priority="critical",
                status="confirmed",
                predicted_issue="Critical battery degradation and cooling issues",
                confidence_score=0.95,
                recommended_actions=["Emergency battery service", "Coolant system repair"]
            ),
            Booking(
                vehicle_id=vehicles[4].id,  # EV005 (maintenance status)
                workshop_id="ws_001",
                workshop_name="AutoTech Center",
                booking_slot=datetime.utcnow() + timedelta(hours=2),
                service_type="inspection",
                estimated_duration=60,
                priority="normal",
                status="in_progress",
                predicted_issue="Routine maintenance completion",
                confidence_score=0.9,
                recommended_actions=["Final inspection", "Software update"]
            )
        ]
        
        for booking in bookings:
            session.add(booking)
        
        # Sample Telemetry Data
        telemetry_data = []
        for vehicle in vehicles:
            # Generate some historical telemetry
            for i in range(10):
                timestamp = datetime.utcnow() - timedelta(hours=i * 6)
                
                # Add some variation to the base values
                variation = 1 + (i * 0.02)  # Slight degradation over time
                
                telemetry = VehicleTelemetry(
                    vehicle_id=vehicle.id,
                    timestamp=timestamp,
                    battery_soh=max(60, vehicle.battery_soh / variation) if vehicle.battery_soh else None,
                    battery_soc=min(100, max(0, vehicle.battery_soc + (i % 3 - 1) * 5)) if vehicle.battery_soc else None,
                    motor_efficiency=max(70, vehicle.motor_efficiency / variation) if vehicle.motor_efficiency else None,
                    coolant_level=max(0, vehicle.coolant_level - i * 0.5) if vehicle.coolant_level else None,
                    battery_temp=vehicle.battery_temp + (i % 3 - 1) * 2 if vehicle.battery_temp else None,
                    motor_temp=vehicle.motor_temp + (i % 3 - 1) * 3 if vehicle.motor_temp else None,
                    coolant_temp=vehicle.coolant_temp + (i % 3 - 1) * 2 if vehicle.coolant_temp else None,
                    charge_cycles=vehicle.charge_cycles + i if vehicle.charge_cycles else None,
                    voltage_imbalance=vehicle.voltage_imbalance + i * 0.01 if vehicle.voltage_imbalance else None,
                    error_codes=vehicle.error_codes if i == 0 else []
                )
                telemetry_data.append(telemetry)
        
        for telemetry in telemetry_data:
            session.add(telemetry)
        
        # Sample Service Logs
        service_logs = [
            ServiceLog(
                vehicle_id=vehicles[0].id,
                service_type="preventive",
                description="Routine maintenance and battery check",
                service_date=datetime.utcnow() - timedelta(days=30),
                completed=True,
                technician="John Smith",
                workshop_id="ws_001",
                cost=250.00,
                parts_replaced=["air_filter", "cabin_filter"],
                notes="All systems operating normally"
            ),
            ServiceLog(
                vehicle_id=vehicles[1].id,
                service_type="corrective",
                description="Battery temperature sensor replacement",
                service_date=datetime.utcnow() - timedelta(days=60),
                completed=True,
                technician="Sarah Johnson",
                workshop_id="ws_002",
                cost=450.00,
                parts_replaced=["temp_sensor_001"],
                notes="Temperature readings normalized after replacement"
            ),
            ServiceLog(
                vehicle_id=vehicles[2].id,
                service_type="inspection",
                description="Pre-service inspection",
                service_date=datetime.utcnow() - timedelta(days=1),
                completed=True,
                technician="Mike Wilson",
                workshop_id="ws_002",
                cost=75.00,
                notes="Multiple issues identified, requires immediate attention"
            )
        ]
        
        for service_log in service_logs:
            session.add(service_log)
        
        await session.commit()
        
        print("✅ Sample data populated successfully!")
        print(f"   - {len(vehicles)} vehicles added")
        print(f"   - {len(workshops)} workshops added")
        print(f"   - {len(bookings)} bookings added")
        print(f"   - {len(telemetry_data)} telemetry records added")
        print(f"   - {len(service_logs)} service logs added")

if __name__ == "__main__":
    asyncio.run(populate_sample_data())