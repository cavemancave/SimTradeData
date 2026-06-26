import pandas as pd

import scripts.download_mootdx as download_mootdx
from scripts.download_mootdx import MootdxDownloader, _latest_stock_coverage


class FakeWriter:
    def __init__(self):
        self.exrights_written = None

    def get_max_date(self, table, _symbol):
        if table == "stocks":
            return "2026-06-23"
        if table == "exrights":
            return None
        return None

    def write_market_data(self, *_args):
        raise AssertionError("market data should not be written")

    def write_exrights(self, symbol, exrights):
        self.exrights_written = (symbol, exrights)


class FakeUnifiedFetcher:
    def __init__(self):
        self.xdxr_called = False

    def fetch_daily_data(self, *_args):
        raise KeyError("datetime")

    def fetch_xdxr(self, _symbol):
        self.xdxr_called = True
        return pd.DataFrame(
            {
                "category": [1],
                "year": [2026],
                "month": [6],
                "day": [18],
                "songzhuangu": [0.0],
                "peigu": [0.0],
                "peigujia": [0.0],
                "fenhong": [1.0],
            }
        )


def test_download_stock_data_still_fetches_xdxr_when_ohlcv_fails():
    downloader = object.__new__(MootdxDownloader)
    downloader.writer = FakeWriter()
    downloader.unified_fetcher = FakeUnifiedFetcher()
    downloader.failed_stocks = []
    downloader._reconnect = lambda: None

    downloaded = downloader.download_stock_data(
        "600000.SS", "2026-01-01", "2026-06-25"
    )

    assert downloaded is True
    assert downloader.unified_fetcher.xdxr_called is True
    assert downloader.writer.exrights_written is not None


def test_download_stock_data_can_skip_ohlcv_and_fetch_xdxr():
    downloader = object.__new__(MootdxDownloader)
    downloader.writer = FakeWriter()
    downloader.unified_fetcher = FakeUnifiedFetcher()
    downloader.failed_stocks = []
    downloader._reconnect = lambda: None

    downloaded = downloader.download_stock_data(
        "600000.SS",
        "2026-01-01",
        "2026-06-25",
        include_ohlcv=False,
    )

    assert downloaded is True
    assert downloader.unified_fetcher.xdxr_called is True
    assert downloader.writer.exrights_written is not None


def test_latest_stock_coverage_counts_only_current_stock_pool_symbols():
    latest_count, total_count, ratio = _latest_stock_coverage(
        {"000001.SZ", "600000.SS", "510300.SS"},
        ["000001.SZ", "000002.SZ", "600000.SS"],
    )

    assert latest_count == 2
    assert total_count == 3
    assert ratio == 2 / 3


def test_skip_ohlcv_empty_stock_list_still_runs_remaining_phase(monkeypatch, tmp_path):
    class DummyLock:
        def __init__(self, _path):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    class FakeResult:
        def fetchall(self):
            return []

    class FakeConn:
        def execute(self, *_args, **_kwargs):
            return FakeResult()

    class FakeWriter:
        def __init__(self):
            self.conn = FakeConn()
            self.trade_days_written = False
            self.benchmark_written = False

        def get_max_date(self, _table):
            return "2026-06-24"

        def write_trade_days(self, _df):
            self.trade_days_written = True

        def write_benchmark(self, _df):
            self.benchmark_written = True

        def close(self):
            pass

    class EmptyStockListFetcher:
        def __init__(self):
            self.logged_out = False

        def login(self):
            pass

        def logout(self):
            self.logged_out = True

        def fetch_stock_list(self):
            return []

        def fetch_trade_calendar(self, *_args):
            return pd.DataFrame(
                {
                    "calendar_date": ["2026-06-25"],
                    "is_trading_day": ["1"],
                }
            )

        def fetch_index_data(self, *_args):
            return pd.DataFrame({"close": [1.0]})

    class FakeDownloader:
        last = None

        def __init__(self, **_kwargs):
            FakeDownloader.last = self
            self.writer = FakeWriter()
            self.unified_fetcher = EmptyStockListFetcher()
            self.failed_stocks = []
            self.fixed_exrights = False
            self.downloaded_fundamentals = False

        def fix_exrights_precision(self):
            self.fixed_exrights = True

        def download_fundamentals_batch(self, *_args, **_kwargs):
            self.downloaded_fundamentals = True

    monkeypatch.setattr(download_mootdx, "ProcessLock", DummyLock)
    monkeypatch.setattr(download_mootdx, "MootdxDownloader", FakeDownloader)
    monkeypatch.setattr(download_mootdx, "DEFAULT_DB_PATH", str(tmp_path / "cn.duckdb"))

    download_mootdx.download_all_data(skip_ohlcv=True)

    downloader = FakeDownloader.last
    assert downloader is not None
    assert downloader.fixed_exrights is True
    assert downloader.downloaded_fundamentals is True
    assert downloader.writer.trade_days_written is True
    assert downloader.writer.benchmark_written is True


def test_skip_bonus_fix_does_not_call_baostock_correction(monkeypatch, tmp_path):
    class DummyLock:
        def __init__(self, _path):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    class FakeResult:
        def fetchall(self):
            return []

        def fetchone(self):
            return [0]

    class FakeConn:
        def execute(self, *_args, **_kwargs):
            return FakeResult()

    class FakeWriter:
        def __init__(self):
            self.conn = FakeConn()

        def get_max_date(self, _table):
            return "2026-06-24"

        def write_trade_days(self, _df):
            pass

        def write_benchmark(self, _df):
            pass

        def close(self):
            pass

    class EmptyStockListFetcher:
        def login(self):
            pass

        def logout(self):
            pass

        def fetch_stock_list(self):
            return []

        def fetch_trade_calendar(self, *_args):
            return pd.DataFrame()

        def fetch_index_data(self, *_args):
            return pd.DataFrame()

    class FakeDownloader:
        last = None

        def __init__(self, **_kwargs):
            FakeDownloader.last = self
            self.writer = FakeWriter()
            self.unified_fetcher = EmptyStockListFetcher()
            self.failed_stocks = []
            self.fixed_exrights = False

        def fix_exrights_precision(self):
            self.fixed_exrights = True

        def download_fundamentals_batch(self, *_args, **_kwargs):
            pass

    monkeypatch.setattr(download_mootdx, "ProcessLock", DummyLock)
    monkeypatch.setattr(download_mootdx, "MootdxDownloader", FakeDownloader)
    monkeypatch.setattr(download_mootdx, "DEFAULT_DB_PATH", str(tmp_path / "cn.duckdb"))

    download_mootdx.download_all_data(skip_ohlcv=True, skip_bonus_fix=True)

    assert FakeDownloader.last.fixed_exrights is False
