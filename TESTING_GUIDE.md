# 🧪 Testing Guide for SwiftQueue

This guide provides comprehensive instructions for testing all aspects of the SwiftQueue application locally before deploying to production.

## 📋 Quick Start

### Option 1: Automated Testing (Recommended)
Run the comprehensive test suite:
```powershell
.\RUN_COMPREHENSIVE_TESTS.ps1
```

This will test:
- ✅ Backend dependencies
- ✅ Frontend dependencies
- ✅ Database connection
- ✅ Backend server health
- ✅ Frontend build
- ✅ API endpoints
- ✅ Authentication
- ✅ Queue operations
- ✅ AI services
- ✅ File upload

### Option 2: Manual Testing

#### Step 1: Start Backend
In **Terminal 1**:
```powershell
.\start-backend.ps1
```

Wait for:
```
Application started successfully!
INFO:     Uvicorn running on http://127.0.0.1:8001
```

#### Step 2: Start Frontend
In **Terminal 2**:
```powershell
.\start-frontend.ps1
```

Wait for:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

#### Step 3: Quick Health Check
In **Terminal 3**:
```powershell
.\health-check.ps1
```

## 🎯 What to Test

### 1. Backend API

#### Health Check
```powershell
curl.exe http://localhost:8001/api/health
```
Expected: `{"status":"healthy","timestamp":"..."}`

#### API Documentation
Open in browser: http://localhost:8001/docs

You should see the Swagger UI with all endpoints.

#### Test Authentication
```powershell
# Register a new user
$body = @{
    email = "testuser@example.com"
    password = "Test123!@#"
    full_name = "Test User"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/api/auth/register" -Method POST -Body $body -ContentType "application/json"
```

```powershell
# Login
$loginBody = @{
    username = "testuser@example.com"
    password = "Test123!@#"
} | ConvertTo-Json

$token = Invoke-RestMethod -Uri "http://localhost:8001/api/auth/login" -Method POST -Body $loginBody -ContentType "application/x-www-form-urlencoded"
```

### 2. Frontend

#### Basic Loading
Open: http://localhost:5173

You should see:
- ✅ SwiftQueue dashboard loads
- ✅ No console errors (F12 → Console)
- ✅ Styling is applied correctly

#### API Integration
1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Interact with the app (login, view queues, etc.)
4. Check that API calls to `/api/*` show:
   - ✅ Status: 200 (or appropriate status)
   - ✅ Request URL: `http://localhost:5173/api/...` (proxied to backend)
   - ✅ Response data is valid JSON

#### Navigation
Test all major routes:
- `/` - Dashboard
- `/login` - Login page
- `/register` - Registration page
- `/queue` - Queue management
- `/services` - Services list
- `/analytics` - Analytics dashboard

### 3. Queue Operations

```powershell
# Get all queues
Invoke-RestMethod -Uri "http://localhost:8001/api/queue/" -Method GET

# Get services
Invoke-RestMethod -Uri "http://localhost:8001/api/services" -Method GET
```

### 4. AI Services

```powershell
# Check AI health
Invoke-RestMethod -Uri "http://localhost:8001/api/ai/health" -Method GET

# Get classifier status
Invoke-RestMethod -Uri "http://localhost:8001/api/classifier/model-status" -Method GET
```

### 5. File Upload

Test through the frontend:
1. Navigate to file upload section
2. Upload a test file
3. Check that file appears in uploads list

Or via API:
```powershell
# Get file stats
Invoke-RestMethod -Uri "http://localhost:8001/api/files/stats" -Method GET
```

## 🐛 Troubleshooting

### Port Already in Use

If you see: `An attempt was made to access a socket in a way forbidden by its access permissions`

```powershell
# Find process using port 8001
netstat -ano | findstr :8001

# Kill it (replace PID)
taskkill /PID <PID> /F
```

The updated `start-backend.ps1` script will handle this automatically.

### Database Not Found

```powershell
cd backend
python init_db.py
```

### Module Not Found Errors

```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
npm install
```

### Frontend Build Fails

```powershell
# Clear cache and reinstall
Remove-Item node_modules -Recurse -Force
Remove-Item package-lock.json
npm install
npm run build
```

### Backend Won't Start

