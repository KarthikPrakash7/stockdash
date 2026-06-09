from training import scheduler


def test_run_pipeline_once_calls_stages_in_order(monkeypatch):
    calls = []

    def fake_fetch_all():
        calls.append("fetch")
        return ["AAPL"]

    def fake_process_all():
        calls.append("process")
        return ["AAPL"]

    def fake_train_all():
        calls.append("train")
        return {"AAPL": {"mae": 1.0, "rmse": 2.0}}

    monkeypatch.setattr(scheduler, "fetch_all", fake_fetch_all)
    monkeypatch.setattr(scheduler, "process_all", fake_process_all)
    monkeypatch.setattr(scheduler, "train_all", fake_train_all)

    result = scheduler.run_pipeline_once()

    assert calls == ["fetch", "process", "train"]
    assert result == {"AAPL": {"mae": 1.0, "rmse": 2.0}}
