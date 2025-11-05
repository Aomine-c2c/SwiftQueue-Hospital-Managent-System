# Start Backend Server for Local Testing
# Run this script to start the FastAPI backend on port 8001

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting SwiftQueue Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if port 8001 is already in use
$portCheck = netstat -ano | findstr :8001
if ($portCheck) {
    Write-Host "⚠️  Port 8001 is already in use!" -ForegroundColor Yellow
    Write-Host "Checking processes..." -ForegroundColor Gray
    Write-Host ""
    netstat -ano | findstr :8001
    Write-Host ""
    Write-Host "Kill the process? (Y/N): " -ForegroundColor Yellow -NoNewline
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        $pid = ($portCheck -split '\s+')[-1]
        taskkill /PID $pid /F
        Write-Host "✓ Process killed" -ForegroundColor Green
        Start-Sleep 2
    } else {
        Write-Host "Exiting..." -ForegroundColor Red
        exit 1
    }
}

# Set environment variables
$env:SECRET_KEY = "dev-secret-key-for-local-testing-only-32chars"
$env:RATE_LIMIT_ENABLED = "false"
$env:ENVIRONMENT = "development"
$env:DATABASE_URL = "sqlite:///./queue_management.db"

Write-Host "Environment configured:" -ForegroundColor Green
Write-Host "  - SECRET_KEY: ****" -ForegroundColor Gray
Write-Host "  - RATE_LIMIT_ENABLED: false" -ForegroundColor Gray
Write-Host "  - ENVIRONMENT: development" -ForegroundColor Gray
Write-Host "  - DATABASE_URL: sqlite:///./queue_management.db" -ForegroundColor Gray
Write-Host ""

# Navigate to backend directory
Set-Location $PSScriptRoot\backend

# Check if database exists
if (-not (Test-Path "queue_management.db")) {
    Write-Host "⚠️  Database not found! Initializing..." -ForegroundColor Yellow
    python init_db.py
    Write-Host "✓ Database initialized" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Starting uvicorn server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend will be available at:" -ForegroundColor Cyan
Write-Host "  • Health Check: http://localhost:8001/api/health" -ForegroundColor White
Write-Host "  • API Docs:     http://localhost:8001/docs" -ForegroundColor White
Write-Host "  • All Routes:   http://localhost:8001/openapi.json" -ForegroundColor White
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Red
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start uvicorn
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
