"""
Quick API test for the symptom classifier
"""

import requests
import json

BASE_URL = "http://localhost:8001"

def test_model_status():
    """Test if models are loaded"""
    print("\n" + "="*70)
    print("1. Testing Model Status")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/classifier/model-status")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_analyze_symptoms():
    """Test symptom analysis"""
    print("\n" + "="*70)
    print("2. Testing Symptom Analysis")
    print("="*70)
    
    test_cases = [
        "chest pain, short breath, dizziness",
        "headache, fever",
        "kurwadziwa moyo, kupfupika kufema",  # Shona
        "cough, wheezing",
    ]
    
    for symptoms in test_cases:
        print(f"\nTesting: {symptoms}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/classifier/analyze-symptoms",
                json={"symptoms": symptoms, "language": "Mixed"}
            )
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Severity: {data['severity']} ({data['confidence']['severity']:.1%})")
                    print(f"   Department: {data['department']} ({data['confidence']['department']:.1%})")
                    if data.get('recommended_service'):
                        print(f"   Service: {data['recommended_service']['name']}")
                except KeyError as ke:
                    print(f"   ERROR - Missing key: {ke}")
                    print(f"   Response: {response.text[:200]}")
            else:
                print(f"   ERROR: {response.text}")
        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()


def test_supported_languages():
    """Test supported languages endpoint"""
    print("\n" + "="*70)
    print("3. Testing Supported Languages")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/classifier/supported-languages")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_severity_levels():
    """Test severity levels endpoint"""
    print("\n" + "="*70)
    print("4. Testing Severity Levels")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/classifier/severity-levels")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print("Testing AI Symptom Classifier API")
    print("Make sure backend is running on http://localhost:8001\n")
    
    test_model_status()
    test_analyze_symptoms()
    test_supported_languages()
    test_severity_levels()
    
    print("\n" + "="*70)
    print("All API tests completed!")
    print("="*70)


if __name__ == "__main__":
    main()
