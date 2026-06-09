from pathlib import Path

WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

ROOT_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
MODELS_DIR = ROOT_DIR / "models"

HOLDOUT_DAYS = 60
RETRAIN_INTERVAL_HOURS = 24
