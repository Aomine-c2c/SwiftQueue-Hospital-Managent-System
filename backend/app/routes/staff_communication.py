"""
Staff Communication Routes for Healthcare Queue Management System
API endpoints for staff messaging and communication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.services.staff_communication_service import staff_communication_service
from app.services.auth_service import get_current_active_user
from app.models.models import User


router = APIRouter(prefix="/staff-communication", tags=["Staff Communication"])


# Pydantic models
class MessageCreate(BaseModel):
    recipient_id: Optional[int] = None
    subject: str
    message: str
    message_type: str = "direct"
    priority: str = "normal"
    department_filter: Optional[str] = None
    role_filter: Optional[str] = None
    expires_at: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    recipient_id: Optional[int]
    subject: str
    message: str
    message_type: str
    priority: str
    is_read: bool
    read_at: Optional[str]
    department_filter: Optional[str]
    role_filter: Optional[str]
    expires_at: Optional[str]
    created_at: str
    sender_name: Optional[str]


class MessageStats(BaseModel):
    total_messages: int
    unread_messages: int
    urgent_messages: int


@router.post("/messages", response_model=MessageResponse)
async def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send a message to staff member(s)."""
    try:
        msg_data = message.dict()
        msg_data["sender_id"] = current_user.id

        staff_message = staff_communication_service.send_message(db, msg_data)

        # Add sender name
        response = MessageResponse(**staff_message.__dict__)
        response.sender_name = current_user.name
        response.created_at = staff_message.created_at.isoformat()
        if staff_message.read_at:
            response.read_at = staff_message.read_at.isoformat()
        if staff_message.expires_at:
            response.expires_at = staff_message.expires_at.isoformat()

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send message: {str(e)}")


@router.get("/messages", response_model=List[MessageResponse])
async def get_messages(
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get messages for current user."""
    messages = staff_communication_service.get_messages(db, current_user.id, unread_only)

    result = []
    for msg in messages:
        response = MessageResponse(**msg.__dict__)
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        response.sender_name = sender.name if sender else "Unknown"
        response.created_at = msg.created_at.isoformat()
        if msg.read_at:
            response.read_at = msg.read_at.isoformat()
        if msg.expires_at:
            response.expires_at = msg.expires_at.isoformat()
        result.append(response)

    return result


@router.put("/messages/{message_id}/read")
async def mark_message_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark a message as read."""
    success = staff_communication_service.mark_message_read(db, message_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found or access denied")

    return {"message": "Message marked as read"}


@router.get("/messages/stats", response_model=MessageStats)
async def get_message_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get message statistics for current user."""
    stats = staff_communication_service.get_message_stats(db, current_user.id)
    return MessageStats(**stats)


@router.post("/broadcast")
async def broadcast_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Broadcast a message to multiple recipients (admin/staff supervisor only)."""
    # Check if user has permission to broadcast
    if current_user.role not in ["admin", "staff"] or not staff_communication_service._get_user_department(db, current_user.id):
        raise HTTPException(status_code=403, detail="Insufficient permissions for broadcast")

    try:
        msg_data = message.dict()
        msg_data["sender_id"] = current_user.id

        messages = staff_communication_service.broadcast_message(db, msg_data)

        return {
            "message": "Broadcast sent successfully",
            "recipients_count": len(messages),
            "message_ids": [msg.id for msg in messages]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to broadcast message: {str(e)}")


@router.post("/tasks/{task_id}/notify")
async def notify_task_assignment(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send notification for task assignment."""
    # This would integrate with the task system
    # For now, return a placeholder response
    return {"message": "Task notification sent", "task_id": task_id}


@router.post("/shifts/{shift_id}/notify")
async def notify_shift_change(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Send notification for shift changes."""
    # This would integrate with the scheduling system
    # For now, return a placeholder response
    return {"message": "Shift notification sent", "shift_id": shift_id}


@router.delete("/messages/expired")
async def cleanup_expired_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Clean up expired messages (admin only)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    deleted_count = staff_communication_service.cleanup_expired_messages(db)

    return {"message": f"Cleaned up {deleted_count} expired messages"}