from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
from contextlib import asynccontextmanager

from database.database import init_db
from agents.agent_coordinator import AgentCoordinator
from api.routes import vehicle_router, booking_router, health_router, set_agent_coordinator
from api.websocket import WebSocketManager

# Initialize agent coordinator and websocket manager
agent_coordinator = AgentCoordinator()
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    set_agent_coordinator(agent_coordinator)
    await agent_coordinator.start()
    yield
    # Shutdown
    await agent_coordinator.stop()

app = FastAPI(
    title="Fleet Maintenance Dashboard API",
    description="Multi-Agent AI System for Rental Fleet Maintenance",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vehicle_router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(booking_router, prefix="/api/bookings", tags=["bookings"])
app.include_router(health_router, prefix="/api/health", tags=["health"])

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_client_message(websocket, data)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Fleet Maintenance Dashboard API", "status": "running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )