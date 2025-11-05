# 🚀 Backend Deployment - Quick Start

Choose your backend hosting platform:

---

## ⭐ Option 1: Back4app (RECOMMENDED)

**Why?** Always-on free tier, no cold starts, perfect for 24/7 hospital system

### Quick Deploy (5 minutes):

1. **Sign up**: https://www.back4app.com/
2. **Create Container App**
3. **Connect GitHub**: `Armutimbire223373Q/SwiftQueue-Hospital-Managent-System`
4. **Configure**:
   - Dockerfile: `backend/Dockerfile.prod`
   - Port: `8000`
   - ENV: `SECRET_KEY=your-secret-key`
5. **Deploy** → Get URL: `https://swiftqueue-backend-xxxxx.back4app.io`

**Full Guide**: See `DEPLOY_BACK4APP.md`

---

## Option 2: Render

**Why?** Well-known platform, 512MB RAM free tier (but sleeps after 15 min)

### Quick Deploy (10 minutes):

1. **Sign up**: https://render.com/
2. **Create Web Service**
3. **Connect GitHub**: Your repository
4. **Configure**:
   - Environment: Docker
   - Dockerfile: `backend/Dockerfile.prod`
   - ENV: `SECRET_KEY=your-secret-key`
5. **Deploy** → Get URL: `https://swiftqueue-api.onrender.com`

**Full Guide**: See `DEPLOY_RENDER.md`

---

## Comparison at a Glance

| Feature | Back4app | Render |
|---------|----------|--------|
| **Free Tier** | ✅ 256MB | ✅ 512MB |
| **Always-On** | ✅ Yes | ❌ No (sleeps) |
| **Cold Starts** | ❌ None | ✅ 30-60s |
| **Best For** | Production | Testing |
| **Cost (Hobby)** | $5/month | $7/month |

**Verdict**: Use **Back4app** for hospital system (needs 24/7 availability) 🏆

---

## After Deployment

### Update Vercel Config

Edit `vercel.json`:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://YOUR-BACKEND-URL/api/:path*"
    }
  ]
}
```

Replace `YOUR-BACKEND-URL` with:
- Back4app: `swiftqueue-backend-xxxxx.back4app.io`
- Render: `swiftqueue-api.onrender.com`

### Redeploy Frontend

```powershell
vercel --prod
```

---

## Test Production

```powershell
# Test backend
curl.exe https://your-backend-url/api/health

# Visit frontend
# https://your-vercel-url

# Test integration
# Login, create queue, verify API calls work
```

---

## 📚 Full Documentation

- **Back4app Guide**: `DEPLOY_BACK4APP.md` ⭐
- **Render Guide**: `DEPLOY_RENDER.md`
- **Comparison**: `HOSTING_COMPARISON.md`
- **Testing First**: `START_TESTING_HERE.md`

---

## 🎯 Recommended Flow

```
1. Test Locally First
   ↓
   Run: .\RUN_COMPREHENSIVE_TESTS.ps1

2. Deploy Backend to Back4app
   ↓
   Follow: DEPLOY_BACK4APP.md (5 minutes)

3. Update Vercel Config
   ↓
   Edit: vercel.json with Back4app URL

4. Deploy Frontend to Vercel
   ↓
   Run: vercel --prod

5. Test Production
   ↓
   Visit your Vercel URL and test everything!
```

---

**Total Time**: ~15 minutes to full production deployment! 🚀
