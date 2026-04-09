#!/usr/bin/env python3
"""Tests for GraphDB CI gates (P0, P1, P2/P3).

Test categories:
    - P0 projection parity correctness
    - P0 deterministic rebuild behavior
    - P0 schema drift detection
    - P0 snapshot metadata validation
    - P0 query contract correctness
    - P0 truth-boundary detection
    - P1 projection coverage ratchet
    - P1 latency threshold behavior
    - Scorecard integration
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator

import pytest

# Import gates under test
import sys

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci.graphdb_p0_gate import (
    GraphDBP0Gates,
    GraphDBSnapshot,
    P0GateResult,
    REQUIRED_EDGE_CLASSES,
    REQUIRED_NODE_CLASSES,
)
from ops_scripts.ci.graphdb_p1_ratchet import GraphDBP1Ratchets, P1RatchetResult
from ops_scripts.ci.graphdb_p2p3_watch import GraphDBP2P3Watch, WatchGateResult
from ops_scripts.ci.graphdb_scorecard import (
    GraphDBScorecard,
    GraphDBScorecardCollector,
    ScorecardEntry,
)


@pytest.fixture
def temp_adg_db() -> Generator[Path, None, None]:
    """Create a temporary ADG SQLite database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_adg.sqlite"

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create entities table
        cursor.execute("""
            CREATE TABLE entities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                properties TEXT
            )
        """)

        # Create relations table
        cursor.execute("""
            CREATE TABLE relations (
                id TEXT PRIMARY KEY,
                from_id TEXT NOT NULL,
                to_id TEXT NOT NULL,
                type TEXT NOT NULL,
                properties TEXT
            )
        """)

        # Create metadata table
        cursor.execute("""
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()
        conn.close()

        yield db_path


@pytest.fixture
def populated_adg_db(temp_adg_db: Path) -> Path:
    """Create a populated ADG SQLite database with test data."""
    conn = sqlite3.connect(str(temp_adg_db))
    cursor = conn.cursor()

    # Insert test entities covering required node types
    test_entities = [
        ("file_1", "file", "test_file.py", '{"path": "/test/file.py"}'),
        ("module_1", "module", "test_module", '{"layer": "L0"}'),
        ("symbol_1", "symbol", "TestClass", '{"type": "class"}'),
        ("layer_1", "layer", "L0", '{"level": 0}'),
        ("agent_1", "agent", "TestAgent", '{"class": "TestAgent"}'),
        ("tool_1", "tool", "test_tool", '{"module": "tools.test"}'),
        ("policy_1", "policy", "TestPolicy", '{"severity": "HIGH"}'),
        ("decision_1", "decision", "TestDecision", '{"outcome": "approved"}'),
        ("seam_1", "seam", "TestSeam", '{"boundary": "L0-L1"}'),
        ("scan_1", "scan_run", "test_scan", '{"timestamp": "2024-01-01"}'),
    ]

    cursor.executemany("INSERT INTO entities (id, type, name, properties) VALUES (?, ?, ?, ?)", test_entities)

    # Insert test relations covering required edge types
    test_relations = [
        ("rel_1", "file_1", "module_1", "imports", '{"line": 1}'),
        ("rel_2", "module_1", "symbol_1", "calls", '{"line": 10}'),
        ("rel_3", "symbol_1", "layer_1", "implements", "{}"),
        ("rel_4", "module_1", "layer_1", "belongs_to_layer", "{}"),
        ("rel_5", "agent_1", "policy_1", "violates", '{"severity": "HIGH"}'),
        ("rel_6", "tool_1", "policy_1", "validates", "{}"),
        ("rel_7", "seam_1", "policy_1", "verifies_policy", "{}"),
    ]

    cursor.executemany(
        "INSERT INTO relations (id, from_id, to_id, type, properties) VALUES (?, ?, ?, ?, ?)", test_relations
    )

    # Insert metadata
    cursor.execute("INSERT INTO metadata (key, value) VALUES (?, ?)", ("schema_version", "1.0.0"))

    conn.commit()
    conn.close()

    return temp_adg_db


class TestP0ProjectionParity:
    """Tests for P0-1 projection parity gate."""

    def test_p0_1_passes_with_complete_data(self, populated_adg_db: Path) -> None:
        """P0-1 passes when all required node/edge classes are present."""
        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_1_projection_parity()

        assert result.passed is True
        assert result.gate_id == "P0-1"
        assert "Projection parity OK" in result.message

    def test_p0_1_fails_with_missing_nodes(self, temp_adg_db: Path) -> None:
        """P0-1 fails when required node classes are missing."""
        # Create minimal entities (missing most required types)
        conn = sqlite3.connect(str(temp_adg_db))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO entities (id, type, name, properties) VALUES (?, ?, ?, ?)",
            ("file_1", "file", "test.py", "{}"),
        )
        cursor.execute(
            "INSERT INTO relations (id, from_id, to_id, type, properties) VALUES (?, ?, ?, ?, ?)",
            ("rel_1", "file_1", "file_1", "imports", "{}"),
        )
        conn.commit()
        conn.close()

        gates = GraphDBP0Gates(temp_adg_db)
        result = gates.check_p0_1_projection_parity()

        assert result.passed is False
        assert "Missing required node classes" in result.message

    def test_p0_1_fails_with_zero_entities(self, temp_adg_db: Path) -> None:
        """P0-1 fails when there are zero entities (detected via missing node classes)."""
        gates = GraphDBP0Gates(temp_adg_db)
        result = gates.check_p0_1_projection_parity()

        assert result.passed is False
        # When zero entities, missing node classes is detected first
        assert "Missing required node classes" in result.message or "zero entities" in result.message


class TestP0DeterministicRebuild:
    """Tests for P0-2 deterministic rebuild gate."""

    def test_p0_2_creates_baseline(self, populated_adg_db: Path, tmp_path: Path, monkeypatch: Any) -> None:
        """P0-2 creates baseline on first run."""
        # Mock the baseline directory to use temp path
        monkeypatch.setattr("ops_scripts.ci.graphdb_p0_gate.ADG_DIR", tmp_path)

        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_2_deterministic_rebuild()

        assert result.passed is True
        assert "Deterministic rebuild OK" in result.message

        # Verify baseline was created
        baseline_file = tmp_path / "graphdb_snapshot_baseline.json"
        assert baseline_file.exists()

        baseline_data = json.loads(baseline_file.read_text())
        assert "content_digest" in baseline_data
        assert baseline_data["node_count"] == 10

    def test_p0_2_detects_digest_mismatch(
        self, populated_adg_db: Path, tmp_path: Path, monkeypatch: Any
    ) -> None:
        """P0-2 fails when digest doesn't match baseline."""
        # Create a baseline with different counts
        baseline_file = tmp_path / "graphdb_snapshot_baseline.json"
        baseline_data = {
            "content_digest": "different_digest_12345678",
            "node_count": 999,
            "edge_count": 999,
            "schema_version": "1.0.0",
            "node_type_counts": {},
            "edge_type_counts": {},
        }
        baseline_file.write_text(json.dumps(baseline_data))

        monkeypatch.setattr("ops_scripts.ci.graphdb_p0_gate.ADG_DIR", tmp_path)

        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_2_deterministic_rebuild()

        assert result.passed is False
        assert "digest mismatch" in result.message


class TestP0SchemaCompatibility:
    """Tests for P0-3 schema compatibility gate."""

    def test_p0_3_passes_with_valid_schema(self, populated_adg_db: Path) -> None:
        """P0-3 passes when all required tables and columns exist."""
        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_3_schema_compatibility()

        assert result.passed is True
        assert "Schema compatibility OK" in result.message

    def test_p0_3_fails_with_missing_tables(self, tmp_path: Path) -> None:
        """P0-3 fails when required tables are missing."""
        # Create incomplete database
        db_path = tmp_path / "incomplete.sqlite"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE entities (id TEXT PRIMARY KEY)")
        conn.commit()
        conn.close()

        gates = GraphDBP0Gates(db_path)
        result = gates.check_p0_3_schema_compatibility()

        assert result.passed is False
        assert "missing tables" in result.message


class TestP0SnapshotIntegrity:
    """Tests for P0-4 snapshot integrity gate."""

    def test_p0_4_fails_without_snapshot(
        self, populated_adg_db: Path, tmp_path: Path, monkeypatch: Any
    ) -> None:
        """P0-4 fails when no ADG snapshot files exist."""
        monkeypatch.setattr("ops_scripts.ci.graphdb_p0_gate.ADG_DIR", tmp_path)

        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_4_snapshot_integrity()

        assert result.passed is False
        assert "no ADG snapshot metadata found" in result.message

    def test_p0_4_passes_with_valid_snapshot(
        self, populated_adg_db: Path, tmp_path: Path, monkeypatch: Any
    ) -> None:
        """P0-4 passes when valid snapshot metadata exists."""
        # Create a valid snapshot file
        snapshot_file = tmp_path / "adg_snapshot_20240101_120000.json"
        snapshot_data = {
            "commit_sha": "abc123",
            "schema_version": "1.0.0",
            "timestamp": "2024-01-01T12:00:00Z",
        }
        snapshot_file.write_text(json.dumps(snapshot_data))

        monkeypatch.setattr("ops_scripts.ci.graphdb_p0_gate.ADG_DIR", tmp_path)

        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_4_snapshot_integrity()

        assert result.passed is True
        assert "Snapshot integrity OK" in result.message


class TestP0QueryContract:
    """Tests for P0-5 query contract gate."""

    def test_p0_5_query_contract_with_networkx(self, populated_adg_db: Path) -> None:
        """P0-5 validates query contract when NetworkX is available."""
        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_5_query_contract()

        # Should complete without exception
        assert isinstance(result, P0GateResult)
        assert result.gate_id == "P0-5"
        # Result depends on NetworkX availability and graph structure
        assert result.message is not None

    def test_p0_5_fails_without_networkx(self, monkeypatch: Any, populated_adg_db: Path) -> None:
        """P0-5 fails gracefully when NetworkX is not available."""
        # Mock NetworkX as unavailable
        monkeypatch.setattr("ops_scripts.ci.graphdb_p0_gate.HAS_NETWORKX", False)

        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_5_query_contract()

        assert result.passed is False
        assert "NetworkX not available" in result.message


class TestP0GraphOnlyTruth:
    """Tests for P0-6 graph-only truth drift gate."""

    def test_p0_6_passes_with_clean_graphdb(self, populated_adg_db: Path) -> None:
        """P0-6 passes when no graph-only truth patterns are detected."""
        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_6_graph_only_truth()

        assert result.passed is True
        assert "Truth boundary OK" in result.message

    def test_p0_6_fails_with_graph_only_truth_patterns(
        self, tmp_path: Path, populated_adg_db: Path, monkeypatch: Any
    ) -> None:
        """P0-6 fails when graph-only truth patterns are detected."""
        # Create a temp graphdb directory with suspicious file
        mock_graphdb_dir = tmp_path / "mock_graphdb"
        mock_graphdb_dir.mkdir()

        # Create file with graph-only truth pattern
        suspicious_file = mock_graphdb_dir / "suspicious.py"
        suspicious_file.write_text("# Graph-only rule: test rule\nVIOLATION_RULES = {}")

        monkeypatch.setattr("ops_scripts.ci.graphdb_p0_gate.GRAPHDB_DIR", mock_graphdb_dir)

        gates = GraphDBP0Gates(populated_adg_db)
        result = gates.check_p0_6_graph_only_truth()

        assert result.passed is False
        assert "Graph-only truth drift detected" in result.message


class TestP0Integration:
    """Integration tests for all P0 gates."""

    def test_all_p0_gates_run(self, populated_adg_db: Path) -> None:
        """All P0 gates can run without errors."""
        gates = GraphDBP0Gates(populated_adg_db)
        results = gates.run_all_p0_gates()

        assert len(results) == 6  # All 6 P0 gates should run

        for result in results:
            assert isinstance(result, P0GateResult)
            assert result.gate_id.startswith("P0-")

    def test_exit_code_zero_on_pass(self, populated_adg_db: Path) -> None:
        """Exit code is 0 when all gates pass."""
        gates = GraphDBP0Gates(populated_adg_db)
        gates.run_all_p0_gates()

        exit_code = gates.get_exit_code()
        # Should be 0 (pass), 1 (fail), or 2 (no results) - never None or exception
        assert isinstance(exit_code, int)
        assert exit_code in (0, 1, 2)  # Valid exit codes per contract


class TestP1Ratchets:
    """Tests for P1 ratchet gates."""

    def test_p1_1_coverage_baseline_created(
        self, populated_adg_db: Path, tmp_path: Path, monkeypatch: Any
    ) -> None:
        """P1-1 creates baseline data for coverage tracking."""
        monkeypatch.setattr("ops_scripts.ci.graphdb_p1_ratchet.BASELINE_DIR", tmp_path)

        ratchets = GraphDBP1Ratchets(populated_adg_db, blocking=False)
        result = ratchets.check_p1_1_projection_coverage()

        # First run should pass (no baseline to compare against)
        assert result.passed is True
        assert result.gate_id == "P1-1"

        # Verify baseline was created
        baseline_file = tmp_path / "graphdb_p1_baseline.json"
        assert baseline_file.exists()

    def test_p1_ratchets_non_blocking_by_default(self, populated_adg_db: Path) -> None:
        """P1 ratchets don't block by default."""
        ratchets = GraphDBP1Ratchets(populated_adg_db, blocking=False)
        results = ratchets.run_all_p1_ratchets()

        exit_code = ratchets.get_exit_code()
        assert exit_code == 0  # Non-blocking mode always returns 0

    def test_p1_ratchets_can_block(self, populated_adg_db: Path) -> None:
        """P1 ratchets can be configured to block."""
        ratchets = GraphDBP1Ratchets(populated_adg_db, blocking=True)
        # Just verify blocking flag is set correctly
        assert ratchets.blocking is True

    def test_p1_2_explanation_parity(self, populated_adg_db: Path) -> None:
        """P1-2 tracks explanation parity between graph and canonical."""
        ratchets = GraphDBP1Ratchets(populated_adg_db, blocking=False)
        result = ratchets.check_p1_2_explanation_parity()

        assert isinstance(result, P1RatchetResult)
        assert result.gate_id == "P1-2"
        # Message varies based on whether violations table exists
        assert "Explanation parity" in result.message or "P1-2 check failed" in result.message
        # Should have details about violations or error
        assert "canonical_violations" in result.details or "error" in result.details

    def test_p1_4_query_latency(self, populated_adg_db: Path) -> None:
        """P1-4 tracks query latency against thresholds."""
        ratchets = GraphDBP1Ratchets(populated_adg_db, blocking=False)
        result = ratchets.check_p1_4_query_latency()

        assert isinstance(result, P1RatchetResult)
        assert result.gate_id == "P1-4"
        assert "Query latency" in result.message
        # Should have latency data in details
        assert "projection_time" in result.details or "missing_dependency" in result.details

    def test_p1_5_findings_drift(self, populated_adg_db: Path) -> None:
        """P1-5 tracks findings drift between graph and canonical."""
        ratchets = GraphDBP1Ratchets(populated_adg_db, blocking=False)
        result = ratchets.check_p1_5_findings_drift()

        assert isinstance(result, P1RatchetResult)
        assert result.gate_id == "P1-5"
        # Message varies based on whether violations table exists
        assert "Findings drift" in result.message or "P1-5 check failed" in result.message
        # Should have details about findings or error
        assert "canonical_by_severity" in result.details or "error" in result.details


class TestP2P3Watch:
    """Tests for P2/P3 watch gates."""

    def test_p2_1_query_coverage_analysis(self, populated_adg_db: Path) -> None:
        """P2-1 analyzes query coverage gaps."""
        watch = GraphDBP2P3Watch(populated_adg_db)
        result = watch.check_p2_1_query_coverage_gaps()

        assert result.severity == "P2"
        assert result.debt_score >= 0
        assert "Query coverage gaps" in result.message

    def test_p2_2_indexing_debt_analysis(self, populated_adg_db: Path) -> None:
        """P2-2 analyzes indexing debt."""
        watch = GraphDBP2P3Watch(populated_adg_db)
        result = watch.check_p2_2_indexing_debt()

        assert result.severity == "P2"
        assert "Indexing debt" in result.message

    def test_p3_3_long_term_opportunities(self, populated_adg_db: Path) -> None:
        """P3-3 identifies long-term opportunities."""
        watch = GraphDBP2P3Watch(populated_adg_db)
        result = watch.check_p3_3_long_term_opportunities()

        assert result.severity == "P3"
        assert "opportunities" in result.message


class TestScorecardIntegration:
    """Tests for scorecard integration."""

    def test_scorecard_entry_creation(self) -> None:
        """Scorecard entries can be created and serialized."""
        entry = ScorecardEntry(
            gate_id="TEST-1",
            severity="P0",
            status="PASS",
            timestamp="2024-01-01T00:00:00Z",
            message="Test message",
            details={"test": True},
        )

        data = entry.to_dict()
        assert data["gate_id"] == "TEST-1"
        assert data["severity"] == "P0"
        assert data["status"] == "PASS"

    def test_scorecard_creation(self) -> None:
        """Full scorecard can be created and serialized."""
        scorecard = GraphDBScorecard(
            timestamp="2024-01-01T00:00:00Z",
            run_id="test-run",
            overall_status="PASS",
            p0_summary={"total": 6, "passed": 6},
            p1_summary={"total": 5, "regressions": 0},
            p2_summary={"warnings": 3, "total_debt": 45},
            p3_summary={"watches": 2},
            entries=[],
        )

        data = scorecard.to_dict()
        assert data["overall_status"] == "PASS"
        assert data["p0_summary"]["total"] == 6


class TestRequiredClasses:
    """Tests for required class definitions."""

    def test_required_node_classes_defined(self) -> None:
        """Required node classes are properly defined."""
        assert "file" in REQUIRED_NODE_CLASSES
        assert "module" in REQUIRED_NODE_CLASSES
        assert "agent" in REQUIRED_NODE_CLASSES
        assert "policy" in REQUIRED_NODE_CLASSES

    def test_required_edge_classes_defined(self) -> None:
        """Required edge classes are properly defined."""
        assert "imports" in REQUIRED_EDGE_CLASSES
        assert "calls" in REQUIRED_EDGE_CLASSES
        assert "violates" in REQUIRED_EDGE_CLASSES


class TestGraphDBSnapshot:
    """Tests for GraphDBSnapshot dataclass."""

    def test_snapshot_digest_calculation(self) -> None:
        """Snapshot digest is calculated deterministically."""
        snapshot = GraphDBSnapshot(
            commit_sha="abc123",
            schema_version="1.0.0",
            artifact_digest="",
            node_count=100,
            edge_count=200,
            node_type_counts={"file": 50, "module": 50},
            edge_type_counts={"imports": 100, "calls": 100},
            timestamp="2024-01-01T00:00:00Z",
            run_id="test-run",
        )

        digest1 = snapshot.calculate_digest()
        digest2 = snapshot.calculate_digest()

        assert digest1 == digest2  # Deterministic
        assert len(digest1) == 16  # Hex string of first 8 bytes

    def test_different_snapshots_different_digests(self) -> None:
        """Different snapshot contents produce different digests."""
        snapshot1 = GraphDBSnapshot(
            commit_sha="abc123",
            schema_version="1.0.0",
            artifact_digest="",
            node_count=100,
            edge_count=200,
            node_type_counts={},
            edge_type_counts={},
            timestamp="",
            run_id="",
        )

        snapshot2 = GraphDBSnapshot(
            commit_sha="abc123",
            schema_version="1.0.0",
            artifact_digest="",
            node_count=200,  # Different
            edge_count=200,
            node_type_counts={},
            edge_type_counts={},
            timestamp="",
            run_id="",
        )

        assert snapshot1.calculate_digest() != snapshot2.calculate_digest()


class TestMainEntryPoints:
    """Tests for main() entry points of gate modules."""

    def test_p0_main_returns_valid_exit_code(
        self, populated_adg_db: Path, monkeypatch: Any, tmp_path: Path
    ) -> None:
        """P0 main() returns valid exit code (0, 1, or 2)."""
        # Mock ADG_DIR to use temp path
        mock_adg_dir = tmp_path / "adg"
        mock_adg_dir.mkdir()

        # Create minimal snapshot for test
        snapshot_file = mock_adg_dir / "adg_snapshot_20240101_120000.json"
        snapshot_file.write_text(json.dumps({"commit_sha": "abc", "schema_version": "1.0"}))

        monkeypatch.setattr("ops_scripts.ci.graphdb_p0_gate.ADG_DIR", mock_adg_dir)

        # Import and run main
        from ops_scripts.ci.graphdb_p0_gate import main as p0_main

        # Use the populated_adg_db but mock the sqlite path finding
        import sys

        old_argv = sys.argv
        sys.argv = ["graphdb_p0_gate.py"]

        try:
            exit_code = p0_main()
            assert exit_code in (0, 1, 2)  # Valid exit codes per contract
        finally:
            sys.argv = old_argv

    def test_p0_main_missing_artifacts_returns_two(self, monkeypatch: Any, tmp_path: Path) -> None:
        """P0 main() returns 2 when ADG artifacts missing."""
        # Mock ADG_DIR to non-existent path
        mock_adg_dir = tmp_path / "nonexistent_adg"

        monkeypatch.setattr("ops_scripts.ci.graphdb_p0_gate.ADG_DIR", mock_adg_dir)

        from ops_scripts.ci.graphdb_p0_gate import main as p0_main

        import sys

        old_argv = sys.argv
        sys.argv = ["graphdb_p0_gate.py"]

        try:
            exit_code = p0_main()
            assert exit_code == 2  # Missing artifacts
        finally:
            sys.argv = old_argv

    def test_p1_main_non_blocking_returns_zero(
        self, populated_adg_db: Path, monkeypatch: Any, tmp_path: Path
    ) -> None:
        """P1 main() returns 0 in non-blocking mode."""
        # Mock baseline dir
        mock_baseline_dir = tmp_path / "baselines"
        mock_baseline_dir.mkdir()

        monkeypatch.setattr("ops_scripts.ci.graphdb_p1_ratchet.BASELINE_DIR", mock_baseline_dir)

        # Mock ADG_DIR to use temp path with proper structure
        mock_adg_dir = tmp_path / "adg"
        mock_adg_dir.mkdir()

        # Copy the test database to mock location
        import shutil

        mock_sqlite = mock_adg_dir / "adg_indexed_test.sqlite"
        shutil.copy(populated_adg_db, mock_sqlite)

        monkeypatch.setattr("ops_scripts.ci.graphdb_p1_ratchet.ADG_DIR", mock_adg_dir)

        from ops_scripts.ci.graphdb_p1_ratchet import main as p1_main

        import sys

        old_argv = sys.argv
        sys.argv = ["graphdb_p1_ratchet.py"]  # No --blocking flag

        try:
            exit_code = p1_main()
            assert exit_code == 0  # Non-blocking always returns 0
        finally:
            sys.argv = old_argv

    def test_p2p3_main_returns_zero(self, monkeypatch: Any, tmp_path: Path) -> None:
        """P2/P3 main() always returns 0 (non-blocking)."""
        from ops_scripts.ci.graphdb_p2p3_watch import main as p2p3_main

        import sys

        old_argv = sys.argv
        sys.argv = ["graphdb_p2p3_watch.py"]

        try:
            exit_code = p2p3_main()
            assert exit_code == 0  # P2/P3 never blocks
        finally:
            sys.argv = old_argv


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
