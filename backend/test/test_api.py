from fastapi.testclient import TestClient
from main import app
import os

os.environ["TESTING"] = "true"


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "UP"
    assert "timestamp" in body
    assert body["timezone"] == "Asia/Kolkata (IST)"
