# from fastapi.testclient import TestClient
# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# from main import app

# client = TestClient(app)


# def test_health():
#     res = client.get("/health")
#     assert res.status_code == 200
#     data = res.json()
#     assert data["status"] == "UP"


# def test_status():
#     payload = {"status": "UP", "response_time_ms": 12.5}

#     res = client.post("/status", json=payload)
#     assert res.status_code == 200

#     data = res.json()
#     assert "logs" in data
#     assert isinstance(data["logs"], list)
#     assert len(data["logs"]) <= 10
