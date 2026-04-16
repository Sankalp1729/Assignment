#!/usr/bin/env python3
"""
Deployment Pre-Flight Checklist

Verifies all systems are ready for production deployment
"""

import os
import sys
import json
from pathlib import Path

def check_file(path, file_type="file"):
    """Check if file/directory exists"""
    p = Path(path)
    if file_type == "dir":
        return p.is_dir()
    return p.is_file()

def check_python_files():
    """Verify all critical Python files exist"""
    critical_files = [
        "utils/gemini_client.py",
        "utils/pdf_extractor.py",
        "utils/observation_extractor.py",
        "utils/merger.py",
        "utils/severity.py",
        "utils/severity_explainer.py",
        "utils/ddr_generator.py",
        "main.py",
    ]
    
    missing = []
    for f in critical_files:
        if not check_file(f):
            missing.append(f)
    
    return missing

def check_documentation():
    """Verify all documentation exists"""
    docs = [
        "README.md",
        "requirements.txt",
        ".env",
    ]
    
    missing = []
    for d in docs:
        if not check_file(d):
            missing.append(d)
    
    return missing

def check_directories():
    """Verify all required directories"""
    dirs = [
        "utils",
        "scripts",
        "docs",
        "config",
        "outputs",
        "data",
    ]
    
    missing = []
    for d in dirs:
        if not check_file(d, "dir"):
            missing.append(d)
    
    return missing

def check_requirements():
    """Verify requirements.txt exists and has content"""
    if not check_file("requirements.txt"):
        return False, "requirements.txt not found"
    
    with open("requirements.txt") as f:
        content = f.read().strip()
        if not content:
            return False, "requirements.txt is empty"
    
    return True, "requirements.txt OK"

def main():
    print("\n" + "="*70)
    print("🚀 DEPLOYMENT PRE-FLIGHT CHECKLIST")
    print("="*70 + "\n")
    
    checks_passed = 0
    checks_failed = 0
    
    # Check Python files
    print("📍 CRITICAL FILES")
    print("-" * 70)
    missing_py = check_python_files()
    if missing_py:
        print(f"❌ Missing Python files: {', '.join(missing_py)}")
        checks_failed += len(missing_py)
    else:
        print("✅ All critical Python files present")
        checks_passed += 1
    
    # Check documentation
    print("\n📍 DOCUMENTATION")
    print("-" * 70)
    missing_docs = check_documentation()
    if missing_docs:
        print(f"⚠️  Missing: {', '.join(missing_docs)}")
        checks_failed += len(missing_docs)
    else:
        print("✅ All critical documentation present")
        checks_passed += 1
    
    # Check directories
    print("\n📍 DIRECTORIES")
    print("-" * 70)
    missing_dirs = check_directories()
    if missing_dirs:
        print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        checks_failed += len(missing_dirs)
    else:
        print("✅ All required directories present")
        checks_passed += 1
    
    # Check requirements
    print("\n📍 DEPENDENCIES")
    print("-" * 70)
    ok, msg = check_requirements()
    if ok:
        print(f"✅ {msg}")
        checks_passed += 1
    else:
        print(f"❌ {msg}")
        checks_failed += 1
    
    # File counts
    print("\n📍 FILE STATISTICS")
    print("-" * 70)
    py_count = len(list(Path(".").rglob("*.py")))
    md_count = len(list(Path(".").rglob("*.md")))
    json_count = len(list(Path("outputs").rglob("*.json"))) if Path("outputs").exists() else 0
    print(f"✅ Python files: {py_count}")
    print(f"✅ Documentation: {md_count} markdown files")
    print(f"✅ Data files: {json_count} JSON outputs")
    
    # Summary
    print("\n" + "="*70)
    if checks_failed == 0:
        print("✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT")
        print("\nNext steps:")
        print("  1. python -m pip install -r requirements.txt")
        print("  2. Configure .env with GEMINI_API_KEY")
        print("  3. python main.py")
        print("  4. Verify outputs/ddr_report.txt")
        return 0
    else:
        print(f"❌ {checks_failed} ISSUE(S) FOUND - FIX BEFORE DEPLOYMENT")
        print("\nReview issues above and fix them.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
