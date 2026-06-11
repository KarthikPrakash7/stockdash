import watchlist


def _use_tmp_path(tmp_path, monkeypatch):
    monkeypatch.setattr(watchlist, "WATCHLIST_PATH", tmp_path / "watchlist.json")


def test_load_returns_default_when_no_file(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)

    assert watchlist.load_watchlist() == watchlist.DEFAULT_WATCHLIST


def test_add_ticker_persists_and_normalizes(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)

    added = watchlist.add_ticker(" tsla ")

    assert added is True
    assert "TSLA" in watchlist.load_watchlist()


def test_add_existing_ticker_returns_false(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)

    assert watchlist.add_ticker("AAPL") is False
    assert watchlist.load_watchlist().count("AAPL") == 1


def test_remove_ticker(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)

    removed = watchlist.remove_ticker("AAPL")

    assert removed is True
    assert "AAPL" not in watchlist.load_watchlist()


def test_remove_missing_ticker_returns_false(tmp_path, monkeypatch):
    _use_tmp_path(tmp_path, monkeypatch)

    assert watchlist.remove_ticker("ZZZZ") is False
