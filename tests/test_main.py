from datetime import datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient

from incident_api.main import app

client = TestClient(app)


def test_root_returns_api_status() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "Incident API is running"}


def test_get_incidents_returns_empty_list() -> None:
    response = client.get("/incidents")

    assert response.status_code == 200
    assert response.json() == []


def test_create_incident() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response = client.post("/incidents", json=incident_data)

    assert response.status_code == 201
    original_data = response.json()
    incident_id = UUID(original_data.pop("id"))
    created_at = datetime.fromisoformat(original_data.pop("created_at"))
    assert original_data.pop("status") == "OPEN"
    assert isinstance(incident_id, UUID)
    assert created_at.tzinfo is not None
    assert created_at.utcoffset() == timedelta(0)
    assert original_data == incident_data


def test_create_incident_rejects_invalid_user_id() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": "abc",
    }

    response = client.post("/incidents", json=incident_data)

    assert response.status_code == 422


def test_create_incident_rejects_invalid_priority() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "SUPER_URGENT",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response = client.post("/incidents", json=incident_data)

    assert response.status_code == 422


def test_create_incident_rejects_invalid_type() -> None:
    incident_data = {
        "type": "UNKNOWN",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response = client.post("/incidents", json=incident_data)

    assert response.status_code == 422
