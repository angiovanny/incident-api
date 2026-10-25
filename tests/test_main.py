from datetime import datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from incident_api.main import Incident, app, incidents

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_incidents():
    incidents.clear()
    yield
    incidents.clear()


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


def test_create_and_store_incident_in_memory() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response = client.post("/incidents", json=incident_data)

    assert response.status_code == 201

    assert len(incidents) == 1
    assert isinstance(incidents[0], Incident)


def test_get_incidents_returns_created_incident() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response_post = client.post("/incidents", json=incident_data)

    response_get = client.get("/incidents")

    assert response_get.status_code == 200
    assert response_get.json()[0] == response_post.json()


def test_get_incident_by_id_returns_created_incident() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response_post = client.post("/incidents", json=incident_data)
    incident_id = response_post.json()["id"]

    response_get = client.get(f"/incidents/{incident_id}")

    assert response_get.status_code == 200
    assert response_get.json() == response_post.json()


def test_get_incident_by_id_returns_404_when_incident_does_not_exist() -> None:
    fake_id = str(uuid4())

    response_get = client.get(f"/incidents/{fake_id}")

    assert response_get.status_code == 404
    assert response_get.json() == {"detail": "Incident not found"}


def test_patch_incident_updates_status() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response = client.post("/incidents", json=incident_data)
    incident_id = response.json()["id"]

    patch_data = {"status": "IN_PROGRESS"}

    response_patch = client.patch(f"/incidents/{incident_id}", json=patch_data)

    assert response_patch.status_code == 200
    assert response_patch.json()["status"] == "IN_PROGRESS"


def test_patch_incident_updates_description() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response = client.post("/incidents", json=incident_data)
    incident_id = response.json()["id"]

    patch_data = {"description": "The ISP provider has technical issues."}

    response_patch = client.patch(f"/incidents/{incident_id}", json=patch_data)

    assert response_patch.status_code == 200
    assert response_patch.json()["description"] == "The ISP provider has technical issues."
    assert response_patch.json()["status"] == response.json()["status"]


def test_patch_incident_returns_404_when_incident_does_not_exist() -> None:
    fake_id = str(uuid4())

    patch_data = {"status": "IN_PROGRESS"}

    response_patch = client.patch(f"/incidents/{fake_id}", json=patch_data)

    assert response_patch.status_code == 404
    assert response_patch.json() == {"detail": "Incident not found"}


def test_patch_incident_rejects_empty_body() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response = client.post("/incidents", json=incident_data)
    incident_id = response.json()["id"]

    response_patch = client.patch(f"/incidents/{incident_id}", json={})

    assert response_patch.status_code == 422


def test_patch_incident_rejects_null_status() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response = client.post("/incidents", json=incident_data)
    incident_id = response.json()["id"]

    response_patch = client.patch(f"/incidents/{incident_id}", json={"status": None})

    assert response_patch.status_code == 422


def test_patch_incident_rejects_null_description() -> None:
    incident_data = {
        "type": "NETWORK",
        "priority": "HIGH",
        "subject": "Internet connection unavailable",
        "description": "The user cannot access the corporate network",
        "user_id": 1,
    }

    response = client.post("/incidents", json=incident_data)
    incident_id = response.json()["id"]

    response_patch = client.patch(f"/incidents/{incident_id}", json={"description": None})

    assert response_patch.status_code == 422
