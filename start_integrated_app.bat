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

echo 🚀 Starting Flask backend server on port 5000...
start "CinemaAI Backend" cmd /k "python web_server.py"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo 🎨 Starting React frontend development server...
cd ..\react-js-movie-web-application
if not exist "node_modules" (
    echo 📦 Installing React dependencies...
    npm install
)
start "CinemaAI Frontend" cmd /k "npm run dev"

echo.
echo ✅ Application started successfully!
echo 🎥 Frontend App: http://localhost:5173 (Vite React App)
echo 🔌 Backend API: http://localhost:5000 (Flask Server)
echo 🤖 Movie Recommendations: Available via API
echo 🖼️ Live TMDB Posters: Enabled
echo.
echo � How to use:
echo 1. Wait for both servers to fully load
echo 2. Open http://localhost:5173 in your browser
echo 3. Search and get AI-powered movie recommendations!
echo.
echo �🛑 Press any key to stop all services
pause >nul

echo 🛑 Stopping all services...
taskkill /f /im python.exe /t >nul 2>&1
taskkill /f /im node.exe /t >nul 2>&1
taskkill /f /im cmd.exe /fi "WINDOWTITLE eq CinemaAI*" /t >nul 2>&1
echo ✅ All services stopped

pause
