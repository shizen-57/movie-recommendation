#!/bin/bash

# CinemaAI Pro - Integrated Movie Recommendation System
# This script sets up and runs both the React frontend and Flask backend

echo "🎬 Starting CinemaAI Pro - Integrated Movie Recommendation System"
echo "=============================================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js and try again."
    exit 1
fi

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if artifacts exist
if [ ! -f "artifacts/movie_list.pkl" ]; then
    echo "⚠️  Movie artifacts not found. Generating movie data..."
    python data_loader.py
fi

echo "🤖 Setting up Gemini AI API key..."
python set_api_key.py

echo "🚀 Starting Flask backend server on port 8000..."
python web_server.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

echo "🎨 Starting React frontend development server..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!

# Wait for services to start
sleep 5

echo ""
echo "✅ Application started successfully!"
echo "🎥 Frontend App: http://localhost:5173"
echo "🔌 Backend API: http://localhost:8000"
echo ""
echo "🛑 Press Ctrl+C to stop all services"

# Function to cleanup processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Wait for user to stop
wait
