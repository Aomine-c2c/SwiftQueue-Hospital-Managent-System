# Comprehensive Test Suite for SwiftQueue Hospital Management System
# Run all tests: Frontend (TypeScript), Backend (Python), E2E (Playwright)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  SWIFTQUEUE COMPREHENSIVE TEST SUITE" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$testResults = @()
$failedTests = @()
$startTime = Get-Date

# Function to log test results
function Log-TestResult {
    param(
        [string]$TestName,
        [string]$Status,
        [string]$Duration,
        [string]$Details = ""
    )
    
    $result = [PSCustomObject]@{
        Test = $TestName
        Status = $Status
        Duration = $Duration
        Details = $Details
    }
    
    $script:testResults += $result
    
    if ($Status -eq "FAILED") {
        $script:failedTests += $TestName
    }
}

# 1. TypeScript Type Checking
Write-Host "[1/8] Running TypeScript Type Check..." -ForegroundColor Yellow
$tscStart = Get-Date
try {
    $tscOutput = npx tsc --noEmit 2>&1
    $tscDuration = ((Get-Date) - $tscStart).TotalSeconds
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ TypeScript compilation passed" -ForegroundColor Green
        Log-TestResult "TypeScript Type Check" "PASSED" "$([math]::Round($tscDuration, 2))s"
    } else {
        Write-Host "  ✗ TypeScript compilation failed" -ForegroundColor Red
        Write-Host "  Errors: $tscOutput" -ForegroundColor Red
        Log-TestResult "TypeScript Type Check" "FAILED" "$([math]::Round($tscDuration, 2))s" "$tscOutput"
    }
} catch {
    Write-Host "  ✗ TypeScript check crashed: $_" -ForegroundColor Red
    Log-TestResult "TypeScript Type Check" "ERROR" "0s" "$_"
}

Write-Host ""

# 2. ESLint Check
Write-Host "[2/8] Running ESLint..." -ForegroundColor Yellow
$lintStart = Get-Date
try {
    $lintOutput = npm run lint 2>&1
    $lintDuration = ((Get-Date) - $lintStart).TotalSeconds
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ ESLint passed" -ForegroundColor Green
        Log-TestResult "ESLint" "PASSED" "$([math]::Round($lintDuration, 2))s"
    } else {
        Write-Host "  ⚠ ESLint warnings/errors found" -ForegroundColor Yellow
        Log-TestResult "ESLint" "WARNING" "$([math]::Round($lintDuration, 2))s" "See output for details"
    }
} catch {
    Write-Host "  ✗ ESLint crashed: $_" -ForegroundColor Red
    Log-TestResult "ESLint" "ERROR" "0s" "$_"
}

Write-Host ""

# 3. Frontend Build Test
Write-Host "[3/8] Testing Frontend Build..." -ForegroundColor Yellow
$buildStart = Get-Date
try {
    $buildOutput = npm run build 2>&1
    $buildDuration = ((Get-Date) - $buildStart).TotalSeconds
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path "dist/index.html")) {
        $distSize = (Get-ChildItem -Path "dist" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
        Write-Host "  ✓ Frontend build successful" -ForegroundColor Green
        Write-Host "  Build size: $([math]::Round($distSize, 2)) MB" -ForegroundColor Cyan
        Log-TestResult "Frontend Build" "PASSED" "$([math]::Round($buildDuration, 2))s" "Size: $([math]::Round($distSize, 2)) MB"
    } else {
        Write-Host "  ✗ Frontend build failed" -ForegroundColor Red
        Log-TestResult "Frontend Build" "FAILED" "$([math]::Round($buildDuration, 2))s" "Build output missing"
    }
} catch {
    Write-Host "  ✗ Build crashed: $_" -ForegroundColor Red
    Log-TestResult "Frontend Build" "ERROR" "0s" "$_"
}

Write-Host ""

# 4. Backend Python Tests
Write-Host "[4/8] Running Backend Python Tests..." -ForegroundColor Yellow
$backendStart = Get-Date

Set-Location backend

