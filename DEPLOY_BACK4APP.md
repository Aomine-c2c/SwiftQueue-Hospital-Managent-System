# Deploying SwiftQueue Backend to Back4app

Back4app is a great alternative to Render - it's built on AWS infrastructure, offers container hosting, and has a generous free tier with better performance than many alternatives.

## Why Back4app?

- ✅ **Free Tier**: 256MB RAM, always-on (no cold starts)
- ✅ **Fast**: Built on AWS infrastructure
- ✅ **Docker Support**: Uses your existing Dockerfile
- ✅ **Auto-deploy**: Connects to GitHub for CI/CD
- ✅ **Database Included**: PostgreSQL available
- ✅ **Better than Render**: No cold starts on free tier

---

## Prerequisites

- [x] GitHub repository (already have it)
- [x] Dockerfile.prod (already created)
- [x] Back4app account (free)

---

## Deployment Steps

### Step 1: Create Back4app Account

1. Go to https://www.back4app.com/
2. Click **"Sign Up Free"**
3. Sign up with GitHub (recommended) or email
4. Verify your email if needed

### Step 2: Create New Container App

1. In Back4app dashboard, click **"Build new app"**
2. Select **"Container as a Service"**
3. Click **"Create a Container App"**

### Step 3: Connect GitHub Repository

1. **App Name**: `swiftqueue-backend`
2. **Region**: Choose closest to your users (e.g., `us-east-1`)
3. **Repository**: 
   - Click **"Connect GitHub"**
   - Authorize Back4app
   - Select: `Armutimbire223373Q/SwiftQueue-Hospital-Managent-System`
   - Branch: `main`
4. **Root Directory**: Leave blank (or type `backend` if prompted)

### Step 4: Configure Build Settings

1. **Dockerfile Path**: `backend/Dockerfile.prod`
2. **Build Context**: `backend/`
3. **Port**: `8000` (our app runs on this port)

### Step 5: Set Environment Variables

Click **"Environment Variables"** and add:

```bash
# Required
SECRET_KEY=your-production-secret-key-min-32-chars-long-random-string

# Optional (with defaults)
ENVIRONMENT=production
RATE_LIMIT_ENABLED=true
DATABASE_URL=sqlite:///./queue_management.db

# If using PostgreSQL (recommended for production)
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

**Important**: Generate a secure SECRET_KEY:
```powershell
# PowerShell - Generate secure key
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

Or use: `openssl rand -hex 32` on Linux/Mac

### Step 6: Choose Plan

**Free Tier** (Recommended to start):
- 256MB RAM
- 0.25 vCPU
- Always-on (no cold starts!)
- 1GB disk space

**Hobby** ($5/month):
- 512MB RAM
- 0.5 vCPU
- Better performance

**Production** ($25+/month):
- Scalable resources
- Custom domains
- SSL certificates

Choose **Free** to start, then click **"Create App"**

### Step 7: Deploy

1. Back4app will:
   - Clone your repository
   - Build Docker image from `backend/Dockerfile.prod`
   - Deploy container
   - Assign a URL

2. Wait 3-5 minutes for first deployment

3. Your backend URL will be:
   ```
   https://swiftqueue-backend-XXXXX.back4app.io
   ```

### Step 8: Verify Deployment

Test your deployed backend:

```powershell
# Test health endpoint
curl.exe https://swiftqueue-backend-XXXXX.back4app.io/api/health

# Expected response:
# {"status":"healthy","timestamp":"..."}
```

Visit API docs:
```
https://swiftqueue-backend-XXXXX.back4app.io/docs
```

---

## Configuration Files

### Option A: Use Existing Dockerfile (Recommended)

Your `backend/Dockerfile.prod` is already Back4app compatible! ✅

### Option B: Back4app Optimized Dockerfile (Optional)

If you want to optimize for Back4app specifically:

```dockerfile
# backend/Dockerfile.back4app
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Database Options

### Option 1: SQLite (Simple, included in container)

**Pros**: No setup needed, works immediately
**Cons**: Data lost on container restart

Environment variable:
```bash
DATABASE_URL=sqlite:///./queue_management.db
```

### Option 2: Back4app PostgreSQL (Recommended for production)

1. In Back4app dashboard, go to **"Database"**
2. Click **"Create Database"**
3. Choose **PostgreSQL**
4. Select plan (free tier available)
5. Copy connection string

Environment variable:
```bash
DATABASE_URL=postgresql://username:password@host.back4app.io:5432/dbname
```

Update `requirements.txt` to include:
```txt
psycopg2-binary>=2.9.0
```

### Option 3: External Database (Supabase, ElephantSQL, etc.)

Use any PostgreSQL provider and set `DATABASE_URL` accordingly.

---

## Update Vercel Configuration

Once deployed, update `vercel.json` with your Back4app URL:

```json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://swiftqueue-backend-XXXXX.back4app.io/api/:path*"
    }
  ]
}
```

Replace `XXXXX` with your actual Back4app subdomain.

---

## Auto-Deploy from GitHub

Back4app automatically deploys when you push to your main branch!

```powershell
git add .
git commit -m "Update backend"
git push origin main
```

Back4app will:
1. Detect the push
2. Rebuild container
3. Deploy new version
4. Zero-downtime deployment

---

## Monitoring & Logs

### View Logs

1. Go to your app in Back4app dashboard
2. Click **"Logs"** tab
3. View real-time logs
4. Filter by level (info, error, warning)

### Health Monitoring

Back4app automatically monitors:
- Container health (via HEALTHCHECK)
- HTTP response times
- Memory usage
- CPU usage

### Restart Container

If needed:
1. Go to app dashboard
2. Click **"Settings"**
3. Click **"Restart Container"**

---

## Custom Domain (Optional)

### Free Subdomain
Your app gets: `swiftqueue-backend-XXXXX.back4app.io`

### Custom Domain ($5+/month plan)
1. Go to **"Settings"** → **"Domains"**
2. Add your domain: `api.yourdomain.com`
3. Configure DNS:
   ```
   CNAME: api.yourdomain.com → swiftqueue-backend-XXXXX.back4app.io
   ```
4. Wait for DNS propagation (15-60 minutes)

---

## Cost Comparison

| Plan | Back4app | Render | Vercel |
|------|----------|--------|--------|
| **Free** | 256MB, always-on | 512MB, sleeps | N/A (frontend only) |
| **Hobby** | $5/month | $7/month | N/A |
| **Pro** | $25/month | $25/month | N/A |

**Winner**: Back4app has better free tier (no cold starts!) 🏆

---

## Troubleshooting

### Build Fails

**Error**: `Cannot find Dockerfile`
**Solution**: 
```bash
# Set correct path in Back4app:
Dockerfile Path: backend/Dockerfile.prod
Build Context: backend/
```

**Error**: `Module not found`
**Solution**: Ensure all dependencies in `requirements.txt`

### Container Crashes

**Check logs**:
1. Dashboard → Logs
2. Look for Python errors
3. Check environment variables

**Common issues**:
- Missing `SECRET_KEY` environment variable
- Database connection fails
- Port mismatch (should be 8000)

### Can't Connect to Backend

**Test locally first**:
```powershell
.\start-backend.ps1
curl.exe http://localhost:8001/api/health
```

**Check Back4app**:
1. Container is running (green status)
2. Port is 8000
3. Health check passes
4. Logs show "Uvicorn running"

### Database Issues

**SQLite**: Data persists only within container lifetime

**PostgreSQL**: 
- Verify connection string
- Check database credentials
- Ensure `psycopg2-binary` installed

---

## Performance Optimization

### 1. Enable Caching

Add to environment variables:
```bash
REDIS_URL=redis://your-redis-url:6379
```

### 2. Use PostgreSQL

SQLite is fine for testing, but PostgreSQL is better for production:
- Better concurrent connections
- Persistent data
- Better performance

### 3. Optimize Docker Image

Use multi-stage builds (already in Dockerfile.prod):
```dockerfile
FROM python:3.11-slim as builder
# ... build deps ...

FROM python:3.11-slim
# ... runtime only ...
```

### 4. Set Resource Limits

In Back4app dashboard:
- CPU: 0.25-0.5 vCPU
- Memory: 256-512MB
- Disk: 1GB

---

## Migration from SQLite to PostgreSQL

If you start with SQLite and want to migrate:

```python
# backend/migrate_to_postgres.py
from sqlalchemy import create_engine
from app.database import Base
from app.models import *  # Import all models

# Create tables in PostgreSQL
postgres_url = "postgresql://user:pass@host:5432/db"
engine = create_engine(postgres_url)
Base.metadata.create_all(bind=engine)

print("Migration complete!")
```

Then:
```powershell
python backend/migrate_to_postgres.py
```

Update `DATABASE_URL` in Back4app environment variables.

---

## Comparison: Back4app vs Render

| Feature | Back4app | Render |
|---------|----------|--------|
| **Cold Starts** | ❌ None | ✅ Yes (free tier) |
| **Free RAM** | 256MB | 512MB |
| **Always On** | ✅ Yes | ❌ No (free tier) |
| **Docker Support** | ✅ Yes | ✅ Yes |
| **Auto Deploy** | ✅ Yes | ✅ Yes |
| **Database** | ✅ Included | ✅ Included |
| **Price** | $5/month | $7/month |

**Verdict**: Back4app is better for apps that need **always-on** availability! 🎯

---

## Complete Deployment Checklist

- [ ] Create Back4app account
- [ ] Create new Container App
- [ ] Connect GitHub repository
- [ ] Configure build settings (Dockerfile path)
- [ ] Set environment variables (SECRET_KEY, etc.)
- [ ] Choose plan (Free tier to start)
- [ ] Deploy and wait 3-5 minutes
- [ ] Test health endpoint
- [ ] Visit API docs
- [ ] Update vercel.json with Back4app URL
- [ ] Redeploy frontend to Vercel
- [ ] Test full integration
- [ ] Monitor logs and performance

---

## Next Steps After Deployment

1. **Update Frontend**:
   ```powershell
   # Edit vercel.json with Back4app URL
   # Then redeploy
   vercel --prod
   ```

2. **Test Integration**:
   - Visit your Vercel frontend URL
   - Test login, queue operations
   - Check browser Network tab
   - Verify API calls work

3. **Monitor**:
   - Check Back4app logs daily
   - Monitor response times
   - Watch for errors

4. **Optimize**:
   - Add PostgreSQL database
   - Enable caching
   - Scale up if needed

---

## Support & Resources

- **Back4app Docs**: https://www.back4app.com/docs/
- **Support**: support@back4app.com
- **Community**: https://community.back4app.com/

---

## 🎉 You're Ready!

Back4app deployment is simpler than Render and has better free tier!

**Quick Start**:
1. Sign up at back4app.com
2. Create Container App
3. Connect GitHub
4. Deploy
5. Update vercel.json
6. Done! 🚀

Your backend will be available 24/7 with no cold starts, even on the free tier!
