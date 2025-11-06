from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json

from app.database import get_db
from app.services.telemedicine_service import TelemedicineService
from app.services.auth_service import get_current_active_user
from app.models.models import User, TelemedicineSession, TelemedicineMessage, TelemedicineWaitingRoom


router = APIRouter()


# Pydantic models for request/response
class SessionCreateRequest(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    session_type: str = Field(default="video", pattern="^(video|audio|chat)$")
    scheduled_start: Optional[datetime] = None
    chief_complaint: Optional[str] = None
    recording_enabled: bool = False


class SessionUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, pattern="^(scheduled|waiting|in_progress|completed|cancelled|failed)$")
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    prescription_issued: bool = False
    connection_quality: Optional[str] = Field(None, pattern="^(poor|fair|good|excellent)$")
    audio_quality: Optional[str] = Field(None, pattern="^(poor|fair|good|excellent)$")
    video_quality: Optional[str] = Field(None, pattern="^(poor|fair|good|excellent)$")


class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: str = Field(default="text", pattern="^(text|file|system)$")


class FeedbackRequest(BaseModel):
    patient_rating: Optional[int] = Field(None, ge=1, le=5)
    patient_feedback: Optional[str] = Field(None, max_length=1000)
    doctor_notes: Optional[str] = Field(None, max_length=2000)


class SessionResponse(BaseModel):
    session_id: str
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    session_type: str
    status: str
    scheduled_start: datetime
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    duration_minutes: Optional[int]
    room_id: Optional[str]
    chief_complaint: Optional[str]
    diagnosis: Optional[str]
    treatment_plan: Optional[str]
    follow_up_instructions: Optional[str]
    prescription_issued: bool
    connection_quality: Optional[str]
    audio_quality: Optional[str]
    video_quality: Optional[str]
    patient_rating: Optional[int]
    patient_feedback: Optional[str]
    doctor_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    session_id: int
    sender_id: int
    message_type: str
    content: str
    file_path: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    is_read: bool
    sent_at: datetime

    class Config:
        from_attributes = True


class WaitingRoomResponse(BaseModel):
    id: int
    session_id: int
    patient_id: int
    joined_at: datetime
    status: str
    estimated_wait_minutes: Optional[int]

    class Config:
        from_attributes = True


# Routes

