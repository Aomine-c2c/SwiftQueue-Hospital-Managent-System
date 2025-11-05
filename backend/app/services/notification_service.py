"""
Notification Service for Healthcare Queue Management System
Handles real-time notifications, alerts, and communication
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.models import Notification, User
from app.services.websocket_manager import enhanced_manager as websocket_manager


class NotificationService:
    """Service for managing notifications and real-time alerts."""

    def __init__(self):
        pass

    def create_notification(self, db: Session, notification_data: Dict[str, Any]) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=notification_data["user_id"],
            title=notification_data["title"],
            message=notification_data["message"],
            type=notification_data.get("type", "info")
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Send real-time notification via WebSocket
        self._send_realtime_notification(notification)

        return notification

    def get_user_notifications(self, db: Session, user_id: int, unread_only: bool = False) -> List[Notification]:
        """Get notifications for a user."""
        query = db.query(Notification).filter(Notification.user_id == user_id)

        if unread_only:
            query = query.filter(Notification.is_read == False)

        return query.order_by(Notification.created_at.desc()).all()

    def mark_notification_read(self, db: Session, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read."""
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()

        if notification and not notification.is_read:
            notification.is_read = True
            db.commit()
            return True

        return False

    def mark_all_read(self, db: Session, user_id: int) -> int:
        """Mark all notifications as read for a user."""
        updated_count = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({"is_read": True})

        db.commit()
        return updated_count

    def delete_notification(self, db: Session, notification_id: int, user_id: int) -> bool:
        """Delete a notification."""
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()

        if notification:
            db.delete(notification)
            db.commit()
            return True

        return False

    def get_notification_stats(self, db: Session, user_id: int) -> Dict[str, int]:
        """Get notification statistics for a user."""
        total = db.query(Notification).filter(Notification.user_id == user_id).count()

        unread = db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).count()

        # Count by type
        type_counts = db.query(
            Notification.type,
            func.count(Notification.id).label('count')
        ).filter(Notification.user_id == user_id).group_by(Notification.type).all()

        types = {row.type: row.count for row in type_counts}

        return {
            "total": total,
            "unread": unread,
            "by_type": types
        }

    def create_queue_notification(self, db: Session, user_id: int, queue_data: Dict[str, Any]) -> Notification:
        """Create a queue-related notification."""
        if queue_data["action"] == "called":
            title = "Your Turn!"
            message = f"You are now being served at counter {queue_data.get('counter', 'TBD')}. Please proceed to the service area."
            notification_type = "success"
        elif queue_data["action"] == "position_update":
            position = queue_data.get("position", 0)
            title = "Queue Position Update"
            message = f"Your current position in queue: {position}"
            notification_type = "info"
        elif queue_data["action"] == "estimated_time":
            estimated_time = queue_data.get("estimated_time", 0)
            title = "Wait Time Update"
            message = f"Estimated wait time: {estimated_time} minutes"
            notification_type = "info"
        else:
            title = "Queue Update"
            message = queue_data.get("message", "Queue status has been updated")
            notification_type = "info"

        return self.create_notification(db, {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type
        })

    def create_appointment_notification(self, db: Session, user_id: int, appointment_data: Dict[str, Any]) -> Notification:
        """Create an appointment-related notification."""
        if appointment_data["action"] == "confirmed":
            title = "Appointment Confirmed"
            message = f"Your appointment for {appointment_data.get('service', 'TBD')} has been confirmed for {appointment_data.get('date', 'TBD')}."
            notification_type = "success"
        elif appointment_data["action"] == "reminder":
            title = "Appointment Reminder"
            message = f"You have an appointment in {appointment_data.get('hours_until', 24)} hours for {appointment_data.get('service', 'TBD')}."
            notification_type = "warning"
        elif appointment_data["action"] == "cancelled":
            title = "Appointment Cancelled"
            message = f"Your appointment for {appointment_data.get('service', 'TBD')} has been cancelled."
            notification_type = "error"
        else:
            title = "Appointment Update"
            message = appointment_data.get("message", "Appointment status has been updated")
            notification_type = "info"

        return self.create_notification(db, {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type
        })

    def create_system_notification(self, db: Session, user_ids: List[int], system_data: Dict[str, Any]) -> List[Notification]:
        """Create system-wide notifications for multiple users."""
        notifications = []

        for user_id in user_ids:
            notification = self.create_notification(db, {
                "user_id": user_id,
                "title": system_data.get("title", "System Notification"),
                "message": system_data["message"],
                "type": system_data.get("type", "info")
            })
            notifications.append(notification)

        return notifications

    def create_emergency_notification(self, db: Session, user_ids: List[int], emergency_data: Dict[str, Any]) -> List[Notification]:
        """Create emergency notifications."""
        notifications = []

        for user_id in user_ids:
            notification = self.create_notification(db, {
                "user_id": user_id,
                "title": "🚨 Emergency Alert",
                "message": emergency_data["message"],
                "type": "error"
            })
            notifications.append(notification)

        return notifications

    def cleanup_old_notifications(self, db: Session, days_old: int = 30) -> int:
        """Clean up old notifications."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        deleted_count = db.query(Notification).filter(
            and_(
                Notification.created_at < cutoff_date,
                Notification.is_read == True
            )
        ).delete()

        db.commit()
        return deleted_count

    def broadcast_notification(self, db: Session, notification_data: Dict[str, Any], target_users: List[int]) -> List[Notification]:
        """Broadcast a notification to multiple users."""
        notifications = []

        for user_id in target_users:
            notification = self.create_notification(db, {
                "user_id": user_id,
                **notification_data
            })
            notifications.append(notification)

        return notifications

    def _send_realtime_notification(self, notification: Notification) -> None:
        """Send notification via WebSocket."""
        try:
            # Send to specific user
            websocket_manager.send_to_user(
                notification.user_id,
                "notification",
                {
                    "id": notification.id,
                    "title": notification.title,
                    "message": notification.message,
                    "type": notification.type,
                    "created_at": notification.created_at.isoformat()
                }
            )
        except Exception as e:
            # Log error but don't fail the notification creation
            print(f"Failed to send real-time notification: {e}")

    def get_unread_count(self, db: Session, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        return db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).count()


# Global notification service instance
notification_service = NotificationService()