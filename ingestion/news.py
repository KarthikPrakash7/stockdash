import logging

import pandas as pd
import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import DATA_NEWS_DIR
from watchlist import load_watchlist

logger = logging.getLogger(__name__)

# VADER's general-purpose lexicon misses (or misreads) finance vocabulary —
# e.g. 'beat' scores as violence. Valence scale is -4..+4 like the stock lexicon.
FINANCE_LEXICON = {
    "soar": 2.9, "soars": 2.9, "soared": 2.9, "soaring": 2.9,
    "surge": 2.6, "surges": 2.6, "surged": 2.6, "surging": 2.6,
    "rally": 2.2, "rallies": 2.2, "rallied": 2.2,
    "rebound": 1.8, "rebounds": 1.8, "rebounded": 1.8,
    "jump": 1.8, "jumps": 1.8, "jumped": 1.8,
    "climb": 1.5, "climbs": 1.5, "climbed": 1.5,
    "outperform": 2.0, "outperforms": 2.0, "outperformed": 2.0,
    "upgrade": 2.0, "upgrades": 2.0, "upgraded": 2.0,
    "bullish": 2.5,
    "breakout": 1.8,
    "beat": 1.5, "beats": 1.5,
    "buyback": 1.5, "buybacks": 1.5,
    "overweight": 1.5,
    "plunge": -2.9, "plunges": -2.9, "plunged": -2.9, "plunging": -2.9,
    "tumble": -2.5, "tumbles": -2.5, "tumbled": -2.5,
    "slump": -2.3, "slumps": -2.3, "slumped": -2.3,
    "sink": -2.0, "sinks": -2.0, "sank": -2.0,
    "slide": -1.8, "slides": -1.8, "slid": -1.8,
    "drop": -1.5, "drops": -1.5, "dropped": -1.5,
    "fall": -1.4, "falls": -1.4, "fell": -1.4,
    "downgrade": -2.0, "downgrades": -2.0, "downgraded": -2.0,
    "bearish": -2.5,
    "selloff": -2.4, "sell-off": -2.4,
    "miss": -1.8, "misses": -1.8, "missed": -1.8,
    "shortfall": -2.0,
    "layoff": -2.0, "layoffs": -2.0,
    "bankruptcy": -3.4,
    "lawsuit": -1.8, "probe": -1.5, "investigation": -1.5,
    "recall": -1.8, "recalls": -1.8,
    "warns": -1.6, "warned": -1.6, "warning": -1.6,
    "underweight": -1.5,
}

_analyzer = SentimentIntensityAnalyzer()
_analyzer.lexicon.update(FINANCE_LEXICON)


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
