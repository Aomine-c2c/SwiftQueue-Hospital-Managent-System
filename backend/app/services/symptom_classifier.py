"""
Symptom Classifier Service
Uses Naive Bayes classifier to predict severity and department from symptoms
Trained on swiftqueue_symptom_training_5000.csv dataset
"""

import pandas as pd
import pickle
import os
from typing import Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline


class SymptomClassifier:
    def __init__(self):
        self.severity_model = None
        self.department_model = None
        self.model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
        os.makedirs(self.model_path, exist_ok=True)
        
    def train_models(self, dataset_path: str) -> Dict[str, float]:
        """
        Train both severity and department classifiers
        
        Args:
            dataset_path: Path to the CSV training dataset
            
        Returns:
            Dictionary with accuracy scores
        """
        print("Loading dataset...")
        df = pd.read_csv(dataset_path)
        
        # Preprocess keywords (convert to lowercase)
        df['keywords'] = df['keywords'].str.lower()
        
        # Split data
        X = df['keywords']
        y_severity = df['severity']
        y_department = df['department']
        
        print(f"Dataset loaded: {len(df)} samples")
        print(f"Severity classes: {y_severity.unique()}")
        print(f"Department classes: {y_department.unique()}")
        
        # Train Severity Model
        print("\n=== Training Severity Classifier ===")
        self.severity_model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),  # Use unigrams and bigrams
                lowercase=True,
                strip_accents='unicode'
            )),
            ('clf', MultinomialNB(alpha=0.1))
        ])
        
        X_train_sev, X_test_sev, y_train_sev, y_test_sev = train_test_split(
            X, y_severity, test_size=0.2, random_state=42, stratify=y_severity
        )
        
        self.severity_model.fit(X_train_sev, y_train_sev)
        y_pred_sev = self.severity_model.predict(X_test_sev)
        severity_accuracy = accuracy_score(y_test_sev, y_pred_sev)
        
        print(f"Severity Model Accuracy: {severity_accuracy:.2%}")
        print("\nSeverity Classification Report:")
        print(classification_report(y_test_sev, y_pred_sev))
        
        # Train Department Model
        print("\n=== Training Department Classifier ===")
        self.department_model = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                lowercase=True,
                strip_accents='unicode'
            )),
            ('clf', MultinomialNB(alpha=0.1))
        ])
        
        X_train_dep, X_test_dep, y_train_dep, y_test_dep = train_test_split(
            X, y_department, test_size=0.2, random_state=42, stratify=y_department
        )
        
        self.department_model.fit(X_train_dep, y_train_dep)
        y_pred_dep = self.department_model.predict(X_test_dep)
        department_accuracy = accuracy_score(y_test_dep, y_pred_dep)
        
        print(f"Department Model Accuracy: {department_accuracy:.2%}")
        print("\nDepartment Classification Report:")
        print(classification_report(y_test_dep, y_pred_dep))
        
        # Save models
        self._save_models()
        
        return {
            'severity_accuracy': severity_accuracy,
            'department_accuracy': department_accuracy,
            'total_samples': len(df),
            'severity_classes': list(y_severity.unique()),
            'department_classes': list(y_department.unique())
        }
    
    def _save_models(self):
        """Save trained models to disk"""
        severity_path = os.path.join(self.model_path, 'severity_classifier.pkl')
        department_path = os.path.join(self.model_path, 'department_classifier.pkl')
        
        with open(severity_path, 'wb') as f:
            pickle.dump(self.severity_model, f)
        
        with open(department_path, 'wb') as f:
            pickle.dump(self.department_model, f)
        
        print(f"\nModels saved to {self.model_path}")
    
    def load_models(self):
        """Load pre-trained models from disk"""
        severity_path = os.path.join(self.model_path, 'severity_classifier.pkl')
        department_path = os.path.join(self.model_path, 'department_classifier.pkl')
        
        if not os.path.exists(severity_path) or not os.path.exists(department_path):
            raise FileNotFoundError(
                "Models not found. Please train models first using train_models()"
            )
        
        with open(severity_path, 'rb') as f:
            self.severity_model = pickle.load(f)
        
        with open(department_path, 'rb') as f:
            self.department_model = pickle.load(f)
        
        # Simple print without emoji for compatibility
        print("Models loaded successfully")
    
    def predict(self, symptoms: str) -> Dict[str, any]:
        """
        Predict severity and department from symptoms
        
        Args:
            symptoms: Comma-separated symptoms (e.g., "chest pain, fever")
            
        Returns:
            Dictionary with predictions and confidence scores
        """
        if self.severity_model is None or self.department_model is None:
            try:
                self.load_models()
            except FileNotFoundError:
                return {
                    'error': 'Models not trained. Please train models first.',
                    'severity': 'Moderate',
                    'department': 'General Practitioner',
                    'confidence': {'severity': 0.0, 'department': 0.0}
                }
        
        # Preprocess input
        symptoms_lower = symptoms.lower()
        
        # Predict severity
        severity_pred = self.severity_model.predict([symptoms_lower])[0]
        severity_proba = self.severity_model.predict_proba([symptoms_lower])[0]
        severity_confidence = max(severity_proba)
        
        # Predict department
        department_pred = self.department_model.predict([symptoms_lower])[0]
        department_proba = self.department_model.predict_proba([symptoms_lower])[0]
        department_confidence = max(department_proba)
        
        # Get all severity probabilities
        severity_classes = self.severity_model.classes_
        severity_scores = {
            cls: float(prob) 
            for cls, prob in zip(severity_classes, severity_proba)
        }
        
        # Get all department probabilities
        department_classes = self.department_model.classes_
        department_scores = {
            cls: float(prob) 
            for cls, prob in zip(department_classes, department_proba)
        }
        
        return {
            'severity': severity_pred,
            'department': department_pred,
            'confidence': {
                'severity': float(severity_confidence),
                'department': float(department_confidence)
            },
            'all_severity_scores': severity_scores,
            'all_department_scores': department_scores,
            'symptoms_analyzed': symptoms
        }
    
    def predict_batch(self, symptoms_list: list) -> list:
        """
        Predict for multiple symptom inputs
        
        Args:
            symptoms_list: List of symptom strings
            
        Returns:
            List of prediction dictionaries
        """
        return [self.predict(symptoms) for symptoms in symptoms_list]


