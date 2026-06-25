import pandas as pd

from simtradedata.fetchers.mootdx_fetcher import MootdxFetcher


def test_fetch_f10_detail_returns_none_when_source_unavailable(monkeypatch):
    fetcher = MootdxFetcher()
    monkeypatch.setattr(fetcher, "_ensure_source_available", lambda: False)

    assert fetcher.fetch_f10_detail("000001.SZ", "latest") is None


class FakeQuotesClient:
    def k(self, **_kwargs):
        return pd.DataFrame()

    def bars(self, **_kwargs):
        return pd.DataFrame(
            {
                "open": [9.20],
                "high": [9.25],
                "low": [9.07],
                "close": [9.09],
                "volume": [836563.0],
                "vol": [836563.0],
                "amount": [763280640.0],
            },
            index=pd.to_datetime(["2026-06-18"]),
        )


def test_fetch_daily_bars_drops_duplicate_volume_from_bars_fallback(monkeypatch):
    fetcher = MootdxFetcher()
    fetcher._client = FakeQuotesClient()
    monkeypatch.setattr(fetcher, "_ensure_source_available", lambda: True)
    monkeypatch.setattr(fetcher, "_ensure_client", lambda: None)

    df = fetcher.fetch_daily_bars("600000.SS", "2026-06-18", "2026-06-25")

    assert not df.empty
    assert df.columns.tolist().count("volume") == 1
    assert df.columns.is_unique
