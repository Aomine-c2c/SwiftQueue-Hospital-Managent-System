from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import uuid
import os
from app.models.models import (
    TelemedicineSession, TelemedicineMessage, TelemedicineWaitingRoom,
    User, Appointment
)
from app.database import get_db


class TelemedicineService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, patient_id: int, doctor_id: int, appointment_id: Optional[int] = None,
                      session_type: str = "video", scheduled_start: datetime = None,
                      chief_complaint: str = None, recording_enabled: bool = False) -> TelemedicineSession:
        """Create a new telemedicine session"""

        if scheduled_start is None:
            scheduled_start = datetime.utcnow() + timedelta(minutes=15)  # Default 15 min from now

        session_id = f"tele-{uuid.uuid4().hex[:12]}"
        room_id = f"room-{uuid.uuid4().hex[:8]}"

        session = TelemedicineSession(
            session_id=session_id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_id=appointment_id,
            session_type=session_type,
            status="scheduled",
            scheduled_start=scheduled_start,
            room_id=room_id,
            chief_complaint=chief_complaint,
            recording_enabled=recording_enabled
        )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[TelemedicineSession]:
        """Get session by session_id"""
        return self.db.query(TelemedicineSession).filter(
            TelemedicineSession.session_id == session_id
        ).first()

    def get_patient_sessions(self, patient_id: int, limit: int = 50) -> List[TelemedicineSession]:
        """Get all sessions for a patient"""
        return self.db.query(TelemedicineSession).filter(
            TelemedicineSession.patient_id == patient_id
        ).order_by(desc(TelemedicineSession.created_at)).limit(limit).all()

    def get_doctor_sessions(self, doctor_id: int, limit: int = 50) -> List[TelemedicineSession]:
        """Get all sessions for a doctor"""
        return self.db.query(TelemedicineSession).filter(
            TelemedicineSession.doctor_id == doctor_id
        ).order_by(desc(TelemedicineSession.created_at)).limit(limit).all()

    def update_session_status(self, session_id: str, status: str,
                             actual_start: datetime = None, actual_end: datetime = None) -> bool:
        """Update session status and timing"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = status
        session.updated_at = datetime.utcnow()

        if actual_start:
            session.actual_start = actual_start
        if actual_end:
            session.actual_end = actual_end
            if session.actual_start:
                duration = (actual_end - session.actual_start).total_seconds() / 60
                session.duration_minutes = int(duration)

        self.db.commit()
        return True

    def start_session(self, session_id: str) -> bool:
        """Mark session as started"""
        return self.update_session_status(session_id, "in_progress", actual_start=datetime.utcnow())

    def end_session(self, session_id: str, diagnosis: str = None, treatment_plan: str = None,
                   follow_up_instructions: str = None, prescription_issued: bool = False) -> bool:
        """End session and record medical details"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = "completed"
        session.actual_end = datetime.utcnow()
        session.diagnosis = diagnosis
        session.treatment_plan = treatment_plan
        session.follow_up_instructions = follow_up_instructions
        session.prescription_issued = prescription_issued

        if session.actual_start:
            duration = (session.actual_end - session.actual_start).total_seconds() / 60
            session.duration_minutes = int(duration)

        self.db.commit()
        return True

    def add_session_message(self, session_id: str, sender_id: int, content: str,
                           message_type: str = "text", file_path: str = None,
                           file_name: str = None, file_size: int = None) -> Optional[TelemedicineMessage]:
        """Add a message to a session"""
        session = self.get_session(session_id)
        if not session:
            return None

        message = TelemedicineMessage(
            session_id=session.id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_session_messages(self, session_id: str, limit: int = 100) -> List[TelemedicineMessage]:
        """Get all messages for a session"""
        session = self.get_session(session_id)
        if not session:
            return []

        return self.db.query(TelemedicineMessage).filter(
            TelemedicineMessage.session_id == session.id
        ).order_by(TelemedicineMessage.sent_at).limit(limit).all()

    def mark_messages_read(self, session_id: str, user_id: int) -> int:
        """Mark all messages in session as read for user"""
        session = self.get_session(session_id)
        if not session:
            return 0

        # Mark messages from other participants as read
        updated = self.db.query(TelemedicineMessage).filter(
            and_(
                TelemedicineMessage.session_id == session.id,
                TelemedicineMessage.sender_id != user_id,
                TelemedicineMessage.is_read == False
            )
        ).update({"is_read": True})

        self.db.commit()
        return updated

    def join_waiting_room(self, session_id: str, patient_id: int) -> Optional[TelemedicineWaitingRoom]:
        """Add patient to waiting room"""
        session = self.get_session(session_id)
        if not session:
            return None

        # Check if already in waiting room
        existing = self.db.query(TelemedicineWaitingRoom).filter(
            and_(
                TelemedicineWaitingRoom.session_id == session.id,
                TelemedicineWaitingRoom.patient_id == patient_id,
                TelemedicineWaitingRoom.status == "waiting"
            )
        ).first()

        if existing:
            return existing

        waiting_entry = TelemedicineWaitingRoom(
            session_id=session.id,
            patient_id=patient_id,
            status="waiting",
            estimated_wait_minutes=5  # Default estimate
        )

        self.db.add(waiting_entry)
        self.db.commit()
        self.db.refresh(waiting_entry)
        return waiting_entry

    def admit_from_waiting_room(self, session_id: str, patient_id: int) -> bool:
        """Admit patient from waiting room to session"""
        session = self.get_session(session_id)
        if not session:
            return False

        updated = self.db.query(TelemedicineWaitingRoom).filter(
            and_(
                TelemedicineWaitingRoom.session_id == session.id,
                TelemedicineWaitingRoom.patient_id == patient_id,
                TelemedicineWaitingRoom.status == "waiting"
            )
        ).update({"status": "admitted"})

        if updated > 0:
            self.update_session_status(session_id, "in_progress", actual_start=datetime.utcnow())

        self.db.commit()
        return updated > 0

    def get_waiting_room(self, session_id: str) -> List[TelemedicineWaitingRoom]:
        """Get all patients in waiting room for session"""
        session = self.get_session(session_id)
        if not session:
            return []

        return self.db.query(TelemedicineWaitingRoom).filter(
            and_(
                TelemedicineWaitingRoom.session_id == session.id,
                TelemedicineWaitingRoom.status == "waiting"
            )
        ).order_by(TelemedicineWaitingRoom.joined_at).all()

    def update_session_feedback(self, session_id: str, patient_rating: int = None,
                               patient_feedback: str = None, doctor_notes: str = None) -> bool:
        """Update session feedback and notes"""
        session = self.get_session(session_id)
        if not session:
            return False

        if patient_rating is not None:
            session.patient_rating = patient_rating
        if patient_feedback is not None:
            session.patient_feedback = patient_feedback
        if doctor_notes is not None:
            session.doctor_notes = doctor_notes

        self.db.commit()
        return True

    def get_upcoming_sessions(self, user_id: int, user_role: str, limit: int = 10) -> List[TelemedicineSession]:
        """Get upcoming sessions for user"""
        now = datetime.utcnow()

        if user_role == "patient":
            filter_condition = TelemedicineSession.patient_id == user_id
        elif user_role in ["doctor", "staff"]:
            filter_condition = TelemedicineSession.doctor_id == user_id
        else:
            return []

        return self.db.query(TelemedicineSession).filter(
            and_(
                filter_condition,
                TelemedicineSession.scheduled_start > now,
                TelemedicineSession.status.in_(["scheduled", "waiting"])
            )
        ).order_by(TelemedicineSession.scheduled_start).limit(limit).all()

    def get_active_sessions(self, user_id: int, user_role: str) -> List[TelemedicineSession]:
        """Get currently active sessions for user"""
        if user_role == "patient":
            filter_condition = TelemedicineSession.patient_id == user_id
        elif user_role in ["doctor", "staff"]:
            filter_condition = TelemedicineSession.doctor_id == user_id
        else:
            return []

        return self.db.query(TelemedicineSession).filter(
            and_(
                filter_condition,
                TelemedicineSession.status == "in_progress"
            )
        ).all()

    def cancel_session(self, session_id: str, reason: str = None) -> bool:
        """Cancel a telemedicine session"""
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = "cancelled"
        session.doctor_notes = reason or "Session cancelled"
        session.updated_at = datetime.utcnow()

        self.db.commit()
        return True

    def generate_session_report(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Generate a comprehensive report for a completed session"""
        session = self.get_session(session_id)
        if not session or session.status != "completed":
            return None

        messages = self.get_session_messages(session_id)

        return {
            "session_id": session.session_id,
            "patient": {
                "id": session.patient.id,
                "name": session.patient.name,
                "email": session.patient.email
            },
            "doctor": {
                "id": session.doctor.id,
                "name": session.doctor.name,
                "email": session.doctor.email
            },
            "session_details": {
                "type": session.session_type,
                "scheduled_start": session.scheduled_start.isoformat(),
                "actual_start": session.actual_start.isoformat() if session.actual_start else None,
                "actual_end": session.actual_end.isoformat() if session.actual_end else None,
                "duration_minutes": session.duration_minutes,
                "status": session.status
            },
            "medical_details": {
                "chief_complaint": session.chief_complaint,
                "diagnosis": session.diagnosis,
                "treatment_plan": session.treatment_plan,
                "follow_up_instructions": session.follow_up_instructions,
                "prescription_issued": session.prescription_issued
            },
            "quality_metrics": {
                "connection_quality": session.connection_quality,
                "audio_quality": session.audio_quality,
                "video_quality": session.video_quality
            },
            "feedback": {
                "patient_rating": session.patient_rating,
                "patient_feedback": session.patient_feedback,
                "doctor_notes": session.doctor_notes
            },
            "messages_count": len(messages),
            "recording_available": session.recording_path is not None
        }