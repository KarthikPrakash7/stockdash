# Docker Milestone — Design

## Context

Milestone 1 (Python pipeline + FastAPI backend + React dashboard) is complete and working
locally via `.venv` + `npm run dev`. Per the long-term MLOps portfolio goal (see
`docs/superpowers/specs/2026-06-08-mvp-stock-dashboard-design.md`), the next milestones are
Docker, CI/CD, MLflow/W&B, K8s+Helm, Terraform, GitOps, Prometheus/Grafana. This spec covers
**only Docker**: containerizing the existing API, frontend, and retrain scheduler so the whole
stack runs via `docker-compose up`. This becomes the foundation for CI/CD and K8s later.

## Decisions

- **Three services:** `api` (FastAPI), `scheduler` (background daily retrain loop), `frontend`
  (React build served by nginx).
- **Image style:** prod-style multi-stage builds — frontend is built to static assets and served
  by nginx; backend runs `uvicorn` without `--reload`. Code changes require
  `docker-compose up --build`. This matches what would later be deployed to K8s.
- **Data persistence:** bind-mount `./data` and `./models` from the host into `api` and
  `scheduler`. The dashboard works immediately using data/models already present locally — no
  cold-start pipeline run required.
- **Networking:** nginx in the `frontend` container proxies `/api/*` to `api:8000` over the
  Docker network, and serves `index.html` for all other paths (SPA fallback). From the browser's
  perspective, frontend and API are same-origin (`localhost:3000`).
- **CORS:** existing `allow_origins=["http://localhost:5173"]` in `api/main.py` is left
  unchanged — it's only exercised by `npm run dev` (vite on :5173), not the dockerized frontend.
- **Python pipeline (`ingestion/`, `training/`) untouched** — same pattern as the React milestone.

## Architecture

```
docker-compose.yml
├── api         → Dockerfile (python:3.12-slim), uvicorn api.main:app, port 8000
├── scheduler   → same image as api, command: python -m training.scheduler
└── frontend    → frontend/Dockerfile (node build → nginx), port 3000 → 80

Bind mounts (api + scheduler):
  ./data   → /app/data
  ./models → /app/models
```

## Components

### Backend image (`Dockerfile`, repo root)
- Base: `python:3.12-slim`
- `pip install -r requirements.txt`
- `COPY . .` (excluding `frontend/`, `.venv/`, `data/`, `models/`, `tests/`, `.git/`, `docs/` —
  via `.dockerignore`)
- Default `CMD`: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
- `scheduler` service overrides `command:` to `python -m training.scheduler`, which calls
  `run_forever()` — runs the pipeline once immediately, then on a daily interval
  (`RETRAIN_INTERVAL_HOURS` from `config.py`).

### Frontend image (`frontend/Dockerfile`)
- Stage 1 (`node:20-alpine`): `npm ci && npm run build` → `frontend/dist`
- Stage 2 (`nginx:alpine`): copies `dist/` to `/usr/share/nginx/html`, copies
  `frontend/nginx.conf` to `/etc/nginx/conf.d/default.conf`
- `nginx.conf`: `location /api/ { proxy_pass http://api:8000; }`, `location / { try_files $uri
  /index.html; }`

### `docker-compose.yml`
Defines `api`, `scheduler`, `frontend` services as described above. `frontend` depends on `api`
(for proxy availability, not a hard requirement at startup).

## Error handling

- If `./data`/`./models` are empty (fresh clone), `api` returns the existing graceful
  empty/null states (`api/chart.py` already handles missing parquet/model files); `scheduler`
  populates them on its first run.

## Known limitations (out of scope for this milestone)

- **Concurrent writes:** `scheduler`'s daily run and a manual `POST /api/retrain` (triggered via
  the UI's Retrain button, served from the `api` container) could both write
  `data/`/`models/` files at the same time. No file-locking is implemented. Acceptable race for
  an MVP/portfolio context; future work could add a lock file or move retrain orchestration to a
  single process.

## Testing

Manual smoke test (no automated tests for Docker config itself, consistent with how ingestion
and dashboard smoke-testing was handled in Milestone 1):
- `docker-compose build && docker-compose up -d`
- `curl http://localhost:8000/api/tickers` — backend direct
- `curl http://localhost:3000` — frontend serves `index.html`
- `curl http://localhost:3000/api/tickers` — proxied through nginx, same response as direct
- `docker-compose logs scheduler` — shows pipeline run output
- `docker-compose down`

## Out of scope (future milestones)

CI/CD pipeline, MLflow/W&B experiment tracking, K8s/Helm deployment, Terraform/cloud storage,
GitOps (ArgoCD/Flux), Prometheus/Grafana observability.
