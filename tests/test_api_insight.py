from fastapi.testclient import TestClient

from api.insight import rank_insights
from api.main import app

client = TestClient(app)


def _stats(ticker, momentum, volume_ratio, sentiment, pred_gap):
    return {
        "ticker": ticker,
        "momentum_5d": momentum,
        "volume_ratio": volume_ratio,
        "sentiment": sentiment,
        "pred_gap": pred_gap,
    }


def test_rank_insights_orders_by_composite_score():
    stats = [
        _stats("COLD", -0.05, 0.8, -0.3, -0.02),
        _stats("HOT", 0.10, 2.5, 0.4, 0.03),
        _stats("MEH", 0.01, 1.0, 0.0, 0.0),
    ]

    ranked = rank_insights(stats)

    assert [r["ticker"] for r in ranked] == ["HOT", "MEH", "COLD"]
    assert ranked[0]["score"] > ranked[1]["score"] > ranked[2]["score"]
    assert "reason" in ranked[0]


def test_rank_insights_handles_zero_variance():
    stats = [
        _stats("A", 0.01, 1.0, 0.0, 0.01),
        _stats("B", 0.01, 1.0, 0.0, 0.01),
    ]

    ranked = rank_insights(stats)

    assert len(ranked) == 2
    assert all(r["score"] == 0.0 for r in ranked)


def test_rank_insights_single_ticker():
    ranked = rank_insights([_stats("ONLY", 0.05, 1.5, 0.2, 0.01)])

    assert len(ranked) == 1


def test_insight_endpoint(monkeypatch):
    import api.insight as mod

    monkeypatch.setattr(mod, "load_watchlist", lambda: ["X", "Y"])
    monkeypatch.setattr(
        mod,
        "_ticker_stats",
        lambda t: _stats(t, 0.05, 2.0, 0.3, 0.02)
        if t == "X"
        else _stats(t, -0.02, 0.9, -0.1, -0.01),
    )

    response = client.get("/api/insight")

    assert response.status_code == 200
    body = response.json()
    assert [r["ticker"] for r in body["insights"]] == ["X", "Y"]
    assert body["insights"][0]["score"] >= body["insights"][1]["score"]
