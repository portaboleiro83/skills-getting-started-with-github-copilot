import pytest


@pytest.mark.usefixtures("reset_activities")
class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify we have 9 activities
        assert len(data) == 9
        
        # Verify key activities exist
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Theater Production" in data

    def test_get_activities_structure(self, client):
        """Test that activities have correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        # Verify each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            
            # Verify types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_chess_club_data(self, client):
        """Test that Chess Club has correct initial data."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_get_activities_participants_are_lists(self, client):
        """Test that all participants are in list format."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            participants = activity_data["participants"]
            assert isinstance(participants, list)
            # Verify each participant is a string (email)
            for participant in participants:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation
