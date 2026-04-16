#!/usr/bin/env python3
"""
Professional Project Structure Verification Script

Verifies that the AI DDR Generator project is properly organized
and all required files are in place.
"""

import os
import sys
from pathlib import Path

def check_directory(directory, files):
    """Check if directory exists and contains expected files."""
    base_path = Path(directory)
    
    if not base_path.exists():
        return False, f"Directory not found: {directory}"
    
    missing = []
    for file in files:
        file_path = base_path / file
        if not file_path.exists():
            missing.append(file)
    
    if missing:
        return False, f"Missing files in {directory}: {', '.join(missing)}"
    
    return True, f"✓ {directory} - All files present"

def main():
    print("\n" + "="*70)
    print("📋 AI DDR GENERATOR — PROFESSIONAL STRUCTURE VERIFICATION")
    print("="*70 + "\n")
    
    base_dir = Path(__file__).parent
    
    # Define expected structure
    checks = {
        "Root Directory": {
            "path": ".",
            "files": [
                "README.md",
                "requirements.txt",
                ".env",
                "main.py",
                "PROJECT_STRUCTURE.md",
                "FILE_INDEX.md",
                "SYSTEM_OVERVIEW.md",
            ]
        },
        "Documentation (docs/)": {
            "path": "docs",
            "files": [
                "QUICKSTART.md",
                "API_SETUP.md",
                "TROUBLESHOOTING.md",
                "STEP5_EXTRACTION.md",
                "STEP6_MERGING.md",
                "STEP7_SEVERITY.md",
                "STEP8_REPORT.md",
            ]
        },
        "Core Modules (utils/)": {
            "path": "utils",
            "files": [
                "gemini_client.py",
                "pdf_extractor.py",
                "observation_extractor.py",
                "merger.py",
                "severity.py",
                "severity_explainer.py",
                "ddr_generator.py",
            ]
        },
        "Demo Scripts (scripts/)": {
            "path": "scripts",
            "files": [
                "step5_extract_observations.py",
                "step6_merge_and_conflict.py",
                "step7_severity_scoring.py",
                "step8_generate_ddr.py",
                "test_gemini.py",
            ]
        },
        "Data Folder (data/)": {
            "path": "data",
            "files": []  # Can be empty, user adds PDFs
        },
        "Outputs Folder (outputs/)": {
            "path": "outputs",
            "files": []  # Auto-created
        },
        "Configuration (config/)": {
            "path": "config",
            "files": [
                "app_config.py",
            ]
        },
    }
    
    # Run checks
    results = []
    all_good = True
    
    for check_name, check_data in checks.items():
        path = base_dir / check_data["path"]
        status, message = check_directory(path, check_data["files"])
        results.append((check_name, status, message))
        if not status:
            all_good = False
        print(f"{'✓' if status else '✗'} {message}")
    
    # Summary
    print("\n" + "="*70)
    
    if all_good:
        print("✅ PROJECT STRUCTURE IS PROPERLY ORGANIZED")
        print("\n📊 Project Statistics:")
        
        # Count files
        total_py = len(list(base_dir.rglob("*.py")))
        total_md = len(list(base_dir.rglob("*.md")))
        total_json = len(list(base_dir.rglob("*.json")))
        
        print(f"  - Python files: {total_py}")
        print(f"  - Documentation: {total_md} markdown files")
        print(f"  - Data files: {total_json} JSON outputs (auto-created)")
        
        print("\n🚀 Ready to use! Next steps:")
        print("  1. Read: README.md")
        print("  2. Setup: docs/QUICKSTART.md")
        print("  3. Run: python main.py")
        
        return 0
    else:
        print("❌ SOME FILES ARE MISSING - Review issues above")
        print("\n💡 To fix:")
        print("  1. Create missing directories")
        print("  2. Move files to proper locations")
        print("  3. Run this script again to verify")
        return 1

if __name__ == "__main__":
    sys.exit(main())
