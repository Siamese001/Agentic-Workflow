"""Unit tests for the runtime bucket lift utility.

Builds two in-memory SQLite databases simulating (a) a static ADG snapshot
and (b) a runtime ADG snapshot, then runs ``lift()`` and asserts the
resulting unified state — bucket=runtime rows inserted, evidence_refs
populated, idempotency preserved on re-run, HIDDEN_PATH stubs created.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.adg.runtime_bucket_lift import (  # noqa: E402
    LiftStats,
    _classify_runtime_edge,
    lift,
)


def _make_static_snapshot(tmp_path: Path) -> Path:
    """Build a minimal static ADG snapshot with the expected schema."""
    p = tmp_path / "static.sqlite"
    con = sqlite3.connect(p)
    con.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL,
            resolved_path TEXT DEFAULT ''
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT DEFAULT '',
            authority TEXT,
            bucket TEXT,
            resolution_status TEXT,
            authority_status TEXT,
            evidence_refs TEXT
        );
        """
    )
    # Seed two static nodes — one will match a runtime edge target, one won't.
    con.execute("INSERT INTO nodes (adg_name, resolved_path) VALUES (?, ?)", ("ADG::Module::A", "a.py"))
    con.execute("INSERT INTO nodes (adg_name, resolved_path) VALUES (?, ?)", ("ADG::Module::B", "b.py"))
    con.commit()
    con.close()
    return p


def _make_runtime_snapshot(tmp_path: Path) -> Path:
    """Build a minimal runtime ADG snapshot with a couple of edges."""
    p = tmp_path / "runtime.sqlite"
    con = sqlite3.connect(p)
    con.executescript(
        """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL
        );
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER,
            dst_id INTEGER,
            relation_type TEXT,
            edge_kind TEXT,
            source_file TEXT,
            line_no INTEGER,
            symbol TEXT,
            timestamp TEXT,
            execution_context TEXT,
            authority TEXT NOT NULL DEFAULT 'runtime_observed'
        );
        """
    )
    # Three nodes — A, B (also in static) and C (only in runtime → HIDDEN_PATH).
    con.execute("INSERT INTO nodes (adg_name) VALUES ('ADG::Module::A')")
    con.execute("INSERT INTO nodes (adg_name) VALUES ('ADG::Module::B')")
    con.execute("INSERT INTO nodes (adg_name) VALUES ('ADG::Module::C_runtime_only')")
    # Three runtime edges:
    # 1) A→B with full trace context (AUTHORITATIVE_RUNTIME)
    # 2) A→C_runtime_only with full trace context (HIDDEN_PATH — C not in static)
    # 3) B→A with empty execution_context (MISSING_TRACE → UNKNOWN_NOT_PROOF)
    full_ctx = json.dumps({"run_id": "run-001", "trace_id": "trace-001", "span_id": "span-001"})
    con.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, "
        "line_no, symbol, timestamp, execution_context) VALUES (1, 2, 'TOOL_CALL_RUNTIME', "
        "'tool_call', 'agentic_core/a.py', 10, 'foo', '2026-04-29T05:00:00Z', ?)",
        (full_ctx,),
    )
    con.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, "
        "line_no, symbol, timestamp, execution_context) VALUES (1, 3, 'TOOL_CALL_RUNTIME', "
        "'tool_call', 'agentic_core/a.py', 20, 'bar', '2026-04-29T05:00:01Z', ?)",
        (full_ctx,),
    )
    con.execute(
        "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, "
        "line_no, symbol, timestamp, execution_context) VALUES (2, 1, 'CALL_GRAPH_RUNTIME', "
        "'call', 'agentic_core/b.py', 30, 'baz', '2026-04-29T05:00:02Z', '')"
    )
    con.commit()
    con.close()
    return p


