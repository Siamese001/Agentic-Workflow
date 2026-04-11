"""Tests for gate_p1_prompt_wiring — prompt-assembly runtime wiring gate.

Covers:
  - Gate attributes and catalog registration (no regressions to existing entries).
  - Positive case: live runtime caller → gate passes.
  - Negative case: test-only caller → gate blocks with explicit message.
  - Fallback path: inline SQL fires when materialized view is absent.
  - Extra: zero callers → gate passes (not AP-18's concern; mv_unknown handles it).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ops_scripts.ci.adg_gates.gate_p1_prompt_wiring import (
    PromptAssemblyWiringGate,
    _VIEW,
)
from ops_scripts.ci.adg_gates.gate_ssot_catalog import GATE_INDEX, build_index


# ---------------------------------------------------------------------------
# Minimal SQLite helpers
# ---------------------------------------------------------------------------


def _make_db(tmp_path: Path, with_mv: bool = True) -> Path:
    """Create a minimal ADG SQLite with nodes + edges (+ optional MV)."""
    db = tmp_path / "adg_test.sqlite"
    conn = sqlite3.connect(str(db))
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
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
    """)
    conn.execute("INSERT INTO meta VALUES ('commit_sha', 'test_sha_abc')")
    if with_mv:
        conn.executescript("""
            CREATE TABLE mv_prompt_assembly_wiring_gaps (
                snapshot_id   TEXT,
                node_id       INTEGER,
                target_symbol TEXT,
                target_file   TEXT,
                layer         TEXT,
                total_callers INTEGER,
                live_callers  INTEGER,
                test_callers  INTEGER,
                gap_type      TEXT
            );
        """)
    conn.commit()
    conn.close()
    return db


def _node(conn: sqlite3.Connection, nid: int, name: str, path: str) -> None:
    conn.execute(
        "INSERT INTO nodes(id,adg_name,entity_type,resolved_path) VALUES (?,?,'module',?)",
        (nid, name, path),
    )


def _edge(conn: sqlite3.Connection, src: int, dst: int, src_file: str) -> None:
    conn.execute(
        "INSERT INTO edges(src_id,dst_id,relation_type,source_file) VALUES (?,?,'imports',?)",
        (src, dst, src_file),
    )


def _mv_row(
    conn: sqlite3.Connection,
    symbol: str,
    file: str,
    live: int,
    test: int,
    gap: str,
) -> None:
    conn.execute(
        "INSERT INTO mv_prompt_assembly_wiring_gaps "
        "(snapshot_id,node_id,target_symbol,target_file,layer,total_callers,live_callers,test_callers,gap_type) "
        "VALUES ('sha',1,?,?,'',(? + ?),?,?,?)",
        (symbol, file, live, test, live, test, gap),
    )


# ---------------------------------------------------------------------------
# Gate attributes
# ---------------------------------------------------------------------------


class TestPromptAssemblyWiringGateAttributes:
    def test_gate_family(self) -> None:
        gate = PromptAssemblyWiringGate.__new__(PromptAssemblyWiringGate)
        assert gate.gate_family == "prompt_assembly_wiring"

    def test_severity(self) -> None:
        gate = PromptAssemblyWiringGate.__new__(PromptAssemblyWiringGate)
        assert gate.severity == "P1"

    def test_source_views(self) -> None:
        gate = PromptAssemblyWiringGate.__new__(PromptAssemblyWiringGate)
        assert _VIEW in gate.source_views

    def test_execution_policy_gate_action_halt(self) -> None:
        gate = PromptAssemblyWiringGate.__new__(PromptAssemblyWiringGate)
        assert gate.execution_policy.gate_action == "halt"

    def test_execution_policy_manual_only(self) -> None:
        gate = PromptAssemblyWiringGate.__new__(PromptAssemblyWiringGate)
        assert gate.execution_policy.repairability == "manual_only"

    def test_execution_policy_signal_source(self) -> None:
        gate = PromptAssemblyWiringGate.__new__(PromptAssemblyWiringGate)
        assert gate.execution_policy.signal_source == "sqlite_mv_ci"


