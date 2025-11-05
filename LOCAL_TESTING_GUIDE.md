# Local Integration Testing Guide

## Quick Start

### Step 1: Start Backend (Terminal 1)
```powershell
.\start-backend.ps1
```

Wait until you see:
```
INFO:     Application started successfully!
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Step 2: Start Frontend (Terminal 2)
```powershell
.\start-frontend.ps1
```

Wait until you see:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

### Step 3: Test in Browser
Open http://localhost:5173 in your browser

## Testing Checklist

### ✓ Backend Health Check
Visit: http://localhost:8001/api/health

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-xx..."
}
```

### ✓ API Documentation
Visit: http://localhost:8001/docs

Should show FastAPI Swagger UI with all endpoints

### ✓ Frontend Loading
Visit: http://localhost:5173

Should see SwiftQueue dashboard

### ✓ Frontend → Backend Integration
1. Open browser DevTools (F12)
2. Go to Network tab
3. Interact with the app (login, view queue, etc.)
4. Check that API calls to `/api/*` return successfully (200 status codes)

### ✓ Authentication Flow
1. Try to login with test credentials
2. Check that auth token is stored
3. Verify protected routes work

### ✓ Real-time Features
1. Check WebSocket connection status
2. Verify live updates work (if applicable)

## Common Issues

### Backend won't start
- **Check if port 8001 is already in use:**
  ```powershell
  netstat -ano | findstr :8001
  ```
  If found, kill the process:
  ```powershell
  taskkill /PID <PID> /F
  ```

- **Database issues:**
  ```powershell
  cd backend
  python init_db.py
  ```

### Frontend can't connect to backend
- Ensure backend is running on port 8001
- Check `vite.config.ts` proxy configuration
- Clear browser cache and reload

### Port conflicts
- Backend: Default 8001 (can change in start-backend.ps1)
- Frontend: Default 5173 (can change in vite.config.ts)

## Manual Testing Commands

If you prefer manual terminal commands:

### Backend (Terminal 1)
```powershell
cd backend
$env:SECRET_KEY = "dev-secret-key-for-local-testing-only-32chars"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend (Terminal 2)
```powershell
npm run dev
```

## Quick Health Check Script

Create a file `test-integration.ps1`:
```powershell
# Test backend
Write-Host "Testing backend..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod http://localhost:8001/api/health
    Write-Host "✓ Backend is healthy: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend not responding" -ForegroundColor Red
    exit 1
}

# Test frontend
Write-Host "Testing frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest http://localhost:5173 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ Frontend is running" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Frontend not responding" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ All services running successfully!" -ForegroundColor Green
```

## Next Steps After Local Testing

Once everything works locally:

1. **Deploy Backend to Render:**
   - Follow `DEPLOY_RENDER.md` instructions
   - Note the deployed backend URL (e.g., `https://swiftqueue-api.onrender.com`)

2. **Update Vercel Configuration:**
   - Edit `vercel.json` line 8
   - Replace `https://your-backend-url.onrender.com` with your actual Render URL

3. **Redeploy Frontend to Vercel:**
   ```powershell
   vercel --prod
   ```

4. **Test Production Integration:**
   - Visit your Vercel URL
   - Verify API calls work through Vercel rewrites
   - Check browser DevTools Network tab

## Troubleshooting Production

If production doesn't work:
- Check Render logs for backend errors
- Verify Vercel rewrite URL is correct
- Check CORS settings in backend
- Verify environment variables are set in Render
