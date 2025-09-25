#!/usr/bin/env python3
"""
Test script for Vercel deployment compatibility
"""

import os
import sys
import json
from pathlib import Path

def test_vercel_compatibility():
    """Test if the application is ready for Vercel deployment."""
    print("🧪 Testing Vercel Deployment Compatibility...")
    
    # Test file structure
    required_files = [
        'vercel.json',
        'requirements.txt',
        'api/index.py',
        '.vercelignore'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    else:
        print("✅ All required files present")
    
    # Test imports
    try:
        sys.path.append('api')
        from index import app
        print("✅ Flask app imports successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test configuration
    try:
        with open('vercel.json', 'r') as f:
            config = json.load(f)
        
        if 'builds' in config and 'routes' in config:
            print("✅ Vercel configuration is valid")
        else:
            print("⚠️  Vercel configuration might be incomplete")
    except Exception as e:
        print(f"❌ Vercel config error: {e}")
        return False
    
    # Test requirements
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Check for serverless-compatible packages
        if 'opencv-python-headless' in requirements:
            print("✅ Using serverless-compatible OpenCV")
        elif 'opencv-python' in requirements:
            print("⚠️  Consider using opencv-python-headless for better serverless compatibility")
        
        if 'flask' in requirements.lower():
            print("✅ Flask included in requirements")
        else:
            print("❌ Flask not found in requirements.txt")
            return False
            
    except Exception as e:
        print(f"❌ Requirements check failed: {e}")
        return False
    
    print("\n🎉 Deployment compatibility check completed!")
    return True

def test_local_api():
    """Test the API locally before deployment."""
    print("\n🌐 Testing Local API...")
    
    try:
        # Start a test client
        sys.path.append('api')
        from index import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Health endpoint working")
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
            
            # Test main page
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Main page loads")
            else:
                print(f"❌ Main page failed: {response.status_code}")
                return False
            
        print("✅ Local API tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Local API test failed: {e}")
        return False

def show_deployment_info():
    """Show deployment information."""
    print("\n📋 Deployment Information:")
    print("=" * 50)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Check if we're in a git repository
    if os.path.exists('.git'):
        print("✅ Git repository detected")
    else:
        print("⚠️  Not a git repository - consider initializing git for easier deployment")
    
    # Check file sizes
    ppt_files = list(Path('.').glob('*.pptx')) + list(Path('.').glob('*.ppt'))
    if ppt_files:
        print(f"📄 Found {len(ppt_files)} PowerPoint files for testing")
    
    # Show next steps
    print("\n🚀 Next Steps for Deployment:")
    print("1. Install Vercel CLI: npm i -g vercel")
    print("2. Login to Vercel: vercel login")
    print("3. Deploy: vercel --prod")
    print("\nOr use GitHub integration:")
    print("1. Push to GitHub")
    print("2. Connect repository in Vercel dashboard")
    print("3. Deploy automatically")
    
    print("\n🔧 Environment Variables to Set in Vercel:")
    print("- GROQ_API_KEY=your_api_key")
    print("- FLASK_SECRET_KEY=your_secret_key")
    print("- MAX_FILE_SIZE=52428800")
    print("\n📚 See DEPLOYMENT.md for detailed instructions")

def main():
    print("🔍 PPT AI Analyzer - Vercel Deployment Test")
    print("=" * 60)
    
    # Test compatibility
    compatibility_ok = test_vercel_compatibility()
    
    # Test local API
    api_ok = test_local_api()
    
    # Show deployment info
    show_deployment_info()
    
    # Final verdict
    print("\n" + "=" * 60)
    if compatibility_ok and api_ok:
        print("🎉 Ready for Vercel deployment!")
        print("✅ All tests passed")
        return 0
    else:
        print("❌ Deployment readiness issues found")
        print("🔧 Please fix the issues above before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
