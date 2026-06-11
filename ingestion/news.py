import logging

import pandas as pd
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import DATA_NEWS_DIR
from watchlist import load_watchlist

logger = logging.getLogger(__name__)

_analyzer = SentimentIntensityAnalyzer()


def score_headline(title):
    return _analyzer.polarity_scores(title)["compound"]


def normalize_items(items):
    """Flatten yfinance news items to {id, date, title, sentiment} rows.

    yfinance has shipped two shapes: flat dicts with providerPublishTime,
    and nested dicts under a 'content' key with an ISO pubDate.
    """
    rows = []
    for item in items:
        if not isinstance(item, dict):
            continue
        content = item.get("content") if isinstance(item.get("content"), dict) else item
        title = content.get("title")
        if not title:
            continue
        pub = content.get("pubDate") or content.get("providerPublishTime")
        if pub is None:
            continue
        if isinstance(pub, (int, float)):
            date = pd.Timestamp(pub, unit="s").strftime("%Y-%m-%d")
        else:
            date = pd.Timestamp(pub).strftime("%Y-%m-%d")
        rows.append(
            {
                "id": item.get("id") or content.get("id") or f"{date}-{hash(title)}",
                "date": date,
                "title": title,
                "sentiment": score_headline(title),
            }
        )
    return rows


def fetch_news(ticker):
    try:
        items = yf.Ticker(ticker).news or []
    except Exception:
        logger.exception("failed to fetch news for %s", ticker)
        return []
    return normalize_items(items)


def save_news(ticker, df):
    """Append rows to the per-ticker news store, dedup by article id."""
    DATA_NEWS_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_NEWS_DIR / f"{ticker}.parquet"
    if path.exists():
        existing = pd.read_parquet(path)
        df = pd.concat([existing, df], ignore_index=True)
    df = df.drop_duplicates(subset="id", keep="first").sort_values("date")
    df.to_parquet(path, index=False)


def collect_news(ticker):
    rows = fetch_news(ticker)
    if not rows:
        return 0
    save_news(ticker, pd.DataFrame(rows))
    return len(rows)


def collect_all_news(watchlist=None):
    if watchlist is None:
        watchlist = load_watchlist()
    collected = {}
    for ticker in watchlist:
        collected[ticker] = collect_news(ticker)
    return collected


def daily_sentiment(ticker):
    """Per-date mean sentiment and article count for one ticker."""
    path = DATA_NEWS_DIR / f"{ticker}.parquet"
    if not path.exists():
        return pd.DataFrame(columns=["sent_mean", "news_count"])
    df = pd.read_parquet(path)
    grouped = df.groupby("date")["sentiment"].agg(sent_mean="mean", news_count="count")
    grouped["news_count"] = grouped["news_count"].astype(float)
    return grouped
