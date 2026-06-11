import pandas as pd

from ingestion import news


def test_score_headline_positive_and_negative():
    assert news.score_headline("great news for investors") > 0
    assert news.score_headline("terrible loss shocks market") < 0


def test_score_headline_knows_finance_jargon():
    assert news.score_headline("stock soars after earnings") > 0
    assert news.score_headline("profit beats expectations") > 0
    assert news.score_headline("analysts upgraded the stock") > 0
    assert news.score_headline("shares plunge on weak guidance") < 0
    assert news.score_headline("analyst downgrades hit the stock") < 0
    assert news.score_headline("company misses revenue estimates") < 0


def test_finance_lexicon_outweighs_generic_reading():
    # 'beat' is negative (violence) in stock VADER; finance sense is positive
    assert news.score_headline("company beat estimates") > 0


def test_normalize_items_handles_nested_content_format():
    items = [
        {
            "id": "abc",
            "content": {"title": "Apple wins big", "pubDate": "2026-06-10T14:00:00Z"},
        }
    ]

    rows = news.normalize_items(items)

    assert len(rows) == 1
    assert rows[0]["id"] == "abc"
    assert rows[0]["title"] == "Apple wins big"
    assert rows[0]["date"] == "2026-06-10"


def test_normalize_items_skips_malformed(caplog):
    items = [{"id": "x"}, {"content": {"title": None}}, "garbage"]

    assert news.normalize_items(items) == []


def test_save_news_dedups_by_id(tmp_path, monkeypatch):
    monkeypatch.setattr(news, "DATA_NEWS_DIR", tmp_path)
    first = pd.DataFrame(
        [{"id": "a", "date": "2026-06-09", "title": "t1", "sentiment": 0.5}]
    )
    second = pd.DataFrame(
        [
            {"id": "a", "date": "2026-06-09", "title": "t1", "sentiment": 0.5},
            {"id": "b", "date": "2026-06-10", "title": "t2", "sentiment": -0.2},
        ]
    )

    news.save_news("AAPL", first)
    news.save_news("AAPL", second)

    stored = pd.read_parquet(tmp_path / "AAPL.parquet")
    assert len(stored) == 2
    assert set(stored["id"]) == {"a", "b"}


def test_daily_sentiment_aggregates_by_date(tmp_path, monkeypatch):
    monkeypatch.setattr(news, "DATA_NEWS_DIR", tmp_path)
    df = pd.DataFrame(
        [
            {"id": "a", "date": "2026-06-09", "title": "t1", "sentiment": 0.4},
            {"id": "b", "date": "2026-06-09", "title": "t2", "sentiment": 0.2},
            {"id": "c", "date": "2026-06-10", "title": "t3", "sentiment": -0.6},
        ]
    )
    news.save_news("AAPL", df)

    daily = news.daily_sentiment("AAPL")

    assert daily.loc["2026-06-09", "sent_mean"] == 0.30000000000000004 or abs(
        daily.loc["2026-06-09", "sent_mean"] - 0.3
    ) < 1e-9
    assert daily.loc["2026-06-09", "news_count"] == 2
    assert daily.loc["2026-06-10", "news_count"] == 1


def test_daily_sentiment_empty_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(news, "DATA_NEWS_DIR", tmp_path)

    daily = news.daily_sentiment("MSFT")

    assert daily.empty
