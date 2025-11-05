# Start Frontend Development Server
# Run this script to start the Vite dev server on port 5173

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting SwiftQueue Frontend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting Vite development server..." -ForegroundColor Yellow
Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Yellow
Write-Host "API requests will proxy to: http://localhost:8001/api" -ForegroundColor Yellow
Write-Host ""
Write-Host "Make sure the backend is running first!" -ForegroundColor Red
Write-Host "Run: .\start-backend.ps1 in another terminal" -ForegroundColor Red
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Red
Write-Host ""

# Start Vite dev server
npm run dev
