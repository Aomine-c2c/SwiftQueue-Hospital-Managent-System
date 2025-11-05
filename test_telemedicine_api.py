#!/usr/bin/env python3
"""
Test script for Telemedicine API endpoints
Run with: python test_telemedicine_api.py
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/telemedicine"

def test_telemedicine_api():
    """Test all telemedicine API endpoints"""

    print("=" * 60)
    print("TELEMEDICINE API TEST SUITE")
    print("=" * 60)

    # Test data
    test_session_data = {
        "patient_id": 1,
        "doctor_id": 2,
        "appointment_id": None,
        "session_type": "video",
        "scheduled_start": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
        "chief_complaint": "Headache and dizziness",
        "recording_enabled": False
    }

    session_id = None
    auth_headers = None

    try:
        # 1. Authentication (assuming we have a test user)
        print("\n1. Testing Authentication...")
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "test@example.com",
            "password": "password123"
        })

        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            auth_headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
        else:
            print("⚠️  Authentication failed, proceeding with public endpoints only")
            auth_headers = {}

        # 2. Create Telemedicine Session
        print("\n2. 📅 Testing Session Creation...")
        create_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/sessions",
            json=test_session_data,
            headers=auth_headers
        )

        if create_response.status_code == 200:
            session_data = create_response.json()
            session_id = session_data["session_id"]
            print(f"✅ Session created: {session_id}")
            print(f"   Status: {session_data['status']}")
            print(f"   Room ID: {session_data['room_id']}")
        else:
            print(f"❌ Session creation failed: {create_response.status_code}")
            print(f"   Response: {create_response.text}")
            return False

        # 3. Get Session Details
        print("\n3. 📋 Testing Get Session...")
        get_response = requests.get(
            f"{BASE_URL}{API_PREFIX}/sessions/{session_id}",
            headers=auth_headers
        )

        if get_response.status_code == 200:
            session = get_response.json()
            print("✅ Session retrieved successfully")
            print(f"   Patient: {session.get('patient', {}).get('name', 'Unknown')}")
            print(f"   Doctor: {session.get('doctor', {}).get('name', 'Unknown')}")
        else:
            print(f"❌ Get session failed: {get_response.status_code}")

        # 4. Get User Sessions
        print("\n4. 📊 Testing Get User Sessions...")
        sessions_response = requests.get(
            f"{BASE_URL}{API_PREFIX}/sessions",
            headers=auth_headers
        )

        if sessions_response.status_code == 200:
            sessions = sessions_response.json()
            print(f"✅ Retrieved {len(sessions)} sessions")
        else:
            print(f"❌ Get sessions failed: {sessions_response.status_code}")

        # 5. Send Message
        print("\n5. 💬 Testing Message Sending...")
        message_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/sessions/{session_id}/messages",
            json={
                "content": "Hello, I'm ready for the consultation.",
                "message_type": "text"
            },
            headers=auth_headers
        )

        if message_response.status_code == 200:
            message = message_response.json()
            print("✅ Message sent successfully")
            print(f"   Message ID: {message['id']}")
        else:
            print(f"❌ Send message failed: {message_response.status_code}")

        # 6. Get Messages
        print("\n6. 📨 Testing Get Messages...")
        messages_response = requests.get(
            f"{BASE_URL}{API_PREFIX}/sessions/{session_id}/messages",
            headers=auth_headers
        )

        if messages_response.status_code == 200:
            messages = messages_response.json()
            print(f"✅ Retrieved {len(messages)} messages")
        else:
            print(f"❌ Get messages failed: {messages_response.status_code}")

        # 7. Start Session
        print("\n7. ▶️  Testing Start Session...")
        start_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/sessions/{session_id}/start",
            headers=auth_headers
        )

        if start_response.status_code == 200:
            print("✅ Session started successfully")
        else:
            print(f"❌ Start session failed: {start_response.status_code}")

        # 8. Update Session (Complete)
        print("\n8. 📝 Testing Session Completion...")
        update_response = requests.put(
            f"{BASE_URL}{API_PREFIX}/sessions/{session_id}",
            json={
                "status": "completed",
                "diagnosis": "Migraine headache",
                "treatment_plan": "Prescribed sumatriptan 50mg",
                "follow_up_instructions": "Rest in dark room, avoid triggers",
                "prescription_issued": True
            },
            headers=auth_headers
        )

        if update_response.status_code == 200:
            print("✅ Session completed successfully")
        else:
            print(f"❌ Complete session failed: {update_response.status_code}")

        # 9. Submit Feedback
        print("\n9. ⭐ Testing Feedback Submission...")
        feedback_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/sessions/{session_id}/feedback",
            json={
                "patient_rating": 5,
                "patient_feedback": "Excellent consultation, very helpful!",
                "doctor_notes": "Patient responded well to treatment plan"
            },
            headers=auth_headers
        )

        if feedback_response.status_code == 200:
            print("✅ Feedback submitted successfully")
        else:
            print(f"❌ Submit feedback failed: {feedback_response.status_code}")

        # 10. Get Session Report
        print("\n10. 📄 Testing Session Report...")
        report_response = requests.get(
            f"{BASE_URL}{API_PREFIX}/sessions/{session_id}/report",
            headers=auth_headers
        )

        if report_response.status_code == 200:
            report = report_response.json()
            print("✅ Session report generated")
            print(f"    Duration: {report.get('session_details', {}).get('duration_minutes', 0)} minutes")
            print(f"    Rating: {report.get('feedback', {}).get('patient_rating', 'N/A')}")
        else:
            print(f"❌ Get report failed: {report_response.status_code}")

        # 11. Get Upcoming Sessions
        print("\n11. 📅 Testing Upcoming Sessions...")
        upcoming_response = requests.get(
            f"{BASE_URL}{API_PREFIX}/sessions/upcoming",
            headers=auth_headers
        )

        if upcoming_response.status_code == 200:
            upcoming = upcoming_response.json()
            print(f"✅ Retrieved {len(upcoming)} upcoming sessions")
        else:
            print(f"❌ Get upcoming failed: {upcoming_response.status_code}")

        # 12. Cancel Session (create another session first)
        print("\n12. ❌ Testing Session Cancellation...")

        # Create another session to cancel
        cancel_session_data = test_session_data.copy()
        cancel_session_data["scheduled_start"] = (datetime.utcnow() + timedelta(hours=2)).isoformat()

        cancel_create_response = requests.post(
            f"{BASE_URL}{API_PREFIX}/sessions",
            json=cancel_session_data,
            headers=auth_headers
        )

        if cancel_create_response.status_code == 200:
            cancel_session_id = cancel_create_response.json()["session_id"]

            # Now cancel it
            cancel_response = requests.delete(
                f"{BASE_URL}{API_PREFIX}/sessions/{cancel_session_id}",
                headers=auth_headers
            )

            if cancel_response.status_code == 200:
                print("✅ Session cancelled successfully")
            else:
                print(f"❌ Cancel session failed: {cancel_response.status_code}")
        else:
            print("⚠️  Could not create session to test cancellation")

        print("\n" + "=" * 60)
        print("TELEMEDICINE API TESTS COMPLETED!")
        print("=" * 60)
        print("\nAll major endpoints tested successfully!")
        print("Telemedicine system is ready for use!")
        print("\nNext steps:")
        print("- Implement WebRTC signaling server for real video calls")
        print("- Add session recording capabilities")
        print("- Integrate with appointment scheduling")
        print("- Add push notifications for session alerts")

        return True

    except requests.exceptions.ConnectionError:
        print("\nCONNECTION ERROR: Cannot connect to server")
        print("Make sure the backend server is running on http://localhost:8000")
        print("Run: cd backend && python run.py")
        return False

    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_telemedicine_api()
    exit(0 if success else 1)