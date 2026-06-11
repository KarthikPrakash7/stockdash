from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_get_tickers_returns_list(monkeypatch):
    import api.tickers as mod

    monkeypatch.setattr(mod, "WATCHLIST", ["FAKE"])
    monkeypatch.setattr(
        mod, "_load_ticker_summary",
        lambda t: {"ticker": t, "price": 100.0, "change_pct": 1.5},
    )

    response = client.get("/api/tickers")

    assert response.status_code == 200
    assert response.json() == [{"ticker": "FAKE", "price": 100.0, "change_pct": 1.5}]


def test_get_tickers_skips_missing(monkeypatch):
    import api.tickers as mod

    monkeypatch.setattr(mod, "WATCHLIST", ["GOOD", "MISSING"])
    monkeypatch.setattr(
        mod, "_load_ticker_summary",
        lambda t: {"ticker": t, "price": 50.0, "change_pct": 0.5} if t == "GOOD" else None,
    )

    response = client.get("/api/tickers")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["ticker"] == "GOOD"
