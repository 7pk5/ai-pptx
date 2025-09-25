#!/usr/bin/env python3
"""
PPT AI Analyzer - Startup Script
Run this script to start the web interface
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    print("🚀 Starting PPT AI Analyzer...")
    print(f"📁 Project directory: {project_root}")
    print("🌐 Web interface will be available at: http://localhost:5000")
    print("📚 For API documentation, see README.md")
    print("-" * 50)
    
    try:
        # Start the Flask application
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down PPT AI Analyzer...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
