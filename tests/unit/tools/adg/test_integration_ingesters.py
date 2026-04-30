"""Smoke tests for tools/adg/integration ingesters.

Each ingester runs in seed mode against an isolated tmp SQLite that
mirrors the canonical schema. Verifies idempotency (re-run yields 0 new).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest


@pytest.fixture
def tmp_adg_sqlite(tmp_path: Path) -> Path:
    """Create a minimal ADG-shaped SQLite with empty edges/nodes/violations tables."""
    p = tmp_path / "adg_indexed_test.sqlite"
    con = sqlite3.connect(p)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL,
            entity_type TEXT,
            layer TEXT,
            identity_kind TEXT,
            confidence REAL,
            resolved_path TEXT,
            precision_type TEXT,
            span_start INTEGER, span_end INTEGER,
            span_line INTEGER, span_column INTEGER,
            span_end_line INTEGER, span_end_column INTEGER,
            logical_sequence_id TEXT,
            control_path_id TEXT,
            temporal_order INTEGER,
            type_surface TEXT,
            enclosing_symbol TEXT,
            body_hash TEXT
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER, dst_id INTEGER,
            relation_type TEXT, edge_kind TEXT,
            source_file TEXT, line_no INTEGER,
            symbol TEXT, semantic_type TEXT,
            confidence_score REAL,
            source_span_start INTEGER, source_span_end INTEGER,
            source_span_line INTEGER, source_span_column INTEGER,
            target_span_start INTEGER, target_span_end INTEGER,
            target_span_line INTEGER, target_span_column INTEGER,
            dynamic_resolution TEXT,
            authority TEXT, bucket TEXT,
            resolution_status TEXT, authority_status TEXT,
            evidence_refs TEXT
        );
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER, category TEXT, evidence TEXT,
            file_path TEXT, line_no INTEGER,
            disposition TEXT, disposition_source TEXT,
            disposition_date TEXT, severity TEXT, violation_class TEXT
        );
        """
    )
    # Seed a couple of edges that calls_ingester can promote
    cur.execute(
        "INSERT INTO nodes (adg_name, resolved_path, layer) VALUES ('a.py', 'a.py', 'L1')"
    )
    cur.execute(
        "INSERT INTO nodes (adg_name, resolved_path, layer) VALUES ('b.py', 'b.py', 'L2')"
    )
    cur.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, "
        "confidence_score) VALUES (1, 2, 'instantiates', 'static', 'a.py', 10, 0.9)"
    )
    con.commit()
    con.close()
    return p


def test_calls_ingester_promotes_and_is_idempotent(tmp_adg_sqlite: Path) -> None:
    from tools.adg.integration.calls_ingester import ingest

    inserted_first = ingest(tmp_adg_sqlite)
    assert inserted_first >= 1

    inserted_second = ingest(tmp_adg_sqlite)
    assert inserted_second == 0


def test_otel_ingester_seed(tmp_adg_sqlite: Path) -> None:
    from tools.adg.integration.otel_ingester import ingest

    n = ingest(tmp_adg_sqlite)
    assert n == 3
    # idempotent
    assert ingest(tmp_adg_sqlite) == 0


def test_branch_coverage_seed(tmp_adg_sqlite: Path) -> None:
    from tools.adg.integration.branch_coverage_bridge import ingest

    n = ingest(tmp_adg_sqlite)
    assert n >= 1
    assert ingest(tmp_adg_sqlite) == 0


def test_secret_access_seed(tmp_adg_sqlite: Path) -> None:
    from tools.adg.integration.secret_access_ingester import ingest

    n = ingest(tmp_adg_sqlite)
    assert n == 3
    assert ingest(tmp_adg_sqlite) == 0


def test_hitl_decision_seed(tmp_adg_sqlite: Path) -> None:
    from tools.adg.integration.hitl_decision_ingester import ingest

    n = ingest(tmp_adg_sqlite)
    assert n == 3
    assert ingest(tmp_adg_sqlite) == 0


def test_profiling_bridge_seed(tmp_adg_sqlite: Path) -> None:
    from tools.adg.integration.profiling_bridge import ingest

    n = ingest(tmp_adg_sqlite)
    assert n == 3
    assert ingest(tmp_adg_sqlite) == 0


def test_severity_enums_pure() -> None:
    """W4 invariant: severity_enums has zero _emit_* calls and zero lifecycle imports."""
    from pathlib import Path

    src = Path("apps_shared/types/severity_enums.py").read_text(encoding="utf-8")
    # Strip docstrings/comments before checking for actual calls
    import re
    code_only = re.sub(r'"""[\s\S]*?"""', '', src)
    code_only = re.sub(r"'''[\s\S]*?'''", '', code_only)
    code_only = re.sub(r'#.*', '', code_only)
    assert "_emit_" not in code_only, "severity_enums must contain no _emit_* calls (code)"
    assert "lifecycle_trace_contract" not in code_only, "severity_enums must not import lifecycle_trace_contract (code)"
    # Round-trip
    from apps_shared.types.severity_enums import (
        sovereign_severity,
        sovereign_event_type,
        to_log_level,
    )
    import logging
    assert sovereign_severity.CRITICAL.value == "CRITICAL"
    assert to_log_level(sovereign_severity.INFO) == logging.INFO
    assert sovereign_event_type.AUDIT_STARTED.value == "AUDIT_STARTED"


def test_shim_backward_compat() -> None:
    """W4 invariant: sovereign_severity_types still exports the same canonical names."""
    from apps_shared.types.sovereign_severity_types import (
        sovereign_severity,
        SovereignSeverity,
        sovereign_event_type,
        SovereignEventType,
        severity_log_levels,
        sovereign_event_categories,
        to_log_level,
    )
    assert sovereign_severity is SovereignSeverity
    assert sovereign_event_type is SovereignEventType
    assert "GOVERNANCE" in sovereign_event_categories
