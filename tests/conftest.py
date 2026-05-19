"""
Pytest configuration and shared fixtures for FastAPI tests
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities as app_activities


@pytest.fixture
def initial_activities():
    """
    Capture the initial state of activities from src.app.
    
    This fixture returns a deep copy of the activities dict from the app module,
    ensuring that the fixture always reflects the current source of truth in src/app.py.
    """
    return copy.deepcopy(app_activities)


@pytest.fixture(autouse=True)
def reset_activities_state(initial_activities):
    """
    Automatically reset the activities state before each test to ensure isolation.
    
    This fixture runs before each test (autouse=True) and resets the module-level
    activities dict to its initial state. This prevents tests from interfering
    with each other when they modify the participants list.
    """
    # Clear and restore the activities dict using deep copies to prevent
    # mutations during a test from affecting the initial state
    app_activities.clear()
    app_activities.update(copy.deepcopy(initial_activities))
    
    yield
    
    # Clean up after test (optional but good practice)
    app_activities.clear()
    app_activities.update(copy.deepcopy(initial_activities))


@pytest.fixture
def client():
    """
    Provides a TestClient instance for testing the FastAPI application.
    
    The TestClient is used to make HTTP requests to the app without running
    an actual server. This fixture uses a context manager to ensure proper
    cleanup and execution of shutdown handlers.
    """
    with TestClient(app) as test_client:
        yield test_client
