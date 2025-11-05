# Complete Terminal Deployment Script
# Deploys SwiftQueue backend using Railway CLI

param(
    [string]$ServiceName = "swiftqueue-api"
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SwiftQueue - Railway Deployment" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Commit latest changes
Write-Host "[1/6] Committing latest changes..." -ForegroundColor Yellow
git add .
git commit -m "Deploy to Railway"
git push origin main
Write-Host "  [OK] Changes pushed to GitHub`n" -ForegroundColor Green

# Step 2: Navigate to backend
Write-Host "[2/6] Navigating to backend directory..." -ForegroundColor Yellow
cd backend
Write-Host "  [OK] In backend directory`n" -ForegroundColor Green

# Step 3: Link Railway project (if not already linked)
Write-Host "[3/6] Ensuring Railway project is linked..." -ForegroundColor Yellow
$status = railway status 2>&1
if ($status -match "None") {
    Write-Host "  [INFO] No service linked yet" -ForegroundColor Cyan
    Write-Host "  [ACTION] Deploying will create service automatically" -ForegroundColor Cyan
}
Write-Host "  [OK] Railway project ready`n" -ForegroundColor Green

# Step 4: Deploy to Railway
Write-Host "[4/6] Deploying to Railway..." -ForegroundColor Yellow
Write-Host "  This will:" -ForegroundColor Gray
Write-Host "    - Upload your backend code" -ForegroundColor Gray
Write-Host "    - Build Docker image" -ForegroundColor Gray
Write-Host "    - Deploy container" -ForegroundColor Gray
Write-Host "    - Assign public URL" -ForegroundColor Gray
Write-Host ""

railway up

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n  [ERROR] Deployment failed!" -ForegroundColor Red
    Write-Host "  Opening Railway dashboard for manual setup..." -ForegroundColor Yellow
    Start-Process "https://railway.com/project/56f61e8f-aea9-4ae5-8248-a6f53fdc56fd"
    exit 1
}

Write-Host "  [OK] Deployment initiated`n" -ForegroundColor Green

# Step 5: Get deployment URL
Write-Host "[5/6] Getting deployment URL..." -ForegroundColor Yellow
Start-Sleep 3

# Railway assigns URLs automatically, get it from status or domain command
$deployUrl = railway domain 2>&1

if ($deployUrl -match "https://") {
    Write-Host "  [OK] Backend URL: $deployUrl`n" -ForegroundColor Green
    
    # Test the deployment
    Write-Host "[6/6] Testing deployment..." -ForegroundColor Yellow
    Start-Sleep 5
    
    try {
        $health = Invoke-RestMethod -Uri "$deployUrl/api/health" -TimeoutSec 10
        Write-Host "  [OK] Backend is healthy!" -ForegroundColor Green
        Write-Host "  Status: $($health.status)" -ForegroundColor Gray
    } catch {
        Write-Host "  [WARN] Backend may still be starting up..." -ForegroundColor Yellow
        Write-Host "  Wait 1-2 minutes and test manually" -ForegroundColor Gray
    }
} else {
    Write-Host "  [INFO] URL not ready yet" -ForegroundColor Cyan
    Write-Host "  Check Railway dashboard for deployment status" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Project: swiftqueue-backend" -ForegroundColor White
Write-Host "Dashboard: https://railway.com/project/56f61e8f-aea9-4ae5-8248-a6f53fdc56fd" -ForegroundColor White

if ($deployUrl -match "https://") {
    Write-Host "Backend URL: $deployUrl" -ForegroundColor Green
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "  1. Test backend: $deployUrl/api/health" -ForegroundColor White
    Write-Host "  2. Update vercel.json with this URL" -ForegroundColor White
    Write-Host "  3. Deploy frontend: vercel --prod" -ForegroundColor White
} else {
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "  1. Visit Railway dashboard (opened in browser)" -ForegroundColor White
    Write-Host "  2. Click on your service" -ForegroundColor White
    Write-Host "  3. Go to Settings > Networking > Generate Domain" -ForegroundColor White
    Write-Host "  4. Copy the URL" -ForegroundColor White
    Write-Host "  5. Update vercel.json with that URL" -ForegroundColor White
    Write-Host "  6. Deploy frontend: vercel --prod" -ForegroundColor White
}

Write-Host "`n========================================`n" -ForegroundColor Cyan
