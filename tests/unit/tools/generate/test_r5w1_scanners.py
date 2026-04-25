"""Unit tests for R5-W1 supplementary scanners (A6, A12).

Tests the edge-writing scanners that complement truth_expansion_enricher:
  - tools.generate.entrypoint_scanner.write_entrypoint_edges (A6)
  - tools.generate.gate_self_test_scanner.write_gate_self_test_edges (A12)

Each test creates a minimal SQLite ADG schema, runs the scanner, and asserts
correct edges + synthetic nodes are produced.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from tools.generate.entrypoint_scanner import write_entrypoint_edges
from tools.generate.gate_self_test_scanner import write_gate_self_test_edges


# --------------------------------------------------------------------- helpers


_NODES_DDL = """
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    adg_name TEXT,
    entity_type TEXT,
    layer TEXT,
    identity_kind TEXT,
    confidence REAL,
    resolved_path TEXT,
    entrypoint_kind TEXT
)
"""

_EDGES_DDL = """
CREATE TABLE edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id INTEGER,
    dst_id INTEGER,
    relation_type TEXT,
    edge_kind TEXT,
    source_file TEXT,
    line_no INTEGER,
    symbol TEXT,
    semantic_type TEXT
)
"""


def _make_adg(tmp_path: Path) -> Path:
    """Build a minimal ADG SQLite with nodes/edges schema."""
    db = tmp_path / "adg_test.sqlite"
    conn = sqlite3.connect(db)
    conn.execute(_NODES_DDL)
    conn.execute(_EDGES_DDL)
    conn.commit()
    conn.close()
    return db


def _seed_module_node(db: Path, rel_path: str, adg_name: str | None = None) -> int:
    """Insert a single module node and return its id."""
    name = adg_name or f"ADG::Module::{rel_path}"
    conn = sqlite3.connect(db)
    cur = conn.execute(
        "INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path) "
        "VALUES (?, 'module', 'L_TOOLS', 'real', 1.0, ?)",
        (name, rel_path),
    )
    node_id = cur.lastrowid
    conn.commit()
    conn.close()
    assert node_id is not None
    return node_id


# ----------------------------------------------------------------- A6 entrypoint


class TestWriteEntrypointEdges:
    def test_returns_int(self, tmp_path: Path) -> None:
        """Scanner returns an integer count even on empty DB."""
        db = _make_adg(tmp_path)
        result = write_entrypoint_edges(db)
        assert isinstance(result, int)
        assert result >= 0

    def test_writes_entrypoint_kind_edges(self, tmp_path: Path) -> None:
        """Scanner writes at least one entrypoint_kind edge."""
        db = _make_adg(tmp_path)
        count = write_entrypoint_edges(db)
        # Real repo always has hooks/CI/MCP entrypoints, so > 0
        assert count > 0, f"expected entrypoint edges, got {count}"

        conn = sqlite3.connect(db)
        edges = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='entrypoint_kind'").fetchone()[0]
        conn.close()
        assert edges == count

    def test_creates_synthetic_target_nodes(self, tmp_path: Path) -> None:
        """Scanner creates ADG::Entrypoint::* synthetic target nodes."""
        db = _make_adg(tmp_path)
        write_entrypoint_edges(db)

        conn = sqlite3.connect(db)
        synthetic = conn.execute(
            "SELECT adg_name FROM nodes WHERE adg_name LIKE 'ADG::Entrypoint::%'"
        ).fetchall()
        conn.close()
        assert len(synthetic) >= 1
        assert all(name[0].startswith("ADG::Entrypoint::") for name in synthetic)

    def test_edge_columns_match_schema(self, tmp_path: Path) -> None:
        """Inserted edges have all expected columns populated."""
        db = _make_adg(tmp_path)
        write_entrypoint_edges(db)

        conn = sqlite3.connect(db)
        row = conn.execute(
            "SELECT relation_type, edge_kind, source_file, symbol "
            "FROM edges WHERE relation_type='entrypoint_kind' LIMIT 1"
        ).fetchone()
        conn.close()
        assert row is not None
        rel, kind, src_file, symbol = row
        assert rel == "entrypoint_kind"
        assert kind == "entrypoint"
        assert src_file  # non-empty path
        assert symbol  # non-empty kind

    def test_idempotent_on_rerun(self, tmp_path: Path) -> None:
        """Running scanner twice does not crash (may add duplicate edges)."""
        db = _make_adg(tmp_path)
        first = write_entrypoint_edges(db)
        second = write_entrypoint_edges(db)
        # Both runs should return same count of detected entrypoints
        assert first == second


# ----------------------------------------------------------------- A12 gate self-test


class TestWriteGateSelfTestEdges:
    def test_returns_int(self, tmp_path: Path) -> None:
        """Scanner returns an integer count even on empty DB."""
        db = _make_adg(tmp_path)
        result = write_gate_self_test_edges(db)
        assert isinstance(result, int)
        assert result >= 0

    def test_writes_gate_self_test_edges(self, tmp_path: Path) -> None:
        """Scanner writes at least one gate_self_test edge."""
        db = _make_adg(tmp_path)
        count = write_gate_self_test_edges(db)
        # Real repo has gate scripts with claim/enforcement mismatches
        assert count > 0, f"expected gate_self_test edges, got {count}"

        conn = sqlite3.connect(db)
        edges = conn.execute("SELECT COUNT(*) FROM edges WHERE relation_type='gate_self_test'").fetchone()[0]
        conn.close()
        assert edges == count

    def test_creates_synthetic_target_nodes(self, tmp_path: Path) -> None:
        """Scanner creates ADG::GateSelfTest::* synthetic target nodes."""
        db = _make_adg(tmp_path)
        write_gate_self_test_edges(db)

        conn = sqlite3.connect(db)
        synthetic = conn.execute(
            "SELECT adg_name FROM nodes WHERE adg_name LIKE 'ADG::GateSelfTest::%'"
        ).fetchall()
        conn.close()
        assert len(synthetic) >= 1
        assert all(name[0].startswith("ADG::GateSelfTest::") for name in synthetic)

    def test_consistency_classification_in_symbol(self, tmp_path: Path) -> None:
        """Edge symbol field carries the consistency classification."""
        db = _make_adg(tmp_path)
        write_gate_self_test_edges(db)

        conn = sqlite3.connect(db)
        symbols = {
            row[0]
            for row in conn.execute(
                "SELECT DISTINCT symbol FROM edges WHERE relation_type='gate_self_test'"
            ).fetchall()
        }
        conn.close()
        assert symbols
        valid = {"claim_without_enforcement", "enforcement_without_claim"}
        assert symbols.issubset(valid), f"unexpected symbols: {symbols - valid}"

    def test_path_normalization_to_forward_slashes(self, tmp_path: Path) -> None:
        """Synthetic module nodes use forward-slash paths (ADG convention)."""
        db = _make_adg(tmp_path)
        write_gate_self_test_edges(db)

        conn = sqlite3.connect(db)
        paths = [
            row[0]
            for row in conn.execute(
                "SELECT resolved_path FROM nodes "
                "WHERE adg_name LIKE 'ADG::Module::%' AND identity_kind='synthetic'"
            ).fetchall()
        ]
        conn.close()
        # Synthetic nodes from this scanner must use forward slashes
        for p in paths:
            assert "\\" not in p, f"backslash leaked into resolved_path: {p}"


# ----------------------------------------------------------------- entrypoint_scanner CLI


class TestEntrypointScannerDetection:
    """Smoke tests for the detection layer (no DB writes)."""

    def test_detect_entrypoints_returns_results(self) -> None:
        from tools.generate.entrypoint_scanner import scan_all_entrypoints

        eps = scan_all_entrypoints()
        assert isinstance(eps, list)
        assert len(eps) > 0
        # Each result is (path, kind)
        for ep in eps[:5]:
            assert len(ep) == 2
            path, kind = ep
            assert isinstance(path, str) and path
            assert kind in {"mcp", "hook", "ci", "cli", "imported", "scheduled", "test"}


class TestGateSelfTestScannerDetection:
    """Smoke tests for the detection layer (no DB writes)."""

    def test_scan_all_gates_returns_results(self) -> None:
        from tools.generate.gate_self_test_scanner import scan_all_gates

        results = scan_all_gates()
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results[:5]:
            assert "path" in r
            assert "consistency" in r
            assert r["consistency"] in {
                "consistent",
                "claim_without_enforcement",
                "enforcement_without_claim",
                "empty",
                "unreadable",
            }
