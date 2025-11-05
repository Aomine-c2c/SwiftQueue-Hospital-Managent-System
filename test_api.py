"""Test call-next endpoint"""
import requests
import json

url = "http://localhost:8001/api/queue/call-next"
data = {
    "service_id": 1,
    "counter_name": "Test Counter"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