class TestRuntimeBucketLift:
    def test_lift_inserts_runtime_edges_into_static(self, tmp_path: Path) -> None:
        static = _make_static_snapshot(tmp_path)
        runtime = _make_runtime_snapshot(tmp_path)
        stats = lift(static_snapshot=static, runtime_snapshot=runtime)
        assert stats.runtime_edges_read == 3
        assert stats.edges_inserted == 3
        assert stats.edges_skipped_duplicate == 0

    def test_lift_creates_stub_node_for_hidden_path(self, tmp_path: Path) -> None:
        static = _make_static_snapshot(tmp_path)
        runtime = _make_runtime_snapshot(tmp_path)
        stats = lift(static_snapshot=static, runtime_snapshot=runtime)
        # C_runtime_only was not in the static graph — must be stubbed.
        assert stats.nodes_stubbed >= 1
        con = sqlite3.connect(static)
        try:
            row = con.execute(
                "SELECT id, resolved_path FROM nodes WHERE adg_name = ?",
                ("ADG::Module::C_runtime_only",),
            ).fetchone()
            assert row is not None, "stub node should have been created"
            _, resolved = row
            assert resolved == "", "stubbed node MUST have empty resolved_path (HIDDEN_PATH signal)"
        finally:
            con.close()

    def test_lift_classifies_authority_status_correctly(self, tmp_path: Path) -> None:
        static = _make_static_snapshot(tmp_path)
        runtime = _make_runtime_snapshot(tmp_path)
        lift(static_snapshot=static, runtime_snapshot=runtime)
        con = sqlite3.connect(static)
        try:
            rows = con.execute(
                "SELECT relation_type, authority_status, resolution_status, evidence_refs "
                "FROM edges WHERE bucket = 'runtime' ORDER BY id"
            ).fetchall()
            assert len(rows) == 3
            # Two edges had full trace context → AUTHORITATIVE_RUNTIME / VERIFIED_RUNTIME.
            tool_call_rows = [r for r in rows if r[0] == "TOOL_CALL_RUNTIME"]
            assert len(tool_call_rows) == 2
            for rel, auth, res, ev in tool_call_rows:
                assert auth == "AUTHORITATIVE_RUNTIME"
                assert res == "VERIFIED_RUNTIME"
                ev_obj = json.loads(ev)
                assert ev_obj["run_id"] == "run-001"
                assert ev_obj["trace_id"] == "trace-001"
                assert ev_obj["span_id"] == "span-001"
            # One edge had empty execution_context → UNKNOWN_NOT_PROOF / MISSING_TRACE.
            empty_rows = [r for r in rows if r[0] == "CALL_GRAPH_RUNTIME"]
            assert len(empty_rows) == 1
            _, auth, res, _ = empty_rows[0]
            assert auth == "UNKNOWN_NOT_PROOF"
            assert res == "MISSING_TRACE"
        finally:
            con.close()

    def test_lift_is_idempotent(self, tmp_path: Path) -> None:
        static = _make_static_snapshot(tmp_path)
        runtime = _make_runtime_snapshot(tmp_path)
        # First lift inserts everything.
        first = lift(static_snapshot=static, runtime_snapshot=runtime)
        assert first.edges_inserted == 3
        # Second lift on same inputs must skip every duplicate.
        second = lift(static_snapshot=static, runtime_snapshot=runtime)
        assert second.edges_inserted == 0
        assert second.edges_skipped_duplicate == 3

    def test_dry_run_rolls_back(self, tmp_path: Path) -> None:
        static = _make_static_snapshot(tmp_path)
        runtime = _make_runtime_snapshot(tmp_path)
        # Read row counts before.
        con = sqlite3.connect(static)
        n_edges_before = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        n_nodes_before = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        con.close()
        lift(static_snapshot=static, runtime_snapshot=runtime, dry_run=True)
        # dry_run rolls back: counts should be unchanged.
        con = sqlite3.connect(static)
        n_edges_after = con.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
        n_nodes_after = con.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        con.close()
        assert n_edges_before == n_edges_after
        assert n_nodes_before == n_nodes_after


class TestRuntimeEdgeClassifier:
    def test_full_context_yields_authoritative_runtime(self) -> None:
        ctx = json.dumps({"run_id": "r", "trace_id": "t", "span_id": "s"})
        assert _classify_runtime_edge(ctx) == ("VERIFIED_RUNTIME", "AUTHORITATIVE_RUNTIME")

    def test_empty_context_yields_unknown_not_proof(self) -> None:
        assert _classify_runtime_edge("") == ("MISSING_TRACE", "UNKNOWN_NOT_PROOF")

    def test_none_context_yields_unknown_not_proof(self) -> None:
        assert _classify_runtime_edge(None) == ("MISSING_TRACE", "UNKNOWN_NOT_PROOF")

    def test_partial_context_yields_partial(self) -> None:
        ctx = json.dumps({"trace_id": "t"})  # only trace, no run/span
        assert _classify_runtime_edge(ctx) == ("PARTIAL_TRACE", "PARTIAL")

    def test_invalid_json_yields_missing_trace(self) -> None:
        assert _classify_runtime_edge("not-json") == ("MISSING_TRACE", "UNKNOWN_NOT_PROOF")
