from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import watchlist as wl
from ingestion.fetch import fetch_ticker, save_raw
from ingestion.features import process_ticker
from training.train import train_ticker

router = APIRouter()


class TickerRequest(BaseModel):
    ticker: str


@router.get("/watchlist")
def get_watchlist():
    return {"tickers": wl.load_watchlist()}


@router.post("/watchlist", status_code=201)
def add_to_watchlist(req: TickerRequest):
    ticker = wl.normalize(req.ticker)
    if not ticker:
        raise HTTPException(status_code=422, detail="empty ticker")
    if ticker in wl.load_watchlist():
        raise HTTPException(status_code=409, detail=f"{ticker} already in watchlist")

    df = fetch_ticker(ticker)
    if df is None:
        raise HTTPException(status_code=404, detail=f"no data found for {ticker}")

    save_raw(ticker, df)
    process_ticker(ticker)
    metrics = train_ticker(ticker)
    wl.add_ticker(ticker)
    return {"ticker": ticker, "metrics": metrics, "tickers": wl.load_watchlist()}


@router.delete("/watchlist/{ticker}")
def remove_from_watchlist(ticker: str):
    if not wl.remove_ticker(ticker):
        raise HTTPException(status_code=404, detail=f"{ticker} not in watchlist")
    return {"tickers": wl.load_watchlist()}
