import pytest


@pytest.mark.usefixtures("reset_activities")
class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant."""
        # Verify participant is initially there
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" in initial_participants
        
        # Unregister
        client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        # Verify participant is removed
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in updated_participants

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from non-existent activity returns 404."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_unregister_participant_not_found(self, client):
        """Test unregister when email is not in the activity returns 404."""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]

    def test_unregister_all_participants(self, client):
        """Test unregistering all participants from an activity."""
        # Get initial participants
        response = client.get("/activities")
        chess_participants = response.json()["Chess Club"]["participants"].copy()
        
        # Unregister all
        for participant in chess_participants:
            delete_response = client.delete(
                f"/activities/Chess Club/unregister?email={participant}"
            )
            assert delete_response.status_code == 200
        
        # Verify activity has no participants
        final_response = client.get("/activities")
        final_participants = final_response.json()["Chess Club"]["participants"]
        assert len(final_participants) == 0

    def test_unregister_one_from_multiple(self, client):
        """Test unregistering one participant when multiple are registered."""
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Chess Club"]["participants"])
        
        # Unregister one
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify count decreased by 1
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()["Chess Club"]["participants"])
        assert updated_count == initial_count - 1
        
        # Verify the other participant is still there
        assert "daniel@mergington.edu" in updated_response.json()["Chess Club"]["participants"]

    def test_unregister_after_signup(self, client):
        """Test unregister after signing up."""
        student_email = "newstudent@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Chess Club/signup?email={student_email}"
        )
        assert signup_response.status_code == 200
        
        # Verify student is registered
        check_response = client.get("/activities")
        assert student_email in check_response.json()["Chess Club"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Chess Club/unregister?email={student_email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify student is unregistered
        final_response = client.get("/activities")
        assert student_email not in final_response.json()["Chess Club"]["participants"]

    def test_unregister_case_sensitive_email(self, client):
        """Test that email unregister is case-sensitive."""
        # Try to unregister with different case
        response = client.delete(
            "/activities/Chess Club/unregister?email=MICHAEL@MERGINGTON.EDU"
        )
        
        # Should fail because email is case-sensitive in the list
        assert response.status_code == 404
        
        # Verify original participant is still there
        check_response = client.get("/activities")
        assert "michael@mergington.edu" in check_response.json()["Chess Club"]["participants"]
