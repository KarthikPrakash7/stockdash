import pandas as pd

from ingestion import fetch


def test_fetch_ticker_returns_dataframe_on_success(monkeypatch):
    fake_df = pd.DataFrame({"Close": [1.0, 2.0], "Volume": [100, 200]})
    monkeypatch.setattr(fetch.yf, "download", lambda *a, **k: fake_df)

    result = fetch.fetch_ticker("AAPL")

    assert result is fake_df


def test_fetch_ticker_returns_none_on_exception(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr(fetch.yf, "download", boom)

    assert fetch.fetch_ticker("AAPL") is None


def test_fetch_ticker_returns_none_on_empty_dataframe(monkeypatch):
    monkeypatch.setattr(fetch.yf, "download", lambda *a, **k: pd.DataFrame())

    assert fetch.fetch_ticker("AAPL") is None
