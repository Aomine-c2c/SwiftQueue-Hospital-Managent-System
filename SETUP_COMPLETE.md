# ✅ Setup Complete - Unified Dev Server

## 🎉 What's Working Now

Your development environment is now configured to run **both frontend and backend together** with a single command!

### Current Setup:
- ✅ **Backend (FastAPI)**: Running on `http://0.0.0.0:8001`
- ✅ **Frontend (Vite)**: Running on `http://localhost:5176/`
- ✅ **Network Access**: `http://10.200.8.155:5176/`
- ✅ **API Proxy**: All `/api/*` requests automatically forwarded to backend
- ✅ **CORS Fixed**: Development mode allows all origins
- ✅ **Auto Port Management**: Automatically kills processes blocking ports

---

## 🚀 Quick Start

### Single Command to Run Everything:
```powershell
npm run dev -- --host
```

This will:
1. Start the FastAPI backend on port 8001
2. Start the Vite frontend on port 5173 (or next available)
3. Enable network access (accessible from other devices on same WiFi)
4. Set up API proxy (no CORS issues!)

### Access URLs:
- **From your computer**: http://localhost:5176/
- **From phone/tablet (same WiFi)**: http://10.200.8.155:5176/
- **API Backend**: http://localhost:8001/docs (Swagger UI)

---

## 📱 Access from Different Devices

### Same Network (WiFi/LAN):
Just use the Network URL shown in the terminal: `http://10.200.8.155:5176/`

**Make sure devices are on the same WiFi network!**

### Different Network (Internet Access):

#### Option 1: ngrok (Easiest)
```powershell
# Install ngrok from https://ngrok.com/download
# Then run:
ngrok http 5176

# Share the https://xxx.ngrok-free.app URL with anyone!
```

#### Option 2: Cloudflare Tunnel (Free Forever)
```powershell
# Install from https://github.com/cloudflare/cloudflared/releases
cloudflared tunnel --url http://localhost:5176
```

#### Option 3: localtunnel
```powershell
npm install -g localtunnel
lt --port 5176
```

See `NETWORK_ACCESS_GUIDE.md` for detailed instructions.

---

## 🔧 Configuration Files Changed

### 1. `package.json`
- Added `concurrently` to run both servers
- New scripts:
  - `npm run dev` - Runs both backend and frontend together
  - `npm run dev:backend` - Backend only
  - `npm run dev:frontend` - Frontend only

### 2. `vite.config.ts`
- Added API proxy configuration (`/api` → `http://localhost:8001`)
- Enabled network access (`host: true`)
- Fixed port to 5173 (with auto-increment if busy)

### 3. `backend/app/middleware/cors_config.py`
- Development mode now allows all origins (`allow_origins: ["*"]`)
- Production still uses strict allowlist

### 4. `scripts/start-backend.ps1` (New)
- Auto-generates SECRET_KEY if not set
- Kills any process using port 8001 before starting
- Sets PYTHONPATH automatically

---

## 🛠️ Troubleshooting

### Backend won't start?
**Port already in use**: The script should auto-kill it, but if it fails:
```powershell
# Find process using port 8001
netstat -ano | Select-String ":8001"

# Kill it (replace PID with actual process ID)
taskkill /F /PID <PID>
```

### Can't access from phone on same WiFi?
**Windows Firewall blocking**: Run as Administrator:
```powershell
New-NetFirewallRule -DisplayName "Vite Dev" -Direction Inbound -LocalPort 5173-5180 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Backend API" -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow
```

### API calls failing?
The Vite proxy should handle this automatically. If issues persist:
1. Check backend is running: http://localhost:8001/docs
2. Check Vite proxy config in `vite.config.ts`
3. Open browser DevTools → Network tab to see exact error

---

## 📋 Commands Cheat Sheet

```powershell
# Start everything (recommended)
npm run dev -- --host

# Start backend only
npm run dev:backend

# Start frontend only  
npm run dev:frontend

# Build for production
npm run build

# Preview production build
npm run preview

# Install dependencies
npm install
```

---

## 🌐 Network URLs

When you run `npm run dev -- --host`, look for these lines:

```
[FRONTEND]   ➜  Local:   http://localhost:5176/
[FRONTEND]   ➜  Network: http://10.200.8.155:5176/
[BACKEND] INFO:     Uvicorn running on http://0.0.0.0:8001
```

- **Local URL**: Use on your development machine
- **Network URL**: Share with devices on same WiFi
- **Backend**: API documentation and testing

---

## 🔐 Environment Variables

The setup auto-generates necessary variables, but you can customize in `.env`:

```env
# Backend
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
DATABASE_URL=sqlite:///./queue_management.db

# Frontend (optional)
VITE_API_URL=http://localhost:8001

# AI Services (optional)
OPENROUTER_API_KEY=your-key
OLLAMA_BASE_URL=http://localhost:11434
```

---

## ✨ What You Can Do Now

1. **Develop locally**: Just run `npm run dev -- --host`
2. **Test on phone**: Use the Network URL on any device on same WiFi
3. **Share with remote users**: Use ngrok/cloudflare tunnel
4. **No CORS issues**: Everything proxied through Vite
5. **Hot reload**: Both frontend and backend auto-reload on changes

---

## 📚 Additional Documentation

- `NETWORK_ACCESS_GUIDE.md` - Detailed network access setup
- `README.md` - Project overview
- `API.md` - API documentation
- Backend API docs: http://localhost:8001/docs

---

## 🎯 Next Steps

1. **Test the app**: Open http://localhost:5176/ in your browser
2. **Test on phone**: Connect phone to same WiFi, use Network URL
3. **Develop features**: Both servers auto-reload on code changes
4. **Deploy**: Run `npm run build` when ready for production

---

**Everything is ready! Just run `npm run dev -- --host` and start building! 🚀**
