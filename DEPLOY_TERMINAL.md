# ONE-COMMAND DEPLOYMENT GUIDE
# Deploy SwiftQueue backend from terminal

## 🚀 Easiest Method: Railway (Already Set Up!)

You're already logged in to Railway! Just run:

```powershell
cd C:\Users\armut\Documents\GitHub\1.1
.\deploy-railway.ps1
```

This script will:
1. ✅ Commit your changes
2. ✅ Push to GitHub
3. ✅ Deploy to Railway
4. ✅ Get your backend URL
5. ✅ Test the deployment

---

## 📱 Alternative: Deploy via Railway Dashboard

Your Railway project is already created:
**URL**: https://railway.com/project/56f61e8f-aea9-4ae5-8248-a6f53fdc56fd

### Quick Steps:
1. **Visit the URL above** (already opened in browser)
2. Click **"+ New"** → **"GitHub Repo"**
3. Select: `SwiftQueue-Hospital-Managent-System`
4. **Root Directory**: Type `backend`
5. Click **"Deploy"**
6. Wait 2-3 minutes
7. Click **"Settings"** → **"Networking"** → **"Generate Domain"**
8. Copy your URL (e.g., `swiftqueue-backend-production.up.railway.app`)

### Set Environment Variables:
1. Go to **"Variables"** tab
2. Add:
   ```
   SECRET_KEY=your-secret-key-min-32-chars-long
   ENVIRONMENT=production
   PORT=8000
   ```

---

## 🎯 After Deployment

### 1. Get Your Backend URL
Railway will give you something like:
```
https://swiftqueue-backend-production.up.railway.app
```

### 2. Update Vercel Config
Edit `vercel.json`:
```json
{
  "rewrites": [{
    "source": "/api/:path*",
    "destination": "https://swiftqueue-backend-production.up.railway.app/api/:path*"
  }]
}
```

### 3. Deploy Frontend
```powershell
vercel --prod
```

### 4. Test Everything
```powershell
# Test backend
curl.exe https://swiftqueue-backend-production.up.railway.app/api/health

# Visit frontend
# https://your-vercel-url
```

---

## 🔧 Railway CLI Commands

### Check Status
```powershell
railway status
```

### View Logs
```powershell
railway logs
```

### Set Environment Variable
```powershell
railway variables
```

### Redeploy
```powershell
cd backend
railway up
```

### Open Dashboard
```powershell
railway open
```

---

## ⚡ Super Fast Deployment

**Option 1 - Automated Script**:
```powershell
.\deploy-railway.ps1
```

**Option 2 - Manual Command**:
```powershell
cd backend
railway up
```

**Option 3 - GitHub Auto-Deploy**:
1. Connect Railway to GitHub (in dashboard)
2. Just push: `git push origin main`
3. Railway auto-deploys!

---

## 💰 Railway Pricing

- **$5 Free Credit/Month**
- Usage-based pricing
- Typically $5-10/month for small apps
- Always-on (no cold starts)
- Includes PostgreSQL if needed

---

## 🐛 Troubleshooting

### Deployment Fails
```powershell
railway logs
```
Check the error and fix in code

### Need to Redeploy
```powershell
cd backend
railway up
```

### Want to Use GitHub Auto-Deploy
1. Dashboard → Settings
2. Connect GitHub Repository
3. Select branch: `main`
4. Root directory: `backend`
5. Enable: "Auto-deploy on push"

---

## 🎉 You're Set!

Railway is now configured! Choose your deployment method:

1. **Quick**: Run `.\deploy-railway.ps1`
2. **Manual**: Visit Railway dashboard
3. **Auto**: Connect GitHub for auto-deploy

Your backend will be live in 2-3 minutes! 🚀
