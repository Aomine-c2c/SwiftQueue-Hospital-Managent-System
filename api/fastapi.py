import os
import sys

# Ensure repo root is on path so app imports resolve
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Expose the existing FastAPI app from backend
from backend.app.main import app

# Vercel expects a WSGI/ASGI object named `app`
# This file acts as a thin wrapper to expose the app


# Optional: set default env vars if not present (useful for Vercel preview)
os.environ.setdefault("ENVIRONMENT", "production")

# If you need to set SECRET_KEY for preview builds, set in Vercel env vars
