# Network Access Setup Guide

This guide explains how to access your development server from different devices and networks.

## Quick Start (Same Network)

### 1. Start the development server:
```powershell
npm run dev -- --host
```

This will start both:
- **Backend (FastAPI)**: http://0.0.0.0:8001
- **Frontend (Vite)**: http://0.0.0.0:5173

### 2. Find your local IP address:
```powershell
# On Windows PowerShell
ipconfig | Select-String "IPv4"

# Look for your local IP (e.g., 192.168.1.100 or 10.200.8.155)
```

### 3. Access from another device on the same network:
Open your browser on the other device and navigate to:
```
http://YOUR_LOCAL_IP:5173
```
Example: `http://192.168.1.100:5173`

### 4. Allow through Windows Firewall (if needed):
```powershell
# Run as Administrator
New-NetFirewallRule -DisplayName "Vite Dev Server" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "FastAPI Backend" -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow
```

---

## Access from Different Network (Internet)

For accessing from a completely different network (e.g., mobile data, friend's WiFi), you need a tunneling service.

### Option 1: Using ngrok (Recommended)

#### Install ngrok:
1. Download from: https://ngrok.com/download
2. Extract and add to PATH or place in project folder
3. Sign up for free account at https://dashboard.ngrok.com/
4. Get your auth token and configure:
```powershell
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

#### Start your dev server:
```powershell
npm run dev -- --host
```

#### In a new terminal, create tunnel:
```powershell
# Tunnel frontend (main access point)
ngrok http 5173

# You'll get a URL like: https://abc123.ngrok-free.app
```

#### Share the ngrok URL:
Anyone with the URL can access your app from anywhere in the world!

**Note**: The free ngrok tier gives you a random URL that changes each session. Paid tiers offer permanent URLs.

### Option 2: Using Cloudflare Tunnel (Free, Permanent URLs)

#### Install cloudflared:
```powershell
# Download from: https://github.com/cloudflare/cloudflared/releases
# Or use winget:
winget install cloudflare.cloudflared
```

#### Start tunnel:
```powershell
# Start your dev server first
npm run dev -- --host

# In new terminal
cloudflared tunnel --url http://localhost:5173
```

### Option 3: Using localtunnel

#### Install:
```powershell
npm install -g localtunnel
```

#### Start tunnel:
```powershell
# Start your dev server first
npm run dev -- --host

# In new terminal
lt --port 5173 --subdomain myapp
# Access at: https://myapp.loca.lt
```

---

## How It Works

### Architecture:
```
┌─────────────────────────────────────────┐
│   Your Device (Developer Machine)       │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │────│   Backend    │  │
│  │  Vite :5173  │    │ FastAPI:8001 │  │
│  └──────────────┘    └──────────────┘  │
│         │                                │
│         │ Vite proxies /api → :8001     │
└─────────┼────────────────────────────────┘
          │
          ├─ Same Network: http://LOCAL_IP:5173
          │
          └─ Different Network: ngrok/cloudflare tunnel
```

### Why Vite Proxy?
The Vite proxy configuration in `vite.config.ts` forwards all `/api/*` requests from the frontend to the backend. This means:
- No CORS issues (same origin from browser perspective)
- Simple setup - just access the Vite URL
- All API calls automatically routed to backend

---

## Troubleshooting

### Can't connect from other device on same network?

**Check Windows Firewall:**
```powershell
# List firewall rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Vite*" -or $_.DisplayName -like "*FastAPI*"}

# Add rules if missing (run as Admin)
New-NetFirewallRule -DisplayName "Vite Dev Server" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "FastAPI Backend" -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow
```

**Check your IP is correct:**
```powershell
# Get all network adapters
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*"}
```

**Make sure both devices are on same network:**
- Both should be connected to the same WiFi/router
- Check router admin panel to see connected devices

### Backend not starting?

**Missing SECRET_KEY:**
The script auto-generates it, but you can set it manually:
```powershell
$env:SECRET_KEY = "your-secret-key-here"
npm run dev
```

**Port already in use:**
```powershell
# Find what's using port 8001
netstat -ano | findstr :8001

# Kill the process (replace PID)
taskkill /F /PID <process_id>
```

### Ngrok "Too many connections" error?

The free tier has connection limits. Solutions:
- Upgrade to paid plan
- Use Cloudflare Tunnel (unlimited)
- Use localtunnel

---

## Production Deployment

For production, use proper hosting:
- **Frontend**: Vercel, Netlify, Cloudflare Pages
- **Backend**: Railway, Render, AWS, Azure, Google Cloud
- **Database**: Use PostgreSQL instead of SQLite

The `npm run build` command creates production-ready files in `dist/`.

---

## Environment Variables

Create a `.env` file in the project root:
```env
# Backend
SECRET_KEY=your-production-secret-key-here
ENVIRONMENT=development
DATABASE_URL=sqlite:///./queue_management.db

# Frontend
VITE_API_URL=http://localhost:8001

# Optional: AI integrations
OPENROUTER_API_KEY=your-key-here
OLLAMA_BASE_URL=http://localhost:11434
```

For different networks (ngrok/cloudflare), update `VITE_API_URL` to your tunnel URL if needed.

---

## Summary of Commands

```powershell
# Local development (same network)
npm run dev -- --host

# Different network with ngrok
npm run dev -- --host
# (in new terminal) ngrok http 5173

# Different network with cloudflare
npm run dev -- --host
# (in new terminal) cloudflared tunnel --url http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview
```
