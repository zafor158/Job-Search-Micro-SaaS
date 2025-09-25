#!/usr/bin/env python3
"""
Startup script for the Job Search Micro-SaaS application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Check if the virtual environment and dependencies are set up"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run: python -m venv venv")
        return False
    
    # Check if requirements are installed
    try:
        import fastapi
        import uvicorn
        import supabase
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting Job Search Micro-SaaS Server...")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        return False
    
    # Check for .env file
    if not Path(".env").exists():
        print("⚠️  Warning: .env file not found. Please create one with your API keys.")
        print("Required environment variables:")
        print("- SUPABASE_URL")
        print("- SUPABASE_SERVICE_ROLE_KEY")
        print("- GROQ_API_KEY")
        print("- SMTP_USERNAME (optional)")
        print("- SMTP_PASSWORD (optional)")
        print()
    
    try:
        # Start the server
        print("🌐 Server starting on http://127.0.0.1:8000")
        print("📧 Enhanced email reminder system is active")
        print("👤 Professional user account management enabled")
        print("📊 Application tracking with deadline reminders enabled")
        print()
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Import and run the app
        import uvicorn
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

if __name__ == "__main__":
    success = start_server()
    sys.exit(0 if success else 1)
