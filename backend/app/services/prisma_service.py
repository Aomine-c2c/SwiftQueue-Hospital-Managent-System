"""
Prisma ORM Integration for SwiftQueue
Provides type-safe database operations with Prisma ORM
"""

from prisma import Prisma
from prisma.models import *
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PrismaService:
    def __init__(self, database_url: str = None):
        self.database_url = database_url
        self.prisma = None

    async def connect(self):
        """Initialize Prisma client connection"""
        if not self.prisma:
            self.prisma = Prisma()
            await self.prisma.connect()
            logger.info("Prisma database connection established")

    async def disconnect(self):
        """Close Prisma client connection"""
        if self.prisma:
            await self.prisma.disconnect()
            logger.info("Prisma database connection closed")

    # User operations
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user"""
        return await self.prisma.user.create(data=user_data)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return await self.prisma.user.find_unique(where={'id': user_id})

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return await self.prisma.user.find_unique(where={'email': email})

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> User:
        """Update user information"""
        return await self.prisma.user.update(
            where={'id': user_id},
            data=user_data
        )

    async def delete_user(self, user_id: int) -> User:
        """Delete user"""
        return await self.prisma.user.delete(where={'id': user_id})

    # Appointment operations
    async def create_appointment(self, appointment_data: Dict[str, Any]) -> Appointment:
        """Create a new appointment"""
        return await self.prisma.appointment.create(data=appointment_data)

    async def get_appointment(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID"""
        return await self.prisma.appointment.find_unique(
            where={'id': appointment_id},
            include={
                'patient': True,
                'service': True,
                'staff': True
            }
        )

    async def get_user_appointments(self, user_id: int, user_role: str) -> List[Appointment]:
        """Get appointments for a user based on their role"""
        if user_role == 'patient':
            return await self.prisma.appointment.find_many(
                where={'patient_id': user_id},
                include={'service': True, 'staff': True},
                order_by={'appointment_date': 'desc'}
            )
        elif user_role in ['doctor', 'staff']:
            return await self.prisma.appointment.find_many(
                where={'staff_id': user_id},
                include={'patient': True, 'service': True},
                order_by={'appointment_date': 'desc'}
            )
        return []

    async def update_appointment(self, appointment_id: int, appointment_data: Dict[str, Any]) -> Appointment:
        """Update appointment"""
        return await self.prisma.appointment.update(
            where={'id': appointment_id},
            data=appointment_data
        )

    # Queue operations
    async def create_queue_entry(self, queue_data: Dict[str, Any]) -> QueueEntry:
        """Create a new queue entry"""
        return await self.prisma.queueentry.create(data=queue_data)

    async def get_queue_entries(self, service_id: Optional[int] = None) -> List[QueueEntry]:
        """Get queue entries, optionally filtered by service"""
        where_clause = {}
        if service_id:
            where_clause['service_id'] = service_id

        return await self.prisma.queueentry.find_many(
            where=where_clause,
            include={'patient': True, 'service': True},
            order_by={'created_at': 'asc'}
        )

    async def update_queue_entry(self, queue_id: int, queue_data: Dict[str, Any]) -> QueueEntry:
        """Update queue entry"""
        return await self.prisma.queueentry.update(
            where={'id': queue_id},
            data=queue_data
        )

    # Telemedicine operations
    async def create_telemedicine_session(self, session_data: Dict[str, Any]) -> TelemedicineSession:
        """Create a new telemedicine session"""
        return await self.prisma.telemedicinesession.create(data=session_data)

    async def get_telemedicine_session(self, session_id: str) -> Optional[TelemedicineSession]:
        """Get telemedicine session by session ID"""
        return await self.prisma.telemedicinesession.find_unique(
            where={'session_id': session_id},
            include={
                'patient': True,
                'doctor': True,
                'appointment': True,
                'messages': {
                    'include': {'sender': True},
                    'order_by': {'sent_at': 'asc'}
                }
            }
        )

    async def get_user_telemedicine_sessions(self, user_id: int, user_role: str) -> List[TelemedicineSession]:
        """Get telemedicine sessions for a user"""
        if user_role == 'patient':
            where_clause = {'patient_id': user_id}
        elif user_role in ['doctor', 'staff']:
            where_clause = {'doctor_id': user_id}
        else:
            return []

        return await self.prisma.telemedicinesession.find_many(
            where=where_clause,
            include={'patient': True, 'doctor': True},
            order_by={'created_at': 'desc'}
        )

    async def update_telemedicine_session(self, session_id: str, session_data: Dict[str, Any]) -> TelemedicineSession:
        """Update telemedicine session"""
        return await self.prisma.telemedicinesession.update(
            where={'session_id': session_id},
            data=session_data
        )

    async def create_telemedicine_message(self, message_data: Dict[str, Any]) -> TelemedicineMessage:
        """Create a telemedicine message"""
        return await self.prisma.telemedicinemessage.create(data=message_data)

    # Prescription operations
    async def create_prescription(self, prescription_data: Dict[str, Any]) -> Prescription:
        """Create a new prescription"""
        return await self.prisma.prescription.create(
            data=prescription_data,
            include={'medications': True}
        )

    async def get_prescription(self, prescription_id: int) -> Optional[Prescription]:
        """Get prescription by ID"""
        return await self.prisma.prescription.find_unique(
            where={'id': prescription_id},
            include={
                'patient': True,
                'doctor': True,
                'medications': True,
                'refills': True
            }
        )

    async def get_patient_prescriptions(self, patient_id: int) -> List[Prescription]:
        """Get all prescriptions for a patient"""
        return await self.prisma.prescription.find_many(
            where={'patient_id': patient_id},
            include={'doctor': True, 'medications': True},
            order_by={'created_at': 'desc'}
        )

    # Analytics operations
    async def get_queue_analytics(self, start_date: str, end_date: str) -> List[Analytics]:
        """Get queue analytics for date range"""
        return await self.prisma.analytics.find_many(
            where={
                'timestamp': {
                    'gte': start_date,
                    'lte': end_date
                }
            },
            order_by={'timestamp': 'asc'}
        )

    async def create_analytics_entry(self, analytics_data: Dict[str, Any]) -> Analytics:
        """Create a new analytics entry"""
        return await self.prisma.analytics.create(data=analytics_data)

    # Bulk operations
    async def bulk_create_queue_entries(self, queue_entries: List[Dict[str, Any]]) -> List[QueueEntry]:
        """Bulk create queue entries"""
        return await self.prisma.queueentry.create_many(
            data=queue_entries,
            skip_duplicates=True
        )

    async def bulk_update_appointments(self, updates: List[Dict[str, Any]]) -> int:
        """Bulk update appointments"""
        count = 0
        for update in updates:
            await self.prisma.appointment.update(
                where={'id': update['id']},
                data=update['data']
            )
            count += 1
        return count

    # Raw SQL queries for complex operations
    async def execute_raw_query(self, query: str, params: List[Any] = None) -> Any:
        """Execute raw SQL query"""
        if params:
            return await self.prisma.execute_raw(query, *params)
        return await self.prisma.execute_raw(query)

    async def query_raw(self, query: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL query and return results"""
        if params:
            return await self.prisma.query_raw(query, *params)
        return await self.prisma.query_raw(query)

# Global instance
prisma_service = PrismaService()

# Export for use in other modules
__all__ = ['PrismaService', 'prisma_service']