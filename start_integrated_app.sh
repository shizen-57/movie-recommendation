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

echo "📦 Installing Node.js dependencies..."
cd frontend
npm install

echo "🔨 Building React frontend..."
npm run build

echo "🔙 Returning to root directory..."
cd ..

echo "🤖 Setting up Gemini AI API key..."
python set_api_key.py

echo "🚀 Starting Flask server..."
echo "📱 Frontend will be available at: http://localhost:5000"
echo "🔌 API endpoints will be available at: http://localhost:5000/api"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python web_server.py
