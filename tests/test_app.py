import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities_contains_known_activity():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant_and_prevents_duplicate():
    client = TestClient(app)
    email = "testuser@example.com"
    activity = "Chess Club"

    # Sign up succeeds
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Signing up same email again should fail
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister_removes_participant():
    client = TestClient(app)
    email = "to-remove@example.com"
    activity = "Basketball Team"

    # Ensure participant is present
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Now unregister
    resp2 = client.post(f"/activities/{activity}/unregister?email={email}")
    assert resp2.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_nonexistent_returns_404():
    client = TestClient(app)
    resp = client.post("/activities/Nonexistent%20Activity/unregister?email=noone@example.com")
    assert resp.status_code == 404
