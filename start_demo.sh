#!/bin/bash

echo "🚗 Fleet Maintenance Dashboard - Demo Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup Backend
echo ""
echo "🔧 Setting up Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Populate sample data
echo "Populating sample data..."
python sample_data.py

echo "✅ Backend setup complete"

# Setup Frontend
echo ""
echo "🎨 Setting up Frontend..."
cd ..

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "✅ Frontend setup complete"

echo ""
echo "🚀 Starting Demo..."
echo ""
echo "The application will start in two terminals:"
echo "1. Backend API Server (http://localhost:8000)"
echo "2. Frontend Development Server (http://localhost:3000)"
echo ""
echo "Press Ctrl+C in either terminal to stop the servers"
echo ""

# Start backend in background
echo "Starting backend server..."
cd backend
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd ..
npm run dev &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Demo stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

echo ""
echo "🌟 Demo is running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Try these test scenarios:"
echo "  - View the fleet dashboard with sample vehicles"
echo "  - Interact with the AI assistant (bottom-right corner)"
echo "  - Click on vehicle cards to see details"
echo "  - Check the booking management page"
echo ""
echo "Press Ctrl+C to stop the demo"

# Wait for user to stop
wait