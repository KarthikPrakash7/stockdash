import json
import logging
import time

import mlflow
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error

from config import (
    DATA_PROCESSED_DIR,
    HOLDOUT_DAYS,
    MLFLOW_EXPERIMENT,
    MLFLOW_TRACKING_URI,
    MODELS_DIR,
)
from watchlist import load_watchlist

logger = logging.getLogger(__name__)

MODEL_PARAMS = {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.05}

FEATURE_COLUMNS = [
    "close",
    "volume",
    "return_1d",
    "close_lag_1",
    "close_lag_2",
    "close_lag_3",
    "close_lag_5",
    "ma_5",
    "ma_10",
    "ma_20",
    "sent_1d",
    "sent_mean_7d",
    "news_count_7d",
]
TARGET_COLUMN = "target_next_close"


def split_train_holdout(df, holdout_days=HOLDOUT_DAYS):
    if len(df) <= holdout_days:
        raise ValueError(f"not enough rows ({len(df)}) for holdout of {holdout_days} days")
    return df.iloc[:-holdout_days], df.iloc[-holdout_days:]


def train_model(train_df):
    model = xgb.XGBRegressor(**MODEL_PARAMS)
    model.fit(train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN])
    return model


def log_training_run(ticker, metrics, params, artifacts=()):
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        mlflow.set_experiment(MLFLOW_EXPERIMENT)
        with mlflow.start_run(run_name=ticker):
            mlflow.set_tag("ticker", ticker)
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            for artifact in artifacts:
                mlflow.log_artifact(str(artifact))
    except Exception:
        # tracking is best-effort: a dead server must never break the pipeline
        logger.exception("mlflow logging failed for %s", ticker)


def evaluate(model, holdout_df):
    preds = model.predict(holdout_df[FEATURE_COLUMNS])
    actual = holdout_df[TARGET_COLUMN].to_numpy()
    mae = float(mean_absolute_error(actual, preds))
    rmse = float(mean_squared_error(actual, preds) ** 0.5)
    return {"mae": mae, "rmse": rmse}


def save_model(ticker, model, metrics):
    ticker_dir = MODELS_DIR / ticker
    ticker_dir.mkdir(parents=True, exist_ok=True)
    model.save_model(ticker_dir / "model.json")

    record = dict(metrics)
    record["trained_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (ticker_dir / "metrics.json").write_text(json.dumps(record, indent=2))


def train_ticker(ticker):
    processed_path = DATA_PROCESSED_DIR / f"{ticker}.parquet"
    if not processed_path.exists():
        logger.warning("no processed data for %s, skipping", ticker)
        return None

    df = pd.read_parquet(processed_path)
    train_df, holdout_df = split_train_holdout(df)
    model = train_model(train_df)
    metrics = evaluate(model, holdout_df)
    save_model(ticker, model, metrics)
    ticker_dir = MODELS_DIR / ticker
    log_training_run(
        ticker,
        metrics=metrics,
        params={
            **MODEL_PARAMS,
            "holdout_days": HOLDOUT_DAYS,
            "train_rows": len(train_df),
            "holdout_rows": len(holdout_df),
        },
        artifacts=[ticker_dir / "model.json", ticker_dir / "metrics.json"],
    )
    return metrics


def train_all(watchlist=None):
    if watchlist is None:
        watchlist = load_watchlist()
    results = {}
    for ticker in watchlist:
        metrics = train_ticker(ticker)
        if metrics is not None:
            results[ticker] = metrics
    return results
