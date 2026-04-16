# Parameter Set for Windows Deployment

param(
    [string]$Action = "setup",  # setup, deploy, start, stop, status
    [string]$Environment = "production"
)

<#
.SYNOPSIS
    AI DDR Generator - PowerShell Deployment Script for Windows

.DESCRIPTION
    Automates deployment tasks for Windows systems

.PARAMETER Action
    Deployment action: setup, deploy, start, stop, status

.PARAMETER Environment
    Environment: production, staging, development

.EXAMPLE
    PS> .\deployment.ps1 -Action setup
    PS> .\deployment.ps1 -Action deploy
#>

$ErrorActionPreference = "Stop"

# Colors for output
$colors = @{
    Info = "Cyan"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
}

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    Write-Host $Message -ForegroundColor $colors[$Type]
}

function Get-PythonVersion {
    try {
        $version = & python --version 2>&1
        return $version
    }
    catch {
        return $null
    }
}

function Install-Dependencies {
    Write-Status "[*] Installing dependencies..." "Info"
    
    if (!(Test-Path "venv")) {
        Write-Status "    Creating virtual environment..." "Info"
        & python -m venv venv
    }
    
    Write-Status "    Activating virtual environment..." "Info"
    & ".\venv\Scripts\Activate.ps1"
    
    Write-Status "    Installing packages..." "Info"
    & pip install --upgrade pip setuptools wheel
    & pip install -r requirements.txt
    
    Write-Status "✓ Dependencies installed" "Success"
}

function Run-Setup {
    Write-Status "================================================================" "Info"
    Write-Status "      AI DDR GENERATOR - WINDOWS DEPLOYMENT" "Success"
    Write-Status "================================================================" "Info"
    Write-Status ""
    
    # Check Python
    Write-Status "[1/4] Checking Python..." "Info"
    $pythonVer = Get-PythonVersion
    if ($null -eq $pythonVer) {
        Write-Status "ERROR: Python not found" "Error"
        exit 1
    }
    Write-Status "✓ $pythonVer" "Success"
    Write-Status ""
    
    # Install dependencies
    Write-Status "[2/4] Setting up environment..." "Info"
    Install-Dependencies
    Write-Status ""
    
    # Run setup wizard
    Write-Status "[3/4] Running setup wizard..." "Info"
    & python setup.py
    Write-Status ""
    
    # Verify installation
    Write-Status "[4/4] Verifying installation..." "Info"
    & python deployment_checklist.py
    Write-Status ""
    
    Write-Status "================================================================" "Info"
    Write-Status "        DEPLOYMENT READY" "Success"
    Write-Status "================================================================" "Info"
    Write-Status ""
    Write-Status "Next steps:" "Info"
    Write-Status "  1. Run: python main.py" "Info"
    Write-Status "  2. View: cat outputs\ddr_report.txt" "Info"
    Write-Status ""
}

function Run-Deployment {
    Write-Status "[*] Building production artifacts..." "Info"
    & python build_for_production.py
    Write-Status "✓ Build complete" "Success"
}

function Start-Application {
    Write-Status "[*] Starting application..." "Info"
    & ".\venv\Scripts\Activate.ps1"
    & python prod_main.py
}

function Stop-Application {
    Write-Status "[*] Stopping application..." "Info"
    $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
    if ($pythonProcesses) {
        $pythonProcesses | Stop-Process -Force
        Write-Status "✓ Application stopped" "Success"
    }
    else {
        Write-Status "No application running" "Warning"
    }
}

function Get-Status {
    Write-Status "Checking application status..." "Info"
    $pythonProcesses = Get-Process python -ErrorAction SilentlyContinue
    
    if ($pythonProcesses) {
        Write-Status "✓ Application is running" "Success"
        $pythonProcesses | Format-Table Name, Id, Handles
    }
    else {
        Write-Status "Application is not running" "Warning"
    }
}

# Main execution
switch ($Action.ToLower()) {
    "setup" {
        Run-Setup
    }
    "deploy" {
        Run-Deployment
    }
    "start" {
        Start-Application
    }
    "stop" {
        Stop-Application
    }
    "status" {
        Get-Status
    }
    default {
        Write-Status "Unknown action: $Action" "Error"
        Write-Status "Valid actions: setup, deploy, start, stop, status" "Info"
        exit 1
    }
}
