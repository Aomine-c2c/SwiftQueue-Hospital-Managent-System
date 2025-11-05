"""
Navigation Service for Healthcare Queue Management System
Handles hospital navigation, wayfinding, and location services
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import math


class NavigationService:
    """Service for hospital navigation and wayfinding."""

    def __init__(self):
        # Hospital layout data (simplified for demo)
        self.hospital_layout = {
            "floors": {
                "Ground": {
                    "departments": ["Emergency", "Registration", "Pharmacy", "Cafeteria"],
                    "coordinates": {"x": 0, "y": 0}
                },
                "First": {
                    "departments": ["Cardiology", "Neurology", "General Medicine"],
                    "coordinates": {"x": 0, "y": 100}
                },
                "Second": {
                    "departments": ["Radiology", "Laboratory", "Surgery"],
                    "coordinates": {"x": 0, "y": 200}
                }
            },
            "services": {
                "Emergency": {"floor": "Ground", "coordinates": {"x": 50, "y": 25}},
                "Registration": {"floor": "Ground", "coordinates": {"x": 25, "y": 25}},
                "Pharmacy": {"floor": "Ground", "coordinates": {"x": 75, "y": 25}},
                "Cardiology": {"floor": "First", "coordinates": {"x": 25, "y": 125}},
                "Neurology": {"floor": "First", "coordinates": {"x": 50, "y": 125}},
                "General Medicine": {"floor": "First", "coordinates": {"x": 75, "y": 125}},
                "Radiology": {"floor": "Second", "coordinates": {"x": 25, "y": 225}},
                "Laboratory": {"floor": "Second", "coordinates": {"x": 50, "y": 225}},
                "Surgery": {"floor": "Second", "coordinates": {"x": 75, "y": 225}}
            }
        }

    def get_directions(self, from_location: str, to_location: str) -> Dict[str, Any]:
        """Get directions between two locations in the hospital."""
        if from_location not in self.hospital_layout["services"]:
            raise ValueError(f"Unknown location: {from_location}")

        if to_location not in self.hospital_layout["services"]:
            raise ValueError(f"Unknown location: {to_location}")

        from_info = self.hospital_layout["services"][from_location]
        to_info = self.hospital_layout["services"][to_location]

        # Calculate distance and path
        distance = self._calculate_distance(from_info["coordinates"], to_info["coordinates"])
        estimated_time = self._estimate_travel_time(distance)

        # Generate step-by-step directions
        directions = self._generate_directions(from_location, to_location, from_info, to_info)

        return {
            "from": from_location,
            "to": to_location,
            "distance_meters": round(distance, 1),
            "estimated_time_minutes": round(estimated_time, 1),
            "directions": directions,
            "accessibility_notes": self._get_accessibility_notes(to_location)
        }

    def get_department_location(self, department: str) -> Dict[str, Any]:
        """Get location information for a department."""
        if department not in self.hospital_layout["services"]:
            return None

        info = self.hospital_layout["services"][department]
        return {
            "department": department,
            "floor": info["floor"],
            "coordinates": info["coordinates"],
            "nearby_services": self._get_nearby_services(department)
        }

    def get_floor_layout(self, floor: str) -> Dict[str, Any]:
        """Get layout information for a specific floor."""
        if floor not in self.hospital_layout["floors"]:
            return None

        floor_info = self.hospital_layout["floors"][floor]
        return {
            "floor": floor,
            "departments": floor_info["departments"],
            "coordinates": floor_info["coordinates"],
            "services": [
                {"name": dept, "coordinates": self.hospital_layout["services"][dept]["coordinates"]}
                for dept in floor_info["departments"]
            ]
        }

    def find_nearest_service(self, current_location: str, service_type: str) -> Dict[str, Any]:
        """Find the nearest service of a specific type."""
        if current_location not in self.hospital_layout["services"]:
            raise ValueError(f"Unknown location: {current_location}")

        current_coords = self.hospital_layout["services"][current_location]["coordinates"]

        # Find services matching the type
        matching_services = [
            service for service in self.hospital_layout["services"].keys()
            if service_type.lower() in service.lower()
        ]

        if not matching_services:
            return None

        # Find nearest
        nearest = min(
            matching_services,
            key=lambda s: self._calculate_distance(
                current_coords,
                self.hospital_layout["services"][s]["coordinates"]
            )
        )

        distance = self._calculate_distance(
            current_coords,
            self.hospital_layout["services"][nearest]["coordinates"]
        )

        return {
            "service": nearest,
            "distance_meters": round(distance, 1),
            "estimated_time_minutes": round(self._estimate_travel_time(distance), 1),
            "directions": self.get_directions(current_location, nearest)
        }

    def get_emergency_navigation(self, current_location: str) -> Dict[str, Any]:
        """Get emergency navigation to the nearest exit or emergency department."""
        emergency_routes = self.get_directions(current_location, "Emergency")

        # Add emergency-specific information
        emergency_routes["emergency_info"] = {
            "nearest_exit": "Main Entrance - 50 meters south",
            "emergency_phones": ["Reception Desk", "Nurse Station"],
            "wheelchair_accessible": True,
            "emergency_elevators": ["Elevator A", "Elevator B"]
        }

        return emergency_routes

    def get_accessible_route(self, from_location: str, to_location: str, accessibility_needs: List[str]) -> Dict[str, Any]:
        """Get an accessible route considering specific accessibility needs."""
        base_route = self.get_directions(from_location, to_location)

        # Add accessibility considerations
        accessibility_features = {
            "wheelchair": {
                "elevators": ["Elevator A (Wheelchair Accessible)", "Elevator B (Wheelchair Accessible)"],
                "ramps": ["Main Ramp", "Side Ramp"],
                "wide_corridors": True
            },
            "visual_impairment": {
                "braille_signs": True,
                "audio_guidance": "Available at main entrances",
                "tactile_flooring": "Installed in main corridors"
            },
            "hearing_impairment": {
                "visual_alerts": "Flashing lights at all stations",
                "text_notifications": "Available via patient portal"
            }
        }

        relevant_features = {}
        for need in accessibility_needs:
            if need in accessibility_features:
                relevant_features[need] = accessibility_features[need]

        base_route["accessibility_features"] = relevant_features
        base_route["accessible_route"] = True

        return base_route

    def _calculate_distance(self, coord1: Dict[str, float], coord2: Dict[str, float]) -> float:
        """Calculate Euclidean distance between two coordinates."""
        return math.sqrt(
            (coord2["x"] - coord1["x"]) ** 2 +
            (coord2["y"] - coord1["y"]) ** 2
        )

    def _estimate_travel_time(self, distance: float, walking_speed: float = 1.4) -> float:
        """Estimate travel time in minutes based on distance and walking speed (m/min)."""
        return distance / walking_speed

    def _generate_directions(self, from_loc: str, to_loc: str, from_info: Dict, to_info: Dict) -> List[str]:
        """Generate step-by-step directions."""
        directions = []

        # Check if same floor
        if from_info["floor"] == to_info["floor"]:
            directions.append(f"Stay on {from_info['floor']} floor")
        else:
            directions.append(f"Take elevator from {from_info['floor']} to {to_info['floor']}")

        # Calculate relative position
        dx = to_info["coordinates"]["x"] - from_info["coordinates"]["x"]
        dy = to_info["coordinates"]["y"] - from_info["coordinates"]["y"]

        if dx > 0:
            directions.append(f"Walk east {abs(dx)} meters")
        elif dx < 0:
            directions.append(f"Walk west {abs(dx)} meters")

        if dy > 0:
            directions.append(f"Walk north {abs(dy)} meters")
        elif dy < 0:
            directions.append(f"Walk south {abs(dy)} meters")

        directions.append(f"Arrive at {to_loc}")

        return directions

    def _get_nearby_services(self, department: str) -> List[str]:
        """Get services nearby to a department."""
        dept_coords = self.hospital_layout["services"][department]["coordinates"]

        nearby = []
        for service, info in self.hospital_layout["services"].items():
            if service != department:
                distance = self._calculate_distance(dept_coords, info["coordinates"])
                if distance <= 50:  # Within 50 meters
                    nearby.append(service)

        return nearby

    def _get_accessibility_notes(self, location: str) -> List[str]:
        """Get accessibility notes for a location."""
        notes = []

        # General accessibility notes
        notes.append("Wheelchair accessible entrance available")
        notes.append("Elevators equipped with audio announcements")

        # Location-specific notes
        if location == "Emergency":
            notes.append("24/7 accessible emergency entrance")
            notes.append("Ambulance bay with ramp access")
        elif location == "Radiology":
            notes.append("Wide doorways for medical equipment")
            notes.append("Accessible changing rooms available")

        return notes


# Global navigation service instance
navigation_service = NavigationService()