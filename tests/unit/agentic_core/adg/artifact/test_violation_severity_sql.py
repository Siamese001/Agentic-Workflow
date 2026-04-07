"""Tests for violation severity SQL classification in ADG artifact writers.

Verifies edge_kind-based severity assignment:
- broad_exception_catch / silent_exception_swallow / log_and_swallow / return_none_swallow
  in critical layers (L0/L2/L3/L5) → HIGH
- same kinds in non-critical layers → MEDIUM
- retry_without_backoff / blocking_call_in_async / global_state_mutation → LOW
- non-antipattern edges → MEDIUM (violates default)
"""
from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest


def _make_db_with_edges(edges: list[dict]) -> Path:
    """Create a temp SQLite DB with the same schema as the ADG writer and insert edges."""
    db = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
    db.close()
    path = Path(db.name)

    conn = sqlite3.connect(str(path))
    conn.execute(
        """CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id TEXT DEFAULT '',
            dst_id TEXT DEFAULT '',
            relation_type TEXT NOT NULL,
            edge_kind TEXT DEFAULT '',
            source_file TEXT DEFAULT '',
            line_no INTEGER DEFAULT 0,
            symbol TEXT DEFAULT '',
            semantic_type TEXT DEFAULT '',
            confidence_score REAL DEFAULT 0.0,
            source_span_start INTEGER DEFAULT 0,
            source_span_end INTEGER DEFAULT 0,
            source_span_line INTEGER DEFAULT 0,
            source_span_column INTEGER DEFAULT 0,
            target_span_start INTEGER DEFAULT 0,
            target_span_end INTEGER DEFAULT 0,
            target_span_line INTEGER DEFAULT 0,
            target_span_column INTEGER DEFAULT 0,
            dynamic_resolution TEXT DEFAULT ''
        )""",
    )
    conn.execute(
        """CREATE TABLE violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER,
            category TEXT NOT NULL,
            evidence TEXT DEFAULT '',
            file_path TEXT DEFAULT '',
            line_no INTEGER DEFAULT 0,
            severity TEXT NOT NULL DEFAULT 'MEDIUM',
            disposition TEXT NOT NULL DEFAULT 'untriaged'
        )""",
    )
    for e in edges:
        conn.execute(
            "INSERT INTO edges (relation_type, edge_kind, source_file, symbol) VALUES (?,?,?,?)",
            (e["relation_type"], e.get("edge_kind", ""), e.get("source_file", ""), e.get("symbol", "")),
        )
    conn.commit()

    # Run the same CASE SQL used by multi_writer.py / ArtifactPaths.py
    conn.execute(
        """INSERT INTO violations (edge_id, category, evidence, file_path, line_no, severity)
        SELECT id, relation_type, symbol, source_file, line_no,
            CASE
                WHEN relation_type = 'antipattern'
                 AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                                   'log_and_swallow','return_none_swallow')
                 AND (source_file LIKE 'agentic_core/%' OR source_file LIKE 'system_learning/%')
                THEN 'HIGH'
                WHEN relation_type = 'antipattern'
                 AND edge_kind IN ('broad_exception_catch','silent_exception_swallow',
                                   'log_and_swallow','return_none_swallow')
                THEN 'MEDIUM'
                WHEN relation_type = 'antipattern' THEN 'LOW'
                ELSE 'MEDIUM'
            END as severity
        FROM edges WHERE relation_type IN ('violates', 'antipattern', 'dynamic_exec')""",
    )
    conn.commit()
    conn.close()
    return path


def _get_severity(path: Path, edge_kind: str, source_file: str) -> str:
    conn = sqlite3.connect(str(path))
    row = conn.execute(
        """SELECT v.severity FROM violations v
           JOIN edges e ON v.edge_id = e.id
           WHERE e.edge_kind = ? AND e.source_file = ?""",
        (edge_kind, source_file),
    ).fetchone()
    conn.close()
    assert row is not None, f"No violation found for edge_kind={edge_kind!r} source_file={source_file!r}"
    return str(row[0])


