from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="Fleet Maintenance Dashboard API",
    description="Multi-Agent AI System for Rental Fleet Maintenance", 
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Fleet Maintenance Dashboard API", "status": "running"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

@app.get("/api/vehicles")
async def get_vehicles():
    return {
        "vehicles": [
            {
                "id": 1,
                "vehicle_reg": "FL-2024-001", 
                "brand": "Tesla",
                "model": "Model 3",
                "status": "operational",
                "battery_soh": 95.2,
                "battery_soc": 87.5,
                "motor_efficiency": 92.1,
                "coolant_level": 98.0,
                "battery_temp": 23.4,
                "last_service_date": "2024-01-01",
                "error_codes": []
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )