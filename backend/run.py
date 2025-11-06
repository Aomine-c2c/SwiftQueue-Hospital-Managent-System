import uvicorn
import sys
import os
import signal
import traceback

def run_backend():
    # Stay in the backend directory
    # Use PORT from environment variable or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print("=" * 70)
    print(f"Starting server on 0.0.0.0:{port}")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Database: {os.getenv('DATABASE_URL', 'sqlite:///./queue_management.db')}")
    print("=" * 70)
    
    try:
        uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False, access_log=True, log_level="info")
    except Exception as e:
        print("\n" + "=" * 70)
        print("ERROR: Failed to start server")
        print("=" * 70)
        print(f"Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    # Start backend serving both API and frontend
    try:
        print("\n" + "=" * 70)
        print("SwiftQueue Hospital Management System")
        print("Initializing backend server...")
        print("=" * 70 + "\n")
        
        # Verify Python version
        print(f"Python version: {sys.version}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        
        # Try importing main app to catch import errors early
        print("\nImporting FastAPI application...")
        from app.main import app
        print("✓ FastAPI application imported successfully")
        
        print("\nStarting Uvicorn server...")
        run_backend()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print("\n" + "=" * 70)
        print("FATAL ERROR: Could not start application")
        print("=" * 70)
        print(f"Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("=" * 70)
        sys.exit(1)
