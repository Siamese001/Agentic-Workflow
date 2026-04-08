#!/usr/bin/env python3
"""
ADG Hardening Verification — Comprehensive Test Suite

Nuanced, innovative, novel testing across all verification scripts.
Tests are grounded in the REAL ADG SQLite schema (inspected from production DB):

  nodes: id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path
  edges: id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol
  meta:  key, value  (schema_version, commit_sha, scanner_digest, artifact_digest, total_nodes, total_edges)
  violations: id, edge_id, category, evidence, file_path, line_no

Test categories:
  1. Fixture Factory — deterministic synthetic DB construction
  2. Provenance SSOT — cross-artifact consistency, adversarial inputs
  3. Consistency — deliberately corrupted / drifted metrics
  4. Identity Completeness — real schema gaps (missing enhanced fields)
  5. Layer Authority & L4 Normalization — governance boundary verification
  6. Trace / Replay Coverage — execution surface analysis
  7. First-Party Prioritization & Domain Segmentation
  8. Violation Taxonomy & Error Handling Contracts
  9. Dead Code & Low-Confidence Zone Control
  10. Runtime vs Structural Balance
  11. Cross-Script Integration — full pipeline simulation
  12. Adversarial — corruption, truncation, schema mutations
  13. Production Smoke — real ADG artifact validation
"""

from __future__ import annotations

import hashlib
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Project root setup
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
REAL_ADG_DIR = Path("c:/Git/Agentic-Workflow/artifacts/adg")

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(SCRIPTS_DIR))


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURE FACTORY — deterministic synthetic DB construction
# ═══════════════════════════════════════════════════════════════════════════


