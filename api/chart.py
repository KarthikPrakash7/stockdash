import pandas as pd
import xgboost as xgb
from fastapi import APIRouter, HTTPException

from config import DATA_PROCESSED_DIR, DATA_RAW_DIR, HOLDOUT_DAYS, MODELS_DIR
from training.train import FEATURE_COLUMNS, split_train_holdout

router = APIRouter()


@router.get("/chart/{ticker}")
def get_chart(ticker: str):
    raw_path = DATA_RAW_DIR / f"{ticker}.parquet"
    if not raw_path.exists():
        raise HTTPException(status_code=404, detail=f"{ticker} not found")

    raw = pd.read_parquet(raw_path)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    ohlcv = []
    for ts, row in raw.iterrows():
        ohlcv.append({
            "time": ts.strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 4),
            "high": round(float(row["High"]), 4),
            "low": round(float(row["Low"]), 4),
            "close": round(float(row["Close"]), 4),
        })

    proc_path = DATA_PROCESSED_DIR / f"{ticker}.parquet"
    model_path = MODELS_DIR / ticker / "model.json"

    if not proc_path.exists() or not model_path.exists():
        return {
            "ohlcv": ohlcv, "sma5": [], "sma10": [], "sma20": [],
            "predictions": [], "tomorrow_pred": None, "holdout_start": None,
        }

    proc = pd.read_parquet(proc_path)

    def _sma_series(col):
        return [{"time": ts.strftime("%Y-%m-%d"), "value": round(float(v), 4)}
                for ts, v in proc[col].items()]

    sma5 = _sma_series("ma_5")
    sma10 = _sma_series("ma_10")
    sma20 = _sma_series("ma_20")

    _, holdout_df = split_train_holdout(proc, HOLDOUT_DAYS)
    model = xgb.XGBRegressor()
    model.load_model(model_path)

    preds = model.predict(holdout_df[FEATURE_COLUMNS])
    predictions = [
        {
            "time": ts.strftime("%Y-%m-%d"),
            "actual": round(float(act), 4),
            "predicted": round(float(pred), 4),
        }
        for ts, act, pred in zip(holdout_df.index, holdout_df["target_next_close"], preds)
    ]

    tomorrow_pred = round(float(model.predict(proc.iloc[[-1]][FEATURE_COLUMNS])[0]), 2)
    holdout_start = holdout_df.index[0].strftime("%Y-%m-%d")

    return {
        "ohlcv": ohlcv,
        "sma5": sma5,
        "sma10": sma10,
        "sma20": sma20,
        "predictions": predictions,
        "tomorrow_pred": tomorrow_pred,
        "holdout_start": holdout_start,
    }
