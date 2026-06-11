import mlflow

from training import train


def _use_tmp_tracking(tmp_path, monkeypatch):
    uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    monkeypatch.setattr(train, "MLFLOW_TRACKING_URI", uri)
    # default artifact root is ./mlruns relative to cwd — keep it inside tmp_path
    monkeypatch.chdir(tmp_path)
    return uri


def test_log_training_run_records_params_and_metrics(tmp_path, monkeypatch):
    uri = _use_tmp_tracking(tmp_path, monkeypatch)

    train.log_training_run(
        "AAPL",
        metrics={"mae": 1.5, "rmse": 2.0},
        params={"n_estimators": 200, "holdout_days": 60},
    )

    mlflow.set_tracking_uri(uri)
    runs = mlflow.search_runs(experiment_names=[train.MLFLOW_EXPERIMENT])
    assert len(runs) == 1
    run = runs.iloc[0]
    assert run["metrics.mae"] == 1.5
    assert run["metrics.rmse"] == 2.0
    assert run["params.n_estimators"] == "200"
    assert run["tags.ticker"] == "AAPL"


def test_log_training_run_logs_artifacts(tmp_path, monkeypatch):
    uri = _use_tmp_tracking(tmp_path, monkeypatch)
    artifact = tmp_path / "model.json"
    artifact.write_text("{}")

    train.log_training_run("MSFT", metrics={"mae": 1.0}, params={}, artifacts=[artifact])

    mlflow.set_tracking_uri(uri)
    runs = mlflow.search_runs(experiment_names=[train.MLFLOW_EXPERIMENT])
    run_id = runs.iloc[0]["run_id"]
    artifact_names = [a.path for a in mlflow.MlflowClient().list_artifacts(run_id)]
    assert "model.json" in artifact_names


def test_log_training_run_swallows_mlflow_errors(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("tracking server down")

    monkeypatch.setattr(train.mlflow, "set_experiment", boom)

    # must not raise — a dead tracking server should never break the pipeline
    train.log_training_run("AAPL", metrics={"mae": 1.0}, params={})
