import uvicorn
import sys
import os
import signal

def run_backend():
    # Stay in the backend directory
    # Use PORT from environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False, access_log=False)

if __name__ == "__main__":
    # Start backend serving both API and frontend
    try:
        run_backend()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
