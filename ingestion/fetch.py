import logging

import yfinance as yf

from config import DATA_RAW_DIR, WATCHLIST

logger = logging.getLogger(__name__)


def fetch_ticker(ticker):
    try:
        df = yf.download(ticker, period="5y", interval="1d", progress=False, auto_adjust=False)
    except Exception:
        logger.exception("failed to fetch %s", ticker)
        return None

    if df.empty:
        logger.warning("no data returned for %s", ticker)
        return None

    return df


def save_raw(ticker, df):
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DATA_RAW_DIR / f"{ticker}.parquet")


def fetch_all(watchlist=WATCHLIST):
    fetched = []
    for ticker in watchlist:
        df = fetch_ticker(ticker)
        if df is not None:
            save_raw(ticker, df)
            fetched.append(ticker)
    return fetched
