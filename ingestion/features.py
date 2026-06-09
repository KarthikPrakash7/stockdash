import logging

import pandas as pd

from config import DATA_PROCESSED_DIR, DATA_RAW_DIR, WATCHLIST

logger = logging.getLogger(__name__)

LAG_DAYS = (1, 2, 3, 5)
MA_WINDOWS = (5, 10, 20)


def build_features(raw):
    df = pd.DataFrame(index=raw.index)
    df["close"] = raw["Close"]
    df["volume"] = raw["Volume"]
    df["return_1d"] = df["close"].pct_change()

    for lag in LAG_DAYS:
        df[f"close_lag_{lag}"] = df["close"].shift(lag)

    for window in MA_WINDOWS:
        df[f"ma_{window}"] = df["close"].rolling(window).mean()

    df["target_next_close"] = df["close"].shift(-1)

    return df.dropna()


def process_ticker(ticker):
    raw_path = DATA_RAW_DIR / f"{ticker}.parquet"
    if not raw_path.exists():
        logger.warning("no raw data for %s, skipping", ticker)
        return None

    raw = pd.read_parquet(raw_path)
    processed = build_features(raw)

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    processed.to_parquet(DATA_PROCESSED_DIR / f"{ticker}.parquet")
    return processed


def process_all(watchlist=WATCHLIST):
    processed = []
    for ticker in watchlist:
        result = process_ticker(ticker)
        if result is not None:
            processed.append(ticker)
    return processed
