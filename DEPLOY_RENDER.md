Render deployment guide — SwiftQueue Hospital Management System

This document shows the simplest, reproducible steps to deploy the backend to Render using a Docker container (recommended), and then how to connect the frontend on Vercel to that backend.

Why use Render
- Render supports full Docker deployments and long-running services (good for FastAPI + DB + websockets).
- You can connect your GitHub repo and enable automatic deploys on each push to a branch.

Prerequisites (local)
- You must have a Render account and GitHub linked to Render.
- You must have pushed your changes to GitHub (already done).
- Ensure you have the repository URL and branch (e.g. main).

Option A — Deploy via Render Web UI (recommended)
1. Open https://dashboard.render.com and log in.
2. Click "New+" → "Web Service".
3. Select "Connect a repository" → choose the GitHub repo: SwiftQueue-Hospital-Managent-System.
4. Configure the service:
   - Name: swiftqueue-backend (or any name)
   - Branch: main
   - Environment: Docker (since the repo contains `backend/Dockerfile.prod`)
   - Docker Build Context / Dockerfile Path: `backend/Dockerfile.prod` (or point to the backend folder)
   - Plan: Free / Starter / Standard (choose as appropriate)
   - Health check path: `/api/health` (optional)
5. Environment variables (add these under "Environment" after creation or in the creation form):
   - SECRET_KEY = <a generated secure 32+ byte hex value>
   - DATABASE_URL = postgres://<user>:<pass>@<host>:<port>/<db>
   - Any other env vars your app needs (SMTP, SENTRY_DSN, REDIS_URL, etc.)
6. Create the service — Render will build the Docker image using your `Dockerfile.prod`.
7. When the build finishes, Render provides a public URL (https://swiftqueue-backend.onrender.com). Test:
   - https://<service-url>/api/health

Option B — Deploy via Render CLI (local)
Note: I cannot run these steps from this environment because I don't have your Render credentials. Run these locally instead.

1. Install Render CLI (if not installed)
   - Linux / macOS: `curl -fsSL https://cdn.render.com/cli/install.sh | bash`
   - Or see Render docs: https://render.com/docs/cli

2. Login from your terminal
```powershell
render login
```
This opens a browser to authorize the CLI.

3. Create a new web service from the repo (example using interactive flow)
```powershell
render services create
# follow prompts: choose "Web Service", select repo, branch, environment Docker, Dockerfile path 'backend/Dockerfile.prod'
```

4. Set environment variables in the Render dashboard for the service, or via CLI using `render service update` commands (see docs).

Notes about Dockerfile
- The repo contains `backend/Dockerfile.prod` which is production-ready and installs system deps, creates a venv and runs `python run.py`.
- Render will use the Dockerfile to build the service.

Connecting Vercel frontend to Render backend
1. On Vercel, set an environment variable `BACKEND_URL` to the public URL of the Render service (no trailing slash), e.g. `https://swiftqueue-backend.onrender.com`.
2. In `vercel.json` you can leave the rewrite from `/api/(.*)` to `${BACKEND_URL}/api/$1`, or add a rewrite in the Vercel dashboard (Project → Settings → Rewrites).
3. Redeploy the Vercel project; the frontend will proxy API calls to Render.

Troubleshooting
- If the Docker build fails on Render, check build logs for missing system libs or failing pip installs. `backend/Dockerfile.prod` already installs common libs (libpq-dev, build-essential).
- If the service starts but `/api/health` returns 500, check Render service logs and environment variables (especially `SECRET_KEY` and `DATABASE_URL`).

Security notes
- Don't store production secrets in the repo. Use Render environment variables and Render secrets.
- Use a managed Postgres instance (Render, ElephantSQL, Supabase) and set `DATABASE_URL` accordingly.

If you'd like I can:
- Create a `render.yaml` spec (example) in the repo for IaC — you can validate it with Render docs before applying.
- Walk you through the CLI `render services create` interactive prompts while you run `render login` locally.

If you want the `render.yaml` example now, tell me and I will add it to the repo as `render.yaml`.
