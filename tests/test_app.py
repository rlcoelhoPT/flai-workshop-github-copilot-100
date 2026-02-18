"""
Tests for the Mergington High School API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset participants to a known state before each test."""
    original_participants = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, data in activities.items():
        data["participants"] = original_participants[name]


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_200(self, client):
        response = client.get("/activities")
        assert response.status_code == 200

    def test_returns_dict(self, client):
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_contains_expected_activities(self, client):
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_has_required_fields(self, client):
        response = client.get("/activities")
        for activity in response.json().values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_signup_success(self, client):
        response = client.post("/activities/Chess Club/signup?email=new@mergington.edu")
        assert response.status_code == 200
        assert "new@mergington.edu" in response.json()["message"]

    def test_signup_adds_participant(self, client):
        client.post("/activities/Chess Club/signup?email=new@mergington.edu")
        response = client.get("/activities")
        assert "new@mergington.edu" in response.json()["Chess Club"]["participants"]

    def test_signup_unknown_activity_returns_404(self, client):
        response = client.post("/activities/Unknown Activity/signup?email=new@mergington.edu")
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self, client):
        client.post("/activities/Chess Club/signup?email=dup@mergington.edu")
        response = client.post("/activities/Chess Club/signup?email=dup@mergington.edu")
        assert response.status_code == 400




# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestUnregister:
    def test_unregister_success(self, client):
        response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response.status_code == 200
        assert "michael@mergington.edu" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
        response = client.get("/activities")
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]

    def test_unregister_unknown_activity_returns_404(self, client):
        response = client.delete("/activities/Unknown Activity/signup?email=michael@mergington.edu")
        assert response.status_code == 404

    def test_unregister_non_participant_returns_400(self, client):
        response = client.delete("/activities/Chess Club/signup?email=nobody@mergington.edu")
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# GET / (redirect)
# ---------------------------------------------------------------------------

class TestRoot:
    def test_root_redirects(self, client):
        response = client.get("/", follow_redirects=False)
        assert response.status_code in (301, 302, 307, 308)
        assert "/static/index.html" in response.headers["location"]
