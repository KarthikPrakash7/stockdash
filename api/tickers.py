import pandas as pd
from fastapi import APIRouter

from config import DATA_RAW_DIR
from watchlist import load_watchlist

router = APIRouter()


def _load_ticker_summary(ticker):
    path = DATA_RAW_DIR / f"{ticker}.parquet"
    if not path.exists():
        return None
    df = pd.read_parquet(path)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    close = df["Close"] if "Close" in df.columns else df.iloc[:, 3]
    price = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if len(close) >= 2 else price
    change_pct = (price - prev) / prev * 100
    return {"ticker": ticker, "price": round(price, 2), "change_pct": round(change_pct, 2)}


@router.get("/tickers")
def get_tickers():
    results = []
    for ticker in load_watchlist():
        summary = _load_ticker_summary(ticker)
        if summary:
            results.append(summary)
    return results
