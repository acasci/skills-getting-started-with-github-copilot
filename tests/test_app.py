"""
Backend FastAPI tests using AAA (Arrange-Act-Assert) pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities data before each test"""
    # Arrange: Store original activities
    original_activities = {
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
            "description": "Competitive basketball training and games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Soccer practice and competitive matches",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": []
        },
        "Art Studio": {
            "description": "Express creativity through painting and drawing",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Drama Club": {
            "description": "Theater arts and performance training",
            "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": []
        },
        "Debate Team": {
            "description": "Learn public speaking and argumentation skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": []
        },
        "Science Club": {
            "description": "Hands-on experiments and scientific exploration",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirects_to_index(self, client):
        # Arrange: Client is ready
        
        # Act: Call the root endpoint
        response = client.get("/", follow_redirects=False)
        
        # Assert: Should redirect to static index.html
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        # Arrange: Activities are already set up in fixture
        
        # Act: Get all activities
        response = client.get("/activities")
        
        # Assert: Should return all activities
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 9
    
    def test_activity_structure(self, client):
        # Arrange: Activities exist
        
        # Act: Get activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Each activity should have required fields
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club


class TestSignupForActivity:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_existing_activity(self, client):
        # Arrange: Test email and activity
        email = "test@mergington.edu"
        activity = "Basketball Team"
        
        # Act: Sign up for activity
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert: Should successfully sign up
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        # Arrange: Invalid activity name
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act: Try to sign up for nonexistent activity
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert: Should return 404
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_prevention(self, client):
        # Arrange: Email already signed up
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act: Try to sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert: Should return 400 error
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is already signed up"
    
    def test_multiple_signups_different_activities(self, client):
        # Arrange: Same email, different activities
        email = "multi@mergington.edu"
        
        # Act: Sign up for multiple activities
        response1 = client.post(f"/activities/Basketball Team/signup?email={email}")
        response2 = client.post(f"/activities/Soccer Club/signup?email={email}")
        
        # Assert: Both should succeed
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify participant in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Basketball Team"]["participants"]
        assert email in activities_data["Soccer Club"]["participants"]


class TestUnregisterFromActivity:
    """Test the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        # Arrange: Participant already signed up
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Act: Unregister from activity
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Assert: Should successfully unregister
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Removed {email} from {activity}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        # Arrange: Invalid activity
        email = "test@mergington.edu"
        activity = "Nonexistent Activity"
        
        # Act: Try to unregister from nonexistent activity
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Assert: Should return 404
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_registered_participant(self, client):
        # Arrange: Email not registered
        email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        # Act: Try to unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Assert: Should return 400 error
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_signup_and_unregister_flow(self, client):
        # Arrange: New participant
        email = "flow@mergington.edu"
        activity = "Art Studio"
        
        # Act: Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert: Signup successful
        assert signup_response.status_code == 200
        
        # Act: Unregister
        unregister_response = client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Assert: Unregister successful
        assert unregister_response.status_code == 200
        
        # Verify participant is gone
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
