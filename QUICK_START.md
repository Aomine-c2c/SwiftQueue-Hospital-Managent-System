# 🚀 Quick Start Guide - Network Access Fixed

## ✅ Current Status

Both servers are now running:
- **Frontend (Vite)**: http://10.200.8.155:5173/
- **Backend (FastAPI)**: http://10.200.8.155:8001/

## 🔥 Fix Windows Firewall (One-time Setup)

**To access from your phone or other devices, you need to allow Windows Firewall:**

### Option 1: Run PowerShell Script (Recommended)
1. Right-click **PowerShell** and select **"Run as Administrator"**
2. Navigate to project folder:
   ```powershell
   cd "C:\Users\armut\Documents\GitHub\1.1"
   ```
3. Run the firewall script:
   ```powershell
   .\scripts\add-firewall-rules.ps1
   ```

### Option 2: Manual Command (Run as Admin)
```powershell
# Allow Vite dev server
New-NetFirewallRule -DisplayName "Vite Dev Server" -Direction Inbound -LocalPort 5173-5180 -Protocol TCP -Action Allow

# Allow FastAPI backend
New-NetFirewallRule -DisplayName "FastAPI Backend" -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow
```

### Option 3: Windows Defender Firewall GUI
1. Open **Windows Defender Firewall with Advanced Security**
2. Click **Inbound Rules** → **New Rule**
3. Choose **Port** → **Next**
4. Choose **TCP** → Enter **5173-5180** → **Next**
5. Choose **Allow the connection** → **Next**
6. Check all profiles → **Next**
7. Name: **Vite Dev Server** → **Finish**
8. Repeat for port **8001** (name it **FastAPI Backend**)

## 📱 Access from Phone/Tablet

### Same WiFi Network:
1. Make sure your phone is connected to **the same WiFi** as your computer
2. Open browser on phone and go to:
   ```
   http://10.200.8.155:5173/
   ```

### Different Network (Internet):
Use **ngrok** (free):
```powershell
# Download from https://ngrok.com/download
ngrok http 5173

# You'll get a URL like: https://abc123.ngrok-free.app
```

## 🛠️ Starting Dev Servers

### Method 1: Both Together (Recommended)
Open **TWO PowerShell windows**:

**Window 1 - Backend:**
```powershell
cd "C:\Users\armut\Documents\GitHub\1.1"
npm run dev:backend
```

**Window 2 - Frontend:**
```powershell
cd "C:\Users\armut\Documents\GitHub\1.1"
npx vite --host
```

### Method 2: Using npm scripts
```powershell
# This should work but may have issues with concurrently
npm run dev
```

## 🔍 Troubleshooting

### "Unable to connect" error on phone?

**1. Check both devices are on same WiFi**
```powershell
# On your PC, verify your IP:
ipconfig | Select-String "IPv4"

# Make sure it matches 10.200.8.155
```

**2. Check firewall rules exist:**
```powershell
Get-NetFirewallRule -DisplayName "*Vite*" | Format-Table DisplayName,Enabled,Direction
Get-NetFirewallRule -DisplayName "*FastAPI*" | Format-Table DisplayName,Enabled,Direction
```

**3. Check servers are running:**
```powershell
Get-NetTCPConnection -LocalPort 5173,8001 -ErrorAction SilentlyContinue | Select-Object LocalPort,State
```

**4. Test from PC first:**
- Open http://localhost:5173/ on your PC
- If that works, the issue is network/firewall

### Port already in use?

**Kill existing processes:**
```powershell
# Find what's using the port
Get-NetTCPConnection -LocalPort 5173 | Select-Object OwningProcess

# Kill it (replace PID)
taskkill /F /PID <process_id>
```

### Backend not responding?

**Check backend logs:**
- Look at the backend PowerShell window for errors
- Visit http://localhost:8001/docs to test directly

## 📊 Access URLs Summary

| Device | Frontend URL | Backend API |
|--------|-------------|-------------|
| Your PC | http://localhost:5173/ | http://localhost:8001/docs |
| Phone/Tablet (same WiFi) | http://10.200.8.155:5173/ | http://10.200.8.155:8001/docs |
| Any device (with ngrok) | https://xxx.ngrok-free.app | Proxied via frontend |

## ✨ What's Working

- ✅ Backend running on port 8001
- ✅ Frontend running on port 5173
- ✅ Network binding enabled (`--host`)
- ✅ API proxy configured (no CORS issues)
- ✅ Auto-reload on code changes
- ⚠️ **Firewall rules need to be added (see above)**

## 🎯 Next Steps

1. **Add firewall rules** (see Option 1, 2, or 3 above)
2. **Test on your PC**: http://localhost:5173/
3. **Test on your phone**: http://10.200.8.155:5173/
4. **Start building!**

---

**The servers are running! Just add the firewall rules and you're good to go! 🚀**
