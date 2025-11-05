# Start backend with required environment variables
$env:ENVIRONMENT = "development"
$env:SECRET_KEY = if ($env:SECRET_KEY) { $env:SECRET_KEY } else { 
    python -c "import secrets,sys;sys.stdout.write(secrets.token_hex(32))"
}
$env:PYTHONPATH = Join-Path $PSScriptRoot "..\backend"

Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host "Environment: $env:ENVIRONMENT" -ForegroundColor Cyan
Write-Host "PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Cyan

# Check if port 8001 is in use and kill the process
$port = 8001
$connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($connection) {
    $processId = $connection.OwningProcess | Select-Object -First 1
    Write-Host "Port $port is in use by process $processId. Stopping it..." -ForegroundColor Yellow
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Host ""

Set-Location (Join-Path $PSScriptRoot "..\backend")
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
