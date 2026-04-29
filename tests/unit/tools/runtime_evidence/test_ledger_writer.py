"""Unit tests for the REQ Coverage Exemplar Ledger writer."""
from __future__ import annotations

import sqlite3
import time

import pytest

from tools.runtime_evidence.ledger_writer import (
    LedgerWriter,
    ensure_schema,
    stats,
    write_emissions,
)


@pytest.fixture()
def tmp_ledger(tmp_path):
    return tmp_path / "ledger.sqlite"


def test_ensure_schema_creates_table(tmp_ledger):
    ensure_schema(tmp_ledger)
    with sqlite3.connect(tmp_ledger) as con:
        names = {
            row[0]
            for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert "req_emission" in names


def test_ensure_schema_is_idempotent(tmp_ledger):
    ensure_schema(tmp_ledger)
    ensure_schema(tmp_ledger)  # second call must not raise
    assert tmp_ledger.exists()


def test_write_emissions_persists_one_row_per_req_id(tmp_ledger):
    spans = [
        {
            "name": "adg.records_execution_trace",
            "trace_id": "t1",
            "span_id": "s1",
            "attributes": {
                "agentic.req.ids": ["REQ-A", "REQ-B"],
                "agentic.req.layer": "L6_OBSERVABILITY",
                "agentic.req.edge_kind": "records_execution_trace",
            },
            "observed_at": 1700000000,
        },
    ]
    result = write_emissions(spans, app_id="apps_rg", source="test", db_path=tmp_ledger)
    assert result["success"] is True
    assert result["rows_written"] == 2
    assert result["distinct_req_ids"] == 2

    with sqlite3.connect(tmp_ledger) as con:
        rows = list(con.execute("SELECT req_id, layer, app_id FROM req_emission"))
    assert {r[0] for r in rows} == {"REQ-A", "REQ-B"}
    assert all(r[1] == "L6_OBSERVABILITY" for r in rows)
    assert all(r[2] == "apps_rg" for r in rows)


def test_write_emissions_silently_skips_spans_without_req_ids(tmp_ledger):
    spans = [
        {"name": "adg.x", "trace_id": "t1", "attributes": {}},
        {"name": "adg.y", "trace_id": "t2", "attributes": {"layer": "L0"}},
    ]
    result = write_emissions(spans, app_id="apps_rg", source="test", db_path=tmp_ledger)
    assert result["success"] is True
    assert result["rows_written"] == 0


def test_write_emissions_handles_string_req_ids(tmp_ledger):
    spans = [
        {
            "name": "adg.x",
            "trace_id": "t1",
            "attributes": {
                "agentic.req.ids": "REQ-A, REQ-B,REQ-C",
                "layer": "L0",
            },
        },
    ]
    result = write_emissions(spans, app_id="apps_rg", source="test", db_path=tmp_ledger)
    assert result["success"] is True
    assert result["rows_written"] == 3


def test_write_emissions_falls_back_to_legacy_keys(tmp_ledger):
    spans = [
        {
            "name": "adg.records_execution_trace",
            "trace_id": "t1",
            "attributes": {
                "req_ids": ["REQ-LEGACY"],
                "layer": "L3_ORCHESTRATION",
                "edge_kind": "records_execution_trace",
            },
        },
    ]
    result = write_emissions(spans, app_id="apps_rg", source="test", db_path=tmp_ledger)
    assert result["success"] is True
    assert result["rows_written"] == 1


def test_write_emissions_extracts_edge_kind_from_span_name_when_absent(tmp_ledger):
    spans = [
        {
            "name": "adg.flows_to",
            "trace_id": "t1",
            "attributes": {"req_ids": ["REQ-X"], "layer": "L1"},
        },
    ]
    write_emissions(spans, app_id="apps_rg", source="test", db_path=tmp_ledger)
    with sqlite3.connect(tmp_ledger) as con:
        edge_kind = con.execute("SELECT edge_kind FROM req_emission").fetchone()[0]
    assert edge_kind == "flows_to"


def test_write_emissions_fail_soft_on_locked_db(tmp_ledger, monkeypatch):
    """Writer must not raise into the caller even on sqlite errors."""
    ensure_schema(tmp_ledger)

    def _boom(*_args, **_kwargs):
        raise sqlite3.OperationalError("simulated lock")

    monkeypatch.setattr(sqlite3, "connect", _boom)
    spans = [
        {
            "name": "adg.x",
            "trace_id": "t1",
            "attributes": {"req_ids": ["REQ-A"], "layer": "L0"},
        },
    ]
    result = write_emissions(spans, app_id="apps_rg", source="test", db_path=tmp_ledger)
    assert result["success"] is False
    assert "simulated lock" in result["error"]


def test_writer_class_query_freshness_within_window(tmp_ledger):
    writer = LedgerWriter(app_id="apps_rg", source="test", db_path=tmp_ledger)
    now = int(time.time())
    spans = [
        {
            "name": "adg.x",
            "trace_id": "t1",
            "attributes": {"req_ids": ["REQ-FRESH"], "layer": "L0"},
            "observed_at": now,
        },
        {
            "name": "adg.x",
            "trace_id": "t2",
            "attributes": {"req_ids": ["REQ-STALE"], "layer": "L0"},
            "observed_at": now - 30 * 24 * 3600,  # 30d ago
        },
    ]
    writer.write(spans)
    fresh = writer.query_freshness(within_seconds=7 * 24 * 3600)
    assert "REQ-FRESH" in fresh
    assert "REQ-STALE" not in fresh
    assert fresh["REQ-FRESH"]["count"] == 1
    assert "apps_rg" in fresh["REQ-FRESH"]["apps"]


def test_stats_reports_zero_when_db_missing(tmp_path):
    missing = tmp_path / "does_not_exist.sqlite"
    s = stats(missing)
    assert s["exists"] is False
    assert s["rows"] == 0


def test_stats_after_write(tmp_ledger):
    spans = [
        {
            "name": "adg.x",
            "trace_id": "t1",
            "attributes": {"req_ids": ["REQ-A", "REQ-B"], "layer": "L0"},
        }
    ]
    write_emissions(spans, app_id="apps_rg", source="test", db_path=tmp_ledger)
    s = stats(tmp_ledger)
    assert s["exists"] is True
    assert s["rows"] == 2
    assert s["distinct_req_ids"] == 2
    assert ("apps_rg", 2) in s["top_apps"]