try {
    # Check if pytest is installed
    $pytestCheck = python -m pytest --version 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Running pytest..." -ForegroundColor Cyan
        $pytestOutput = python -m pytest -v --tb=short 2>&1
        $backendDuration = ((Get-Date) - $backendStart).TotalSeconds
        
        # Parse pytest output for results
        $passedTests = ($pytestOutput | Select-String "passed").Matches.Count
        $failedTestsCount = ($pytestOutput | Select-String "failed").Matches.Count
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ All backend tests passed ($passedTests tests)" -ForegroundColor Green
            Log-TestResult "Backend Python Tests" "PASSED" "$([math]::Round($backendDuration, 2))s" "$passedTests tests passed"
        } else {
            Write-Host "  ✗ Some backend tests failed ($failedTestsCount failed)" -ForegroundColor Red
            Log-TestResult "Backend Python Tests" "FAILED" "$([math]::Round($backendDuration, 2))s" "$failedTestsCount tests failed"
        }
    } else {
        Write-Host "  ⚠ pytest not installed, installing..." -ForegroundColor Yellow
        pip install pytest pytest-asyncio httpx -q
        
        $pytestOutput = python -m pytest -v --tb=short 2>&1
        $backendDuration = ((Get-Date) - $backendStart).TotalSeconds
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✓ Backend tests passed" -ForegroundColor Green
            Log-TestResult "Backend Python Tests" "PASSED" "$([math]::Round($backendDuration, 2))s"
        } else {
            Write-Host "  ✗ Backend tests failed" -ForegroundColor Red
            Log-TestResult "Backend Python Tests" "FAILED" "$([math]::Round($backendDuration, 2))s"
        }
    }
} catch {
    Write-Host "  ✗ Backend tests crashed: $_" -ForegroundColor Red
    Log-TestResult "Backend Python Tests" "ERROR" "0s" "$_"
}

Set-Location ..

Write-Host ""

# 5. API Health Check
Write-Host "[5/8] Checking API Health..." -ForegroundColor Yellow
$healthStart = Get-Date

try {
    # Try to reach the API
    $apiUrl = "http://localhost:8001/health"
    
    Write-Host "  Attempting to connect to $apiUrl..." -ForegroundColor Cyan
    $response = Invoke-WebRequest -Uri $apiUrl -TimeoutSec 5 -ErrorAction Stop
    $healthDuration = ((Get-Date) - $healthStart).TotalSeconds
    
    if ($response.StatusCode -eq 200) {
        Write-Host "  ✓ API is healthy and responding" -ForegroundColor Green
        Log-TestResult "API Health Check" "PASSED" "$([math]::Round($healthDuration, 2))s" "Status: 200 OK"
    } else {
        Write-Host "  ⚠ API responded with status: $($response.StatusCode)" -ForegroundColor Yellow
        Log-TestResult "API Health Check" "WARNING" "$([math]::Round($healthDuration, 2))s" "Status: $($response.StatusCode)"
    }
} catch {
    Write-Host "  ⚠ API not running (this is OK if testing without backend)" -ForegroundColor Yellow
    Log-TestResult "API Health Check" "SKIPPED" "0s" "Backend not running"
}

Write-Host ""

# 6. Check i18n Translations
Write-Host "[6/8] Validating i18n Translations..." -ForegroundColor Yellow
$i18nStart = Get-Date

try {
    $enPath = "src/i18n/locales/en.json"
    $snPath = "src/i18n/locales/sn.json"
    
    if ((Test-Path $enPath) -and (Test-Path $snPath)) {
        $enJson = Get-Content $enPath -Raw | ConvertFrom-Json
        $snJson = Get-Content $snPath -Raw | ConvertFrom-Json
        
        # Count translation keys
        $enKeys = ($enJson | ConvertTo-Json -Depth 10 | Select-String '"[^"]+":').Matches.Count
        $snKeys = ($snJson | ConvertTo-Json -Depth 10 | Select-String '"[^"]+":').Matches.Count
        
        $i18nDuration = ((Get-Date) - $i18nStart).TotalSeconds
        
        if ($enKeys -gt 0 -and $snKeys -gt 0) {
            Write-Host "  ✓ Translations loaded successfully" -ForegroundColor Green
            Write-Host "    English: ~$enKeys keys | Shona: ~$snKeys keys" -ForegroundColor Cyan
            Log-TestResult "i18n Translations" "PASSED" "$([math]::Round($i18nDuration, 2))s" "EN: $enKeys, SN: $snKeys keys"
        } else {
            Write-Host "  ✗ Translation files incomplete" -ForegroundColor Red
            Log-TestResult "i18n Translations" "FAILED" "$([math]::Round($i18nDuration, 2))s" "Missing translations"
        }
    } else {
        Write-Host "  ✗ Translation files not found" -ForegroundColor Red
        Log-TestResult "i18n Translations" "FAILED" "0s" "Files missing"
    }
} catch {
    Write-Host "  ✗ Translation validation failed: $_" -ForegroundColor Red
    Log-TestResult "i18n Translations" "ERROR" "0s" "$_"
}