1. Check Python version: `python --version` (should be 3.8+)
2. Check if virtual environment is active
3. Ensure all environment variables are set
4. Check database file exists: `backend/queue_management.db`

### API Calls Fail with CORS Errors

Check in browser console. If you see CORS errors:
1. Verify backend is running on port 8001
2. Check `vite.config.ts` has correct proxy settings
3. Verify backend CORS configuration in `app/main.py`

## 📊 Test Coverage

### Critical Paths to Test
- [ ] User registration
- [ ] User login
- [ ] Token refresh
- [ ] Join queue
- [ ] Check queue status
- [ ] Call next patient
- [ ] View analytics
- [ ] Upload files
- [ ] AI symptom analysis
- [ ] Service recommendations

### Performance Tests
- [ ] Multiple concurrent users
- [ ] Large queue operations
- [ ] File upload with large files
- [ ] Real-time WebSocket updates

### Security Tests
- [ ] Invalid login attempts
- [ ] Token expiration handling
- [ ] Unauthorized access attempts
- [ ] SQL injection prevention (try malicious inputs)
- [ ] XSS prevention (try script tags in inputs)

## 🚀 Ready for Production?

Once all tests pass locally:

### 1. Deploy Backend to Render
Follow `DEPLOY_RENDER.md`:
```bash
# Push to GitHub (Render will auto-deploy)
git add .
git commit -m "Ready for production deployment"
git push origin main
```

### 2. Get Backend URL
After Render deployment, note your backend URL:
```
https://swiftqueue-api.onrender.com
```

### 3. Update Vercel Configuration
Edit `vercel.json` line 8:
```json
"destination": "https://swiftqueue-api.onrender.com/api/:path*"
```

### 4. Deploy Frontend to Vercel
```powershell
vercel --prod
```

### 5. Test Production
Visit your Vercel URL and test:
- [ ] Frontend loads correctly
- [ ] API calls work through Vercel rewrites
- [ ] Authentication works
- [ ] All features functional

## 📝 Test Checklist

Use this checklist before each deployment:

```
Local Testing:
[ ] Backend dependencies installed
[ ] Frontend dependencies installed
[ ] Database initialized
[ ] Backend starts without errors
[ ] Frontend builds successfully
[ ] Health endpoints respond
[ ] Authentication works
[ ] Queue operations work
[ ] AI services respond
[ ] File uploads work
[ ] No console errors
[ ] All routes accessible

Production Testing:
[ ] Backend deployed to Render
[ ] Render health check passes
[ ] vercel.json updated with Render URL
[ ] Frontend deployed to Vercel
[ ] Production frontend loads
[ ] Production API calls work
[ ] Production authentication works
[ ] Environment variables set correctly
[ ] Logs show no errors
[ ] Performance acceptable
```

## 🔧 Useful Commands

```powershell
# Start everything
.\start-backend.ps1    # Terminal 1
.\start-frontend.ps1   # Terminal 2

# Check health
.\health-check.ps1

# Run comprehensive tests
.\RUN_COMPREHENSIVE_TESTS.ps1

# Build frontend
npm run build

# Test frontend build locally
npm run preview

# Check backend logs
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --log-level debug

# Run backend tests
cd backend
pytest -v

# Check package versions
pip list                # Backend
npm list --depth=0      # Frontend
```

## 📚 Additional Resources

- **API Documentation**: http://localhost:8001/docs (when backend is running)
- **Deployment Guide**: See `VERCEL_DEPLOYMENT.md`
- **Render Guide**: See `DEPLOY_RENDER.md`
- **Local Testing**: See `LOCAL_TESTING_GUIDE.md`

## 🆘 Getting Help

If tests fail:
1. Check the error messages carefully
2. Look in the troubleshooting section above
3. Check backend logs: Look at the terminal running `start-backend.ps1`
4. Check frontend console: F12 → Console in browser
5. Run comprehensive tests for detailed diagnostics: `.\RUN_COMPREHENSIVE_TESTS.ps1`

## ✅ Success Indicators

You're ready for production when:
- ✅ All automated tests pass
- ✅ No errors in backend logs
- ✅ No errors in frontend console
- ✅ All critical paths work
- ✅ Performance is acceptable
- ✅ Security tests pass
- ✅ Database operations work correctly
- ✅ Frontend build completes without warnings
