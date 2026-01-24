from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200


def test_status():
    payload = {"status": "UP", "response_time_ms": 12.5}

    res = client.post("/status", json=payload)
    assert res.status_code == 200

    data = res.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)
    assert len(data["logs"]) <= 10
