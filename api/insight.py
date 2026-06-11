import logging

import pandas as pd
import xgboost as xgb
from fastapi import APIRouter

from config import DATA_PROCESSED_DIR, DATA_RAW_DIR, MODELS_DIR
from ingestion.news import daily_sentiment
from training.train import FEATURE_COLUMNS
from watchlist import load_watchlist

logger = logging.getLogger(__name__)

router = APIRouter()

SCORE_COMPONENTS = ("momentum_5d", "volume_ratio", "sentiment", "pred_gap")


def _ticker_stats(ticker):
    raw_path = DATA_RAW_DIR / f"{ticker}.parquet"
    if not raw_path.exists():
        return None
    raw = pd.read_parquet(raw_path)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    close = raw["Close"]
    volume = raw["Volume"]
    if len(close) < 21:
        return None

    momentum_5d = float(close.iloc[-1] / close.iloc[-6] - 1)
    volume_ratio = float(volume.iloc[-1] / volume.iloc[-20:].mean())

    sent = daily_sentiment(ticker)
    sentiment = float(sent["sent_mean"].tail(7).mean()) if not sent.empty else 0.0

    pred_gap = 0.0
    proc_path = DATA_PROCESSED_DIR / f"{ticker}.parquet"
    model_path = MODELS_DIR / ticker / "model.json"
    if proc_path.exists() and model_path.exists():
        try:
            proc = pd.read_parquet(proc_path)
            model = xgb.XGBRegressor()
            model.load_model(model_path)
            pred = float(model.predict(proc.iloc[[-1]][FEATURE_COLUMNS])[0])
            last_close = float(close.iloc[-1])
            pred_gap = (pred - last_close) / last_close
        except Exception:
            logger.exception("prediction failed for %s", ticker)

    return {
        "ticker": ticker,
        "momentum_5d": momentum_5d,
        "volume_ratio": volume_ratio,
        "sentiment": sentiment,
        "pred_gap": pred_gap,
    }


def _reason(row):
    parts = [
        f"5d momentum {row['momentum_5d'] * 100:+.1f}%",
        f"volume {row['volume_ratio']:.1f}× 20d avg",
    ]
    if row["sentiment"] != 0:
        parts.append(f"news sentiment {row['sentiment']:+.2f}")
    parts.append(f"model sees {row['pred_gap'] * 100:+.1f}%")
    return ", ".join(parts)


def rank_insights(stats):
    """Z-score each component across the watchlist, rank by the mean z."""
    df = pd.DataFrame(stats).set_index("ticker")
    for col in SCORE_COMPONENTS:
        std = df[col].std(ddof=0)
        df[f"z_{col}"] = 0.0 if std == 0 else (df[col] - df[col].mean()) / std
    df["score"] = df[[f"z_{c}" for c in SCORE_COMPONENTS]].mean(axis=1)
    df = df.sort_values("score", ascending=False)

    ranked = []
    for ticker, row in df.iterrows():
        ranked.append(
            {
                "ticker": ticker,
                "score": round(float(row["score"]), 3),
                "momentum_5d": round(float(row["momentum_5d"]), 4),
                "volume_ratio": round(float(row["volume_ratio"]), 2),
                "sentiment": round(float(row["sentiment"]), 3),
                "pred_gap": round(float(row["pred_gap"]), 4),
                "reason": _reason(row),
            }
        )
    return ranked


@router.get("/insight")
def get_insight():
    stats = [s for s in (_ticker_stats(t) for t in load_watchlist()) if s is not None]
    if not stats:
        return {"insights": []}
    return {"insights": rank_insights(stats)}
