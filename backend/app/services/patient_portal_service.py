"""
Patient Portal Service for Healthcare Queue Management System
Handles patient messaging, document management, and portal functionality
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.models import (
    PatientMessage, PatientDocument, PatientPreference,
    LabResult, User
)
from app.services.auth_service import get_user_by_id


class PatientPortalService:
    """Service for managing patient portal functionality."""

    def __init__(self):
        pass

    def send_patient_message(self, db: Session, message_data: Dict[str, Any]) -> PatientMessage:
        """Send a message from patient to staff or vice versa."""
        # Determine sender type and set appropriate fields
        if message_data.get("is_patient_sender", True):
            patient_id = message_data["patient_id"]
            staff_id = message_data.get("staff_id")
        else:
            patient_id = message_data.get("patient_id")
            staff_id = message_data["staff_id"]

        message = PatientMessage(
            patient_id=patient_id,
            staff_id=staff_id,
            subject=message_data["subject"],
            message=message_data["message"],
            message_type=message_data.get("message_type", "general"),
            priority=message_data.get("priority", "normal"),
            is_patient_sender=message_data.get("is_patient_sender", True)
        )

        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_patient_messages(self, db: Session, patient_id: int, status_filter: Optional[str] = None) -> List[PatientMessage]:
        """Get messages for a patient."""
        query = db.query(PatientMessage).filter(PatientMessage.patient_id == patient_id)

        if status_filter:
            query = query.filter(PatientMessage.status == status_filter)

        return query.order_by(PatientMessage.created_at.desc()).all()

    def get_staff_messages(self, db: Session, staff_id: int, status_filter: Optional[str] = None) -> List[PatientMessage]:
        """Get messages for a staff member."""
        query = db.query(PatientMessage).filter(PatientMessage.staff_id == staff_id)

        if status_filter:
            query = query.filter(PatientMessage.status == status_filter)

        return query.order_by(PatientMessage.created_at.desc()).all()

    def mark_message_read(self, db: Session, message_id: int, user_id: int) -> bool:
        """Mark a message as read."""
        message = db.query(PatientMessage).filter(PatientMessage.id == message_id).first()

        if not message:
            return False

        # Check if user is authorized to mark this message as read
        is_authorized = (
            (message.is_patient_sender and message.patient_id == user_id) or
            (not message.is_patient_sender and message.staff_id == user_id)
        )

        if is_authorized and message.status == "unread":
            message.status = "read"
            message.read_at = datetime.utcnow()
            db.commit()
            return True

        return False

    def reply_to_message(self, db: Session, message_id: int, reply_data: Dict[str, Any]) -> PatientMessage:
        """Reply to a message."""
        parent_message = db.query(PatientMessage).filter(PatientMessage.id == message_id).first()

        if not parent_message:
            raise ValueError("Parent message not found")

        # Create reply
        reply = PatientMessage(
            patient_id=parent_message.patient_id,
            staff_id=parent_message.staff_id,
            subject=f"Re: {parent_message.subject}",
            message=reply_data["message"],
            message_type=parent_message.message_type,
            priority=parent_message.priority,
            is_patient_sender=not parent_message.is_patient_sender,  # Flip sender type
            parent_message_id=message_id
        )

        # Update parent message status
        parent_message.status = "replied"

        db.add(reply)
        db.commit()
        db.refresh(reply)
        return reply

    def get_message_thread(self, db: Session, message_id: int) -> List[PatientMessage]:
        """Get full message thread including replies."""
        # Get the root message
        root_message = db.query(PatientMessage).filter(PatientMessage.id == message_id).first()

        if not root_message:
            return []

        # Get all messages in the thread (same patient-staff pair, same subject)
        thread_messages = db.query(PatientMessage).filter(
            and_(
                PatientMessage.patient_id == root_message.patient_id,
                PatientMessage.staff_id == root_message.staff_id,
                or_(
                    PatientMessage.subject == root_message.subject,
                    PatientMessage.subject.like(f"Re: {root_message.subject}")
                )
            )
        ).order_by(PatientMessage.created_at.asc()).all()

        return thread_messages

    def upload_patient_document(self, db: Session, document_data: Dict[str, Any]) -> PatientDocument:
        """Upload a patient document."""
        document = PatientDocument(
            patient_id=document_data["patient_id"],
            document_type=document_data["document_type"],
            title=document_data["title"],
            description=document_data.get("description"),
            file_path=document_data["file_path"],
            file_size=document_data.get("file_size", 0),
            mime_type=document_data.get("mime_type"),
            uploaded_by=document_data.get("uploaded_by"),
            is_patient_visible=document_data.get("is_patient_visible", True)
        )

        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def get_patient_documents(self, db: Session, patient_id: int, document_type: Optional[str] = None) -> List[PatientDocument]:
        """Get documents for a patient."""
        query = db.query(PatientDocument).filter(
            and_(
                PatientDocument.patient_id == patient_id,
                PatientDocument.is_patient_visible == True
            )
        )

        if document_type:
            query = query.filter(PatientDocument.document_type == document_type)

        return query.order_by(PatientDocument.uploaded_at.desc()).all()

    def get_patient_preferences(self, db: Session, patient_id: int) -> Optional[PatientPreference]:
        """Get patient preferences."""
        return db.query(PatientPreference).filter(
            PatientPreference.patient_id == patient_id
        ).first()

    def update_patient_preferences(self, db: Session, patient_id: int, preferences: Dict[str, Any]) -> PatientPreference:
        """Update or create patient preferences."""
        existing_prefs = self.get_patient_preferences(db, patient_id)

        if existing_prefs:
            # Update existing preferences
            for key, value in preferences.items():
                if hasattr(existing_prefs, key):
                    setattr(existing_prefs, key, value)
            existing_prefs.updated_at = datetime.utcnow()
        else:
            # Create new preferences
            existing_prefs = PatientPreference(patient_id=patient_id, **preferences)
            db.add(existing_prefs)

        db.commit()
        db.refresh(existing_prefs)
        return existing_prefs

    def get_lab_results(self, db: Session, patient_id: int, status_filter: Optional[str] = None) -> List[LabResult]:
        """Get lab results for a patient."""
        query = db.query(LabResult).filter(
            and_(
                LabResult.patient_id == patient_id,
                LabResult.is_patient_visible == True
            )
        )

        if status_filter:
            query = query.filter(LabResult.status == status_filter)

        return query.order_by(LabResult.result_date.desc()).all()

    def get_dashboard_summary(self, db: Session, patient_id: int) -> Dict[str, Any]:
        """Get patient dashboard summary."""
        # Unread messages
        unread_messages = db.query(PatientMessage).filter(
            and_(
                PatientMessage.patient_id == patient_id,
                PatientMessage.status == "unread",
                PatientMessage.is_patient_sender == False  # Messages from staff
            )
        ).count()

        # Recent documents
        recent_docs = db.query(PatientDocument).filter(
            and_(
                PatientDocument.patient_id == patient_id,
                PatientDocument.is_patient_visible == True
            )
        ).order_by(PatientDocument.uploaded_at.desc()).limit(5).all()

        # Recent lab results
        recent_labs = db.query(LabResult).filter(
            and_(
                LabResult.patient_id == patient_id,
                LabResult.is_patient_visible == True
            )
        ).order_by(LabResult.result_date.desc()).limit(5).all()

        # Abnormal results count
        abnormal_results = db.query(LabResult).filter(
            and_(
                LabResult.patient_id == patient_id,
                LabResult.abnormal_flag == True,
                LabResult.is_patient_visible == True
            )
        ).count()

        # Preferences
        preferences = self.get_patient_preferences(db, patient_id)

        # Total documents count
        total_documents = db.query(PatientDocument).filter(
            and_(
                PatientDocument.patient_id == patient_id,
                PatientDocument.is_patient_visible == True
            )
        ).count()

        return {
            "unread_messages": unread_messages,
            "recent_documents": recent_docs,
            "recent_lab_results": recent_labs,
            "abnormal_results_count": abnormal_results,
            "preferences": preferences,
            "total_documents": total_documents
        }

    def create_lab_result(self, db: Session, lab_data: Dict[str, Any]) -> LabResult:
        """Create a new lab result."""
        lab_result = LabResult(
            patient_id=lab_data["patient_id"],
            test_name=lab_data["test_name"],
            test_category=lab_data.get("test_category"),
            result_value=lab_data.get("result_value"),
            normal_range=lab_data.get("normal_range"),
            unit=lab_data.get("unit"),
            abnormal_flag=lab_data.get("abnormal_flag", False),
            status=lab_data.get("status", "pending"),
            ordered_by=lab_data.get("ordered_by"),
            notes=lab_data.get("notes"),
            test_date=lab_data.get("test_date"),
            is_patient_visible=lab_data.get("is_patient_visible", True)
        )

        db.add(lab_result)
        db.commit()
        db.refresh(lab_result)
        return lab_result

    def update_lab_result(self, db: Session, result_id: int, updates: Dict[str, Any]) -> Optional[LabResult]:
        """Update a lab result."""
        result = db.query(LabResult).filter(LabResult.id == result_id).first()

        if not result:
            return None

        for key, value in updates.items():
            if hasattr(result, key):
                setattr(result, key, value)

        db.commit()
        db.refresh(result)
        return result


# Global patient portal service instance
patient_portal_service = PatientPortalService()