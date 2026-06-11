from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.tickers import router as tickers_router
from api.chart import router as chart_router
from api.pipeline import router as pipeline_router

app = FastAPI(title="StockDash API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickers_router, prefix="/api")
app.include_router(chart_router, prefix="/api")
app.include_router(pipeline_router, prefix="/api")
