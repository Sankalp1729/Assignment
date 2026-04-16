#!/bin/bash
# Deployment Bash Script for Linux/macOS
# Automated setup and deployment for Unix-like systems

set -e  # Exit on error

clear

echo "================================================================"
echo "       AI DDR GENERATOR - LINUX/macOS DEPLOYMENT WIZARD"
echo "================================================================"
echo ""

# Check Python
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "OK: Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "[2/5] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Created virtual environment"
else
    echo "Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo "OK: Virtual environment activated"
echo ""

# Install/upgrade pip
echo "[4/5] Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "OK: Dependencies installed"
echo ""

# Setup configuration
echo "[5/5] Running setup wizard..."
python setup.py
if [ $? -ne 0 ]; then
    echo "ERROR: Setup failed"
    exit 1
fi

clear

echo "================================================================"
echo "           DEPLOYMENT COMPLETE"
echo "================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Run the system:"
echo "   python main.py"
echo ""
echo "3. View results:"
echo "   cat outputs/ddr_report.txt"
echo ""
echo "4. Install as system service (optional):"
echo "   sudo cp ai-ddr-generator.service /etc/systemd/system/"
echo "   sudo systemctl daemon-reload"
echo "   sudo systemctl enable ai-ddr-generator"
echo "   sudo systemctl start ai-ddr-generator"
echo ""
echo "================================================================"
echo ""
