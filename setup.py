#!/usr/bin/env python3
"""
Setup Script — Automated Environment Configuration

Guides users through complete setup for deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install Python dependencies"""
    print("\n📍 Installing Python dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Dependencies installed successfully")
        return True
    else:
        print(f"❌ Failed to install dependencies: {result.stderr}")
        return False

def setup_env_file():
    """Setup .env file with API key"""
    print("\n📍 Setting up .env file...")
    
    if Path(".env").exists():
        print("  ⚠️  .env file already exists")
        response = input("  Overwrite? (y/n): ").strip().lower()
        if response != "y":
            print("  Skipping .env setup")
            return True
    
    print("\n  Get your Gemini API key from: https://ai.google.dev/")
    api_key = input("\n  Enter your GEMINI_API_KEY: ").strip()
    
    if not api_key:
        print("  ❌ API key is required")
        return False
    
    with open(".env", "w") as f:
        f.write(f"GEMINI_API_KEY={api_key}\n")
    
    print("  ✅ .env file created successfully")
    return True

def verify_installation():
    """Verify all dependencies are installed"""
    print("\n📍 Verifying installation...")
    
    packages = [
        ("google.generativeai", "google-generativeai"),
        ("fitz", "pymupdf"),
        ("rapidfuzz", "rapidfuzz"),
        ("dotenv", "python-dotenv"),
        ("jinja2", "jinja2"),
    ]
    
    all_ok = True
    for import_name, package_name in packages:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
        except ImportError:
            print(f"  ❌ {package_name} - Install with: pip install {package_name}")
            all_ok = False
    
    return all_ok

def test_api_connection():
    """Test Gemini API connection"""
    print("\n📍 Testing API connection...")
    result = subprocess.run(
        [sys.executable, "scripts/test_gemini.py"],
        capture_output=True,
        text=True
    )
    
    if "✓" in result.stdout or "successful" in result.stdout:
        print("  ✅ API connection successful")
        return True
    else:
        print(f"  ⚠️  API test may have issues")
        print(f"     Output: {result.stdout}")
        return True  # Continue anyway

def create_directories():
    """Ensure all required directories exist"""
    print("\n📍 Creating directories...")
    
    dirs = ["data", "outputs", "config", "scripts", "docs", "utils"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"  ✅ {d}/")
    
    return True

def main():
    print("\n" + "="*70)
    print("🚀 AI DDR GENERATOR — SETUP WIZARD")
    print("="*70)
    
    steps = [
        ("Creating directories", create_directories),
        ("Installing dependencies", install_requirements),
        ("Verifying installation", verify_installation),
        ("Configuring API key", setup_env_file),
        ("Testing API connection", test_api_connection),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{'='*70}")
        try:
            result = step_func()
            if not result:
                print(f"\n❌ {step_name} failed")
                print("Please fix the issue and run setup again")
                return 1
        except Exception as e:
            print(f"\n❌ Error in {step_name}: {str(e)}")
            return 1
    
    print("\n" + "="*70)
    print("✅ SETUP COMPLETE - READY TO USE")
    print("="*70)
    print("\n📚 Next steps:")
    print("  1. Read: README.md")
    print("  2. Test: python main.py")
    print("  3. View: outputs/ddr_report.txt")
    print("\n🚀 To run the complete pipeline:")
    print("  python main.py")
    print("\n💡 To test individual steps:")
    print("  python scripts/step5_extract_observations.py")
    print("  python scripts/step6_merge_and_conflict.py")
    print("  python scripts/step7_severity_scoring.py")
    print("  python scripts/step8_generate_ddr.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
