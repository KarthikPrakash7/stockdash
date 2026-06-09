import pandas as pd
import pytest

from training import train


class _StubModel:
    def __init__(self, preds):
        self._preds = preds

    def predict(self, X):
        return self._preds


def _holdout_df(targets):
    data = {col: [0.0] * len(targets) for col in train.FEATURE_COLUMNS}
    data[train.TARGET_COLUMN] = targets
    return pd.DataFrame(data)


def test_split_train_holdout_splits_by_row_count():
    df = pd.DataFrame({"x": range(100)})

    train_df, holdout_df = train.split_train_holdout(df, holdout_days=20)

    assert len(train_df) == 80
    assert len(holdout_df) == 20
    assert train_df.iloc[-1]["x"] == 79
    assert holdout_df.iloc[0]["x"] == 80


def test_split_train_holdout_raises_when_not_enough_rows():
    df = pd.DataFrame({"x": range(10)})

    with pytest.raises(ValueError):
        train.split_train_holdout(df, holdout_days=20)


def test_evaluate_computes_mae_and_rmse():
    holdout = _holdout_df(targets=[10.0, 12.0, 14.0])
    model = _StubModel(preds=[11.0, 11.0, 11.0])

    metrics = train.evaluate(model, holdout)

    # errors: -1, 1, 3 -> MAE = (1+1+3)/3; RMSE = sqrt((1+1+9)/3)
    assert metrics["mae"] == pytest.approx(5 / 3)
    assert metrics["rmse"] == pytest.approx((11 / 3) ** 0.5)
