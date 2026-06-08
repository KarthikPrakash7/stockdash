# MVP Stock Dashboard — Design

## Context

Long-term goal (see project brief in conversation history) is a self-retraining stock-prediction
dashboard that doubles as an MLOps/platform-engineering portfolio piece (model serving,
observability, GitOps, IaC, CI/CD, K8s). That's too large for one spec — this document covers
**only Milestone 1: the MVP** — a local, end-to-end loop of ingest → train → serve in a dashboard.
Later milestones (Docker, MLflow/W&B, K8s+Helm, Terraform, GitOps, CI/CD, Prometheus/Grafana)
get their own specs once this loop works.

## Decisions

- **Data source:** `yfinance` (free, no API key, sufficient for daily OHLCV history).
- **Prediction target:** next-day closing price (regression).
- **Watchlist:** small fixed set of 5 megacap tech tickers — `AAPL, MSFT, GOOGL, AMZN, NVDA`.
- **Model:** XGBoost regressor (stronger baseline than linear, still fast, room to grow into
  LSTM/transformer later).
- **Retraining:** simple scheduled loop (daily) plus a manual "retrain now" trigger from the
  dashboard — closer to the "self-learning" framing without needing a real scheduler/cron yet.
- **Storage:** local files (parquet) under `data/raw/` and `data/processed/`; model artifacts
  under `models/<TICKER>/`. No MinIO/S3 yet — storage is filesystem-only so it can be swapped
  for an object-store-backed layer later without touching ingestion/training/dashboard logic.
- **UI:** Streamlit (Python-native, fast to build, good for charts/metrics/buttons — lets effort
  go toward the ML/MLOps differentiators rather than UI plumbing).
- **Repo layout:** build at repo root (`ingestion/`, `training/`, `dashboard/`, `data/`,
  `models/`) — this repo *is* the project, no extra nesting under a `stock-dashboard/` subfolder.

## Architecture

```
ingestion/fetch.py    → data/raw/<TICKER>.parquet
ingestion/features.py → data/processed/<TICKER>.parquet  (lag features + next-day-close label)
training/train.py     → models/<TICKER>/model.json + models/<TICKER>/metrics.json
training/scheduler.py → loops fetch → features → train on an interval (default: daily)
dashboard/app.py      → reads data/processed + models, renders predictions vs actuals
```

Each stage communicates only through the filesystem (parquet files, JSON artifacts) — no shared
in-process state. Any stage can later be backed by an object store (MinIO/S3) or tracked via
MLflow/W&B by changing only that stage's read/write layer.

## Components

### 1. Ingestion (`ingestion/`)
- `fetch.py` — pulls daily OHLCV history per ticker via `yfinance`, writes raw parquet to
  `data/raw/<TICKER>.parquet`. Network/ticker-not-found errors are logged and that ticker is
  skipped — the batch continues for the rest of the watchlist.
- `features.py` — builds the feature set (lagged closes, rolling moving averages, daily returns,
  volume) plus the next-day-close label, writes `data/processed/<TICKER>.parquet`.

### 2. Training (`training/`)
- `train.py` — loads processed data per ticker, trains an XGBoost regressor predicting next-day
  close, evaluates on a holdout tail (last 60 days), saves `models/<TICKER>/model.json` and
  `models/<TICKER>/metrics.json` (MAE, RMSE, trained_at timestamp).
- `scheduler.py` — simple loop (`schedule` lib or `while True` + `sleep`) that re-runs
  fetch → features → train on an interval (default daily); runnable as its own background
  process, independent of the dashboard.

### 3. Dashboard (`dashboard/`)
- `app.py` (Streamlit) — ticker selector from the watchlist; line chart of actual vs predicted
  close over the holdout window; latest "tomorrow" prediction; model metrics (MAE/RMSE, last
  trained time); a "Retrain now" button that synchronously runs fetch → features → train and
  reloads. Shows a graceful "no model yet" state if training hasn't run.

## Error handling

- Ingestion: per-ticker try/except — log and skip on failure, don't crash the batch.
- Dashboard: handle missing model/data artifacts gracefully (empty/placeholder state, not a crash).

## Testing

- Unit tests for feature engineering (`features.py`) — deterministic transforms, easy to assert
  exact values on a small fixture DataFrame.
- Unit tests for the train/evaluate split + metric computation in `train.py`.
- Ingestion (network calls) and dashboard (UI) are smoke-tested manually — not unit-testable
  without heavy mocking that would test the mock, not the code.

## Out of scope (future milestones)

Docker, MLflow/W&B experiment tracking, K8s/Helm deployment, Terraform/cloud storage, GitOps
(ArgoCD/Flux), CI/CD pipeline, Prometheus/Grafana observability. Each becomes its own spec once
this MVP loop is proven.
