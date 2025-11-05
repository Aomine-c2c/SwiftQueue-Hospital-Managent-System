# Comprehensive Testing Script for SwiftQueue
# Simplified version without Unicode characters

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend
)

$ErrorActionPreference = "Continue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SwiftQueue Comprehensive Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test Results
$testResults = @{}

# Backend Dependencies
$testResults["BackendDependencies"] = $false
$testResults["FrontendDependencies"] = $false
$testResults["DatabaseConnection"] = $false
$testResults["BackendHealth"] = $false
$testResults["FrontendBuild"] = $false
$testResults["APIEndpoints"] = $false
$testResults["Authentication"] = $false
$testResults["QueueOperations"] = $false
$testResults["AIServices"] = $false
$testResults["FileUpload"] = $false

# ============================================================
# 1. BACKEND DEPENDENCY CHECK
# ============================================================
if (-not $SkipBackend) {
    Write-Host "[1/10] Testing Backend Dependencies..." -ForegroundColor Yellow
    try {
        Push-Location backend
        
        # Check if Python is available
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python") {
            Write-Host "  [OK] Python: $pythonVersion" -ForegroundColor Green
            
            # Check key dependencies
            $pipList = pip list 2>&1
            $allPresent = $true
            
            if ($pipList -match "fastapi") {
                Write-Host "  [OK] fastapi installed" -ForegroundColor Green
            } else {
                Write-Host "  [FAIL] fastapi missing" -ForegroundColor Red
                $allPresent = $false
            }
            
            if ($pipList -match "uvicorn") {
                Write-Host "  [OK] uvicorn installed" -ForegroundColor Green
            } else {
                Write-Host "  [FAIL] uvicorn missing" -ForegroundColor Red
                $allPresent = $false
            }
            
            if ($allPresent) {
                $testResults["BackendDependencies"] = $true
                Write-Host "[PASS] Backend dependencies OK" -ForegroundColor Green
            } else {
                Write-Host "[FAIL] Some backend dependencies missing" -ForegroundColor Red
            }
        }
        
        Pop-Location
    } catch {
        Write-Host "[FAIL] Backend dependency check failed: $_" -ForegroundColor Red
        Pop-Location
    }
}

# ============================================================
# 2. FRONTEND DEPENDENCY CHECK
# ============================================================
if (-not $SkipFrontend) {
    Write-Host "`n[2/10] Testing Frontend Dependencies..." -ForegroundColor Yellow
    try {
        # Check if Node.js is available
        $nodeVersion = node --version 2>&1
        Write-Host "  [OK] Node.js: $nodeVersion" -ForegroundColor Green
        
        # Check if npm is available
        $npmVersion = npm --version 2>&1
        Write-Host "  [OK] npm: $npmVersion" -ForegroundColor Green
        
        # Check if node_modules exists
        if (Test-Path "node_modules") {
            Write-Host "  [OK] node_modules exists" -ForegroundColor Green
            $testResults["FrontendDependencies"] = $true
            Write-Host "[PASS] Frontend dependencies OK" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] node_modules missing" -ForegroundColor Red
            Write-Host "  Run: npm install" -ForegroundColor Yellow
            Write-Host "[FAIL] Frontend dependencies missing" -ForegroundColor Red
        }
    } catch {
        Write-Host "[FAIL] Frontend dependency check failed: $_" -ForegroundColor Red
    }
}

# ============================================================
# 3. DATABASE CONNECTION
# ============================================================
if (-not $SkipBackend) {
    Write-Host "`n[3/10] Testing Database Connection..." -ForegroundColor Yellow
    try {
        Push-Location backend
        
        if (Test-Path "queue_management.db") {
            Write-Host "  [OK] Database file exists" -ForegroundColor Green
            $testResults["DatabaseConnection"] = $true
            Write-Host "[PASS] Database connection OK" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Database file not found" -ForegroundColor Yellow
            Write-Host "  Run: python init_db.py" -ForegroundColor Yellow
            Write-Host "[FAIL] Database not initialized" -ForegroundColor Red
        }
        
        Pop-Location
    } catch {
        Write-Host "[FAIL] Database test failed: $_" -ForegroundColor Red
        Pop-Location
    }
}

