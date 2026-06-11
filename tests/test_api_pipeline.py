from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_retrain_calls_pipeline_and_returns_ok(monkeypatch):
    import api.pipeline as mod

    monkeypatch.setattr(mod, "run_pipeline_once", lambda: {"AAPL": {"mae": 1.0, "rmse": 2.0}})

    response = client.post("/api/retrain")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["results"] == {"AAPL": {"mae": 1.0, "rmse": 2.0}}