# ---------------------------------------------------------------------------
# Catalog registration
# ---------------------------------------------------------------------------


class TestCatalogRegistration:
    def test_gate_in_catalog(self) -> None:
        """G-P1-PROMPT-WIRING must be registered in the SSOT catalog."""
        assert "G-P1-PROMPT-WIRING" in GATE_INDEX

    def test_catalog_entry_severity(self) -> None:
        entry = GATE_INDEX["G-P1-PROMPT-WIRING"]
        assert entry.severity == "P1"

    def test_catalog_entry_class(self) -> None:
        entry = GATE_INDEX["G-P1-PROMPT-WIRING"]
        assert entry.cls == "PromptAssemblyWiringGate"

    def test_catalog_entry_gate_class(self) -> None:
        entry = GATE_INDEX["G-P1-PROMPT-WIRING"]
        assert entry.gate_class == "structural_conformance"

    def test_catalog_entry_gate_action(self) -> None:
        entry = GATE_INDEX["G-P1-PROMPT-WIRING"]
        assert entry.policy.gate_action == "halt"

    def test_build_index_no_regressions(self) -> None:
        """build_index() must pass validation with the new entry — no duplicate IDs, no invalid fields."""
        index = build_index()
        assert "G-P1-PROMPT-WIRING" in index
        assert "G-P1-TRACE" in index
        assert "G-P0-WRITE" in index


# ---------------------------------------------------------------------------
# Positive case: live caller → pass
# ---------------------------------------------------------------------------


