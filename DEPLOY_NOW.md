# 🚀 Deploy Backend NOW - Railway Trial Expired

Your Railway trial expired, but you have **better FREE options**!

## ⭐ EASIEST: Render (5 Minutes, No Credit Card)

### Quick Deploy via Web UI:

1. **Go to**: https://render.com/
2. **Sign up** with GitHub (free, no card needed)
3. **Click**: "New +" → "Web Service"
4. **Connect GitHub**: Select `SwiftQueue-Hospital-Managent-System`
5. **Configure**:
   - **Name**: `swiftqueue-backend`
   - **Region**: Singapore (closest to you)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `Dockerfile`
   - **Instance Type**: `Free`
6. **Environment Variables** (click "Advanced"):
   ```
   SECRET_KEY=your-random-32-char-secret-key-here
   PORT=8000
   ```
7. **Click**: "Create Web Service"
8. **Wait**: 3-5 minutes
9. **Copy URL**: `https://swiftqueue-backend.onrender.com`

**Done!** ✅

---

## Alternative: Back4app (Always-On, No Cold Starts)

### Quick Deploy via Web UI:

1. **Go to**: https://www.back4app.com/
2. **Sign up** with GitHub
3. **Create Container App**
4. **Connect GitHub**: Your repo
5. **Configure**:
   - **Root**: `backend`
   - **Dockerfile**: `Dockerfile`
   - **Port**: `8000`
6. **Add ENV**:
   ```
   SECRET_KEY=your-secret-key
   ```
7. **Deploy**
8. **Get URL**: `https://swiftqueue-xxxxx.back4app.io`

---

## Next Steps After Deployment

### 1. Test Backend
```powershell
curl.exe https://your-backend-url/api/health
```

### 2. Update Frontend Config
Edit `vercel.json`:
```json
{
  "rewrites": [{
    "source": "/api/:path*",
    "destination": "https://your-backend-url/api/:path*"
  }]
}
```

### 3. Deploy Frontend
```powershell
vercel --prod
```

---

## 🎯 Which One to Choose?

| Feature | Render | Back4app |
|---------|--------|----------|
| **Free Tier** | 512MB | 256MB |
| **Always On** | ❌ No (sleeps) | ✅ Yes |
| **Setup Time** | 5 min | 5 min |
| **Best For** | Testing | Production |

**For hospital 24/7 system**: Use **Back4app** (always-on)
**For testing first**: Use **Render** (more RAM)

---

## Complete Guides

- **Render**: See `DEPLOY_RENDER.md`
- **Back4app**: See `DEPLOY_BACK4APP.md`
- **Comparison**: See `HOSTING_COMPARISON.md`

---

## 💡 Pro Tip

Deploy to **both**:
1. Test on Render first (more RAM, easier debugging)
2. Move to Back4app for production (always-on)

Both are free, no credit card needed! 🎉
