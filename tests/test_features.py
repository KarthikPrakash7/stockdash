import pandas as pd
import pytest

from ingestion import features


def _make_raw(n=30):
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    close = pd.Series([100.0 + i for i in range(n)], index=idx)
    volume = pd.Series([1000 + i * 10 for i in range(n)], index=idx)
    return pd.DataFrame({"Close": close, "Volume": volume})


def test_build_features_computes_expected_columns_and_values():
    raw = _make_raw(30)

    result = features.build_features(raw)

    assert len(result) == 10
    first = result.iloc[0]
    assert first["close"] == 119.0
    assert first["volume"] == 1190
    assert first["close_lag_1"] == 118.0
    assert first["close_lag_2"] == 117.0
    assert first["close_lag_3"] == 116.0
    assert first["close_lag_5"] == 114.0
    assert first["ma_5"] == pytest.approx(117.0)
    assert first["ma_10"] == pytest.approx(114.5)
    assert first["ma_20"] == pytest.approx(109.5)
    assert first["return_1d"] == pytest.approx(1 / 118)
    assert first["target_next_close"] == 120.0


def test_build_features_drops_rows_with_nans():
    raw = _make_raw(30)

    result = features.build_features(raw)

    assert not result.isna().any().any()
