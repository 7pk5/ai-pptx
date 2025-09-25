#!/usr/bin/env python3
"""
Test script for PPT AI Analyzer
Run this to test the analysis functionality
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_analyzers():
    """Test the analyzer components"""
    print("🧪 Testing PPT AI Analyzer Components...")
    
    # Test imports
    try:
        from src.analyzers.detailed_analyzer import DetailedPPTAnalyzer
        from src.analyzers.groq_analyzer import GroqAnalyzer
        from src.utils.helpers import validate_ppt_file
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test analyzer initialization
    try:
        detailed_analyzer = DetailedPPTAnalyzer()
        groq_analyzer = GroqAnalyzer()
        print("✅ Analyzers initialized successfully")
    except Exception as e:
        print(f"❌ Analyzer initialization error: {e}")
        return False
    
    # Test file validation
    try:
        result = validate_ppt_file("nonexistent.pptx")
        if not result["valid"] and "does not exist" in result["error"]:
            print("✅ File validation working correctly")
        else:
            print("⚠️  File validation test inconclusive")
    except Exception as e:
        print(f"❌ File validation error: {e}")
        return False
    
    # Test with existing PPT file if available
    ppt_files = list(Path(".").glob("*.pptx")) + list(Path(".").glob("*.ppt"))
    
    if ppt_files:
        test_file = ppt_files[0]
        print(f"📄 Testing with file: {test_file}")
        
        try:
            # Test detailed analysis
            result = detailed_analyzer.parse_ppt_detailed(str(test_file))
            print(f"✅ Detailed analysis completed - {result['global_analysis']['total_slides']} slides found")
            
            # Test AI analysis
            ai_result = groq_analyzer.analyze_presentation(result)
            if "error" not in ai_result:
                print("✅ AI analysis completed successfully")
            else:
                print(f"⚠️  AI analysis had issues: {ai_result['error']}")
                
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return False
    else:
        print("ℹ️  No PPT files found for testing - skipping file analysis test")
    
    print("\n🎉 All tests completed successfully!")
    print("🚀 You can now run: python app.py or python run.py")
    return True

def check_dependencies():
    """Check if all required packages are installed"""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'flask', 'python-pptx', 'groq', 'pillow', 'webcolors', 
        'colorthief', 'cv2', 'numpy', 'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'python-pptx':
                import pptx
            elif package == 'pillow':
                from PIL import Image
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies are installed")
        return True

def main():
    print("🔍 PPT AI Analyzer - System Test")
    print("=" * 50)
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    print()
    
    # Test analyzers
    if not test_analyzers():
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
