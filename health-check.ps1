# Quick Health Check Script
# Run this to verify both frontend and backend are running

Write-Host "`n🏥 SwiftQueue Health Check" -ForegroundColor Cyan
Write-Host "===========================`n" -ForegroundColor Cyan

$allHealthy = $true

# Check Backend
Write-Host "Checking Backend (port 8001)..." -ForegroundColor Yellow
try {
    $backend = Invoke-RestMethod -Uri "http://localhost:8001/api/health" -Method GET -TimeoutSec 3
    Write-Host "✓ Backend is healthy" -ForegroundColor Green
    Write-Host "  Status: $($backend.status)" -ForegroundColor Gray
    if ($backend.timestamp) {
        Write-Host "  Timestamp: $($backend.timestamp)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Backend is not responding" -ForegroundColor Red
    Write-Host "  Start it with: .\start-backend.ps1" -ForegroundColor Yellow
    $allHealthy = $false
}

Write-Host ""

# Check Frontend
Write-Host "Checking Frontend (port 5173)..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:5173" -Method GET -TimeoutSec 3 -UseBasicParsing
    if ($frontend.StatusCode -eq 200) {
        Write-Host "✓ Frontend is running" -ForegroundColor Green
        Write-Host "  Status: $($frontend.StatusCode) OK" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ Frontend is not responding" -ForegroundColor Red
    Write-Host "  Start it with: .\start-frontend.ps1" -ForegroundColor Yellow
    $allHealthy = $false
}

Write-Host ""

# Check API Documentation
if ($allHealthy) {
    Write-Host "Checking API Documentation..." -ForegroundColor Yellow
    try {
        $docs = Invoke-WebRequest -Uri "http://localhost:8001/docs" -Method GET -TimeoutSec 3 -UseBasicParsing
        if ($docs.StatusCode -eq 200) {
            Write-Host "✓ API docs available at http://localhost:8001/docs" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠ API docs might not be accessible" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Summary
Write-Host "===========================`n" -ForegroundColor Cyan
if ($allHealthy) {
    Write-Host "✅ All services are healthy!" -ForegroundColor Green
    Write-Host "`nYou can access:" -ForegroundColor Cyan
    Write-Host "  • Frontend:  http://localhost:5173" -ForegroundColor White
    Write-Host "  • Backend:   http://localhost:8001" -ForegroundColor White
    Write-Host "  • API Docs:  http://localhost:8001/docs" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Some services are down" -ForegroundColor Red
    Write-Host "`nStart missing services:" -ForegroundColor Yellow
    Write-Host "  • Backend:  .\start-backend.ps1" -ForegroundColor White
    Write-Host "  • Frontend: .\start-frontend.ps1" -ForegroundColor White
    Write-Host ""
}
