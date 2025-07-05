#!/usr/bin/env pwsh
# CinemaAI Pro - One Command Startup Script
# Starts both Flask backend and React frontend

Write-Host "🎬 CinemaAI Pro - Movie Recommender System" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check Python
try {
    python --version | Out-Null
    Write-Host "✅ Python found" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    node --version | Out-Null
    Write-Host "✅ Node.js found" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js" -ForegroundColor Red
    exit 1
}

# Set environment variables
if (-not $env:TMDB_API_KEY) {
    Write-Host "⚠️  Setting default TMDB API key..." -ForegroundColor Yellow
    $env:TMDB_API_KEY = "3c9b7eab0c5e86570cf6cc98a30ec20a"
}

if (-not $env:GEMINI_API_KEY) {
    Write-Host "⚠️  Setting default Gemini API key..." -ForegroundColor Yellow
    $env:GEMINI_API_KEY = "AIzaSyDJ3TY3gZP2g8yiV40sc-3a1gevGuHUXIU"
}

Write-Host "📦 Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt | Out-Null

# Check artifacts
if (-not (Test-Path "artifacts\movie_list.pkl")) {
    Write-Host "🔄 Generating movie artifacts..." -ForegroundColor Yellow
    python data_loader.py
}

Write-Host "🚀 Starting Flask backend (Port 5000)..." -ForegroundColor Magenta
$backend = Start-Process -FilePath "python" -ArgumentList "web_server.py" -PassThru -WindowStyle Minimized

Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "🎨 Starting React frontend (Port 5173)..." -ForegroundColor Magenta
Set-Location "..\react-js-movie-web-application"

if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing React dependencies..." -ForegroundColor Yellow
    npm install
}

$frontend = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -PassThru -WindowStyle Minimized

Write-Host ""
Write-Host "✅ CinemaAI Pro Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "🎥 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔌 Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "🤖 Features: AI Recommendations + Live TMDB Posters" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Usage:" -ForegroundColor Yellow
Write-Host "1. Open http://localhost:5173 in your browser" -ForegroundColor White
Write-Host "2. Search for movies and get AI recommendations!" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Red

# Wait for user to stop
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "🛑 Stopping services..." -ForegroundColor Red
    Stop-Process -Id $backend.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontend.Id -Force -ErrorAction SilentlyContinue
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "✅ All services stopped" -ForegroundColor Green
}
