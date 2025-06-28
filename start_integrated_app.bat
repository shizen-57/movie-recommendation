@echo off
title CinemaAI Pro - Movie Recommender System

echo 🎬 Starting CinemaAI Pro - Integrated Movie Recommendation System
echo ==============================================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js and try again.
    pause
    exit /b 1
)

echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Check if artifacts exist
if not exist "artifacts\movie_list.pkl" (
    echo ⚠️  Movie artifacts not found. Generating movie data...
    python data_loader.py
)

echo 🤖 Setting up Gemini AI API key...
python set_api_key.py

echo 🚀 Starting Flask backend server on port 8000...
start "Backend Server" python web_server.py

REM Wait for backend to start
timeout /t 3 /nobreak >nul

echo 🎨 Starting React frontend development server...
cd frontend
start "Frontend Server" npm run dev

echo.
echo ✅ Application started successfully!
echo 🎥 Frontend App: http://localhost:5173
echo 🔌 Backend API: http://localhost:8000
echo.
echo 🛑 Press any key to stop all services
pause >nul

REM Kill all related processes
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo ✅ All services stopped

pause
