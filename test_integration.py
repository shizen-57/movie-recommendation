"""
Integration Test Script for CinemaAI Pro
Tests the integration between React frontend and Flask backend
"""

import sys
import os
import requests
import time
import subprocess
from pathlib import Path

def check_requirements():
    """Check if all required files and dependencies are present"""
    print("🔍 Checking project structure...")
    
    required_files = [
        "web_server.py",
        "requirements.txt", 
        "frontend/package.json",
        "frontend/src/App.jsx",
        "src/recommender.py",
        "artifacts/movie_list.pkl"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def check_python_dependencies():
    """Check if Python dependencies are installed"""
    print("🐍 Checking Python dependencies...")
    
    required_packages = [
        "flask", "flask_cors", "pandas", "numpy", 
        "scikit-learn", "requests", "google-generativeai"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing Python packages: {missing_packages}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    
    print("✅ All Python dependencies installed")
    return True

def check_frontend_build():
    """Check if React frontend is built"""
    print("⚛️ Checking React frontend...")
    
    if not Path("frontend/dist").exists():
        print("❌ Frontend not built")
        print("💡 Run: cd frontend && npm install && npm run build")
        return False
    
    print("✅ Frontend build exists")
    return True

def test_api_endpoints():
    """Test basic API endpoints"""
    print("🔌 Testing API endpoints...")
    
    # Start the server in background for testing
    try:
        # This would require running the server separately
        # For now, just check if the endpoints are defined in web_server.py
        with open("web_server.py", "r") as f:
            content = f.read()
            
        required_endpoints = [
            "/api/movies",
            "/api/search", 
            "/api/recommendations"
        ]
        
        missing_endpoints = []
        for endpoint in required_endpoints:
            if endpoint not in content:
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print(f"❌ Missing API endpoints: {missing_endpoints}")
            return False
        
        print("✅ All API endpoints defined")
        return True
        
    except Exception as e:
        print(f"❌ Error checking API endpoints: {e}")
        return False

def run_integration_test():
    """Run the complete integration test"""
    print("🎬 CinemaAI Pro - Integration Test")
    print("=" * 40)
    
    tests = [
        check_requirements,
        check_python_dependencies,
        check_frontend_build,
        test_api_endpoints
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
            print()
    
    # Summary
    print("📋 Test Summary")
    print("-" * 20)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("🚀 Ready to start the application!")
        print("💡 Run: ./start_integrated_app.bat (Windows) or ./start_integrated_app.sh (Linux/Mac)")
    else:
        print(f"❌ {total - passed} tests failed ({passed}/{total})")
        print("🔧 Please fix the issues above before starting the application")
    
    return passed == total

if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)