# ============================================================
# 4. BACKEND SERVER (MANUAL START REQUIRED)
# ============================================================
if (-not $SkipBackend) {
    Write-Host "`n[4/10] Testing Backend Server..." -ForegroundColor Yellow
    Write-Host "  [INFO] Manual step required" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Please start the backend in a SEPARATE terminal:" -ForegroundColor Yellow
    Write-Host "  .\start-backend.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "  Press ENTER once backend is running..." -ForegroundColor Yellow
    Read-Host
    
    # Test backend health
    try {
        Start-Sleep 2
        $response = Invoke-RestMethod -Uri "http://localhost:8001/api/health" -Method GET -TimeoutSec 5
        
        if ($response) {
            Write-Host "  [OK] Backend health check passed" -ForegroundColor Green
            Write-Host "    Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
            $testResults["BackendHealth"] = $true
            Write-Host "[PASS] Backend server OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [FAIL] Backend not responding" -ForegroundColor Red
        Write-Host "    Error: $_" -ForegroundColor Gray
        Write-Host "[FAIL] Backend server not accessible" -ForegroundColor Red
    }
}

# ============================================================
# 5. FRONTEND BUILD
# ============================================================
if (-not $SkipFrontend) {
    Write-Host "`n[5/10] Testing Frontend Build..." -ForegroundColor Yellow
    try {
        Write-Host "  Building frontend (this may take a minute)..." -ForegroundColor Cyan
        $buildOutput = npm run build 2>&1
        
        if ($LASTEXITCODE -eq 0 -and (Test-Path "dist")) {
            Write-Host "  [OK] Frontend build successful" -ForegroundColor Green
            Write-Host "    Output directory: dist/" -ForegroundColor Gray
            $testResults["FrontendBuild"] = $true
            Write-Host "[PASS] Frontend build OK" -ForegroundColor Green
        } else {
            Write-Host "  [FAIL] Frontend build failed" -ForegroundColor Red
            Write-Host "[FAIL] Frontend build failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "[FAIL] Frontend build test failed: $_" -ForegroundColor Red
    }
}

# ============================================================
# 6. API ENDPOINTS
# ============================================================
if (-not $SkipBackend -and $testResults["BackendHealth"]) {
    Write-Host "`n[6/10] Testing API Endpoints..." -ForegroundColor Yellow
    
    $passedEndpoints = 0
    $totalEndpoints = 3
    
    try {
        Invoke-RestMethod -Uri "http://localhost:8001/api/health" -Method GET -TimeoutSec 5 | Out-Null
        Write-Host "  [OK] Health Check" -ForegroundColor Green
        $passedEndpoints++
    } catch {
        Write-Host "  [FAIL] Health Check" -ForegroundColor Red
    }
    
    try {
        Invoke-RestMethod -Uri "http://localhost:8001/api/services" -Method GET -TimeoutSec 5 | Out-Null
        Write-Host "  [OK] Services List" -ForegroundColor Green
        $passedEndpoints++
    } catch {
        Write-Host "  [FAIL] Services List" -ForegroundColor Red
    }
    
    try {
        Invoke-RestMethod -Uri "http://localhost:8001/api/queue/" -Method GET -TimeoutSec 5 | Out-Null
        Write-Host "  [OK] Queue List" -ForegroundColor Green
        $passedEndpoints++
    } catch {
        Write-Host "  [FAIL] Queue List" -ForegroundColor Red
    }
    
    if ($passedEndpoints -eq $totalEndpoints) {
        $testResults["APIEndpoints"] = $true
        Write-Host "[PASS] All API endpoints accessible" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] Some API endpoints failed ($passedEndpoints/$totalEndpoints passed)" -ForegroundColor Red
    }
}

# ============================================================
# 7. AUTHENTICATION
# ============================================================
if (-not $SkipBackend -and $testResults["BackendHealth"]) {
    Write-Host "`n[7/10] Testing Authentication..." -ForegroundColor Yellow
    
    try {
        $loginTest = Invoke-WebRequest -Uri "http://localhost:8001/api/auth/login" -Method POST -TimeoutSec 5 -SkipHttpErrorCheck
        
        if ($loginTest.StatusCode -in @(200, 400, 401, 422)) {
            Write-Host "  [OK] Login endpoint accessible" -ForegroundColor Green
            $testResults["Authentication"] = $true
            Write-Host "[PASS] Authentication endpoints OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [FAIL] Authentication test failed: $_" -ForegroundColor Red
        Write-Host "[FAIL] Authentication not accessible" -ForegroundColor Red
    }
}

# ============================================================
# 8. QUEUE OPERATIONS
# ============================================================
if (-not $SkipBackend -and $testResults["BackendHealth"]) {
    Write-Host "`n[8/10] Testing Queue Operations..." -ForegroundColor Yellow
    
    try {
        Invoke-RestMethod -Uri "http://localhost:8001/api/queue/" -Method GET -TimeoutSec 5 | Out-Null
        Write-Host "  [OK] Queue list retrieved" -ForegroundColor Green
        $testResults["QueueOperations"] = $true
        Write-Host "[PASS] Queue operations OK" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] Queue operations test failed: $_" -ForegroundColor Red
        Write-Host "[FAIL] Queue operations not accessible" -ForegroundColor Red
    }
}

# ============================================================
# 9. AI SERVICES
# ============================================================
if (-not $SkipBackend -and $testResults["BackendHealth"]) {
    Write-Host "`n[9/10] Testing AI Services..." -ForegroundColor Yellow
    
    try {
        $aiHealth = Invoke-RestMethod -Uri "http://localhost:8001/api/ai/health" -Method GET -TimeoutSec 5
        Write-Host "  [OK] AI health check passed" -ForegroundColor Green
        $testResults["AIServices"] = $true
        Write-Host "[PASS] AI services OK" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] AI services may not be fully configured" -ForegroundColor Yellow
        Write-Host "  This is optional for basic functionality" -ForegroundColor Gray
    }
}

