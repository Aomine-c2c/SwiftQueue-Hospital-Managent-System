import requests
import json

# Test 1: Model Status
print("Testing Model Status...")
try:
    r = requests.get("http://localhost:8001/api/classifier/model-status", timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}\n")
except Exception as e:
    print(f"Error: {e}\n")

# Test 2: Analyze Symptoms
print("Testing Symptom Analysis...")
try:
    r = requests.post(
        "http://localhost:8001/api/classifier/analyze-symptoms",
        json={"symptoms": "chest pain, fever"},
        timeout=5
    )
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"Severity: {data['severity']}")
        print(f"Department: {data['department']}")
        print(f"Confidence: {data['confidence']}")
    else:
        print(f"Error: {r.text}")
except Exception as e:
    print(f"Error: {e}")
