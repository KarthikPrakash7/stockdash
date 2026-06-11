import json

from config import DEFAULT_WATCHLIST, WATCHLIST_PATH


def load_watchlist():
    if WATCHLIST_PATH.exists():
        return json.loads(WATCHLIST_PATH.read_text())
    return list(DEFAULT_WATCHLIST)


def save_watchlist(tickers):
    WATCHLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    WATCHLIST_PATH.write_text(json.dumps(tickers, indent=2))


def normalize(ticker):
    return ticker.strip().upper()


def add_ticker(ticker):
    ticker = normalize(ticker)
    tickers = load_watchlist()
    if ticker in tickers:
        return False
    tickers.append(ticker)
    save_watchlist(tickers)
    return True


def remove_ticker(ticker):
    ticker = normalize(ticker)
    tickers = load_watchlist()
    if ticker not in tickers:
        return False
    tickers.remove(ticker)
    save_watchlist(tickers)
    return True
