@echo off
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

echo 📦 Installing Node.js dependencies...
cd frontend
npm install

echo 🔨 Building React frontend...
npm run build

echo 🔙 Returning to root directory...
cd ..

echo 🤖 Setting up Gemini AI API key...
python set_api_key.py

echo 🚀 Starting Flask server...
echo 📱 Frontend will be available at: http://localhost:5000
echo 🔌 API endpoints will be available at: http://localhost:5000/api
echo.
echo 🛑 Press Ctrl+C to stop the server
echo.

python web_server.py

pause