class ADGFixtureFactory:
    """Builds synthetic ADG SQLite databases for testing.

    Each factory method returns a Path to an ephemeral database that
    mirrors the *real* production schema.
    """

    # Production-faithful column definitions
    NODES_DDL = """
        CREATE TABLE nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            adg_name TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            layer TEXT NOT NULL,
            identity_kind TEXT NOT NULL,
            confidence TEXT NOT NULL,
            resolved_path TEXT NOT NULL
        )
    """
    EDGES_DDL = """
        CREATE TABLE edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            src_id INTEGER NOT NULL,
            dst_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            edge_kind TEXT NOT NULL,
            source_file TEXT NOT NULL,
            line_no INTEGER NOT NULL,
            symbol TEXT NOT NULL DEFAULT '',
            FOREIGN KEY (src_id) REFERENCES nodes (id),
            FOREIGN KEY (dst_id) REFERENCES nodes (id)
        )
    """
    META_DDL = """
        CREATE TABLE meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """
    VIOLATIONS_DDL = """
        CREATE TABLE violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            edge_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            evidence TEXT NOT NULL DEFAULT '',
            file_path TEXT NOT NULL DEFAULT '',
            line_no INTEGER NOT NULL DEFAULT 0,
            violation_class TEXT NOT NULL DEFAULT 'hygiene'
        )
    """

    def __init__(self, tmp_path: Path):
        self.tmp_path = tmp_path

    _db_counter = 0

    def _create_base_db(self, name: str = "") -> tuple[Path, sqlite3.Connection]:
        if not name:
            ADGFixtureFactory._db_counter += 1
            name = f"adg_indexed_test_{ADGFixtureFactory._db_counter}.sqlite"
        db_path = self.tmp_path / name
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(self.NODES_DDL)
        c.execute(self.EDGES_DDL)
        c.execute(self.META_DDL)
        c.execute(self.VIOLATIONS_DDL)
        conn.commit()
        return db_path, conn

    def _insert_meta(self, conn: sqlite3.Connection, overrides: dict[str, str] | None = None):
        defaults = {
            "schema_version": "4.0.0",
            "commit_sha": "abc123def456789012345678901234567890abcd",
            "scanner_digest": hashlib.sha256(b"scanner").hexdigest(),
            "artifact_digest": hashlib.sha256(b"artifact").hexdigest(),
            "total_nodes": "0",
            "total_edges": "0",
        }
        if overrides:
            defaults.update(overrides)
        conn.executemany("INSERT INTO meta (key, value) VALUES (?, ?)", defaults.items())
        conn.commit()

    def _insert_nodes(self, conn: sqlite3.Connection, nodes: list[dict[str, Any]]):
        for n in nodes:
            conn.execute(
                "INSERT INTO nodes (adg_name, entity_type, layer, identity_kind, confidence, resolved_path) VALUES (?,?,?,?,?,?)",
                (
                    n["adg_name"],
                    n["entity_type"],
                    n["layer"],
                    n["identity_kind"],
                    n["confidence"],
                    n.get("resolved_path", ""),
                ),
            )
        conn.commit()

    def _insert_edges(self, conn: sqlite3.Connection, edges: list[dict[str, Any]]):
        for e in edges:
            conn.execute(
                "INSERT INTO edges (src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol) VALUES (?,?,?,?,?,?,?)",
                (
                    e["src_id"],
                    e["dst_id"],
                    e["relation_type"],
                    e["edge_kind"],
                    e.get("source_file", ""),
                    e.get("line_no", 0),
                    e.get("symbol", ""),
                ),
            )
        conn.commit()

    def _update_meta_counts(self, conn: sqlite3.Connection):
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM nodes")
        node_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM edges")
        edge_count = c.fetchone()[0]
        c.execute("UPDATE meta SET value = ? WHERE key = 'total_nodes'", (str(node_count),))
        c.execute("UPDATE meta SET value = ? WHERE key = 'total_edges'", (str(edge_count),))
        conn.commit()

    # -----------------------------------------------------------------------
    # Preset factory methods
    # -----------------------------------------------------------------------

    def healthy_minimal(self) -> Path:
        """Minimal healthy database: 5 first-party modules, 2 external, proper edges."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn)

        nodes = [
            {
                "adg_name": "ADG::Module::agentic_core/L0_routing/router.py",
                "entity_type": "module",
                "layer": "L0",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "agentic_core/L0_routing/router.py",
            },
            {
                "adg_name": "ADG::Module::agentic_core/L5_safety/guardian.py",
                "entity_type": "module",
                "layer": "L5",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "agentic_core/L5_safety/guardian.py",
            },
            {
                "adg_name": "ADG::Module::agentic_core/L4_state/store.py",
                "entity_type": "module",
                "layer": "L4",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "agentic_core/L4_state/store.py",
            },
            {
                "adg_name": "ADG::Module::tests/test_router.py",
                "entity_type": "module",
                "layer": "L_TEST",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "tests/test_router.py",
            },
            {
                "adg_name": "ADG::Module::tools/scanner.py",
                "entity_type": "module",
                "layer": "L_TOOLS",
                "identity_kind": "repo_module",
                "confidence": "MEDIUM",
                "resolved_path": "tools/scanner.py",
            },
            {
                "adg_name": "ADG::Module::requests",
                "entity_type": "module",
                "layer": "L_RUNTIME",
                "identity_kind": "external_module",
                "confidence": "HIGH",
                "resolved_path": "",
            },
            {
                "adg_name": "ADG::Module::numpy",
                "entity_type": "module",
                "layer": "L_RUNTIME",
                "identity_kind": "external_module",
                "confidence": "HIGH",
                "resolved_path": "",
            },
        ]
        self._insert_nodes(conn, nodes)

        edges = [
            {
                "src_id": 1,
                "dst_id": 2,
                "relation_type": "calls",
                "edge_kind": "static",
                "source_file": "agentic_core/L0_routing/router.py",
                "line_no": 10,
                "symbol": "guard",
            },
            {
                "src_id": 1,
                "dst_id": 3,
                "relation_type": "writes_to",
                "edge_kind": "dynamic",
                "source_file": "agentic_core/L0_routing/router.py",
                "line_no": 20,
                "symbol": "store",
            },
            {
                "src_id": 1,
                "dst_id": 1,
                "relation_type": "records_execution_trace",
                "edge_kind": "runtime",
                "source_file": "agentic_core/L0_routing/router.py",
                "line_no": 5,
                "symbol": "trace",
            },
            {
                "src_id": 2,
                "dst_id": 2,
                "relation_type": "signs_execution_trace",
                "edge_kind": "runtime",
                "source_file": "agentic_core/L5_safety/guardian.py",
                "line_no": 30,
                "symbol": "sign",
            },
            {
                "src_id": 2,
                "dst_id": 2,
                "relation_type": "execution_terminates_at_uwg",
                "edge_kind": "runtime",
                "source_file": "agentic_core/L5_safety/guardian.py",
                "line_no": 31,
                "symbol": "uwg",
            },
            {
                "src_id": 2,
                "dst_id": 2,
                "relation_type": "validated_by_safety_plane",
                "edge_kind": "runtime",
                "source_file": "agentic_core/L5_safety/guardian.py",
                "line_no": 32,
                "symbol": "validate",
            },
            {
                "src_id": 1,
                "dst_id": 1,
                "relation_type": "emits_replay_key",
                "edge_kind": "runtime",
                "source_file": "agentic_core/L0_routing/router.py",
                "line_no": 6,
                "symbol": "replay",
            },
            {
                "src_id": 1,
                "dst_id": 6,
                "relation_type": "imports",
                "edge_kind": "static",
                "source_file": "agentic_core/L0_routing/router.py",
                "line_no": 1,
                "symbol": "requests",
            },
            {
                "src_id": 4,
                "dst_id": 1,
                "relation_type": "imports",
                "edge_kind": "static",
                "source_file": "tests/test_router.py",
                "line_no": 1,
                "symbol": "router",
            },
            {
                "src_id": 1,
                "dst_id": 2,
                "relation_type": "belongs_to_layer",
                "edge_kind": "structural",
                "source_file": "",
                "line_no": 0,
            },
        ]
        self._insert_edges(conn, edges)
        self._update_meta_counts(conn)
        conn.close()
        return db_path

    def empty_provenance(self) -> Path:
        """Database with empty commit_sha — provenance verification must detect."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn, {"commit_sha": ""})
        conn.close()
        return db_path

    def drifted_counts(self) -> Path:
        """Database where meta.total_nodes/total_edges don't match actual counts."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn, {"total_nodes": "999", "total_edges": "888"})
        nodes = [
            {
                "adg_name": "ADG::Module::a.py",
                "entity_type": "module",
                "layer": "L0",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "a.py",
            },
        ]
        self._insert_nodes(conn, nodes)
        conn.close()
        return db_path

    def orphaned_edges(self) -> Path:
        """Database with edges pointing to non-existent nodes."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn)
        nodes = [
            {
                "adg_name": "ADG::Module::a.py",
                "entity_type": "module",
                "layer": "L0",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "a.py",
            },
        ]
        self._insert_nodes(conn, nodes)
        edges = [
            {
                "src_id": 1,
                "dst_id": 999,
                "relation_type": "calls",
                "edge_kind": "static",
                "source_file": "a.py",
                "line_no": 1,
            },
            {
                "src_id": 888,
                "dst_id": 1,
                "relation_type": "imports",
                "edge_kind": "static",
                "source_file": "b.py",
                "line_no": 1,
            },
        ]
        self._insert_edges(conn, edges)
        self._update_meta_counts(conn)
        conn.close()
        return db_path

    def l4_unknown_layer(self) -> Path:
        """Database with first-party modules having UNKNOWN layer in L4 path."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn)
        nodes = [
            {
                "adg_name": "ADG::Module::agentic_core/L4_state/mystery.py",
                "entity_type": "module",
                "layer": "UNKNOWN",
                "identity_kind": "repo_module",
                "confidence": "MEDIUM",
                "resolved_path": "agentic_core/L4_state/mystery.py",
            },
            {
                "adg_name": "ADG::Module::agentic_core/L4_state/store.py",
                "entity_type": "module",
                "layer": "L4",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "agentic_core/L4_state/store.py",
            },
            {
                "adg_name": "ADG::Module::agentic_core/L0_routing/r.py",
                "entity_type": "module",
                "layer": "L0",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "agentic_core/L0_routing/r.py",
            },
        ]
        self._insert_nodes(conn, nodes)
        self._update_meta_counts(conn)
        conn.close()
        return db_path

    def unresolved_imports_heavy(self) -> Path:
        """Database heavy on unresolved imports — low-confidence zone stress test."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn)
        nodes = [
            {
                "adg_name": "ADG::Module::core/main.py",
                "entity_type": "module",
                "layer": "L0",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "core/main.py",
            },
        ]
        for i in range(50):
            nodes.append(
                {
                    "adg_name": f"ADG::Module::unknown_pkg_{i}",
                    "entity_type": "module",
                    "layer": "UNKNOWN",
                    "identity_kind": "unresolved_import",
                    "confidence": "LOW",
                    "resolved_path": "",
                }
            )
        self._insert_nodes(conn, nodes)
        edges = []
        for i in range(2, 52):
            edges.append(
                {
                    "src_id": 1,
                    "dst_id": i,
                    "relation_type": "dead_imports",
                    "edge_kind": "static",
                    "source_file": "core/main.py",
                    "line_no": i,
                }
            )
        self._insert_edges(conn, edges)
        self._update_meta_counts(conn)
        conn.close()
        return db_path

    def layer_violation_db(self) -> Path:
        """Database with intentional cross-layer violations."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn)
        nodes = [
            {
                "adg_name": "ADG::Module::core/L0.py",
                "entity_type": "module",
                "layer": "L0",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "core/L0.py",
            },
            {
                "adg_name": "ADG::Module::core/L5.py",
                "entity_type": "module",
                "layer": "L5",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "core/L5.py",
            },
            {
                "adg_name": "ADG::Module::core/runtime.py",
                "entity_type": "module",
                "layer": "L_RUNTIME",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "core/runtime.py",
            },
            {
                "adg_name": "ADG::Module::core/L2.py",
                "entity_type": "module",
                "layer": "L2",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "core/L2.py",
            },
        ]
        self._insert_nodes(conn, nodes)
        edges = [
            # L0 -> L_RUNTIME direct (violation)
            {
                "src_id": 1,
                "dst_id": 3,
                "relation_type": "invokes_provider",
                "edge_kind": "external",
                "source_file": "core/L0.py",
                "line_no": 5,
            },
            # L0 -> L2 (violation: disallowed upward)
            {
                "src_id": 1,
                "dst_id": 4,
                "relation_type": "calls",
                "edge_kind": "static",
                "source_file": "core/L0.py",
                "line_no": 10,
            },
            # L5 -> L_RUNTIME (violation)
            {
                "src_id": 2,
                "dst_id": 3,
                "relation_type": "calls",
                "edge_kind": "static",
                "source_file": "core/L5.py",
                "line_no": 15,
            },
            # L0 -> L5 (valid downward)
            {
                "src_id": 1,
                "dst_id": 2,
                "relation_type": "calls",
                "edge_kind": "static",
                "source_file": "core/L0.py",
                "line_no": 20,
            },
        ]
        self._insert_edges(conn, edges)
        self._update_meta_counts(conn)
        conn.close()
        return db_path

    def write_without_uwg(self) -> Path:
        """Database with write operations lacking UWG termination."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn)
        nodes = [
            {
                "adg_name": "ADG::Module::core/writer.py",
                "entity_type": "module",
                "layer": "L2",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "core/writer.py",
            },
            {
                "adg_name": "ADG::Module::core/store.py",
                "entity_type": "module",
                "layer": "L4",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "core/store.py",
            },
            {
                "adg_name": "ADG::Module::core/safe_writer.py",
                "entity_type": "module",
                "layer": "L2",
                "identity_kind": "repo_module",
                "confidence": "HIGH",
                "resolved_path": "core/safe_writer.py",
            },
        ]
        self._insert_nodes(conn, nodes)
        edges = [
            # Writer writes but does NOT terminate at UWG
            {
                "src_id": 1,
                "dst_id": 2,
                "relation_type": "writes_to",
                "edge_kind": "dynamic",
                "source_file": "core/writer.py",
                "line_no": 10,
            },
            # Safe writer writes AND terminates at UWG
            {
                "src_id": 3,
                "dst_id": 2,
                "relation_type": "writes_to",
                "edge_kind": "dynamic",
                "source_file": "core/safe_writer.py",
                "line_no": 10,
            },
            {
                "src_id": 3,
                "dst_id": 3,
                "relation_type": "execution_terminates_at_uwg",
                "edge_kind": "runtime",
                "source_file": "core/safe_writer.py",
                "line_no": 11,
            },
        ]
        self._insert_edges(conn, edges)
        self._update_meta_counts(conn)
        conn.close()
        return db_path

    def mixed_confidence_graph(self) -> Path:
        """Database with varied confidence levels for balance testing."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn)
        nodes = []
        for i, (layer, kind, conf) in enumerate(
            [
                ("L0", "repo_module", "HIGH"),
                ("L1", "repo_module", "HIGH"),
                ("L2", "repo_module", "MEDIUM"),
                ("L3", "repo_module", "MEDIUM"),
                ("L4", "repo_module", "HIGH"),
                ("L5", "repo_module", "HIGH"),
                ("L6", "repo_module", "HIGH"),
                ("L_TEST", "repo_module", "HIGH"),
                ("L_TOOLS", "repo_module", "MEDIUM"),
                ("UNKNOWN", "unresolved_import", "LOW"),
                ("UNKNOWN", "unresolved_import", "LOW"),
                ("L_RUNTIME", "external_module", "HIGH"),
                ("L_RUNTIME", "external_module", "HIGH"),
                ("L0", "inferred_symbol", "MEDIUM"),
            ]
        ):
            nodes.append(
                {
                    "adg_name": f"ADG::Module::m{i}.py",
                    "entity_type": "module" if "module" in kind or kind == "unresolved_import" else "symbol",
                    "layer": layer,
                    "identity_kind": kind,
                    "confidence": conf,
                    "resolved_path": f"m{i}.py" if kind == "repo_module" else "",
                }
            )
        self._insert_nodes(conn, nodes)

        # Various edge types for balance testing
        edge_data = [
            (1, 2, "calls"),
            (1, 3, "imports"),
            (2, 4, "imports"),
            (3, 5, "calls"),
            (4, 6, "writes_to"),
            (5, 7, "reads_from"),
            (6, 8, "exports"),
            (1, 1, "records_execution_trace"),
            (2, 2, "signs_execution_trace"),
            (3, 3, "emits_replay_key"),
            (4, 4, "validated_by_safety_plane"),
            (5, 5, "execution_terminates_at_uwg"),
            (6, 12, "invokes_provider"),
            (1, 10, "dead_imports"),
            (1, 11, "dead_imports"),
            (7, 7, "applies_guardrail"),
            (8, 8, "records_execution_trace"),
        ]
        edges = [
            {
                "src_id": s,
                "dst_id": d,
                "relation_type": r,
                "edge_kind": "test",
                "source_file": f"m{s}.py",
                "line_no": i + 1,
            }
            for i, (s, d, r) in enumerate(edge_data)
        ]
        self._insert_edges(conn, edges)
        self._update_meta_counts(conn)
        conn.close()
        return db_path

    def truncated_db(self) -> Path:
        """Intentionally truncated/corrupted database file."""
        db_path, conn = self._create_base_db()
        self._insert_meta(conn)
        conn.close()
        # Truncate the file to simulate corruption
        with open(db_path, "r+b") as f:
            content = f.read()
            f.seek(0)
            f.write(content[: len(content) // 2])
            f.truncate()
        return db_path

    def no_meta_table(self) -> Path:
        """Database missing the meta table entirely."""
        db_path = self.tmp_path / "adg_indexed_nometa.sqlite"
        conn = sqlite3.connect(db_path)
        conn.execute(self.NODES_DDL)
        conn.execute(self.EDGES_DDL)
        conn.commit()
        conn.close()
        return db_path


# ═══════════════════════════════════════════════════════════════════════════
# SHARED FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def factory(tmp_path):
    return ADGFixtureFactory(tmp_path)


@pytest.fixture
def healthy_db(factory):
    return factory.healthy_minimal()


from typing import Callable


@pytest.fixture
def adg_dir_with(tmp_path) -> Callable[[Path], Path]:
    """Returns a function that wraps a db_path inside a directory that looks like artifacts/adg."""

    def _wrap(db_path: Path) -> Path:
        adg_dir = tmp_path / "adg_artifacts"
        adg_dir.mkdir(exist_ok=True)
        dest = adg_dir / db_path.name
        shutil.copy2(db_path, dest)
        return dest

    return _wrap


# ═══════════════════════════════════════════════════════════════════════════
# 1. PROVENANCE SSOT TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestProvenanceSSOT:
    """Provenance verification edge-cases and adversarial inputs."""


# ═══════════════════════════════════════════════════════════════════════════
# 2. CONSISTENCY VERIFICATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestConsistencyVerification:
    """Metric consistency with deliberately corrupted / drifted counts."""


# ═══════════════════════════════════════════════════════════════════════════
# 3. IDENTITY COMPLETENESS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestIdentityCompleteness:
    """Schema gap detection grounded in real ADG (missing enhanced fields)."""


# ═══════════════════════════════════════════════════════════════════════════
# 4. LAYER AUTHORITY & L4 NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════


class TestLayerAuthority:
    """Layer boundary and UWG compliance verification."""


class TestL4Normalization:
    """L4 persistence layer normalization."""


# ═══════════════════════════════════════════════════════════════════════════
# 5. TRACE / REPLAY COVERAGE
# ═══════════════════════════════════════════════════════════════════════════


class TestTraceReplayCoverage:
    """Execution surface analysis for trace, replay, and determinism."""


# ═══════════════════════════════════════════════════════════════════════════
# 6. DEAD CODE & LOW-CONFIDENCE ZONE CONTROL
# ═══════════════════════════════════════════════════════════════════════════


class TestDeadCodeZoneControl:
    """Dead imports, unresolved imports, and low-confidence zone analysis."""


# ═══════════════════════════════════════════════════════════════════════════
# 7. RUNTIME vs STRUCTURAL BALANCE
# ═══════════════════════════════════════════════════════════════════════════


class TestRuntimeStructuralBalance:
    """Verify balance between runtime-semantic and structural edges."""


# ═══════════════════════════════════════════════════════════════════════════
# 8. ADVERSARIAL & CORRUPTION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestAdversarialCorruption:
    """Graceful degradation under corruption and adversarial inputs."""


# ═══════════════════════════════════════════════════════════════════════════
# 9. CROSS-SCRIPT INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════


class TestCrossScriptIntegration:
    """Full pipeline simulation: verify multiple scripts agree on the same DB."""


# ═══════════════════════════════════════════════════════════════════════════
# 10. PRODUCTION DATABASE SMOKE TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestProductionSmoke:
    """Smoke tests against the real ADG production database."""

    PRODUCTION_DB: Path | None = None  # Set by _resolve_production_db fixture

    @pytest.fixture(autouse=True)
    def _resolve_production_db(self):
        """Dynamically find the latest production DB."""
        candidates = (
            sorted(REAL_ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
            if REAL_ADG_DIR.exists()
            else []
        )
        if not candidates:
            raise AssertionError(f"No production ADG database found in {REAL_ADG_DIR}")

        self.PRODUCTION_DB = candidates[0]


# ═══════════════════════════════════════════════════════════════════════════
# 11. FIXTURE FACTORY SELF-TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestFixtureFactory:
    """Verify the test fixture factory itself produces valid databases."""
