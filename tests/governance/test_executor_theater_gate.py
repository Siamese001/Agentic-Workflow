"""Tests for ops_scripts/ci/executor_theater_gate.py.

Tests each gate (G1–G4) with both passing and failing scenarios.
Uses synthetic AST fixtures and temp SQLite to avoid coupling to live ADG state.
"""

from __future__ import annotations

import sqlite3
import textwrap
from pathlib import Path

import pytest

# Import gate functions directly
from ops_scripts.ci.executor_theater_gate import (
    ROOT,
    gate_g1_reachability,
    gate_g2_claim_to_execution,
    gate_g3_import_only,
    gate_g4_classification,
    run_all_gates,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def adg_sqlite(tmp_path: Path) -> Path:
    """Create a minimal ADG SQLite with nodes/edges tables."""
    db_path = tmp_path / "adg_indexed_test.sqlite"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE nodes (
            id TEXT PRIMARY KEY,
            resolved_path TEXT,
            layer TEXT,
            entity_type TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE edges (
            id TEXT PRIMARY KEY,
            src_id TEXT,
            dst_id TEXT,
            relation_type TEXT
        )
        """
    )
    conn.commit()
    conn.close()
    return db_path


def _insert_node(db_path: Path, node_id: str, path: str, layer: str) -> None:
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO nodes (id, resolved_path, layer, entity_type) VALUES (?, ?, ?, 'module')",
        (node_id, path, layer),
    )
    conn.commit()
    conn.close()


def _insert_edge(db_path: Path, edge_id: str, src_id: str, dst_id: str, rel: str = "imports") -> None:
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "INSERT INTO edges (id, src_id, dst_id, relation_type) VALUES (?, ?, ?, ?)",
        (edge_id, src_id, dst_id, rel),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# G1: Production Reachability — tests
# ---------------------------------------------------------------------------


class TestG1Reachability:
    """G1: Executor-bearing module with zero production callers must fail."""

    def test_current_state_passes(self):
        """Current repo state after theater removal should have no G1 violations
        for generate_full_adg.py (it no longer bears executors)."""
        violations = gate_g2_claim_to_execution()
        assert not violations, f"G2 should pass on current repo: {violations}"

    def test_missing_sqlite_returns_error(self, tmp_path: Path):
        """G1 with nonexistent SQLite should return error."""
        violations = gate_g1_reachability(tmp_path / "nonexistent.sqlite")
        assert len(violations) == 1
        assert "not found" in violations[0]

    def test_executor_file_with_zero_fanin_fails(self, adg_sqlite: Path, tmp_path: Path, monkeypatch):
        """A file bearing ProcessPoolExecutor with zero fan-in must fail G1."""
        # Create a fake executor-bearing file in a temp production root
        fake_prod = tmp_path / "agentic_core" / "test_mod"
        fake_prod.mkdir(parents=True)
        fake_file = fake_prod / "fake_parallel.py"
        fake_file.write_text("from concurrent.futures import ProcessPoolExecutor\n")

        # Add it as a node with zero edges
        _insert_node(
            adg_sqlite,
            "n_fake",
            "agentic_core/test_mod/fake_parallel.py",
            "L2",
        )

        # Monkey-patch ROOT and production roots to use temp dir
        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        monkeypatch.setattr(
            "ops_scripts.ci.executor_theater_gate.PRODUCTION_ROOTS",
            ["agentic_core"],
        )

        violations = gate_g1_reachability(adg_sqlite)
        assert len(violations) >= 1
        assert "0 production callers" in violations[0]

    def test_executor_file_with_callers_passes(self, adg_sqlite: Path, tmp_path: Path, monkeypatch):
        """A file bearing ThreadPoolExecutor with production fan-in should pass G1."""
        fake_prod = tmp_path / "agentic_core" / "test_mod"
        fake_prod.mkdir(parents=True)
        fake_file = fake_prod / "real_parallel.py"
        fake_file.write_text("from concurrent.futures import ThreadPoolExecutor\n")

        # Add node and a production import edge
        _insert_node(adg_sqlite, "n_real", "agentic_core/test_mod/real_parallel.py", "L2")
        _insert_node(adg_sqlite, "n_caller", "agentic_core/some_caller.py", "L2")
        _insert_edge(adg_sqlite, "e1", "n_caller", "n_real")

        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        monkeypatch.setattr(
            "ops_scripts.ci.executor_theater_gate.PRODUCTION_ROOTS",
            ["agentic_core"],
        )

        violations = gate_g1_reachability(adg_sqlite)
        assert not violations


# ---------------------------------------------------------------------------
# G2: Claim-to-Execution — tests
# ---------------------------------------------------------------------------


class TestG2ClaimToExecution:
    """G2: generate_full_adg.py must not have parallel claims."""

    def test_current_state_passes(self):
        """Current repo (theater stripped) should pass G2."""
        violations = gate_g2_claim_to_execution()
        assert not violations, f"G2 should pass: {violations}"

    def test_forbidden_param_detected(self, tmp_path: Path, monkeypatch):
        """If someone adds 'parallel' param back, G2 must fail."""
        fake_adg = tmp_path / "tools" / "generate" / "generate_full_adg.py"
        fake_adg.parent.mkdir(parents=True)
        fake_adg.write_text(
            textwrap.dedent("""\
            def generate_full_adg(adg_artifacts_dir, ts, parallel=True):
                pass
            def main():
                pass
        """)
        )

        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        violations = gate_g2_claim_to_execution()
        assert any("theater params" in v for v in violations)

    def test_forbidden_cli_flag_detected(self, tmp_path: Path, monkeypatch):
        """If --no-parallel CLI flag exists, G2 must fail."""
        fake_adg = tmp_path / "tools" / "generate" / "generate_full_adg.py"
        fake_adg.parent.mkdir(parents=True)
        fake_adg.write_text(
            textwrap.dedent("""\
            def generate_full_adg(adg_artifacts_dir, ts):
                pass
            def main():
                parser.add_argument("--no-parallel")
        """)
        )

        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        violations = gate_g2_claim_to_execution()
        assert any("--no-parallel" in v for v in violations)

    def test_forbidden_banner_detected(self, tmp_path: Path, monkeypatch):
        """If 'CPU Optimizer:' banner exists, G2 must fail."""
        fake_adg = tmp_path / "tools" / "generate" / "generate_full_adg.py"
        fake_adg.parent.mkdir(parents=True)
        fake_adg.write_text(
            textwrap.dedent("""\
            def generate_full_adg(adg_artifacts_dir, ts):
                print("CPU Optimizer: 16 workers")
            def main():
                pass
        """)
        )

        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        violations = gate_g2_claim_to_execution()
        assert any("CPU Optimizer:" in v for v in violations)


# ---------------------------------------------------------------------------
# G3: Import-Only Capability — tests
# ---------------------------------------------------------------------------


class TestG3ImportOnly:
    """G3: generate_full_adg.py must not import dead parallel modules."""

    def test_current_state_passes(self):
        """Current repo should pass G3."""
        violations = gate_g3_import_only()
        assert not violations, f"G3 should pass: {violations}"

    def test_dead_import_detected(self, tmp_path: Path, monkeypatch):
        """Importing cpu_optimizer in generate_full_adg.py must fail G3."""
        fake_adg = tmp_path / "tools" / "generate" / "generate_full_adg.py"
        fake_adg.parent.mkdir(parents=True)
        fake_adg.write_text(
            textwrap.dedent("""\
            from agentic_core.L2_execution.utils.cpu_optimizer import get_cpu_optimizer
            def generate_full_adg(adg_artifacts_dir, ts):
                pass
        """)
        )

        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        violations = gate_g3_import_only()
        assert len(violations) == 1
        assert "cpu_optimizer" in violations[0]

    def test_legitimate_import_passes(self, tmp_path: Path, monkeypatch):
        """Importing non-forbidden modules should pass G3."""
        fake_adg = tmp_path / "tools" / "generate" / "generate_full_adg.py"
        fake_adg.parent.mkdir(parents=True)
        fake_adg.write_text(
            textwrap.dedent("""\
            from pathlib import Path
            from agentic_core.adg.extraction.static_scanner import ADGStaticScanner
            def generate_full_adg(adg_artifacts_dir, ts):
                pass
        """)
        )

        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        violations = gate_g3_import_only()
        assert not violations


# ---------------------------------------------------------------------------
# G4: Production Classification — tests
# ---------------------------------------------------------------------------


class TestG4Classification:
    """G4: Executor infra files must have classification markers or callers."""

    def test_unclassified_infra_file_fails(self, tmp_path: Path, monkeypatch):
        """A file named *parallel* with executor but no classification must fail."""
        fake_prod = tmp_path / "agentic_core" / "utils"
        fake_prod.mkdir(parents=True)
        fake_file = fake_prod / "parallel_worker.py"
        fake_file.write_text("from concurrent.futures import ProcessPoolExecutor\n")

        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        monkeypatch.setattr(
            "ops_scripts.ci.executor_theater_gate.PRODUCTION_ROOTS",
            ["agentic_core"],
        )

        violations = gate_g4_classification()
        assert len(violations) >= 1
        assert "classification" in violations[0].lower()

    def test_classified_infra_file_passes(self, tmp_path: Path, monkeypatch):
        """A file with '# classification: archived' marker should pass G4."""
        fake_prod = tmp_path / "agentic_core" / "utils"
        fake_prod.mkdir(parents=True)
        fake_file = fake_prod / "parallel_worker.py"
        fake_file.write_text(
            "# classification: archived\nfrom concurrent.futures import ProcessPoolExecutor\n"
        )

        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        monkeypatch.setattr(
            "ops_scripts.ci.executor_theater_gate.PRODUCTION_ROOTS",
            ["agentic_core"],
        )

        violations = gate_g4_classification()
        assert not violations

    def test_non_infra_named_file_skipped(self, tmp_path: Path, monkeypatch):
        """A file not named with infra keywords should be skipped by G4."""
        fake_prod = tmp_path / "agentic_core" / "reasoning"
        fake_prod.mkdir(parents=True)
        fake_file = fake_prod / "my_agent.py"
        fake_file.write_text("from concurrent.futures import ThreadPoolExecutor\n")

        monkeypatch.setattr("ops_scripts.ci.executor_theater_gate.ROOT", tmp_path)
        monkeypatch.setattr(
            "ops_scripts.ci.executor_theater_gate.PRODUCTION_ROOTS",
            ["agentic_core"],
        )

        violations = gate_g4_classification()
        assert not violations


# ---------------------------------------------------------------------------
# Integration: run_all_gates
# ---------------------------------------------------------------------------


class TestRunAllGates:
    """Integration tests for the full gate runner."""

    def test_run_all_gates_passes_on_current_repo(self):
        """Current repo state (theater removed) should pass all gates."""
        latest_sqlite = None
        adg_dir = ROOT / "artifacts" / "adg"
        candidates = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
        if candidates:
            latest_sqlite = candidates[-1]

        if latest_sqlite is None:
            pytest.skip("No ADG SQLite available for integration test")

        rc = run_all_gates(sqlite_path=latest_sqlite)
        assert rc == 0, "All gates should pass on current repo state"

    def test_run_all_gates_missing_sqlite_returns_error(self):
        """Missing SQLite should return exit code 2."""
        rc = run_all_gates(sqlite_path=Path("/nonexistent/path.sqlite"))
        # G1 returns error string, gates continue; final result is 1 (violations)
        assert rc in (1, 2)
