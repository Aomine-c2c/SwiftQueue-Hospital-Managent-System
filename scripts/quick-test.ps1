# Quick Test Script for SwiftQueue
# Runs essential tests to validate the application

Write-Host "`n=== SwiftQueue Quick Test Suite ===" -ForegroundColor Cyan
Write-Host "Starting tests...`n" -ForegroundColor Cyan

$script:passedTests = 0
$script:failedTests = 0
$script:skippedTests = 0

# Test 1: TypeScript Type Check
Write-Host "[1/6] TypeScript Type Check..." -ForegroundColor Yellow
try {
    $output = npx tsc --noEmit 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  PASS: No TypeScript errors" -ForegroundColor Green
        $script:passedTests++
    } else {
        Write-Host "  FAIL: TypeScript errors found" -ForegroundColor Red
        $script:failedTests++
    }
} catch {
    Write-Host "  FAIL: $_" -ForegroundColor Red
    $script:failedTests++
}

# Test 2: ESLint
Write-Host "`n[2/6] ESLint..." -ForegroundColor Yellow
try {
    npm run lint 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  PASS: No linting errors" -ForegroundColor Green
        $script:passedTests++
    } else {
        Write-Host "  FAIL: Linting errors found" -ForegroundColor Red
        $script:failedTests++
    }
} catch {
    Write-Host "  FAIL: $_" -ForegroundColor Red
    $script:failedTests++
}

# Test 3: Frontend Build
Write-Host "`n[3/6] Frontend Build..." -ForegroundColor Yellow
try {
    npm run build 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0 -and (Test-Path "dist")) {
        Write-Host "  PASS: Build successful" -ForegroundColor Green
        $script:passedTests++
    } else {
        Write-Host "  FAIL: Build failed" -ForegroundColor Red
        $script:failedTests++
    }
} catch {
    Write-Host "  FAIL: $_" -ForegroundColor Red
    $script:failedTests++
}

# Test 4: i18n Files
Write-Host "`n[4/6] i18n Translation Files..." -ForegroundColor Yellow
$enFile = "src/i18n/locales/en.json"
$snFile = "src/i18n/locales/sn.json"

if ((Test-Path $enFile) -and (Test-Path $snFile)) {
    try {
        $enContent = Get-Content $enFile -Raw | ConvertFrom-Json
        $snContent = Get-Content $snFile -Raw | ConvertFrom-Json
        
        if ($enContent -and $snContent) {
            Write-Host "  PASS: Both translation files valid" -ForegroundColor Green
            $script:passedTests++
        } else {
            Write-Host "  FAIL: Translation files invalid" -ForegroundColor Red
            $script:failedTests++
        }
    } catch {
        Write-Host "  FAIL: $_" -ForegroundColor Red
        $script:failedTests++
    }
} else {
    Write-Host "  FAIL: Translation files missing" -ForegroundColor Red
    $script:failedTests++
}

# Test 5: Required Dependencies
Write-Host "`n[5/6] Required Dependencies..." -ForegroundColor Yellow
$required = @("react", "react-dom", "i18next", "react-i18next")
$missing = @()

foreach ($pkg in $required) {
    if (!(Test-Path "node_modules/$pkg")) {
        $missing += $pkg
    }
}

if ($missing.Count -eq 0) {
    Write-Host "  PASS: All required dependencies installed" -ForegroundColor Green
    $script:passedTests++
} else {
    Write-Host "  FAIL: Missing dependencies: $($missing -join ', ')" -ForegroundColor Red
    $script:failedTests++
}

# Test 6: Backend Tests (if available)
Write-Host "`n[6/6] Backend Tests..." -ForegroundColor Yellow
if (Test-Path "backend") {
    Push-Location backend
    try {
        $pytestCheck = python -m pytest --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            python -m pytest -v --tb=short 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  PASS: Backend tests passed" -ForegroundColor Green
                $script:passedTests++
            } else {
                Write-Host "  FAIL: Backend tests failed" -ForegroundColor Red
                $script:failedTests++
            }
        } else {
            Write-Host "  SKIP: pytest not installed" -ForegroundColor Gray
            $script:skippedTests++
        }
    } catch {
        Write-Host "  SKIP: $_" -ForegroundColor Gray
        $script:skippedTests++
    }
    Pop-Location
} else {
    Write-Host "  SKIP: Backend not found" -ForegroundColor Gray
    $script:skippedTests++
}

# Summary
Write-Host "`n=== Test Results ===" -ForegroundColor Cyan
Write-Host "Passed:  $script:passedTests" -ForegroundColor Green
Write-Host "Failed:  $script:failedTests" -ForegroundColor Red
Write-Host "Skipped: $script:skippedTests" -ForegroundColor Gray

if ($script:failedTests -eq 0) {
    Write-Host "`nALL TESTS PASSED!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSOME TESTS FAILED!" -ForegroundColor Red
    exit 1
}