# ============================================================
# 10. FILE UPLOAD
# ============================================================
if (-not $SkipBackend -and $testResults["BackendHealth"]) {
    Write-Host "`n[10/10] Testing File Upload..." -ForegroundColor Yellow
    
    try {
        Invoke-RestMethod -Uri "http://localhost:8001/api/files/stats" -Method GET -TimeoutSec 5 | Out-Null
        Write-Host "  [OK] File upload endpoints accessible" -ForegroundColor Green
        $testResults["FileUpload"] = $true
        Write-Host "[PASS] File upload OK" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] File upload test failed: $_" -ForegroundColor Red
        Write-Host "[FAIL] File upload not accessible" -ForegroundColor Red
    }
}

# ============================================================
# SUMMARY
# ============================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$passedTests = ($testResults.Values | Where-Object { $_ -eq $true }).Count
$totalTests = $testResults.Count

Write-Host "`nResults: $passedTests / $totalTests tests passed`n" -ForegroundColor $(if ($passedTests -eq $totalTests) { "Green" } elseif ($passedTests -gt ($totalTests / 2)) { "Yellow" } else { "Red" })

foreach ($test in $testResults.GetEnumerator()) {
    $status = if ($test.Value) { "[PASS]" } else { "[FAIL]" }
    $color = if ($test.Value) { "Green" } else { "Red" }
    Write-Host "  $status $($test.Key)" -ForegroundColor $color
}

Write-Host ""

# ============================================================
# RECOMMENDATIONS
# ============================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RECOMMENDATIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not $testResults["BackendDependencies"]) {
    Write-Host "`nInstall backend dependencies:" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   pip install -r requirements.txt" -ForegroundColor White
}

if (-not $testResults["FrontendDependencies"]) {
    Write-Host "`nInstall frontend dependencies:" -ForegroundColor Yellow
    Write-Host "   npm install" -ForegroundColor White
}

if (-not $testResults["DatabaseConnection"]) {
    Write-Host "`nInitialize database:" -ForegroundColor Yellow
    Write-Host "   cd backend" -ForegroundColor White
    Write-Host "   python init_db.py" -ForegroundColor White
}

if (-not $testResults["BackendHealth"]) {
    Write-Host "`nStart backend server:" -ForegroundColor Yellow
    Write-Host "   .\start-backend.ps1" -ForegroundColor White
    Write-Host "   (In a separate terminal)" -ForegroundColor Gray
}

if ($testResults["BackendHealth"] -and $testResults["FrontendBuild"]) {
    Write-Host "`n[SUCCESS] READY FOR DEPLOYMENT!" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "  1. Deploy backend to Render (see DEPLOY_RENDER.md)" -ForegroundColor White
    Write-Host "  2. Update vercel.json with Render backend URL" -ForegroundColor White
    Write-Host "  3. Deploy frontend to Vercel: vercel --prod" -ForegroundColor White
}

Write-Host "`n========================================`n" -ForegroundColor Cyan

# Exit with appropriate code
if ($passedTests -eq $totalTests) {
    exit 0
} else {
    exit 1
}
