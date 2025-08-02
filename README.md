# Rental Fleet Dashboard

An AI-powered rental fleet management system with predictive maintenance capabilities, built with FastAPI backend and React frontend.

## 🚀 Features

### AI Agents
- **Health Monitor Agent**: Detects anomalies and predicts maintenance needs using machine learning
- **Planner Agent**: Optimizes maintenance scheduling with workshop availability
- **Communicator Agent**: Handles notifications to rental companies and workshops
- **Logger Agent**: Maintains comprehensive audit trails and maintenance history
- **Orchestrator Agent**: Coordinates multi-agent workflows and system management

### Core Functionality
- **Real-time Vehicle Monitoring**: Live telemetry data analysis
- **Predictive Maintenance**: AI-driven maintenance predictions
- **Smart Scheduling**: Automated workshop booking optimization
- **Alert System**: Critical issue detection and notification
- **Analytics Dashboard**: Fleet health and cost analysis
- **AI Assistant**: Intelligent help and recommendations

## 🏗️ Architecture

```
rental-fleet-dashboard/
│
├── backend/
│   ├── agents/                 # AI Agent System
│   │   ├── health_monitor.py   # Anomaly detection & maintenance prediction
│   │   ├── planner.py          # Workshop scheduling optimization
│   │   ├── communicator.py     # Notification management
│   │   ├── logger.py           # Audit trails & history
│   │   └── orchestrator.py     # Multi-agent coordination
│   │
│   ├── api/                    # FastAPI Backend
│   │   ├── main.py            # API routes and endpoints
│   │   ├── models.py          # Pydantic models & schemas
│   │   ├── database.py        # SQLAlchemy ORM setup
│   │   └── crud.py            # Database operations
│   │
│   ├── data/                   # Sample Data
│   │   └── sample_vehicle_data.json
│   │
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/         # React Components
│   │   │   ├── VehicleCard.jsx
│   │   │   ├── BookingCalendar.jsx
│   │   │   ├── AIAssistantPanel.jsx
│   │   │   └── Notifications.jsx
│   │   │
│   │   ├── pages/             # Page Components
│   │   │   ├── Dashboard.jsx
│   │   │   └── VehicleDetail.jsx
│   │   │
│   │   ├── services/          # API Integration
│   │   │   └── api.js
│   │   │
│   │   ├── App.jsx
│   │   └── index.js
│   │
│   ├── styles/
│   │   └── tailwind.css       # TailwindCSS configuration
│   │
│   └── package.json           # Node.js dependencies
│
└── README.md
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **SQLite/PostgreSQL**: Database
- **Scikit-learn**: Machine learning for anomaly detection
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Modern React with hooks
- **TailwindCSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **Lucide React**: Icon library
- **Axios**: HTTP client
- **React Router**: Client-side routing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend server**:
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## 📊 API Endpoints

### Vehicles
- `GET /vehicles` - Get all vehicles
- `GET /vehicles/{id}` - Get specific vehicle
- `POST /vehicles` - Create new vehicle
- `PUT /vehicles/{id}` - Update vehicle
- `DELETE /vehicles/{id}` - Delete vehicle

### Telemetry
- `POST /telemetry` - Submit vehicle telemetry
- `GET /vehicles/{id}/telemetry` - Get telemetry history
- `GET /vehicles/{id}/telemetry/latest` - Get latest telemetry

### Health Analysis
- `GET /vehicles/{id}/health` - Get health analysis
- `GET /vehicles/{id}/health/history` - Get health history

### Maintenance
- `POST /maintenance/tasks` - Create maintenance task
- `GET /maintenance/tasks` - Get maintenance tasks
- `PUT /maintenance/tasks/{id}` - Update maintenance task

### Bookings
- `POST /bookings` - Create booking
- `GET /bookings` - Get bookings
- `GET /bookings/{id}` - Get specific booking
- `PUT /bookings/{id}` - Update booking
- `DELETE /bookings/{id}` - Cancel booking

### Analytics
- `GET /analytics/fleet` - Get fleet analytics
- `GET /reports/fleet` - Generate fleet report

## 🤖 AI Agent System

### Health Monitor Agent
- **Anomaly Detection**: Uses isolation forest algorithm
- **Maintenance Prediction**: Based on mileage and component health
- **Health Scoring**: 0-100 score based on multiple factors
- **Alert Generation**: Automatic alert creation for critical issues

### Planner Agent
- **Workshop Optimization**: Finds best available workshops
- **Scheduling Algorithm**: Considers cost, rating, and availability
- **Time Slot Management**: Optimizes booking times
- **Cost Analysis**: Estimates maintenance costs

### Communicator Agent
- **Email Notifications**: HTML email templates
- **SMS Integration**: Ready for Twilio integration
- **Priority Handling**: Emergency notifications
- **Workshop Communication**: Automated booking confirmations

### Logger Agent
- **Audit Trails**: Complete system activity logging
- **Maintenance History**: Detailed service records
- **Health Logs**: Vehicle health tracking over time
- **Report Generation**: Export capabilities

### Orchestrator Agent
- **Workflow Coordination**: Manages multi-agent interactions
- **System State Management**: Tracks fleet status
- **Emergency Handling**: Critical issue response
- **Performance Monitoring**: System health tracking

## 🎨 UI Features

### Dashboard
- **Real-time Stats**: Fleet overview with live metrics
- **Vehicle Cards**: Individual vehicle status and health
- **Search & Filter**: Advanced vehicle filtering
- **AI Assistant**: Floating chat interface

### Vehicle Details
- **Live Telemetry**: Real-time vehicle data
- **Health Analysis**: Detailed health breakdown
- **Maintenance History**: Complete service records
- **Quick Actions**: One-click maintenance scheduling

### Booking Calendar
- **Interactive Calendar**: Date and time selection
- **Workshop Comparison**: Rating and cost comparison
- **Service Selection**: Maintenance type selection
- **Cost Estimation**: Real-time cost calculation

### Notifications
- **Alert Management**: Critical and warning alerts
- **Filter System**: Alert type filtering
- **Read/Unread**: Alert status tracking
- **Bulk Actions**: Mark all as read

## 🔧 Configuration

### Environment Variables
```bash
# Backend
DATABASE_URL=sqlite:///./rental_fleet.db
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

### Database Setup
The system uses SQLite by default. For production, configure PostgreSQL:

```python
# backend/api/database.py
DATABASE_URL = "postgresql://user:password@localhost/rental_fleet"
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Performance

- **Real-time Updates**: WebSocket support for live data
- **Optimized Queries**: Database indexing and query optimization
- **Caching**: Redis integration ready
- **Scalability**: Microservices architecture ready

## 🔒 Security

- **Input Validation**: Pydantic model validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Cross-origin request handling
- **Rate Limiting**: API rate limiting ready

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Production Setup
1. Configure environment variables
2. Set up PostgreSQL database
3. Configure SMTP for notifications
4. Set up SSL certificates
5. Configure reverse proxy (nginx)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the code comments for implementation details

## 🔮 Future Enhancements

- **Machine Learning**: Advanced predictive models
- **IoT Integration**: Real vehicle sensor data
- **Mobile App**: React Native mobile application
- **Blockchain**: Maintenance record verification
- **AR/VR**: Virtual vehicle inspection
- **Voice Commands**: AI assistant voice interface 