#!/bin/bash

# GR Cup Analytics Startup Script

echo "🏁 Starting GR Cup Analytics Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# Start backend
echo "📦 Starting backend server..."
cd backend
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

echo "🚀 Starting FastAPI server on http://localhost:8000"
python main.py &
BACKEND_PID=$!

cd ..

# Start frontend
echo "📦 Starting frontend server..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "🚀 Starting Vite dev server on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ GR Cup Analytics is running!"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait

