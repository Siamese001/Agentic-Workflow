"""Tests for ADG CI gate base class."""

import json
import tempfile
from pathlib import Path

import pytest

from ops_scripts.ci.adg_gates.gate_base import (
    ADGGateBase,
    CI_RATchet_DIR,
    GateResult,
    GateViolation,
)


class MockGate(ADGGateBase):
    """Mock gate for testing."""

    gate_family = "mock_gate"
    severity = "P1"
    source_views = ["mv_test"]

    def _execute_gate_logic(self) -> GateResult:
        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id or "test_snapshot",
            timestamp="2026-01-01T00:00:00Z",
            status="passed",
            violations=[],
            summary={"test": True},
        )


class TestGateBase:
    """Test cases for ADGGateBase."""

    def test_init_finds_sqlite(self):
        """Test that gate initializes and finds SQLite."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock ADG structure
            adg_dir = Path(tmpdir) / "artifacts" / "adg"
            adg_dir.mkdir(parents=True)
            sqlite_file = adg_dir / "adg_indexed_20260101_1200.sqlite"
            sqlite_file.touch()

            gate = MockGate(sqlite_path=sqlite_file)
            assert gate.sqlite_path == sqlite_file

    def test_is_in_modified_area(self):
        """Test modified area detection."""
        gate = MockGate(modified_files=["src/core/module.py", "tests/test_core.py"])

        assert gate._is_in_modified_area("src/core/module.py") is True
        assert gate._is_in_modified_area("other/module.py") is False
        assert gate._is_in_modified_area(None) is False

    def test_save_and_load_baseline(self):
        """Test baseline persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Patch CI_RATchet_DIR
            import ops_scripts.ci.adg_gates.gate_base as base_module

            original_dir = base_module.CI_RATchet_DIR
            base_module.CI_RATchet_DIR = Path(tmpdir)

            try:
                gate = MockGate()
                test_data = {"count": 42, "threshold": 0.8}

                gate._save_baseline("test_gate", test_data)
                loaded = gate._load_baseline("test_gate")

                assert loaded == test_data
            finally:
                base_module.CI_RATchet_DIR = original_dir

    def test_save_and_load_trend(self):
        """Test trend persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import ops_scripts.ci.adg_gates.gate_base as base_module

            original_dir = base_module.CI_RATchet_DIR
            base_module.CI_RATchet_DIR = Path(tmpdir)

            try:
                gate = MockGate()
                test_data = {"history": [1, 2, 3], "consecutive_increases": 2}

                gate._save_trend("test_gate", test_data)
                loaded = gate._load_trend("test_gate")

                assert loaded == test_data
            finally:
                base_module.CI_RATchet_DIR = original_dir


class TestGateViolation:
    """Test cases for GateViolation dataclass."""

    def test_violation_creation(self):
        """Test creating a violation."""
        v = GateViolation(
            violation_id="v1",
            source_view="mv_test",
            source_node="node1",
            source_edge=None,
            file="test.py",
            line=42,
            layer_src="L0",
            layer_dst="L2",
            path_id="path1",
            first_illegal_hop="L0->L2",
            path_criticality=3.5,
            in_modified_area=True,
            message="Test violation",
        )

        assert v.violation_id == "v1"
        assert v.path_criticality == 3.5
        assert v.in_modified_area is True


class TestGateResult:
    """Test cases for GateResult dataclass."""

    def test_result_to_dict(self):
        """Test converting result to dict."""
        v = GateViolation(
            violation_id="v1",
            source_view="mv_test",
            source_node="node1",
            source_edge=None,
            file="test.py",
            line=42,
            layer_src="L0",
            layer_dst="L2",
            path_id=None,
            first_illegal_hop=None,
            path_criticality=2.0,
            in_modified_area=False,
            message="Test",
        )

        result = GateResult(
            gate_family="test",
            severity="P1",
            snapshot_id="snap1",
            timestamp="2026-01-01T00:00:00Z",
            status="blocked",
            violations=[v],
            summary={"count": 1},
        )

        d = result.to_dict()
        assert d["gate_family"] == "test"
        assert d["severity"] == "P1"
        assert d["status"] == "blocked"
        assert len(d["violations"]) == 1
        assert d["violations"][0]["violation_id"] == "v1"


class TestGateBaseAdvanced:
    """Advanced test cases for ADGGateBase edge cases and integration."""

    def test_find_latest_sqlite_multiple_files(self):
        """GAP 1: Test auto-discovery picks latest file when multiple exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adg_dir = Path(tmpdir) / "artifacts" / "adg"
            adg_dir.mkdir(parents=True)
            # Create multiple SQLite files with different timestamps
            (adg_dir / "adg_indexed_20260101_1200.sqlite").touch()
            (adg_dir / "adg_indexed_20260102_1300.sqlite").touch()
            latest = adg_dir / "adg_indexed_20260103_1400.sqlite"
            latest.touch()

            gate = MockGate()
            # Temporarily patch ADG_DIR
            import ops_scripts.ci.adg_gates.gate_base as base_module

            original_dir = base_module.ADG_DIR
            base_module.ADG_DIR = adg_dir
            try:
                found = gate._find_latest_sqlite()
                assert found == latest
            finally:
                base_module.ADG_DIR = original_dir

    def test_find_latest_sqlite_no_files_raises(self):
        """GAP 2: Test RuntimeError when no SQLite files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adg_dir = Path(tmpdir) / "artifacts" / "adg"
            adg_dir.mkdir(parents=True)

            gate = MockGate()
            import ops_scripts.ci.adg_gates.gate_base as base_module

            original_dir = base_module.ADG_DIR
            base_module.ADG_DIR = adg_dir
            try:
                with pytest.raises(RuntimeError, match="No ADG SQLite file found"):
                    gate._find_latest_sqlite()
            finally:
                base_module.ADG_DIR = original_dir

    def test_get_snapshot_id_no_meta_table(self):
        """GAP 4: Test _get_snapshot_id returns empty string when meta missing."""
        import sqlite3

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create SQLite file without meta table
            db_path = Path(tmpdir) / "test.db"
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE nodes (id TEXT)")  # Only nodes table
            conn.close()

            gate = MockGate(sqlite_path=db_path)
            gate._connect()
            snapshot_id = gate._get_snapshot_id()
            gate._close()
            assert snapshot_id == ""

    def test_write_artifacts_creates_files(self):
        """GAP 5: Test _write_artifacts creates expected files on disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import ops_scripts.ci.adg_gates.gate_base as base_module

            original_dir = base_module.CI_ARTIFACTS_DIR
            base_module.CI_ARTIFACTS_DIR = Path(tmpdir) / "artifacts"

            try:
                gate = MockGate()
                result = GateResult(
                    gate_family="test",
                    severity="P1",
                    snapshot_id="snap1",
                    timestamp="2026-01-01T00:00:00Z",
                    status="blocked",
                    violations=[],
                    summary={"count": 0},
                )

                artifact_dir = gate._write_artifacts(result)

                # Verify directory and files created
                assert artifact_dir.exists()
                assert (artifact_dir / "gate_test.json").exists()
                assert (artifact_dir / "gate_test_findings.txt").exists()
                assert (artifact_dir / "gate_test_provenance.json").exists()

                # Verify JSON content
                json_content = (artifact_dir / "gate_test.json").read_text()
                data = json.loads(json_content)
                assert data["gate_family"] == "test"
                assert data["status"] == "blocked"
            finally:
                base_module.CI_ARTIFACTS_DIR = original_dir

    def test_run_and_exit_blocked_returns_1(self):
        """GAP 6a: Test run_and_exit returns 1 when blocked."""

        class BlockingGate(ADGGateBase):
            gate_family = "blocking"
            severity = "P0"
            source_views = []

            def _execute_gate_logic(self):
                return GateResult(
                    gate_family="blocking",
                    severity="P0",
                    snapshot_id="snap",
                    timestamp="2026-01-01T00:00:00Z",
                    status="blocked",
                    violations=[
                        GateViolation(
                            violation_id="v1",
                            source_view="mv",
                            source_node=None,
                            source_edge=None,
                            file="test.py",
                            line=1,
                            layer_src=None,
                            layer_dst=None,
                            path_id=None,
                            first_illegal_hop=None,
                            path_criticality=1.0,
                            in_modified_area=False,
                            message="Test violation",
                        )
                    ],
                    summary={"blocked": True},
                )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal SQLite
            import sqlite3

            db_path = Path(tmpdir) / "test.db"
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE meta (key TEXT, value TEXT)")
            conn.execute("INSERT INTO meta VALUES ('commit_sha', 'abc123')")
            conn.commit()
            conn.close()

            gate = BlockingGate(sqlite_path=db_path)
            exit_code = gate.run_and_exit()
            assert exit_code == 1

    def test_run_and_exit_passed_returns_0(self):
        """GAP 6b: Test run_and_exit returns 0 when passed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import sqlite3

            db_path = Path(tmpdir) / "test.db"
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE meta (key TEXT, value TEXT)")
            conn.execute("INSERT INTO meta VALUES ('commit_sha', 'abc123')")
            conn.commit()
            conn.close()

            gate = MockGate(sqlite_path=db_path)
            exit_code = gate.run_and_exit()
            assert exit_code == 0

    def test_run_integration_connects_executes_closes(self):
        """GAP 7: Test run() properly connects, executes, and closes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import sqlite3

            db_path = Path(tmpdir) / "test.db"
            conn = sqlite3.connect(str(db_path))
            conn.execute("CREATE TABLE meta (key TEXT, value TEXT)")
            conn.execute("INSERT INTO meta VALUES ('commit_sha', 'test_snap')")
            conn.commit()
            conn.close()

            gate = MockGate(sqlite_path=db_path)
            # Connection should be None before run
            assert gate.conn is None

            result = gate.run(emit_artifacts=False)

            # Connection should be None after run (closed)
            assert gate.conn is None
            assert result.snapshot_id == "test_snap"
            assert result.status == "passed"
