"""Tests for table-level API delta export."""

import json
import subprocess
import sys
import tarfile
from pathlib import Path

import pandas as pd

from simtradedata.writers.duckdb_writer import DuckDBWriter


def _seed_delta_db(db_path: Path) -> None:
    writer = DuckDBWriter(db_path=str(db_path))
    try:
        market_df = pd.DataFrame({
            "date": pd.to_datetime(["2026-06-25", "2026-06-26"]),
            "open": [10.0, 10.5],
            "close": [10.2, 10.8],
            "high": [10.3, 10.9],
            "low": [9.9, 10.4],
            "preclose": [9.8, 10.2],
            "volume": [1000, 1200],
            "money": [10000.0, 12960.0],
        })
        valuation_df = pd.DataFrame({
            "date": pd.to_datetime(["2026-06-25", "2026-06-26"]),
            "pe_ttm": [12.1, 12.3],
            "pb": [1.3, 1.4],
        })

        writer.write_market_data("000001.SZ", market_df)
        writer.write_market_data("600000.SS", market_df.iloc[[0]])
        writer.write_valuation("000001.SZ", valuation_df)
        writer.write_valuation("600000.SS", valuation_df.iloc[[0]])
        writer.write_stock_status("20260626", "HALT", ["000001.SZ"])
        writer.write_stock_metadata(pd.DataFrame({
            "symbol": ["000001.SZ", "600000.SS"],
            "stock_name": ["Ping An Bank", "Shanghai Bank"],
            "listed_date": ["1991-04-03", "1999-11-10"],
            "de_listed_date": ["2900-01-01", "2900-01-01"],
            "security_type": ["1", "1"],
            "listing_status": ["1", "1"],
            "blocks": ["{}", "{}"],
        }))
    finally:
        writer.close()


def _run_export(tmp_path: Path, db_path: Path, last_sync: str, *extra: str) -> subprocess.CompletedProcess:
    output = tmp_path / "delta.tar.gz"
    return subprocess.run(
        [
            sys.executable,
            "scripts/api_export_delta.py",
            "--market",
            "cn",
            "--db",
            str(db_path),
            "--last-sync",
            last_sync,
            "--output",
            str(output),
            *extra,
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=False,
    )


def test_api_delta_exports_table_level_tarball(tmp_path):
    db_path = tmp_path / "cn.duckdb"
    _seed_delta_db(db_path)

    result = _run_export(tmp_path, db_path, "2026-06-25")

    assert result.returncode == 0, result.stderr
    archive = tmp_path / "delta.tar.gz"
    with tarfile.open(archive, "r:gz") as tar:
        names = set(tar.getnames())
        assert names == {
            "manifest.json",
            "stocks.parquet",
            "valuation.parquet",
            "stock_status.parquet",
            "stock_metadata.parquet",
        }
        manifest = json.load(tar.extractfile("manifest.json"))

    assert manifest["package_format"] == "simtradedata_api_delta_v1"
    assert manifest["market"] == "cn"
    assert manifest["from_version"] == "2026-06-25"
    assert manifest["to_version"] == "2026-06-26"
    assert manifest["up_to_date"] is False
    assert manifest["fallback_to_baseline"] is False
    assert {item["table"] for item in manifest["tables"]} == {
        "stocks",
        "valuation",
        "stock_status",
        "stock_metadata",
    }
    assert all(item["sha256"] for item in manifest["tables"])


def test_api_delta_returns_empty_manifest_when_up_to_date(tmp_path):
    db_path = tmp_path / "cn.duckdb"
    _seed_delta_db(db_path)

    result = _run_export(tmp_path, db_path, "2026-06-26")

    assert result.returncode == 0, result.stderr
    with tarfile.open(tmp_path / "delta.tar.gz", "r:gz") as tar:
        assert tar.getnames() == ["manifest.json"]
        manifest = json.load(tar.extractfile("manifest.json"))

    assert manifest["up_to_date"] is True
    assert manifest["tables"] == []


def test_api_delta_recommends_baseline_when_window_is_too_large(tmp_path):
    db_path = tmp_path / "cn.duckdb"
    _seed_delta_db(db_path)

    result = _run_export(tmp_path, db_path, "2026-04-01", "--max-days", "30")

    assert result.returncode == 0, result.stderr
    with tarfile.open(tmp_path / "delta.tar.gz", "r:gz") as tar:
        assert tar.getnames() == ["manifest.json"]
        manifest = json.load(tar.extractfile("manifest.json"))

    assert manifest["fallback_to_baseline"] is True
    assert manifest["reason"] == "delta_window_too_large"
    assert manifest["tables"] == []
