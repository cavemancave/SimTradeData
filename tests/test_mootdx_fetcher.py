from simtradedata.fetchers.mootdx_fetcher import MootdxFetcher


def test_fetch_f10_detail_returns_none_when_source_unavailable(monkeypatch):
    fetcher = MootdxFetcher()
    monkeypatch.setattr(fetcher, "_ensure_source_available", lambda: False)

    assert fetcher.fetch_f10_detail("000001.SZ", "latest") is None
