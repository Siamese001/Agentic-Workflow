"""Tests for AP-18: Prompt assembly subsystem disconnected from runtime.

Verifies _query_ap18_prompt_assembly_orphan() fires on the pre-Stage-3
disconnected state (test-only callers) and stays silent after the fix
(live orchestrator caller).
"""

from __future__ import annotations

import sqlite3

import pytest

from tools.generate.validation.gates import (
    _PROMPT_ASSEMBLY_PATH_FRAGMENTS,
    _query_ap18_prompt_assembly_orphan,
)


# ---------------------------------------------------------------------------
# Minimal in-memory SQLite helpers
# ---------------------------------------------------------------------------


def _make_conn() -> sqlite3.Connection:
    """Return an in-memory SQLite connection with nodes + edges tables."""
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE nodes (
            id            INTEGER PRIMARY KEY,
            adg_name      TEXT NOT NULL,
            entity_type   TEXT NOT NULL DEFAULT 'module',
            layer         TEXT NOT NULL DEFAULT '',
            resolved_path TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE edges (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id        INTEGER NOT NULL,
            dst_id        INTEGER NOT NULL,
            relation_type TEXT NOT NULL DEFAULT 'imports',
            source_file   TEXT NOT NULL DEFAULT ''
        );
    """)
    return conn


def _node(conn: sqlite3.Connection, nid: int, name: str, path: str) -> None:
    conn.execute(
        "INSERT INTO nodes(id,adg_name,entity_type,resolved_path) VALUES (?,?,'module',?)",
        (nid, name, path),
    )


def _edge(conn: sqlite3.Connection, src: int, dst: int, source_file: str) -> None:
    conn.execute(
        "INSERT INTO edges(src_id,dst_id,relation_type,source_file) VALUES (?,?,'imports',?)",
        (src, dst, source_file),
    )


# ---------------------------------------------------------------------------
# Constants contract
# ---------------------------------------------------------------------------


class TestAP18Constants:
    def test_path_fragments_covers_dispatcher(self) -> None:
        assert any("c0_dispatcher" in f for f in _PROMPT_ASSEMBLY_PATH_FRAGMENTS)

    def test_path_fragments_covers_bridge(self) -> None:
        assert any("c0_bridge_adapter" in f for f in _PROMPT_ASSEMBLY_PATH_FRAGMENTS)

    def test_path_fragments_covers_prompt_assembly_dir(self) -> None:
        assert any("tools/adg/prompt_assembly/" in f for f in _PROMPT_ASSEMBLY_PATH_FRAGMENTS)

    def test_path_fragments_covers_evidence_contract(self) -> None:
        assert any("c0_evidence_contract_types" in f for f in _PROMPT_ASSEMBLY_PATH_FRAGMENTS)


# ---------------------------------------------------------------------------
# Core query behaviour
# ---------------------------------------------------------------------------


class TestAP18Query:
    def test_empty_db_returns_no_violations(self) -> None:
        conn = _make_conn()
        result = _query_ap18_prompt_assembly_orphan(conn)
        assert result == []

    def test_negative_test_only_caller_fires(self) -> None:
        """Reproduces pre-Stage-3 state: dispatcher only imported by test file."""
        conn = _make_conn()
        _node(conn, 1, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py")
        _node(conn, 2, "test_dispatch", "tests/unit/tools/adg/prompt_assembly/test_c0_dispatcher.py")
        _edge(conn, 2, 1, "tests/unit/tools/adg/prompt_assembly/test_c0_dispatcher.py")
        conn.commit()
        result = _query_ap18_prompt_assembly_orphan(conn)
        assert len(result) == 1
        v = result[0]
        assert "missing_runtime_consumer" in v["evidence"]
        assert "0 live runtime callers" in v["evidence"]

    def test_positive_live_caller_does_not_fire(self) -> None:
        """After Stage 3 fix: sovereign_rag_orchestrator imports dispatcher → no violation."""
        conn = _make_conn()
        _node(conn, 1, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py")
        _node(
            conn,
            2,
            "sovereign_rag_orchestrator",
            "agentic_core/L3_orchestration/reasoning/engines/sovereign_rag_orchestrator.py",
        )
        _edge(
            conn,
            2,
            1,
            "agentic_core/L3_orchestration/reasoning/engines/sovereign_rag_orchestrator.py",
        )
        conn.commit()
        result = _query_ap18_prompt_assembly_orphan(conn)
        assert result == [], f"expected no violations but got: {result}"

    def test_mixed_callers_does_not_fire(self) -> None:
        """Both live and test callers — live caller is enough to suppress violation."""
        conn = _make_conn()
        _node(conn, 1, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py")
        _node(conn, 2, "live_orch", "agentic_core/L3_orchestration/orch.py")
        _node(conn, 3, "test_module", "tests/unit/test_d.py")
        _edge(conn, 2, 1, "agentic_core/L3_orchestration/orch.py")
        _edge(conn, 3, 1, "tests/unit/test_d.py")
        conn.commit()
        result = _query_ap18_prompt_assembly_orphan(conn)
        assert result == []

    def test_no_callers_does_not_fire(self) -> None:
        """Zero callers at all — AP-18 does NOT fire; mv_unknown_taxonomy_and_orphans covers it."""
        conn = _make_conn()
        _node(conn, 1, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py")
        conn.commit()
        result = _query_ap18_prompt_assembly_orphan(conn)
        assert result == [], (
            "AP-18 requires test_callers > 0 to fire; zero-caller case belongs to mv_unknown_taxonomy_and_orphans"
        )

    def test_non_prompt_assembly_module_ignored(self) -> None:
        """Modules outside the prompt-assembly surface are not flagged even if test-only."""
        conn = _make_conn()
        _node(conn, 1, "unrelated_mod", "agentic_core/L3_orchestration/some_helper.py")
        _node(conn, 2, "test_helper", "tests/unit/test_helper.py")
        _edge(conn, 2, 1, "tests/unit/test_helper.py")
        conn.commit()
        result = _query_ap18_prompt_assembly_orphan(conn)
        assert result == []

    def test_bridge_adapter_also_covered(self) -> None:
        """c0_bridge_adapter (another wiring surface) is caught if test-only."""
        conn = _make_conn()
        _node(conn, 1, "c0_bridge_adapter", "tools/adg/prompt_assembly/adapters/c0_bridge_adapter.py")
        _node(conn, 2, "test_bridge", "tests/unit/tools/adg/test_bridge.py")
        _edge(conn, 2, 1, "tests/unit/tools/adg/test_bridge.py")
        conn.commit()
        result = _query_ap18_prompt_assembly_orphan(conn)
        assert len(result) == 1
        assert "missing_runtime_consumer" in result[0]["evidence"]

    def test_evidence_message_format(self) -> None:
        """Evidence string contains the symbol name and key diagnostic labels."""
        conn = _make_conn()
        _node(conn, 1, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py")
        _node(conn, 2, "test_file", "tests/unit/test_x.py")
        _edge(conn, 2, 1, "tests/unit/test_x.py")
        conn.commit()
        result = _query_ap18_prompt_assembly_orphan(conn)
        assert result
        evidence = result[0]["evidence"]
        assert "c0_dispatcher" in evidence
        assert "test" in evidence.lower()
        assert "live runtime callers" in evidence

    def test_multiple_disconnected_surfaces_all_reported(self) -> None:
        """Two disconnected surfaces both appear in violations."""
        conn = _make_conn()
        _node(conn, 1, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py")
        _node(conn, 2, "c0_bridge_adapter", "tools/adg/prompt_assembly/adapters/c0_bridge_adapter.py")
        _node(conn, 3, "test_both", "tests/unit/test_both.py")
        _edge(conn, 3, 1, "tests/unit/test_both.py")
        _edge(conn, 3, 2, "tests/unit/test_both.py")
        conn.commit()
        result = _query_ap18_prompt_assembly_orphan(conn)
        assert len(result) == 2
