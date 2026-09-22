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