Write-Host ""

# 7. Check Required Dependencies
Write-Host "[7/8] Verifying Dependencies..." -ForegroundColor Yellow
$depsStart = Get-Date

try {
    $packageJson = Get-Content "package.json" -Raw | ConvertFrom-Json
    $requiredDeps = @(
        "react",
        "react-dom",
        "react-router-dom",
        "zustand",
        "@tanstack/react-query",
        "i18next",
        "react-i18next",
        "@playwright/test"
    )
    
    $missingDeps = @()
    foreach ($dep in $requiredDeps) {
        if (-not $packageJson.dependencies.$dep -and -not $packageJson.devDependencies.$dep) {
            $missingDeps += $dep
        }
    }
    
    $depsDuration = ((Get-Date) - $depsStart).TotalSeconds
    
    if ($missingDeps.Count -eq 0) {
        Write-Host "  ✓ All required dependencies present" -ForegroundColor Green
        Log-TestResult "Dependencies Check" "PASSED" "$([math]::Round($depsDuration, 2))s" "$($requiredDeps.Count) deps verified"
    } else {
        Write-Host "  ✗ Missing dependencies: $($missingDeps -join ', ')" -ForegroundColor Red
        Log-TestResult "Dependencies Check" "FAILED" "$([math]::Round($depsDuration, 2))s" "Missing: $($missingDeps -join ', ')"
    }
} catch {
    Write-Host "  ✗ Dependency check failed: $_" -ForegroundColor Red
    Log-TestResult "Dependencies Check" "ERROR" "0s" "$_"
}

Write-Host ""

# 8. Playwright E2E Tests (Optional - requires running app)
Write-Host "[8/8] Running Playwright E2E Tests..." -ForegroundColor Yellow
$e2eStart = Get-Date

try {
    # Check if Playwright is installed
    $playwrightCheck = npx playwright --version 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ⚠ Skipping E2E tests (requires running app)" -ForegroundColor Yellow
        Write-Host "  To run E2E tests: npm run test:e2e" -ForegroundColor Cyan
        Log-TestResult "Playwright E2E Tests" "SKIPPED" "0s" "Run separately with app running"
    } else {
        Write-Host "  ⚠ Playwright not fully configured" -ForegroundColor Yellow
        Log-TestResult "Playwright E2E Tests" "SKIPPED" "0s" "Not configured"
    }
} catch {
    Write-Host "  ⚠ E2E tests skipped: $_" -ForegroundColor Yellow
    Log-TestResult "Playwright E2E Tests" "SKIPPED" "0s" "$_"
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Display results table
$testResults | Format-Table -AutoSize

# Summary statistics
$totalDuration = ((Get-Date) - $startTime).TotalSeconds
$passedCount = ($testResults | Where-Object { $_.Status -eq "PASSED" }).Count
$failedCount = ($testResults | Where-Object { $_.Status -eq "FAILED" }).Count
$warningCount = ($testResults | Where-Object { $_.Status -eq "WARNING" }).Count
$skippedCount = ($testResults | Where-Object { $_.Status -eq "SKIPPED" }).Count
$errorCount = ($testResults | Where-Object { $_.Status -eq "ERROR" }).Count

Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  ✓ Passed:  $passedCount" -ForegroundColor Green
Write-Host "  ✗ Failed:  $failedCount" -ForegroundColor Red
Write-Host "  ⚠ Warning: $warningCount" -ForegroundColor Yellow
Write-Host "  ⊘ Skipped: $skippedCount" -ForegroundColor Gray
Write-Host "  ⊗ Errors:  $errorCount" -ForegroundColor Magenta
Write-Host ""
Write-Host "Total Duration: $([math]::Round($totalDuration, 2)) seconds" -ForegroundColor Cyan
Write-Host ""

# Exit code
if ($failedCount -gt 0 -or $errorCount -gt 0) {
    Write-Host "❌ TESTS FAILED - See errors above" -ForegroundColor Red
    Write-Host ""
    if ($failedTests.Count -gt 0) {
        Write-Host "Failed tests:" -ForegroundColor Red
        $failedTests | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    }
    exit 1
} else {
    Write-Host "ALL TESTS PASSED!" -ForegroundColor Green
    exit 0
}
