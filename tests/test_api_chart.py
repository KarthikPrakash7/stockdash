from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_get_chart_unknown_ticker_returns_404():
    response = client.get("/api/chart/DOESNOTEXIST_XYZ123")
    assert response.status_code == 404


def test_get_chart_response_keys(monkeypatch):
    import api.chart as mod
    import numpy as np
    import pandas as pd

    idx = pd.date_range("2024-01-01", periods=80, freq="D")
    closes = [100.0 + i for i in range(80)]
    raw_df = pd.DataFrame({
        "Open": closes, "High": [c + 1 for c in closes],
        "Low": [c - 1 for c in closes], "Close": closes,
        "Volume": [1000] * 80,
    }, index=idx)

    proc_idx = idx[19:]
    proc_closes = closes[19:]
    proc_df = pd.DataFrame({
        "close": proc_closes,
        "volume": [1000] * 61,
        "return_1d": [0.01] * 61,
        "close_lag_1": closes[18:79],
        "close_lag_2": closes[17:78],
        "close_lag_3": closes[16:77],
        "close_lag_5": closes[14:75],
        "ma_5": proc_closes,
        "ma_10": proc_closes,
        "ma_20": proc_closes,
        "sent_1d": [0.0] * 61,
        "sent_mean_7d": [0.0] * 61,
        "news_count_7d": [0.0] * 61,
        "target_next_close": closes[20:] + [0.0],
    }, index=proc_idx)

    monkeypatch.setattr(mod.pd, "read_parquet", lambda p: raw_df if "raw" in str(p) else proc_df)

    raw_dir = type("D", (), {"__truediv__": lambda s, x: type("F", (), {
        "exists": lambda self: True, "__str__": lambda self: f"data/raw/{x}"
    })()})()
    proc_dir = type("D", (), {"__truediv__": lambda s, x: type("F", (), {
        "exists": lambda self: True, "__str__": lambda self: f"data/processed/{x}"
    })()})()
    models_dir = type("D", (), {"__truediv__": lambda s, x: type("D2", (), {
        "__truediv__": lambda s2, y: type("F", (), {
            "exists": lambda self: True, "__str__": lambda self: f"models/{x}/{y}"
        })()
    })()})()

    monkeypatch.setattr(mod, "DATA_RAW_DIR", raw_dir)
    monkeypatch.setattr(mod, "DATA_PROCESSED_DIR", proc_dir)
    monkeypatch.setattr(mod, "MODELS_DIR", models_dir)

    class FakeModel:
        def load_model(self, path): pass
        def predict(self, X): return np.full(len(X), X.iloc[0]["close"] + 1.0)

    monkeypatch.setattr(mod.xgb, "XGBRegressor", FakeModel)

    response = client.get("/api/chart/FAKE")
    assert response.status_code == 200
    body = response.json()
    for key in ("ohlcv", "sma5", "sma10", "sma20", "predictions", "tomorrow_pred", "holdout_start"):
        assert key in body, f"missing key: {key}"
    assert len(body["ohlcv"]) == 80
    assert len(body["predictions"]) == 60
