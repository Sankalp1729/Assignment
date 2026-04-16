@echo off
REM Deployment Batch Script for Windows
REM Automated setup and deployment for Windows systems

setlocal enabledelayedexpansion

title AI DDR Generator - Windows Deployment

cls
echo.
echo ================================================================
echo          AI DDR GENERATOR - WINDOWS DEPLOYMENT WIZARD
echo ================================================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)
echo OK: Python found
echo.

REM Create virtual environment
echo [2/5] Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Created virtual environment
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo OK: Virtual environment activated
echo.

REM Install dependencies
echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo OK: Dependencies installed
echo.

REM Setup configuration
echo [5/5] Running setup wizard...
python setup.py
if errorlevel 1 (
    echo ERROR: Setup failed
    pause
    exit /b 1
)

cls
echo.
echo ================================================================
echo          DEPLOYMENT COMPLETE
echo ================================================================
echo.
echo Next steps:
echo.
echo 1. Run the system:
echo    python main.py
echo.
echo 2. View results:
echo    type outputs\ddr_report.txt
echo.
echo 3. Test individual steps:
echo    python scripts\step5_extract_observations.py
echo    python scripts\step6_merge_and_conflict.py
echo    python scripts\step7_severity_scoring.py
echo    python scripts\step8_generate_ddr.py
echo.
echo ================================================================
echo.
pause
