import logging
import time

import schedule

from config import RETRAIN_INTERVAL_HOURS
from ingestion.fetch import fetch_all
from ingestion.features import process_all
from ingestion.news import collect_all_news
from training.train import train_all

logger = logging.getLogger(__name__)


def run_pipeline_once():
    fetched = fetch_all()
    news_counts = collect_all_news()
    processed = process_all()
    results = train_all()
    logger.info(
        "pipeline run complete: fetched=%s news=%s processed=%s trained=%s",
        fetched,
        news_counts,
        processed,
        list(results),
    )
    return results


def run_forever(interval_hours=RETRAIN_INTERVAL_HOURS):
    schedule.every(interval_hours).hours.do(run_pipeline_once)
    run_pipeline_once()
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_forever()
