import logging

import pandas as pd

from config import DATA_PROCESSED_DIR, DATA_RAW_DIR
from ingestion.news import daily_sentiment
from watchlist import load_watchlist

logger = logging.getLogger(__name__)

LAG_DAYS = (1, 2, 3, 5)
MA_WINDOWS = (5, 10, 20)


def build_features(raw, news_daily=None):
    df = pd.DataFrame(index=raw.index)
    df["close"] = raw["Close"]
    df["volume"] = raw["Volume"]
    df["return_1d"] = df["close"].pct_change()

    for lag in LAG_DAYS:
        df[f"close_lag_{lag}"] = df["close"].shift(lag)

    for window in MA_WINDOWS:
        df[f"ma_{window}"] = df["close"].rolling(window).mean()

    # news sentiment: zero-filled where no headlines exist (yfinance only
    # provides recent news, so history accumulates from deployment onward)
    date_keys = df.index.strftime("%Y-%m-%d")
    if news_daily is not None and not news_daily.empty:
        df["sent_1d"] = news_daily["sent_mean"].reindex(date_keys).fillna(0).to_numpy()
        daily_count = news_daily["news_count"].reindex(date_keys).fillna(0).to_numpy()
    else:
        df["sent_1d"] = 0.0
        daily_count = 0.0
    df["sent_mean_7d"] = df["sent_1d"].rolling(7, min_periods=1).mean()
    df["news_count_7d"] = pd.Series(daily_count, index=df.index).rolling(7, min_periods=1).sum()

    df["target_next_close"] = df["close"].shift(-1)

    return df.dropna()


def process_ticker(ticker):
    raw_path = DATA_RAW_DIR / f"{ticker}.parquet"
    if not raw_path.exists():
        logger.warning("no raw data for %s, skipping", ticker)
        return None

    raw = pd.read_parquet(raw_path)
    processed = build_features(raw, news_daily=daily_sentiment(ticker))

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    processed.to_parquet(DATA_PROCESSED_DIR / f"{ticker}.parquet")
    return processed


def process_all(watchlist=None):
    if watchlist is None:
        watchlist = load_watchlist()
    processed = []
    for ticker in watchlist:
        result = process_ticker(ticker)
        if result is not None:
            processed.append(ticker)
    return processed
