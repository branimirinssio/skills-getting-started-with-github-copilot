"""
Pytest configuration and shared fixtures for FastAPI tests
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def initial_activities():
    """Store the initial state of activities for test isolation"""
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team and drills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Soccer practice and friendly matches",
            "schedule": "Wednesdays and Saturdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Painting, drawing, and visual arts exploration",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["grace@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Band and orchestral music performance",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        }
    }


@pytest.fixture(autouse=True)
def reset_activities_state(initial_activities):
    """
    Automatically reset the activities state before each test to ensure isolation.
    
    This fixture runs before each test (autouse=True) and resets the module-level
    activities dict to its initial state. This prevents tests from interfering
    with each other when they modify the participants list.
    """
    # Clear and restore the activities dict
    activities.clear()
    activities.update(initial_activities)
    
    yield
    
    # Clean up after test (optional but good practice)
    activities.clear()
    activities.update(initial_activities)


@pytest.fixture
def client():
    """
    Provides a TestClient instance for testing the FastAPI application.
    
    The TestClient is used to make HTTP requests to the app without running
    an actual server. This fixture is used in all endpoint tests.
    """
    return TestClient(app)
