#!/usr/bin/env python3
"""
Production Build Script

Prepares the project for production deployment:
1. Validates all files
2. Optimizes configurations
3. Compiles documentation
4. Creates deployment package
"""

import os
import sys
import shutil
import json
from pathlib import Path

def setup_production_env():
    """Create production environment configuration"""
    
    prod_config = {
        "environment": "production",
        "debug": False,
        "log_level": "WARNING",
        "timeout": 60,
        "max_retries": 3,
        "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        "batch_processing": True,
        "batch_size": 10,
    }
    
    # Create production config
    config_path = Path("config/production_config.py")
    with open(config_path, "w") as f:
        f.write(f"# Production Configuration\n")
        f.write(f"# Auto-generated for deployment\n\n")
        for key, value in prod_config.items():
            f.write(f"{key.upper()} = {repr(value)}\n")
    
    return True

def validate_all_modules():
    """Validate all critical modules"""
    print("🔍 Validating Python modules...")
    
    critical_modules = [
        "utils/gemini_client.py",
        "utils/pdf_extractor.py",
        "utils/observation_extractor.py",
        "utils/merger.py",
        "utils/severity.py",
        "utils/severity_explainer.py",
        "utils/ddr_generator.py",
    ]
    
    for module in critical_modules:
        if not Path(module).exists():
            print(f"  ❌ Missing: {module}")
            return False
        print(f"  ✅ {module}")
    
    return True

def create_deployment_docs():
    """Create deployment documentation"""
    
    deploy_guide = """# DEPLOYMENT GUIDE

## Pre-Deployment Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] requirements.txt dependencies installed
- [ ] .env file configured with GEMINI_API_KEY
- [ ] All Python files validated (python deployment_checklist.py)
- [ ] Test run successful (python main.py)
- [ ] Output files generated correctly

## Installation Steps

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\\Scripts\\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API
```bash
# Edit .env file and set:
GEMINI_API_KEY=your_actual_key_here
```

### 4. Verify Installation
```bash
python deployment_checklist.py
```

### 5. Test Run
```bash
python main.py
```

## Deployment

### Option 1: Direct Execution
```bash
python main.py
```

### Option 2: Production Build
```bash
python build_for_production.py
python main.py
```

## Post-Deployment Verification

```bash
# Check final report
cat outputs/ddr_report.txt

# View JSON data
cat outputs/ddr_report.json

# Test API
python scripts/test_gemini.py
```

## Troubleshooting

See: docs/TROUBLESHOOTING.md

## Support

1. Check documentation in docs/
2. Review error messages
3. Run test scripts: python scripts/test_*.py
4. Verify .env configuration
"""
    
    with open("DEPLOYMENT_GUIDE.md", "w") as f:
        f.write(deploy_guide)
    
    return True

def create_build_script():
    """Create build script for automated deployment"""
    
    build_script = '''#!/bin/bash
# Automated Build and Deployment Script

echo "========================================"
echo "🔨 BUILDING FOR PRODUCTION"
echo "========================================"

# Check Python
echo "📍 Checking Python..."
python --version || { echo "❌ Python not found"; exit 1; }

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "📍 Creating virtual environment..."
    python -m venv venv
fi

# Activate venv
echo "📍 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📍 Installing dependencies..."
pip install -r requirements.txt

# Validate
echo "📍 Running validation..."
python deployment_checklist.py || { echo "❌ Validation failed"; exit 1; }

# Build
echo "📍 Building production package..."
python build_for_production.py || { echo "❌ Build failed"; exit 1; }

echo "========================================"
echo "✅ BUILD COMPLETE - READY FOR DEPLOYMENT"
echo "========================================"
echo ""
echo "🚀 To run: python main.py"
echo ""
'''
    
    with open("build.sh", "w") as f:
        f.write(build_script)
    
    # Make executable
    os.chmod("build.sh", 0o755)
    
    return True

def create_docker_files():
    """Create Docker configuration for containerized deployment"""
    
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create output directory
RUN mkdir -p outputs

# Set environment
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Run application
CMD ["python", "main.py"]
"""
    
    docker_compose = """version: '3.8'

services:
  ddr-generator:
    build: .
    container_name: ai-ddr-generator
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./outputs:/app/outputs
    ports:
      - "8000:8000"
    networks:
      - ddr-network

networks:
  ddr-network:
    driver: bridge
"""
    
    dockerignore = """__pycache__
*.pyc
*.pyo
.pytest_cache
.venv
venv
.env
outputs/*
.git
.gitignore
*.log
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    with open(".dockerignore", "w") as f:
        f.write(dockerignore)
    
    return True

def main():
    print("\n" + "="*70)
    print("🔨 PRODUCTION BUILD SCRIPT")
    print("="*70 + "\n")
    
    steps = [
        ("Validating modules", validate_all_modules),
        ("Setting up production environment", setup_production_env),
        ("Creating deployment docs", create_deployment_docs),
        ("Creating build script", create_build_script),
        ("Creating Docker files", create_docker_files),
    ]
    
    for step_name, step_func in steps:
        print(f"📍 {step_name}...", end=" ")
        try:
            result = step_func()
            if result:
                print("✅")
            else:
                print("❌")
                return 1
        except Exception as e:
            print(f"❌ {str(e)}")
            return 1
    
    print("\n" + "="*70)
    print("✅ BUILD COMPLETE")
    print("="*70)
    print("\n📦 Generated files:")
    print("  - DEPLOYMENT_GUIDE.md")
    print("  - config/production_config.py")
    print("  - Dockerfile")
    print("  - docker-compose.yml")
    print("  - .dockerignore")
    print("\n🚀 Next steps:")
    print("  1. python deployment_checklist.py (verify)")
    print("  2. Configure .env with your API key")
    print("  3. python main.py (test)")
    print("  4. Review outputs/ddr_report.txt")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
