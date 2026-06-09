import json

import pandas as pd
import streamlit as st
import xgboost as xgb

from config import DATA_PROCESSED_DIR, HOLDOUT_DAYS, MODELS_DIR, WATCHLIST
from training.scheduler import run_pipeline_once
from training.train import FEATURE_COLUMNS, TARGET_COLUMN, split_train_holdout

st.set_page_config(page_title="Self-Learning Stock Dashboard", layout="wide")
st.title("Self-Learning Stock Dashboard")

ticker = st.sidebar.selectbox("Ticker", WATCHLIST)

if st.sidebar.button("Retrain now"):
    with st.spinner("Fetching data and retraining all tickers..."):
        run_pipeline_once()
    st.sidebar.success("Retrain complete")

processed_path = DATA_PROCESSED_DIR / f"{ticker}.parquet"
model_path = MODELS_DIR / ticker / "model.json"
metrics_path = MODELS_DIR / ticker / "metrics.json"

if not processed_path.exists() or not model_path.exists():
    st.info(f"No model yet for {ticker}. Click 'Retrain now' in the sidebar to train one.")
else:
    df = pd.read_parquet(processed_path)
    _, holdout_df = split_train_holdout(df, HOLDOUT_DAYS)

    model = xgb.XGBRegressor()
    model.load_model(model_path)

    preds = model.predict(holdout_df[FEATURE_COLUMNS])
    chart_df = pd.DataFrame(
        {"actual": holdout_df[TARGET_COLUMN].to_numpy(), "predicted": preds},
        index=holdout_df.index,
    )

    st.subheader(f"{ticker}: actual vs predicted next-day close (last {HOLDOUT_DAYS} trading days)")
    st.line_chart(chart_df)

    latest_features = df.iloc[[-1]][FEATURE_COLUMNS]
    tomorrow_pred = float(model.predict(latest_features)[0])
    st.metric("Predicted next close", f"${tomorrow_pred:,.2f}")

    metrics = json.loads(metrics_path.read_text())
    col1, col2, col3 = st.columns(3)
    col1.metric("MAE", f"{metrics['mae']:.3f}")
    col2.metric("RMSE", f"{metrics['rmse']:.3f}")
    col3.metric("Last trained (UTC)", metrics["trained_at"])
