"""
Test the Symptom Classifier
Quick test script to verify the classifier works correctly
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.symptom_classifier import SymptomClassifier


def test_classifier():
    print("🧪 Testing Symptom Classifier\n")
    
    classifier = SymptomClassifier()
    
    # Try to load models
    try:
        classifier.load_models()
        print("✅ Models loaded successfully\n")
    except FileNotFoundError:
        print("❌ Models not found. Please train models first:")
        print("   Run: python backend/train_classifier.py\n")
        return
    
    # Test cases
    test_cases = [
        {
            "symptoms": "chest pain, short breath, dizziness",
            "expected_severity": "Critical/High",
            "expected_department": "Emergency/Cardiology"
        },
        {
            "symptoms": "headache, fever",
            "expected_severity": "Moderate/High",
            "expected_department": "General Practitioner"
        },
        {
            "symptoms": "kurwadziwa moyo, kupfupika kufema",  # Shona: heart pain, shortness of breath
            "expected_severity": "Critical",
            "expected_department": "Emergency/Cardiology"
        },
        {
            "symptoms": "cough, wheezing",
            "expected_severity": "Moderate/Critical",
            "expected_department": "Emergency/Pulmonology"
        },
        {
            "symptoms": "blurred vision, eye pain",
            "expected_severity": "Moderate/High",
            "expected_department": "Neurology/Ophthalmology"
        }
    ]
    
    print("=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test['symptoms']}")
        print(f"   Expected: {test['expected_severity']} → {test['expected_department']}")
        
        result = classifier.predict(test['symptoms'])
        
        print(f"   Predicted: {result['severity']} → {result['department']}")
        print(f"   Confidence: Severity {result['confidence']['severity']:.1%}, "
              f"Department {result['confidence']['department']:.1%}")
        
        # Show top 3 severity predictions
        severity_scores = sorted(
            result['all_severity_scores'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        print(f"   Top Severities: {', '.join([f'{s}({p:.1%})' for s, p in severity_scores])}")
        
        # Show top 3 department predictions
        dept_scores = sorted(
            result['all_department_scores'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        print(f"   Top Departments: {', '.join([f'{d}({p:.1%})' for d, p in dept_scores])}")
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)


if __name__ == "__main__":
    test_classifier()
