# Run this script as Administrator to allow network access
# Right-click PowerShell and select "Run as Administrator", then run this script

Write-Host "Adding Windows Firewall rules for dev servers..." -ForegroundColor Cyan

# Add rule for Vite dev server (ports 5173-5180 to handle auto-increment)
try {
    New-NetFirewallRule -DisplayName "Vite Dev Server (5173-5180)" `
        -Direction Inbound `
        -LocalPort 5173-5180 `
        -Protocol TCP `
        -Action Allow `
        -ErrorAction Stop
    Write-Host "✓ Added firewall rule for Vite (ports 5173-5180)" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*already exists*") {
        Write-Host "✓ Firewall rule for Vite already exists" -ForegroundColor Yellow
    } else {
        Write-Host "✗ Error adding Vite firewall rule: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Add rule for FastAPI backend
try {
    New-NetFirewallRule -DisplayName "FastAPI Backend (8001)" `
        -Direction Inbound `
        -LocalPort 8001 `
        -Protocol TCP `
        -Action Allow `
        -ErrorAction Stop
    Write-Host "✓ Added firewall rule for Backend (port 8001)" -ForegroundColor Green
} catch {
    if ($_.Exception.Message -like "*already exists*") {
        Write-Host "✓ Firewall rule for Backend already exists" -ForegroundColor Yellow
    } else {
        Write-Host "✗ Error adding Backend firewall rule: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Firewall configuration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now access the dev server from other devices:" -ForegroundColor Cyan
Write-Host "  http://10.200.8.155:5173/" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
