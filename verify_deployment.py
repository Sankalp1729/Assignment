#!/usr/bin/env python3
"""
Deployment Infrastructure Verification Script
Checks that all deployment files are in place and ready for production
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class DeploymentVerifier:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def check_file_exists(self, path, description):
        """Check if a file exists"""
        file_path = self.base_dir / path
        if file_path.exists():
            size = file_path.stat().st_size
            self.results['passed'].append(f"✓ {description} ({size} bytes)")
            return True
        else:
            self.results['failed'].append(f"✗ {description} — NOT FOUND at {path}")
            return False
    
    def check_directory_exists(self, path, description):
        """Check if a directory exists"""
        dir_path = self.base_dir / path
        if dir_path.exists() and dir_path.is_dir():
            file_count = len(list(dir_path.glob('*')))
            self.results['passed'].append(f"✓ {description} ({file_count} items)")
            return True
        else:
            self.results['failed'].append(f"✗ {description} — NOT FOUND at {path}")
            return False
    
    def verify_all(self):
        """Run all verification checks"""
        print("\n" + "="*70)
        print("  DEPLOYMENT INFRASTRUCTURE VERIFICATION")
        print("="*70 + "\n")
        
        # Check documentation
        print("[1/4] Checking Documentation Files...")
        self.check_file_exists("START_HERE_PRODUCTION.md", "Production start guide")
        self.check_file_exists("DEPLOYMENT.md", "Complete deployment guide")
        self.check_file_exists("DEPLOYMENT_SUMMARY.md", "Deployment summary")
        self.check_file_exists("DEPLOYMENT_CHECKLIST.md", "Pre-flight checklist")
        self.check_file_exists("README_DEPLOYMENT.md", "Deployment README")
        self.check_file_exists("docs/ENVIRONMENT_VARIABLES.md", "Environment variables guide")
        
        # Check deployment scripts
        print("[2/4] Checking Deployment Scripts...")
        self.check_file_exists("deployment.bat", "Windows batch script")
        self.check_file_exists("deployment.sh", "Linux/macOS shell script")
        self.check_file_exists("deployment.ps1", "PowerShell script")
        self.check_file_exists("setup_scheduled_task.bat", "Windows Task Scheduler setup")
        
        # Check systemd files
        print("[3/4] Checking Systemd Files...")
        self.check_file_exists("ai-ddr-generator.service", "Systemd service file")
        self.check_file_exists("ai-ddr-generator.timer", "Systemd timer file")
        
        # Check core files
        print("[4/4] Checking Core Application Files...")
        self.check_file_exists("main.py", "Standard entry point")
        self.check_file_exists("prod_main.py", "Production entry point")
        self.check_file_exists("setup.py", "Setup wizard")
        self.check_file_exists("deployment_checklist.py", "Deployment checker")
        self.check_file_exists("build_for_production.py", "Production builder")
        
        # Check directories
        self.check_directory_exists("utils", "Core modules")
        self.check_directory_exists("docs", "Documentation")
        self.check_directory_exists("config", "Configuration")
        self.check_directory_exists("scripts", "Demo scripts")
        
        self.print_results()
    
    def print_results(self):
        """Print verification results"""
        print("\n" + "-"*70)
        print("  VERIFICATION RESULTS")
        print("-"*70 + "\n")
        
        # Passed
        print(f"✓ PASSED: {len(self.results['passed'])} items\n")
        for item in self.results['passed']:
            print(f"  {item}")
        
        # Failed
        if self.results['failed']:
            print(f"\n✗ FAILED: {len(self.results['failed'])} items\n")
            for item in self.results['failed']:
                print(f"  {item}")
        
        # Warnings
        if self.results['warnings']:
            print(f"\n⚠ WARNINGS: {len(self.results['warnings'])} items\n")
            for item in self.results['warnings']:
                print(f"  {item}")
        
        # Summary
        print("\n" + "="*70)
        total = len(self.results['passed']) + len(self.results['failed'])
        if self.results['failed']:
            print(f"  STATUS: ✗ INCOMPLETE ({len(self.results['passed'])}/{total} files)")
        else:
            print(f"  STATUS: ✅ DEPLOYMENT INFRASTRUCTURE COMPLETE")
            print(f"  Total items verified: {len(self.results['passed'])}")
        print("="*70 + "\n")
        
        # Next steps
        if not self.results['failed']:
            print("📋 NEXT STEPS:\n")
            print("  1. Choose your deployment method:")
            print("     • Windows: Run 'deployment.bat'")
            print("     • Linux/macOS: Run './deployment.sh'")
            print("     • Docker: Run 'docker-compose up'")
            print()
            print("  2. Read the appropriate guide:")
            print("     • Quick start: START_HERE_PRODUCTION.md")
            print("     • Full details: DEPLOYMENT.md")
            print()
            print("  3. Verify your setup:")
            print("     • Run: python deployment_checklist.py")
            print()
            print("  4. Deploy to production:")
            print("     • Run: python main.py")
            print()
        else:
            print("⚠ Please resolve the above issues before deploying.")
            print()

def main():
    verifier = DeploymentVerifier()
    verifier.verify_all()
    
    # Exit with appropriate code
    if verifier.results['failed']:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
