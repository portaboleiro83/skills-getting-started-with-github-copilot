import pytest


@pytest.mark.usefixtures("reset_activities")
class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity."""
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()["Chess Club"]["participants"]
        initial_count = len(initial_participants)
        
        # Sign up new participant
        client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        # Get updated state
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()["Chess Club"]["participants"]
        updated_count = len(updated_participants)
        
        # Verify participant was added
        assert updated_count == initial_count + 1
        assert "newstudent@mergington.edu" in updated_participants

    def test_signup_nonexistent_activity(self, client):
        """Test signup to a non-existent activity returns 404."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple students can sign up for the same activity."""
        # Sign up first student
        response1 = client.post(
            "/activities/Chess Club/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            "/activities/Chess Club/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are in the activity
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants

    def test_signup_different_activities(self, client):
        """Test that a student can sign up for multiple activities."""
        student_email = "student@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={student_email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={student_email}"
        )
        assert response2.status_code == 200
        
        # Verify student is in both activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        assert student_email in activities_data["Chess Club"]["participants"]
        assert student_email in activities_data["Programming Class"]["participants"]

    def test_signup_duplicate_email_same_activity(self, client):
        """Test signup with duplicate email in same activity."""
        student_email = "newstudent@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Chess Club/signup?email={student_email}"
        )
        assert response1.status_code == 200
        
        # Duplicate signup (same activity, same email)
        response2 = client.post(
            f"/activities/Chess Club/signup?email={student_email}"
        )
        # Second signup also succeeds (backend allows duplicate registrations)
        assert response2.status_code == 200
        
        # Verify participant appears twice (current backend behavior)
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        count = participants.count(student_email)
        assert count == 2

    def test_signup_with_special_characters_email(self, client):
        """Test signup with email containing special characters."""
        response = client.post(
            "/activities/Chess Club/signup?email=john.doe%2Btest@mergington.edu"
        )
        
        assert response.status_code == 200
        
        # Verify it was added
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert "john.doe+test@mergington.edu" in participants
