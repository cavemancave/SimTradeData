"""Tests for BaoStock fetcher session handling."""

import importlib
from types import SimpleNamespace

from scripts.download import run_baostock_download
from simtradedata.fetchers.baostock_fetcher import BaoStockFetcher


def reset_baostock_state():
    BaoStockFetcher._bs_logged_in = False
    BaoStockFetcher._bs_login_count = 0


def test_login_retries_transient_baostock_failure(monkeypatch):
    reset_baostock_state()
    retry_module = importlib.import_module("simtradedata.resilience.retry")
    monkeypatch.setattr(retry_module.time, "sleep", lambda _: None)

    attempts = []

    def fake_login():
        attempts.append(1)
        if len(attempts) == 1:
            return SimpleNamespace(error_code="100010", error_msg="网络接收错误。")
        return SimpleNamespace(error_code="0", error_msg="success")

    monkeypatch.setattr("simtradedata.fetchers.baostock_fetcher.bs.login", fake_login)

    fetcher = BaoStockFetcher()
    fetcher.login()

    assert len(attempts) == 2
    assert BaoStockFetcher._bs_logged_in is True
    assert BaoStockFetcher._bs_login_count == 1

    reset_baostock_state()


def test_baostock_phase_keeps_index_constituents_enabled(monkeypatch):
    captured = {}

    def fake_download_all_data(**kwargs):
        captured.update(kwargs)

    monkeypatch.setitem(
        __import__("sys").modules,
        "download_efficient",
        SimpleNamespace(download_all_data=fake_download_all_data),
    )

    assert run_baostock_download(valuation_only=True) is True
    assert captured["skip_fundamentals"] is True
    assert captured["skip_metadata"] is False
    assert captured["valuation_only"] is True
