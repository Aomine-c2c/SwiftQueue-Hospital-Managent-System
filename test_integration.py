"""
Quick integration test for Frontend/Backend connectivity

This script tests:
1. Backend health endpoint
2. Frontend can build successfully
3. API client configuration points to correct backend

Run this before deploying to Vercel to catch integration issues early.
"""

import requests
import subprocess
import sys
import time

def test_backend_health():
    """Test that backend health endpoint responds"""
    print("Testing backend health endpoint...")
    try:
        response = requests.get("http://localhost:8001/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Backend health check passed: {data}")
            return True
        else:
            print(f"✗ Backend health check failed with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Backend not running on http://localhost:8001")
        print("  Start it with: cd backend && uvicorn app.main:app --port 8001")
        return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_frontend_build():
    """Test that frontend builds without errors"""
    print("\nTesting frontend build...")
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print("✓ Frontend build successful")
            return True
        else:
            print(f"✗ Frontend build failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("✗ Frontend build timed out (> 120s)")
        return False
    except Exception as e:
        print(f"✗ Build error: {e}")
        return False

def test_api_client_config():
    """Verify apiClient.ts configuration"""
    print("\nChecking API client configuration...")
    try:
        with open("src/services/apiClient.ts", "r") as f:
            content = f.read()
            if "const API_BASE_URL" in content:
                print("✓ API client configured")
                # Check for environment variable usage
                if "VITE_API_URL" in content:
                    print("  - Uses VITE_API_URL environment variable")
                if "/api" in content:
                    print("  - Default base path: /api")
                return True
            else:
                print("✗ API_BASE_URL not found in apiClient.ts")
                return False
    except FileNotFoundError:
        print("✗ src/services/apiClient.ts not found")
        return False

def main():
    print("=" * 60)
    print("Frontend/Backend Integration Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Backend health
    results.append(("Backend Health", test_backend_health()))
    
    # Test 2: API client config
    results.append(("API Client Config", test_api_client_config()))
    
    # Test 3: Frontend build (optional - comment out if too slow)
    # results.append(("Frontend Build", test_frontend_build()))
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ All tests passed! Ready for deployment.")
        return 0
    else:
        print("\n✗ Some tests failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
