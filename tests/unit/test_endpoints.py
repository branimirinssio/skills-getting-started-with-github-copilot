"""
Unit tests for FastAPI High School Management System API

Tests follow the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested (make HTTP request)
- Assert: Verify the response and side effects
"""

import pytest


class TestRootEndpoint:
    """Tests for the root GET / endpoint"""
    
    def test_root_redirect(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /
        Assert: Verify redirect response with correct location
        """
        # Arrange
        # (no setup needed, client is provided by fixture)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /activities
        Assert: Verify 200 status and all 9 activities are returned
        """
        # Arrange
        expected_activity_count = 9
        expected_activity_names = {
            "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
            "Soccer Club", "Art Club", "Music Ensemble", "Debate Team", "Science Club"
        }
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        assert set(data.keys()) == expected_activity_names
    
    def test_get_activities_structure(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /activities
        Assert: Verify each activity has required fields
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict), f"{activity_name} data should be a dict"
            assert set(activity_data.keys()) == required_fields, \
                f"{activity_name} missing or has extra fields"
            
            # Verify field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_participants_are_emails(self, client):
        """
        Arrange: TestClient is ready
        Act: Make GET request to /activities
        Assert: Verify participants are email addresses (contain @)
        """
        # Arrange
        # (no setup needed)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant, f"{participant} should be an email address"


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_activity(self, client):
        """
        Arrange: Valid activity name and new student email
        Act: Make POST request to signup endpoint
        Assert: Verify 200 status, success message, and student added to activity
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert student_email in data["message"]
        assert activity_name in data["message"]
        
        # Verify student was added to the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email in activities[activity_name]["participants"]
    
    def test_signup_activity_nonexistent(self, client):
        """
        Arrange: Invalid (non-existent) activity name
        Act: Make POST request to signup for non-existent activity
        Assert: Verify 404 status and error detail
        """
        # Arrange
        activity_name = "NonExistent Activity"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_duplicate(self, client):
        """
        Arrange: Student already signed up for an activity
        Act: Make POST request to signup again for same activity
        Assert: Verify 400 status and error detail about duplicate signup
        """
        # Arrange
        activity_name = "Chess Club"
        # michael@mergington.edu is already in Chess Club participants
        existing_student_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students_same_activity(self, client):
        """
        Arrange: Multiple new students signing up for same activity
        Act: Make two POST requests for different students
        Assert: Verify both are added successfully
        """
        # Arrange
        activity_name = "Art Club"
        student1_email = "student1@mergington.edu"
        student2_email = "student2@mergington.edu"
        
        # Act - Sign up first student
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student1_email}
        )
        
        # Act - Sign up second student
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student2_email}
        )
        
        # Assert both requests succeeded
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both students are in the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        participants = activities[activity_name]["participants"]
        assert student1_email in participants
        assert student2_email in participants

    def test_signup_invalid_email(self, client):
        """
        Arrange: Activity name and invalid email
        Act: Make POST request to signup with invalid email
        Assert: Verify 422 status and error detail
        """
        # Arrange
        activity_name = "Chess Club"
        invalid_email = "not-an-email"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": invalid_email}
        )

        # Assert
        assert response.status_code == 422


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_activity(self, client):
        """
        Arrange: Student already signed up for an activity
        Act: Make POST request to unregister
        Assert: Verify 200 status and student removed from activity
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

        # Verify student was removed from the activity
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert student_email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """
        Arrange: Invalid (non-existent) activity name
        Act: Make POST request to unregister from non-existent activity
        Assert: Verify 404 status and error detail
        """
        # Arrange
        activity_name = "NonExistent Activity"
        student_email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_signed_up(self, client):
        """
        Arrange: Student not signed up for an activity
        Act: Make POST request to unregister
        Assert: Verify 404 status and error detail
        """
        # Arrange
        activity_name = "Chess Club"
        student_email = "noone@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": student_email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_unregister_invalid_email(self, client):
        """
        Arrange: Activity name and invalid email
        Act: Make POST request to unregister with invalid email
        Assert: Verify 422 status and error detail
        """
        # Arrange
        activity_name = "Chess Club"
        invalid_email = "not-an-email"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": invalid_email}
        )

        # Assert
        assert response.status_code == 422
