"""Simple test of just the query part"""
import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.models.models import QueueEntry

db = SessionLocal()

try:
    # Test query
    service_id = 1
    print(f"Querying for service_id={service_id}, status='waiting'")
    
    patients = db.query(QueueEntry).filter(
        QueueEntry.service_id == service_id,
        QueueEntry.status == "waiting"
    ).all()
    
    print(f"Found {len(patients)} waiting patients")
    for p in patients:
        print(f"  - ID: {p.id}, Queue#: {p.queue_number}, Priority: {p.priority}")
    
    if patients:
        first = patients[0]
        print(f"\nTrying to update status...")
        first.status = "called"
        db.commit()
        print("Success!")
        
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    print(traceback.format_exc())
finally:
    db.close()
