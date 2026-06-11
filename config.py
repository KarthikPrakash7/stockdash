import os
from pathlib import Path

DEFAULT_WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

ROOT_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DATA_NEWS_DIR = ROOT_DIR / "data" / "news"
MODELS_DIR = ROOT_DIR / "models"
WATCHLIST_PATH = ROOT_DIR / "data" / "watchlist.json"

HOLDOUT_DAYS = 60
RETRAIN_INTERVAL_HOURS = 24

MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", f"sqlite:///{ROOT_DIR / 'mlflow.db'}")
MLFLOW_EXPERIMENT = "stock-portfolio"
