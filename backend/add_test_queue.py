"""
Quick script to add test queue entries for testing
"""
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.models import QueueEntry, Service, User

def main():
    db = SessionLocal()
    
    try:
        # Check if we have services
        services = db.query(Service).all()
        if not services:
            print("Creating test service...")
            service = Service(
                id=1,
                name="Emergency Care",
                description="Emergency medical treatment",
                estimated_time=30,
                department="Emergency"
            )
            db.add(service)
            db.commit()
            service_id = 1
        else:
            service_id = services[0].id
            print(f"Using existing service: {services[0].name} (ID: {service_id})")
        
        # Check if we have users
        users = db.query(User).filter_by(role='patient').all()
        if not users:
            print("Creating test patients...")
            test_patients = [
                {"name": "John Doe", "email": "john@test.com", "priority": "high"},
                {"name": "Jane Smith", "email": "jane@test.com", "priority": "medium"},
                {"name": "Bob Wilson", "email": "bob@test.com", "priority": "low"},
                {"name": "Alice Brown", "email": "alice@test.com", "priority": "urgent"},
                {"name": "Charlie Davis", "email": "charlie@test.com", "priority": "medium"},
            ]
            
            for patient in test_patients:
                user = User(
                    name=patient["name"],
                    email=patient["email"],
                    phone=f"+256770001234",
                    role="patient",
                    hashed_password="dummy_hash"
                )
                db.add(user)
            db.commit()
            users = db.query(User).filter_by(role='patient').all()
        else:
            print(f"Using {len(users)} existing patients")
        
        # Add test queue entries
        print("Adding test queue entries...")
        priorities = ["high", "medium", "low", "urgent", "medium"]
        
        for i, user in enumerate(users[:5], start=1):
            queue_entry = QueueEntry(
                queue_number=100 + i,
                service_id=service_id,
                patient_id=user.id,
                priority=priorities[i-1],
                status="waiting",
                created_at=datetime.now()
            )
            db.add(queue_entry)
            print(f"  ✓ Added: {user.name} - Ticket: {100+i} - Priority: {priorities[i-1]}")
        
        db.commit()
        print("\n✅ Successfully added test queue entries!")
        
        # Show summary
        waiting_count = db.query(QueueEntry).filter_by(status='waiting').count()
        print(f"\nTotal waiting patients: {waiting_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
