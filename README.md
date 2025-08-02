# Fleet Maintenance Dashboard

A modern, AI-powered rental fleet maintenance dashboard built with a multi-agent system architecture. This application provides real-time vehicle monitoring, predictive maintenance scheduling, and automated booking workflows for electric vehicle fleets.

## 🚀 Features

### Multi-Agent AI System
- **Health Monitor Agent**: Detects anomalies in vehicle telemetry and predicts service needs
- **Planner Agent**: Coordinates booking schedules and finds nearby workshops
- **Communicator Agent**: Sends notifications and alerts to fleet managers and workshops
- **Logger Agent**: Maintains comprehensive vehicle health history and service logs

### Modern Dashboard Interface
- **Card-based UI**: Clean, spacious design with vehicle images and real-time stats
- **Real-time Updates**: WebSocket connections for live vehicle status updates
- **AI Assistant**: Interactive chat interface for fleet management assistance
- **Responsive Design**: Works seamlessly on desktop and mobile devices

### Core Functionality
- Vehicle telemetry monitoring (battery health, motor efficiency, cooling system)
- Predictive maintenance scheduling with AI-powered insights
- Automated workshop booking with availability checking
- Real-time anomaly detection and alerting
- Comprehensive reporting and analytics

## 🏗️ Architecture

### Backend (FastAPI + SQLAlchemy)
```
backend/
├── main.py                 # FastAPI application entry point
├── database/
│   ├── models.py          # SQLAlchemy database models
│   └── database.py        # Database connection and initialization
├── agents/
│   ├── base_agent.py      # Base agent class with common functionality
│   ├── health_monitor_agent.py    # Vehicle health monitoring
│   ├── planner_agent.py           # Booking and scheduling
│   ├── communicator_agent.py      # Notifications and alerts
│   ├── logger_agent.py            # Data logging and history
│   └── agent_coordinator.py       # Multi-agent orchestration
└── api/
    ├── routes.py          # API endpoints
    ├── schemas.py         # Pydantic models
    └── websocket.py       # Real-time WebSocket manager
```

### Frontend (React + TailwindCSS)
```
src/
├── components/
│   ├── VehicleCard.jsx    # Main vehicle display component
│   ├── AIAssistant.jsx    # Interactive AI chat interface
│   └── Layout.jsx         # Application layout and navigation
├── pages/
│   ├── Dashboard.jsx      # Main fleet overview
│   ├── VehicleDetail.jsx  # Individual vehicle details
│   └── BookingManagement.jsx  # Maintenance scheduling
├── hooks/
│   └── useWebSocket.jsx   # WebSocket connection management
└── App.jsx               # Main application component
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup
1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 📊 API Endpoints

### Vehicle Management
- `GET /api/vehicles` - List all vehicles with filtering options
- `GET /api/vehicles/{id}` - Get detailed vehicle information
- `POST /api/vehicles` - Create a new vehicle
- `POST /api/vehicles/{id}/telemetry` - Ingest vehicle telemetry data
- `POST /api/vehicles/{id}/health-check` - Perform AI health assessment

### Booking Management
- `GET /api/bookings` - List bookings with filtering
- `POST /api/bookings` - Create new maintenance booking
- `PUT /api/bookings/{id}` - Update existing booking
- `DELETE /api/bookings/{id}` - Cancel booking
- `GET /api/bookings/workshops/available` - Find available workshops

### Health Monitoring
- `GET /api/health/agent-status` - Get status of all AI agents
- `POST /api/health/emergency` - Handle emergency situations
- `POST /api/health/fleet-report` - Generate fleet health reports
- `GET /api/health/notifications` - Get notifications for recipients

### Test Simulation
- `POST /api/health/test-scenario` - Simulate various test scenarios:
  - `critical_battery` - Simulate critical battery conditions
  - `emergency` - Simulate emergency situations
  - `maintenance_due` - Simulate routine maintenance needs

## 🧪 Testing the System

### Simulate Vehicle Data
You can test the multi-agent system by sending telemetry data:

```bash
curl -X POST "http://localhost:8000/api/vehicles/1/telemetry" \
  -H "Content-Type: application/json" \
  -d '{
    "battery_soh": 65.0,
    "battery_temp": 47.0,
    "voltage_imbalance": 0.6,
    "motor_efficiency": 78.0,
    "coolant_level": 15.0,
    "error_codes": ["BATT_001", "TEMP_002"]
  }'
```

### Test Emergency Scenarios
```bash
curl -X POST "http://localhost:8000/api/health/test-scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "scenario_type": "critical_battery"
  }'
```

## 🎨 Design System

The application uses a modern design system with:
- **Color Palette**: Primary blue theme with semantic status colors
- **Typography**: Inter font family for clean, professional appearance
- **Components**: Reusable card-based components with consistent styling
- **Icons**: Lucide React icons for consistent visual language
- **Spacing**: Tailwind's spacing system for consistent layouts

### Status Indicators
- 🟢 **Operational**: Vehicle is functioning normally
- 🟡 **Warning**: Vehicle needs attention soon
- 🔴 **Critical**: Immediate action required
- 🔵 **Maintenance**: Vehicle is currently being serviced

## 🤖 AI Agent Workflows

### Vehicle Telemetry Processing
1. **Logger Agent**: Stores incoming telemetry data
2. **Health Monitor**: Analyzes data for anomalies
3. **Planner Agent**: Schedules maintenance if issues found
4. **Communicator**: Sends notifications to relevant parties

### Emergency Handling
1. **Immediate Alert**: Critical notifications sent to fleet managers
2. **Emergency Booking**: Highest priority maintenance scheduling
3. **Status Update**: Vehicle marked as critical in system
4. **Follow-up**: Automated progress tracking and updates

## 🔧 Configuration

### Database
The application uses SQLite by default for development. For production, update the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:password@localhost/fleet_db"
```

### Agent Configuration
Agent thresholds and behaviors can be configured in the respective agent classes:
- Battery health thresholds in `health_monitor_agent.py`
- Booking priorities in `planner_agent.py`
- Notification templates in `communicator_agent.py`

## 🚀 Deployment

### Backend Deployment
1. Set up environment variables for production database
2. Use a WSGI server like Gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
1. Build the production bundle:
```bash
npm run build
```

2. Serve the built files with any static file server

## 📈 Future Enhancements

- **Advanced Analytics**: Machine learning models for better predictions
- **Mobile App**: Native mobile application for field technicians
- **Integration APIs**: Connect with existing fleet management systems
- **Advanced Reporting**: Custom report builder with data visualization
- **Multi-tenant Support**: Support for multiple fleet operators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions and support, please open an issue in the GitHub repository or contact the development team.

---

Built with ❤️ for modern fleet management 