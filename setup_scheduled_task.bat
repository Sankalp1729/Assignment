@echo off
REM Window Task Scheduler Setup Script
REM This script creates a scheduled task for the AI DDR Generator

echo.
echo Setting up Windows Task Scheduler...
echo.

setlocal enabledelayedexpansion

REM Get the current directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Get Python path
for /f "delims=" %%i in ('where python') do set "PYTHON_PATH=%%i"

if "%PYTHON_PATH%"=="" (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

echo Python found at: %PYTHON_PATH%
echo Working directory: %SCRIPT_DIR%
echo.

REM Create scheduled task
echo Creating Windows Task Scheduler entry...
echo.

REM Task name
set "TASK_NAME=AI-DDR-Generator"

REM Check if task already exists
tasklist /FI "TASKNAME eq %TASK_NAME%" 2>NUL | find /I /N "%TASK_NAME%">NUL
if "%ERRORLEVEL%"=="0" (
    echo Removing existing task...
    schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1
)

REM Create new task
REM Runs daily at 2:00 AM
schtasks /create /tn "%TASK_NAME%" ^
    /tr "cd /d %SCRIPT_DIR% && %PYTHON_PATH% prod_main.py" ^
    /sc DAILY /st 02:00:00 ^
    /ru SYSTEM ^
    /f

if "%ERRORLEVEL%"=="0" (
    echo.
    echo ✓ Task created successfully!
    echo.
    echo Task Details:
    echo   Name: %TASK_NAME%
    echo   Schedule: Daily at 2:00 AM
    echo   Location: %SCRIPT_DIR%
    echo   Command: python prod_main.py
    echo.
    echo You can manage this task in:
    echo   - Task Scheduler GUI
    echo   - Or use: schtasks /query /tn "%TASK_NAME%"
    echo.
) else (
    echo.
    echo ✗ Failed to create task
    echo Please run this script as Administrator
    echo.
)

pause
