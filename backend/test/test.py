from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_should_return_200():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "UP"


def test_status_should_return_logs():
    payload = {"status": "UP", "response_time_ms": 12.5}

    res = client.post("/status", json=payload)
    assert res.status_code == 200

    data = res.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)
    assert len(data["logs"]) <= 10
