import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    activities.clear()
    activities.update(copy.deepcopy(original))
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_activities_returns_activity_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_participant(client):
    response = client.post("/activities/Soccer Team/signup?email=student@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up student@mergington.edu for Soccer Team"
    assert "student@mergington.edu" in activities["Soccer Team"]["participants"]


def test_duplicate_signup_is_rejected(client):
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities["Chess Club"]["participants"].count("michael@mergington.edu") == 1


def test_signup_for_missing_activity_returns_404(client):
    response = client.post("/activities/Unknown Activity/signup?email=student@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email(client):
    response = client.delete("/activities/Chess Club/participants/michael@mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404(client):
    response = client.delete("/activities/Gym Class/participants/ghost@mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
