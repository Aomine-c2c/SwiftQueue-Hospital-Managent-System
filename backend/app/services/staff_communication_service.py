"""
Staff Communication Service for Healthcare Queue Management System
Handles staff messaging, notifications, and communication workflows
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.models import User
from app.models.staff_models import StaffCommunication, StaffProfile, Department
from app.services.auth_service import get_user_by_id


class StaffCommunicationService:
    """Service for managing staff communications and messaging."""

    def __init__(self):
        pass

    def send_message(self, db: Session, message_data: Dict[str, Any]) -> StaffCommunication:
        """Send a message to staff member(s)."""
        message = StaffCommunication(
            sender_id=message_data["sender_id"],
            recipient_id=message_data.get("recipient_id"),
            subject=message_data["subject"],
            message=message_data["message"],
            message_type=message_data.get("message_type", "direct"),
            priority=message_data.get("priority", "normal"),
            department_filter=message_data.get("department_filter"),
            role_filter=message_data.get("role_filter"),
            expires_at=message_data.get("expires_at")
        )

        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_messages(self, db: Session, user_id: int, unread_only: bool = False) -> List[StaffCommunication]:
        """Get messages for a staff member."""
        query = db.query(StaffCommunication).filter(
            or_(
                StaffCommunication.recipient_id == user_id,
                and_(
                    StaffCommunication.recipient_id.is_(None),
                    or_(
                        StaffCommunication.department_filter.is_(None),
                        StaffCommunication.department_filter == self._get_user_department(db, user_id)
                    ),
                    or_(
                        StaffCommunication.role_filter.is_(None),
                        StaffCommunication.role_filter == self._get_user_role(db, user_id)
                    )
                )
            )
        )

        if unread_only:
            query = query.filter(StaffCommunication.is_read == False)

        return query.order_by(StaffCommunication.created_at.desc()).all()

    def mark_message_read(self, db: Session, message_id: int, user_id: int) -> bool:
        """Mark a message as read."""
        message = db.query(StaffCommunication).filter(
            and_(
                StaffCommunication.id == message_id,
                or_(
                    StaffCommunication.recipient_id == user_id,
                    StaffCommunication.recipient_id.is_(None)
                )
            )
        ).first()

        if message:
            message.is_read = True
            message.read_at = datetime.utcnow()
            db.commit()
            return True
        return False

    def get_message_stats(self, db: Session, user_id: int) -> Dict[str, int]:
        """Get message statistics for a user."""
        total_messages = db.query(StaffCommunication).filter(
            or_(
                StaffCommunication.recipient_id == user_id,
                and_(
                    StaffCommunication.recipient_id.is_(None),
                    or_(
                        StaffCommunication.department_filter.is_(None),
                        StaffCommunication.department_filter == self._get_user_department(db, user_id)
                    ),
                    or_(
                        StaffCommunication.role_filter.is_(None),
                        StaffCommunication.role_filter == self._get_user_role(db, user_id)
                    )
                )
            )
        ).count()

        unread_messages = db.query(StaffCommunication).filter(
            and_(
                or_(
                    StaffCommunication.recipient_id == user_id,
                    and_(
                        StaffCommunication.recipient_id.is_(None),
                        or_(
                            StaffCommunication.department_filter.is_(None),
                            StaffCommunication.department_filter == self._get_user_department(db, user_id)
                        ),
                        or_(
                            StaffCommunication.role_filter.is_(None),
                            StaffCommunication.role_filter == self._get_user_role(db, user_id)
                        )
                    )
                ),
                StaffCommunication.is_read == False
            )
        ).count()

        urgent_messages = db.query(StaffCommunication).filter(
            and_(
                or_(
                    StaffCommunication.recipient_id == user_id,
                    and_(
                        StaffCommunication.recipient_id.is_(None),
                        or_(
                            StaffCommunication.department_filter.is_(None),
                            StaffCommunication.department_filter == self._get_user_department(db, user_id)
                        ),
                        or_(
                            StaffCommunication.role_filter.is_(None),
                            StaffCommunication.role_filter == self._get_user_role(db, user_id)
                        )
                    )
                ),
                StaffCommunication.priority == "urgent",
                StaffCommunication.is_read == False
            )
        ).count()

        return {
            "total_messages": total_messages,
            "unread_messages": unread_messages,
            "urgent_messages": urgent_messages
        }

    def broadcast_message(self, db: Session, message_data: Dict[str, Any]) -> List[StaffCommunication]:
        """Broadcast a message to multiple recipients based on filters."""
        # Get target users based on filters
        target_users = self._get_broadcast_targets(db, message_data)

        messages = []
        for user_id in target_users:
            msg_data = message_data.copy()
            msg_data["recipient_id"] = user_id

            message = self.send_message(db, msg_data)
            messages.append(message)

        return messages

    def create_task_notification(self, db: Session, task_data: Dict[str, Any]) -> StaffCommunication:
        """Create a notification for a new task assignment."""
        message_data = {
            "sender_id": task_data["assigned_by"],
            "recipient_id": task_data["assigned_to"],
            "subject": f"New Task: {task_data['title']}",
            "message": f"You have been assigned a new task: {task_data['description']}",
            "message_type": "task",
            "priority": task_data.get("priority", "normal")
        }

        return self.send_message(db, message_data)

    def create_shift_notification(self, db: Session, shift_data: Dict[str, Any]) -> StaffCommunication:
        """Create a notification for shift changes or assignments."""
        message_data = {
            "sender_id": shift_data.get("created_by", 1),  # Default to admin
            "recipient_id": shift_data["staff_id"],
            "subject": "Shift Schedule Update",
            "message": f"Your shift has been updated: {shift_data.get('shift_date', 'TBD')} - {shift_data.get('shift_type', 'TBD')}",
            "message_type": "announcement",
            "priority": "normal"
        }

        return self.send_message(db, message_data)

    def cleanup_expired_messages(self, db: Session) -> int:
        """Clean up expired messages."""
        expired_count = db.query(StaffCommunication).filter(
            and_(
                StaffCommunication.expires_at.isnot(None),
                StaffCommunication.expires_at < datetime.utcnow()
            )
        ).delete()

        db.commit()
        return expired_count

    def _get_broadcast_targets(self, db: Session, message_data: Dict[str, Any]) -> List[int]:
        """Get list of user IDs for broadcast message."""
        query = db.query(User.id)

        # Apply department filter
        if message_data.get("department_filter"):
            query = query.join(StaffProfile).filter(
                StaffProfile.department == message_data["department_filter"]
            )

        # Apply role filter
        if message_data.get("role_filter"):
            query = query.filter(User.role == message_data["role_filter"])

        # Exclude sender
        if message_data.get("sender_id"):
            query = query.filter(User.id != message_data["sender_id"])

        return [user_id for (user_id,) in query.all()]

    def _get_user_department(self, db: Session, user_id: int) -> Optional[str]:
        """Get user's department."""
        profile = db.query(StaffProfile).filter(StaffProfile.user_id == user_id).first()
        return profile.department if profile else None

    def _get_user_role(self, db: Session, user_id: int) -> Optional[str]:
        """Get user's role."""
        user = get_user_by_id(db, user_id)
        return user.role if user else None


# Global staff communication service instance
staff_communication_service = StaffCommunicationService()