class TestGatePositiveCases:
    def test_live_caller_passes(self, tmp_path: Path) -> None:
        """After Stage 3 fix: sovereign_rag_orchestrator imports dispatcher → gate passes."""
        db = _make_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _mv_row(conn, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py", 1, 1, "ok")
        conn.commit()
        conn.close()

        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        gate._snapshot_id = gate._get_snapshot_id()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.status == "passed"
        assert result.violations == []

    def test_mixed_callers_passes(self, tmp_path: Path) -> None:
        """Both live and test callers → gap_type='ok' → gate passes."""
        db = _make_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _mv_row(
            conn, "c0_bridge_adapter", "tools/adg/prompt_assembly/adapters/c0_bridge_adapter.py", 2, 1, "ok"
        )
        conn.commit()
        conn.close()

        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        gate._snapshot_id = gate._get_snapshot_id()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.status == "passed"

    def test_empty_mv_passes(self, tmp_path: Path) -> None:
        """Empty materialized view (no prompt-assembly modules) → gate passes."""
        db = _make_db(tmp_path)
        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        gate._snapshot_id = gate._get_snapshot_id()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.status == "passed"
        assert result.violations == []

    def test_zero_callers_passes(self, tmp_path: Path) -> None:
        """Zero callers at all: gap_type='disconnected' but test_callers=0.

        AP-18 and this gate require test_callers>0 to fire.
        The zero-caller case belongs to mv_unknown_taxonomy_and_orphans.
        """
        db = _make_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _mv_row(conn, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py", 0, 0, "disconnected")
        conn.commit()
        conn.close()

        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        gate._snapshot_id = gate._get_snapshot_id()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.status == "passed", "zero callers should not trip P1-PROMPT-WIRING"


# ---------------------------------------------------------------------------
# Negative case: test-only caller → block
# ---------------------------------------------------------------------------


class TestGateNegativeCases:
    def test_test_only_caller_blocks(self, tmp_path: Path) -> None:
        """Negative case: dispatcher has test-only caller → gate blocks."""
        db = _make_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _mv_row(
            conn,
            "c0_dispatcher",
            "tools/adg/prompt_assembly/c0_dispatcher.py",
            live=0,
            test=2,
            gap="disconnected",
        )
        conn.commit()
        conn.close()

        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        gate._snapshot_id = gate._get_snapshot_id()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.status == "blocked"
        assert len(result.violations) == 1
        v = result.violations[0]
        assert "c0_dispatcher" in v.message
        assert "live_callers=0" in v.message
        assert "test_callers=2" in v.message
        assert "test-only subsystem, no runtime caller" in v.message

    def test_violation_extra_fields(self, tmp_path: Path) -> None:
        """Extra dict on violation contains all required diagnostic fields."""
        db = _make_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _mv_row(
            conn,
            "c0_bridge_adapter",
            "tools/adg/prompt_assembly/adapters/c0_bridge_adapter.py",
            0,
            1,
            "disconnected",
        )
        conn.commit()
        conn.close()

        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.status == "blocked"
        extra = result.violations[0].extra
        assert extra["live_callers"] == 0
        assert extra["test_callers"] == 1
        assert extra["gap_type"] == "disconnected"
        assert "remediation" in extra

    def test_multiple_disconnected_surfaces_all_reported(self, tmp_path: Path) -> None:
        """Two orphaned surfaces both appear in violations."""
        db = _make_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _mv_row(conn, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py", 0, 3, "disconnected")
        _mv_row(
            conn,
            "c0_bridge_adapter",
            "tools/adg/prompt_assembly/adapters/c0_bridge_adapter.py",
            0,
            1,
            "disconnected",
        )
        conn.commit()
        conn.close()

        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.status == "blocked"
        assert len(result.violations) == 2
        symbols = {v.extra["target_symbol"] for v in result.violations}
        assert "c0_dispatcher" in symbols
        assert "c0_bridge_adapter" in symbols

    def test_summary_counts_match_violations(self, tmp_path: Path) -> None:
        """summary['disconnected_surfaces'] matches len(violations)."""
        db = _make_db(tmp_path)
        conn = sqlite3.connect(str(db))
        _mv_row(conn, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py", 0, 1, "disconnected")
        conn.commit()
        conn.close()

        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.summary["disconnected_surfaces"] == len(result.violations)
        assert result.summary["total_violations"] == len(result.violations)


# ---------------------------------------------------------------------------
# Fallback path: inline SQL when MV is absent
# ---------------------------------------------------------------------------


class TestGateFallbackInlineSQL:
    def _make_db_without_mv(self, tmp_path: Path) -> Path:
        """Create a DB without the materialized view — triggers fallback."""
        return _make_db(tmp_path, with_mv=False)

    def test_fallback_passes_with_live_caller(self, tmp_path: Path) -> None:
        """When MV absent, inline SQL fallback used: live caller → pass."""
        db = self._make_db_without_mv(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py")
        _node(conn, 2, "live_orch", "agentic_core/L3_orchestration/orch.py")
        _edge(conn, 2, 1, "agentic_core/L3_orchestration/orch.py")
        conn.commit()
        conn.close()

        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.status == "passed"

    def test_fallback_blocks_on_test_only_caller(self, tmp_path: Path) -> None:
        """When MV absent, inline SQL fallback detects test-only caller → block."""
        db = self._make_db_without_mv(tmp_path)
        conn = sqlite3.connect(str(db))
        _node(conn, 1, "c0_dispatcher", "tools/adg/prompt_assembly/c0_dispatcher.py")
        _node(conn, 2, "test_caller", "tests/unit/tools/adg/prompt_assembly/test_c0_dispatcher.py")
        _edge(conn, 2, 1, "tests/unit/tools/adg/prompt_assembly/test_c0_dispatcher.py")
        conn.commit()
        conn.close()

        gate = PromptAssemblyWiringGate(sqlite_path=db)
        gate._connect()
        result = gate._execute_gate_logic()
        gate._close()

        assert result.status == "blocked"
        assert len(result.violations) == 1
        assert "test-only subsystem" in result.violations[0].message
