# SwiftQueue Vercel Deployment Guide

## Current Setup: Frontend-Only on Vercel

The Vercel deployment is configured for **frontend static hosting only**. The backend must be deployed separately.

### Why Not Host Backend on Vercel?

Vercel's Python serverless functions have limitations:
- 50MB deployment size limit
- Cold start issues with heavy dependencies (SQLAlchemy, sklearn, etc.)
- No persistent file system (database files, model files won't persist)
- 10-second execution timeout (not suitable for long-running operations)
- No WebSocket support

### Recommended Architecture

1. **Frontend → Vercel** (static React/Vite app)
2. **Backend → Render/Railway/Fly** (full FastAPI server with database)

## Quick Deployment Steps

### Option 1: Deploy Backend to Render (Recommended - Free Tier Available)

1. **Create a Render account** at https://render.com

2. **Create a new Web Service**:
   - Connect your GitHub repository
   - Select branch: `main`
   - Root directory: `backend`
   - Environment: `Docker`
   - Dockerfile path: `backend/Dockerfile.prod`

3. **Set environment variables** in Render:
   ```
   SECRET_KEY=<generate-with-openssl-rand-hex-32>
   DATABASE_URL=<your-postgres-url>
   ENVIRONMENT=production
   RATE_LIMIT_ENABLED=true
   ```

4. **Deploy and copy the URL** (e.g., `https://swiftqueue-backend.onrender.com`)

### Option 2: Deploy Backend to Railway

1. Install Railway CLI:
   ```powershell
   npm install -g @railway/cli
   railway login
   ```

2. Deploy from backend directory:
   ```powershell
   cd backend
   railway init
   railway up
   ```

3. Set environment variables via Railway dashboard

4. Copy the deployment URL

### Option 3: Use Dockerfile Locally and Deploy to Any Cloud

The `backend/Dockerfile.prod` is production-ready and can be deployed to:
- Google Cloud Run
- AWS ECS/Fargate
- Azure Container Instances
- DigitalOcean App Platform
- Fly.io

## Configure Vercel After Backend Deployment

1. **Update `vercel.json`** with your actual backend URL:
   - Edit line 8: Replace `https://your-backend-url.onrender.com` with your actual backend URL
   - Commit and push the change

2. **Or set environment variable** in Vercel (alternative):
   - Go to Vercel → Project Settings → Environment Variables
   - Add: `BACKEND_URL` = `https://your-actual-backend-url.com`
   - Then update `vercel.json` to use: `"destination": "$BACKEND_URL/api/:path*"`

3. **Redeploy on Vercel** - it should now build successfully

## Verification

After both deployments:

1. **Test backend directly**:
   ```bash
   curl https://your-backend-url.onrender.com/api/health
   ```
   Should return: `{"status":"healthy",...}`

2. **Test frontend on Vercel**:
   - Visit: `https://your-app.vercel.app`
   - Open browser DevTools → Network tab
   - Navigate in the app and verify API calls are proxied correctly

3. **Test API proxy**:
   ```bash
   curl https://your-app.vercel.app/api/health
   ```
   Should return the same response (proxied through Vercel to backend)

## Troubleshooting

### Vercel Build Fails
- Check Node version is 22.x in `package.json` ✓ (already set)
- Check build command is `npm run build` ✓
- Check output directory is `dist` ✓

### API Calls Return 404
- Verify the rewrite destination URL in `vercel.json` is correct
- Check backend is actually running and accessible
- Check CORS is configured on backend to allow Vercel domain

### API Calls Timeout
- Backend might be on a free tier that sleeps (Render free tier)
- First request after sleep can take 30-60 seconds
- Consider upgrading to paid tier or using Railway (doesn't sleep)

## Cost Estimates

- **Vercel**: Free tier sufficient for frontend
- **Render Free Tier**: Sleeps after inactivity, 750 hours/month
- **Render Starter**: $7/month, doesn't sleep
- **Railway Hobby**: $5/month usage-based

## Next Steps

1. Choose a backend hosting provider (Render recommended)
2. Deploy the backend using steps above
3. Update `vercel.json` with the backend URL
4. Commit and push
5. Verify both frontend and backend work together

Need help with any step? Check the detailed guides:
- `DEPLOY_RENDER.md` - Full Render deployment guide
- Or ask for Railway/Fly.io specific instructions