@router.post("/sessions")
async def create_session(
    request: SessionCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new telemedicine session"""
    # Authorization: Only doctors, staff, or admins can create sessions
    if current_user.role not in ["doctor", "staff", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only medical staff can create telemedicine sessions"
        )

    service = TelemedicineService(db)

    try:
        session = service.create_session(
            patient_id=request.patient_id,
            doctor_id=request.doctor_id,
            appointment_id=request.appointment_id,
            session_type=request.session_type,
            scheduled_start=request.scheduled_start,
            chief_complaint=request.chief_complaint,
            recording_enabled=request.recording_enabled
        )
        # Convert SQLAlchemy model to dict
        return {
            "session_id": session.session_id,
            "patient_id": session.patient_id,
            "doctor_id": session.doctor_id,
            "appointment_id": session.appointment_id,
            "session_type": session.session_type,
            "status": session.status,
            "room_id": session.room_id,
            "scheduled_start": session.scheduled_start.isoformat() if session.scheduled_start else None,
            "chief_complaint": session.chief_complaint,
            "recording_enabled": session.recording_enabled,
            "created_at": session.created_at.isoformat() if session.created_at else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get session details"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only participants can view session
    if current_user.id not in [session.patient_id, session.doctor_id] and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return session


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    status_filter: Optional[str] = None
):
    """Get sessions for current user"""
    service = TelemedicineService(db)

    if current_user.role == "patient":
        sessions = service.get_patient_sessions(current_user.id, limit)
    elif current_user.role in ["doctor", "staff"]:
        sessions = service.get_doctor_sessions(current_user.id, limit)
    else:
        sessions = []

    # Apply status filter if provided
    if status_filter:
        sessions = [s for s in sessions if s.status == status_filter]

    return sessions


@router.put("/sessions/{session_id}")
async def update_session(
    session_id: str,
    request: SessionUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update session details"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only doctor or admin can update session
    if current_user.id != session.doctor_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned doctor can update this session"
        )

    # Update status if provided
    if request.status:
        success = service.update_session_status(session_id, request.status)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update session status"
            )

    # Update medical details if session is completed
    if request.status == "completed":
        success = service.end_session(
            session_id=session_id,
            diagnosis=request.diagnosis,
            treatment_plan=request.treatment_plan,
            follow_up_instructions=request.follow_up_instructions,
            prescription_issued=request.prescription_issued
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to complete session"
            )

    # Update quality metrics
    if any([request.connection_quality, request.audio_quality, request.video_quality]):
        # Get updated session
        session = service.get_session(session_id)
        if request.connection_quality:
            session.connection_quality = request.connection_quality
        if request.audio_quality:
            session.audio_quality = request.audio_quality
        if request.video_quality:
            session.video_quality = request.video_quality
        db.commit()

    return service.get_session(session_id)


@router.post("/sessions/{session_id}/start")
async def start_session(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start a telemedicine session"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only doctor can start session
    if current_user.id != session.doctor_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned doctor can start this session"
        )

    success = service.start_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to start session"
        )

    return {"message": "Session started successfully", "room_id": session.room_id}


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    request: MessageCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message in a session"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only participants can send messages
    if current_user.id not in [session.patient_id, session.doctor_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    message = service.add_session_message(
        session_id=session_id,
        sender_id=current_user.id,
        content=request.content,
        message_type=request.message_type
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send message"
        )

    return message


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """Get messages for a session"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only participants can view messages
    if current_user.id not in [session.patient_id, session.doctor_id] and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    messages = service.get_session_messages(session_id, limit)

    # Mark messages as read for current user
    service.mark_messages_read(session_id, current_user.id)

    return messages


@router.post("/sessions/{session_id}/waiting-room/join")
async def join_waiting_room(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Join waiting room for a session"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only patient can join their own session
    if current_user.id != session.patient_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    waiting_entry = service.join_waiting_room(session_id, current_user.id)
    if not waiting_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to join waiting room"
        )

    return {"message": "Joined waiting room successfully", "position": waiting_entry.id}


@router.post("/sessions/{session_id}/waiting-room/admit")
async def admit_from_waiting_room(
    session_id: str,
    patient_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Admit patient from waiting room (doctor only)"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only doctor can admit patients
    if current_user.id != session.doctor_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned doctor can admit patients"
        )

    success = service.admit_from_waiting_room(session_id, patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to admit patient"
        )

    return {"message": "Patient admitted successfully"}


@router.get("/sessions/{session_id}/waiting-room")
async def get_waiting_room(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get waiting room for a session (doctor only)"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only doctor can view waiting room
    if current_user.id != session.doctor_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return service.get_waiting_room(session_id)


@router.post("/sessions/{session_id}/feedback")
async def submit_feedback(
    session_id: str,
    request: FeedbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for a completed session"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Patient can submit rating/feedback, doctor can submit notes
    if current_user.id == session.patient_id:
        # Patient feedback
        success = service.update_session_feedback(
            session_id=session_id,
            patient_rating=request.patient_rating,
            patient_feedback=request.patient_feedback
        )
    elif current_user.id == session.doctor_id or current_user.role == "admin":
        # Doctor notes
        success = service.update_session_feedback(
            session_id=session_id,
            doctor_notes=request.doctor_notes
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit feedback"
        )

    return {"message": "Feedback submitted successfully"}


@router.get("/sessions/upcoming")
async def get_upcoming_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get upcoming sessions for current user"""
    service = TelemedicineService(db)
    return service.get_upcoming_sessions(current_user.id, current_user.role, limit)


@router.get("/sessions/active")
async def get_active_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get active sessions for current user"""
    service = TelemedicineService(db)
    return service.get_active_sessions(current_user.id, current_user.role)


@router.delete("/sessions/{session_id}")
async def cancel_session(
    session_id: str,
    reason: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a telemedicine session"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only doctor or admin can cancel
    if current_user.id != session.doctor_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned doctor can cancel this session"
        )

    success = service.cancel_session(session_id, reason)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel session"
        )

    return {"message": "Session cancelled successfully"}


@router.get("/sessions/{session_id}/report")
async def get_session_report(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive session report"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only participants or admin can view report
    if current_user.id not in [session.patient_id, session.doctor_id] and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    report = service.generate_session_report(session_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Report not available for incomplete session"
        )

    return report


# WebRTC Signaling endpoints (simplified - would need proper WebRTC server for production)
@router.post("/sessions/{session_id}/signal")
async def webrtc_signal(
    session_id: str,
    signal_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Handle WebRTC signaling (simplified version)"""
    service = TelemedicineService(db)
    session = service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Authorization: Only participants can send signals
    if current_user.id not in [session.patient_id, session.doctor_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    # In a real implementation, this would forward signals to the other participant
    # For now, just acknowledge receipt
    return {"message": "Signal received", "type": signal_data.get("type", "unknown")}