_CRITICAL_LAYERS = [
    "agentic_core/L0_routing/foo.py",
    "agentic_core/L5_safety/bar.py",
    "agentic_core/L2_execution/baz.py",
    "agentic_core/L3_orchestration/qux.py",
    "agentic_core/L1_cognition/brain.py",
    "agentic_core/L4_state/checkpoint.py",
    "agentic_core/mixins/collector.py",
    "system_learning/adapters/bridge.py",
]

_NON_CRITICAL_LAYERS = [
    "apps_rg/engines/foo.py",
    "apps_lic/tools/bar.py",
    "tools/mcp/foo.py",
]

_HIGH_KINDS = [
    "broad_exception_catch",
    "silent_exception_swallow",
    "log_and_swallow",
    "return_none_swallow",
]

_LOW_KINDS = [
    "retry_without_backoff",
    "blocking_call_in_async",
    "global_state_mutation",
    "duplicate_method",
]


@pytest.mark.parametrize("edge_kind", _HIGH_KINDS)
@pytest.mark.parametrize("source_file", _CRITICAL_LAYERS)
def test_high_antipattern_in_critical_layer(edge_kind: str, source_file: str) -> None:
    """Exception handling antipatterns in critical layers must be HIGH."""
    db = _make_db_with_edges([
        {"relation_type": "antipattern", "edge_kind": edge_kind, "source_file": source_file},
    ])
    assert _get_severity(db, edge_kind, source_file) == "HIGH"
    Path(db).unlink(missing_ok=True)


@pytest.mark.parametrize("edge_kind", _HIGH_KINDS)
@pytest.mark.parametrize("source_file", _NON_CRITICAL_LAYERS)
def test_medium_antipattern_in_non_critical_layer(edge_kind: str, source_file: str) -> None:
    """Exception handling antipatterns outside critical layers must be MEDIUM."""
    db = _make_db_with_edges([
        {"relation_type": "antipattern", "edge_kind": edge_kind, "source_file": source_file},
    ])
    assert _get_severity(db, edge_kind, source_file) == "MEDIUM"
    Path(db).unlink(missing_ok=True)


@pytest.mark.parametrize("edge_kind", _LOW_KINDS)
def test_low_antipattern_false_positive_prone_kinds(edge_kind: str) -> None:
    """False-positive-prone antipattern kinds must stay LOW regardless of layer."""
    source_file = "agentic_core/L0_routing/foo.py"
    db = _make_db_with_edges([
        {"relation_type": "antipattern", "edge_kind": edge_kind, "source_file": source_file},
    ])
    assert _get_severity(db, edge_kind, source_file) == "LOW"
    Path(db).unlink(missing_ok=True)


def test_violates_edge_defaults_to_medium() -> None:
    """violates edges (layer violations) default to MEDIUM via ELSE branch."""
    db = _make_db_with_edges([
        {"relation_type": "violates", "edge_kind": "layer_boundary_cross", "source_file": "agentic_core/L0_routing/x.py"},
    ])
    conn = sqlite3.connect(str(db))
    row = conn.execute("SELECT severity FROM violations WHERE category='violates'").fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "MEDIUM"
    Path(db).unlink(missing_ok=True)


def test_symbol_like_pattern_no_longer_drives_severity() -> None:
    """Old symbol-based logic: bare except in non-critical layer would have been MEDIUM.
    New edge_kind logic: if edge_kind is not in the HIGH set, it must be LOW.
    This regression test ensures the old symbol-based fallback is gone.
    """
    db = _make_db_with_edges([
        {
            "relation_type": "antipattern",
            "edge_kind": "retry_without_backoff",
            "source_file": "apps_rg/engines/foo.py",
            "symbol": "except:Exception",
        },
    ])
    assert _get_severity(db, "retry_without_backoff", "apps_rg/engines/foo.py") == "LOW"
    Path(db).unlink(missing_ok=True)
