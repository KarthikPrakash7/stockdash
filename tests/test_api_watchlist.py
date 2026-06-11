import pandas as pd
from fastapi.testclient import TestClient

import watchlist as wl
from api.main import app

client = TestClient(app)


def _use_tmp_path(tmp_path, monkeypatch):
    monkeypatch.setattr(wl, "WATCHLIST_PATH", tmp_path / "watchlist.json")


def _stub_pipeline(monkeypatch, fetch_result="df"):
    import api.watchlist as mod

    df = pd.DataFrame({"Close": [1.0]}) if fetch_result == "df" else None
    monkeypatch.setattr(mod, "fetch_ticker", lambda t: df)
    monkeypatch.setattr(mod, "save_raw", lambda t, d: None)
    monkeypatch.setattr(mod, "process_ticker", lambda t: None)
    monkeypatch.setattr(mod, "train_ticker", lambda t: {"mae": 1.0, "rmse": 2.0})


def test_get_watchlist_returns_default(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)

    response = client.get("/api/watchlist")

    assert response.status_code == 200
    assert response.json() == {"tickers": wl.DEFAULT_WATCHLIST}


def test_add_ticker_runs_pipeline_and_persists(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)
    _stub_pipeline(monkeypatch)

    response = client.post("/api/watchlist", json={"ticker": "tsla"})

    assert response.status_code == 201
    body = response.json()
    assert body["ticker"] == "TSLA"
    assert "TSLA" in body["tickers"]
    assert "TSLA" in wl.load_watchlist()


def test_add_duplicate_ticker_409(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)
    _stub_pipeline(monkeypatch)

    response = client.post("/api/watchlist", json={"ticker": "AAPL"})

    assert response.status_code == 409


def test_add_unknown_ticker_404(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)
    _stub_pipeline(monkeypatch, fetch_result=None)

    response = client.post("/api/watchlist", json={"ticker": "ZZZZQ"})

    assert response.status_code == 404
    assert "ZZZZQ" not in wl.load_watchlist()


def test_remove_ticker(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)

    response = client.delete("/api/watchlist/AAPL")

    assert response.status_code == 200
    assert "AAPL" not in response.json()["tickers"]


def test_remove_missing_ticker_404(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)

    response = client.delete("/api/watchlist/ZZZZ")

    assert response.status_code == 404
