"""
Train Symptom Classifier Models
Run this script to train the Naive Bayes classifiers on the symptom dataset
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.symptom_classifier import SymptomClassifier


def main():
    print("=" * 70)
    print("🏥 SWIFTQUEUE SYMPTOM CLASSIFIER TRAINING")
    print("=" * 70)
    print()
    
    # Path to dataset
    dataset_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'dataset', 
        'swiftqueue_symptom_training_5000(1).csv'
    )
    
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found at: {dataset_path}")
        print("Please ensure the dataset file exists.")
        return 1
    
    print(f"📂 Dataset: {dataset_path}")
    print(f"📊 Loading and training models...\n")
    
    # Initialize classifier and train
    classifier = SymptomClassifier()
    
    try:
        results = classifier.train_models(dataset_path)
        
        print("\n" + "=" * 70)
        print("✅ TRAINING COMPLETE")
        print("=" * 70)
        print(f"📈 Total Samples: {results['total_samples']}")
        print(f"🎯 Severity Accuracy: {results['severity_accuracy']:.2%}")
        print(f"🏥 Department Accuracy: {results['department_accuracy']:.2%}")
        print()
        print(f"📋 Severity Classes: {', '.join(results['severity_classes'])}")
        print(f"🏢 Department Classes: {', '.join(results['department_classes'])}")
        print("=" * 70)
        
        # Test predictions
        print("\n" + "=" * 70)
        print("🧪 SAMPLE PREDICTIONS")
        print("=" * 70)
        
        test_cases = [
            "chest pain, short breath, dizziness",
            "headache, fever",
            "abdominal pain, bloating, nausea",
            "kurwadziwa moyo, kupfupika kufema",  # Shona
            "cough, wheezing",
            "blurred vision, eye pain",
            "joint pain, back pain",
            "fatigue, weakness"
        ]
        
        for i, symptoms in enumerate(test_cases, 1):
            result = classifier.predict(symptoms)
            print(f"\n{i}. Symptoms: {symptoms}")
            print(f"   ├─ Severity: {result['severity']} "
                  f"(confidence: {result['confidence']['severity']:.1%})")
            print(f"   └─ Department: {result['department']} "
                  f"(confidence: {result['confidence']['department']:.1%})")
        
        print("\n" + "=" * 70)
        print("✅ Models trained and ready for use!")
        print("=" * 70)
        print("\n📌 Next steps:")
        print("   1. Start the backend API server")
        print("   2. Use POST /api/ai/analyze-symptoms to analyze symptoms")
        print("   3. Check GET /api/ai/model-status to verify models are loaded")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
