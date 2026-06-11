from fastapi import APIRouter

from training.scheduler import run_pipeline_once

router = APIRouter()


@router.post("/retrain")
def retrain():
    results = run_pipeline_once()
    return {"status": "ok", "results": results}
