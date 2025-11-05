"""
AI Symptom Analysis Routes
Uses trained Naive Bayes classifier instead of Ollama/OpenRouter
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.models import Service
from ..services.symptom_classifier import get_classifier

router = APIRouter(tags=["AI Classifier"])


class SymptomRequest(BaseModel):
    symptoms: str = Field(..., description="Comma-separated symptoms or description")
    language: Optional[str] = Field(default="English", description="Language of symptoms")


class PredictionResponse(BaseModel):
    severity: str
    department: str
    recommended_service: Optional[Dict] = None
    confidence: Dict[str, float]
    all_severity_scores: Dict[str, float]
    all_department_scores: Dict[str, float]
    symptoms_analyzed: str


class TrainingStatusResponse(BaseModel):
    models_trained: bool
    severity_accuracy: Optional[float] = None
    department_accuracy: Optional[float] = None
    message: str


@router.post("/analyze-symptoms", response_model=PredictionResponse)
async def analyze_symptoms(
    request: SymptomRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze symptoms using trained AI model
    
    Returns predicted severity level and recommended department
    """
    try:
        # Get classifier and predict
        classifier = get_classifier()
        prediction = classifier.predict(request.symptoms)
        
        # Check if there was an error
        if 'error' in prediction:
            raise HTTPException(status_code=503, detail=prediction['error'])
        
        # Find matching service in database
        recommended_service = None
        department_name = prediction['department']
        
        # Try to find a service in the predicted department
        service = db.query(Service).filter(
            Service.department.ilike(f"%{department_name}%")
        ).first()
        
        if service:
            recommended_service = {
                "id": service.id,
                "name": service.name,
                "department": service.department,
                "estimated_time": service.estimated_time
            }
        
        return PredictionResponse(
            severity=prediction['severity'],
            department=prediction['department'],
            recommended_service=recommended_service,
            confidence=prediction['confidence'],
            all_severity_scores=prediction['all_severity_scores'],
            all_department_scores=prediction['all_department_scores'],
            symptoms_analyzed=prediction['symptoms_analyzed']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing symptoms: {str(e)}"
        )


@router.post("/batch-analyze", response_model=List[PredictionResponse])
async def batch_analyze_symptoms(
    requests: List[SymptomRequest],
    db: Session = Depends(get_db)
):
    """
    Analyze multiple symptom descriptions in batch
    """
    try:
        results = []
        classifier = get_classifier()
        
        for request in requests:
            prediction = classifier.predict(request.symptoms)

            if 'error' in prediction:
                raise HTTPException(status_code=503, detail=prediction['error'])
            
            # Find matching service
            recommended_service = None
            department_name = prediction['department']
            service = db.query(Service).filter(
                Service.department.ilike(f"%{department_name}%")
            ).first()
            
            if service:
                recommended_service = {
                    "id": service.id,
                    "name": service.name,
                    "department": service.department,
                    "estimated_time": service.estimated_time
                }
            
            results.append(PredictionResponse(
                severity=prediction['severity'],
                department=prediction['department'],
                recommended_service=recommended_service,
                confidence=prediction['confidence'],
                all_severity_scores=prediction['all_severity_scores'],
                all_department_scores=prediction['all_department_scores'],
                symptoms_analyzed=prediction['symptoms_analyzed']
            ))
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch analysis: {str(e)}"
        )


@router.get("/model-status", response_model=TrainingStatusResponse)
async def get_model_status():
    """
    Check if AI models are trained and ready
    """
    try:
        classifier = get_classifier()
        
        # Try to load models
        try:
            classifier.load_models()
            return TrainingStatusResponse(
                models_trained=True,
                message="AI models loaded and ready"
            )
        except FileNotFoundError:
            return TrainingStatusResponse(
                models_trained=False,
                message="Models not trained. Run training script first."
            )
        except Exception as load_error:
            return TrainingStatusResponse(
                models_trained=False,
                message=f"Error loading models: {str(load_error)}"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking model status: {str(e)}"
        )


@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages for symptom input
    """
    return {
        "languages": ["English", "Shona", "Mixed"],
        "note": "Model is trained on multilingual data including English and Shona keywords"
    }


@router.get("/severity-levels")
async def get_severity_levels():
    """
    Get all possible severity levels
    """
    return {
        "levels": ["Critical", "High", "Moderate", "Low"],
        "descriptions": {
            "Critical": "Immediate attention required - life threatening",
            "High": "Urgent care needed - serious condition",
            "Moderate": "Important but not urgent",
            "Low": "Non-urgent, routine care"
        }
    }


@router.get("/departments")
async def get_departments(db: Session = Depends(get_db)):
    """
    Get all available departments from database
    """
    services = db.query(Service.department).distinct().all()
    departments = [s[0] for s in services if s[0]]
    
    return {
        "departments": departments,
        "count": len(departments)
    }