# Global classifier instance
classifier = SymptomClassifier()


def get_classifier() -> SymptomClassifier:
    """Get the global classifier instance"""
    return classifier


if __name__ == "__main__":
    # Train models when run directly
    import sys
    
    dataset_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', '..', 
        'dataset', 
        'swiftqueue_symptom_training_5000(1).csv'
    )
    
    print("🚀 Starting Symptom Classifier Training...")
    print(f"Dataset: {dataset_path}\n")
    
    clf = SymptomClassifier()
    results = clf.train_models(dataset_path)
    
    print("\n" + "="*60)
    print("📊 TRAINING COMPLETE")
    print("="*60)
    print(f"Total Samples: {results['total_samples']}")
    print(f"Severity Accuracy: {results['severity_accuracy']:.2%}")
    print(f"Department Accuracy: {results['department_accuracy']:.2%}")
    print(f"\nSeverity Classes: {results['severity_classes']}")
    print(f"Department Classes: {results['department_classes']}")
    
    # Test with sample predictions
    print("\n" + "="*60)
    print("🧪 SAMPLE PREDICTIONS")
    print("="*60)
    
    test_cases = [
        "chest pain, short breath, dizziness",
        "headache, fever",
        "abdominal pain, bloating",
        "kurwadziwa moyo, kupfupika kufema",  # Shona: heart pain, shortness of breath
        "cough, wheezing"
    ]
    
    for symptoms in test_cases:
        result = clf.predict(symptoms)
        print(f"\n📝 Symptoms: {symptoms}")
        print(f"   Severity: {result['severity']} (confidence: {result['confidence']['severity']:.2%})")
        print(f"   Department: {result['department']} (confidence: {result['confidence']['department']:.2%})")
