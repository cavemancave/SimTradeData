import pandas as pd

from scripts.download_efficient import EfficientBaoStockDownloader


class FakeWriter:
    def __init__(self):
        self.valuation_writes = []

    def get_max_date(self, table, symbol=None):
        return None

    def begin(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def write_valuation(self, symbol, df):
        self.valuation_writes.append((symbol, df.copy()))


class FakeFetcher:
    def fetch_unified_daily_data(self, symbol, start_date, end_date):
        return pd.DataFrame(
            {
                "date": ["2026-06-24"],
                "peTTM": [10.0],
                "isST": [0],
                "tradestatus": [1],
            }
        )


class FakeSplitter:
    def __init__(self, split_data):
        self._split_data = split_data

    def split_data(self, df):
        return self._split_data


def make_valuation_only_downloader(split_data):
    downloader = EfficientBaoStockDownloader.__new__(EfficientBaoStockDownloader)
    downloader.valuation_only = True
    downloader.status_cache = {}
    downloader.failed_stocks = []
    downloader.writer = FakeWriter()
    downloader.unified_fetcher = FakeFetcher()
    downloader.data_splitter = FakeSplitter(split_data)
    return downloader


def test_valuation_only_batch_counts_written_valuation_as_updated():
    valuation = pd.DataFrame(
        {"pe_ttm": [10.0]},
        index=pd.to_datetime(["2026-06-24"]),
    )
    status = pd.DataFrame(
        {"date": ["2026-06-24"], "isST": [0], "tradestatus": [1]}
    )
    downloader = make_valuation_only_downloader(
        {"valuation": valuation, "status": status}
    )

    result = downloader.download_batch(
        ["000001.SZ"],
        "2015-01-01",
        "2026-06-24",
    )

    assert result == [{"stock_code": "000001.SZ"}]
    assert len(downloader.writer.valuation_writes) == 1
    assert downloader.status_cache["000001.SZ"].equals(status)


def test_valuation_only_batch_does_not_count_empty_split_as_updated():
    downloader = make_valuation_only_downloader(
        {
            "valuation": pd.DataFrame(),
            "status": pd.DataFrame(),
        }
    )

    result = downloader.download_batch(
        ["000001.SZ"],
        "2015-01-01",
        "2026-06-24",
    )

    assert result == []
    assert downloader.writer.valuation_writes == []
    assert downloader.status_cache == {}
